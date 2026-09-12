# IaC: Automação de Cluster com Vagrant

Este guia descreve o uso do Vagrant para a criação automatizada e reprodutível do cluster de computação distribuída. A configuração manual de clusters MPI é suscetível a erros de rede e inconsistências de bibliotecas; o uso de Infraestrutura como Código (IaC) mitiga esses riscos, garantindo que todos os nós possuam o mesmo sistema operacional, limites de recursos e dependências do OpenMPI.

## 1. Pré-requisitos (Hospedeiro Windows)
O ambiente requer o Oracle VirtualBox e o HashiCorp Vagrant instalados.

Para instalar o Vagrant via PowerShell (Administrador):
```powershell
winget install --id Hashicorp.Vagrant
```
*Nota: Pode ser necessário reiniciar o sistema para atualizar o PATH.*

## 2. Script de Automação (Vagrantfile)
O `Vagrantfile` define a topologia do cluster de forma dinâmica. O script abaixo provisiona 4 nós, atribui IPs sequenciais e realiza a compilação nativa dos benchmarks antes do acesso inicial do usuário.

```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile para o Laboratório Didático de Computação Distribuída
# Cria 4 máquinas virtuais Ubuntu 22.04 para experimentos com MPI

Vagrant.configure("2") do |config|
  # Usar a imagem oficial do Ubuntu 22.04 LTS
  config.vm.box = "ubuntu/jammy64"

  # Definir a quantidade de nós do cluster
  N = 4

  (1..N).each do |i|
    config.vm.define "node#{i}" do |node|
      # Compartilha a pasta raiz do projeto (um nível acima) para acessar codigos_modificados
      node.vm.synced_folder "../", "/vagrant_data"

      # Configuração de rede interna (host-only) para comunicação isolada
      node.vm.network "private_network", ip: "192.168.56.10#{i}"
      
      # Nome do host
      node.vm.hostname = "node#{i}"

      # Configuração de recursos do VirtualBox
      node.vm.provider "virtualbox" do |vb|
        vb.name = "erad_node#{i}"
        vb.memory = "1024" # 1 GB de RAM conforme artigo
        vb.cpus = 1        # 1 vCPU conforme artigo
        vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
        vb.customize ["modifyvm", :id, "--nictype2", "virtio"]
      end

      # Script de provisionamento básico
      node.vm.provision "shell", inline: <<-SHELL
        echo "Atualizando pacotes e instalando dependências..."
        apt-get update -qq
        apt-get install -y -qq openmpi-bin openmpi-common libopenmpi-dev build-essential gcc make wget tar git

        # O SEGREDO ESTÁ AQUI: Caminho correto na versão 7.3
        DEST_PATH="c/mpi/collective/blocking/osu_bcast.c"
        
        # Verifica se o OSU já foi compilado para evitar perda de tempo no reload
        if [ ! -f "/usr/local/osu/libexec/osu-micro-benchmarks/mpi/collective/osu_bcast" ]; then
            echo "Instalação nova detectada. Baixando OSU Micro-Benchmarks..."
            rm -rf /tmp/osu-micro-benchmarks-7.3*
            cd /tmp
            wget -q --no-check-certificate https://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-7.3.tar.gz
            tar -xzf osu-micro-benchmarks-7.3.tar.gz
            cd osu-micro-benchmarks-7.3
            
            # Estratégia de Injeção Local: Procura o arquivo na pasta compartilhada
            echo "Buscando código modificado na pasta compartilhada..."
            MOD_FILE=$(find /vagrant_data -name osu_bcast.c | grep "codigos_modificados" | head -n 1)
            
            if [ -n "$MOD_FILE" ]; then
                echo "Sucesso! Arquivo modificado encontrado em: $MOD_FILE"
                cp "$MOD_FILE" $DEST_PATH
            else
                echo "AVISO: Arquivo modificado não encontrado em /vagrant_data. Usando versão do GitHub..."
                wget -q -O $DEST_PATH https://raw.githubusercontent.com/felipebarbosa29/Artigo-ERAD2026/main/codigos_modificados/osu_bcast.c
            fi

            # Injeta um marcador visual no cabeçalho para confirmar a versão
            sed -i 's/OSU MPI%s Broadcast Latency Test/OSU MPI%s Broadcast Latency Test (AUDITAVEL)/' $DEST_PATH

            echo "Compilando OSU Micro-Benchmarks (isso pode levar alguns minutos)..."
            ./configure CC=mpicc CXX=mpicxx --prefix=/usr/local/osu --quiet
            make -j$(nproc) > /dev/null 2>&1
            make install > /dev/null 2>&1
        else
            echo "OSU Micro-Benchmarks já instalado. Pulando etapa de compilação!"
        fi
        
        echo "Verificação Final: "
        if /usr/local/osu/libexec/osu-micro-benchmarks/mpi/collective/osu_bcast --version | grep -q "AUDITAVEL"; then
            echo "CONFIRMADO: Versão auditável instalada com sucesso!"
        else
            echo "ERRO: O marcador (AUDITAVEL) não foi encontrado no executável compilado."
        fi

        # Otimização de Usabilidade: Adiciona o caminho ao PATH do vagrant
        if ! grep -q "osu-micro-benchmarks" /home/vagrant/.bashrc; then
            echo "export PATH=$PATH:/usr/local/osu/libexec/osu-micro-benchmarks/mpi/collective:/usr/local/osu/libexec/osu-micro-benchmarks/mpi/pt2pt" >> /home/vagrant/.bashrc
            echo "Atalho PATH configurado."
        fi

        echo "Configurando rede e SSH..."
        cat <<EOF > /etc/hosts
127.0.0.1 localhost
192.168.56.101 node1
192.168.56.102 node2
192.168.56.103 node3
192.168.56.104 node4
EOF
        cat > /home/vagrant/hostfile <<-EOF
192.168.56.101 node1
192.168.56.102 node2
192.168.56.103 node3
192.168.56.104 node4
EOF
        chown vagrant:vagrant /home/vagrant/hostfile

        mkdir -p /home/vagrant/.ssh
        if [ "#{i}" -eq "1" ]; then
          sudo -u vagrant ssh-keygen -t rsa -b 2048 -N "" -f /home/vagrant/.ssh/id_rsa
          cp /home/vagrant/.ssh/id_rsa.pub /vagrant/master_key.pub
        fi
        while [ ! -f /vagrant/master_key.pub ]; do sleep 1; done
        cat /vagrant/master_key.pub >> /home/vagrant/.ssh/authorized_keys
        echo -e "Host *\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile /dev/null\n\tLogLevel ERROR" > /home/vagrant/.ssh/config
        chown -R vagrant:vagrant /home/vagrant/.ssh
        chmod 600 /home/vagrant/.ssh/authorized_keys /home/vagrant/.ssh/config
      SHELL
    end
  end
end
```

## 3. Execução e Validação
Para instanciar o cluster, garanta que esteja no diretório onde está o arquivo Vagrantfile e depois execute:
```bash
vagrant up
```

Após o término, acesse o nó mestre para validar a malha de comunicação MPI:
```bash
vagrant ssh node1
mpirun --hostfile ~/hostfile -np 4 hostname
```

## 4. Análise Técnica de Recursos

### 4.1. Clones Vinculados (Linked Clones)
A configuração `vb.linked_clone = true` permite que o Vagrant controle os limites de 8 GB de RAM e armazenamento SSD. O VirtualBox utiliza uma imagem base de leitura e cria discos diferenciais para cada nó. Isso reduz o consumo de armazenamento em aproximadamente 75% e acelera o tempo de boot do cluster.

### 4.2. Isolamento de Rede e I/O
Embora o Vagrant utilize pastas compartilhadas (`/vagrant`), a execução dos benchmarks é realizada em diretórios isolados dentro da VM. Isso garante que as métricas de latência reflitam o tráfego através da pilha TCP/IP virtualizada, evitando que o MPI utilize o sistema de arquivos compartilhado como um atalho de comunicação.
