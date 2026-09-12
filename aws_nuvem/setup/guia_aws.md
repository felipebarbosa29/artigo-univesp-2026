# Guia de Configuração: Ambiente em Nuvem (AWS)

Este documento descreve o passo a passo para configurar o ambiente de computação distribuída utilizando a infraestrutura da AWS. O foco aqui é a medição de latência entre redes geograficamente distantes.

## 1. Infraestrutura de Rede
Para este experimento, não utilizamos a internet pública para a comunicação MPI. Em vez disso, configuramos **redes virtuais privadas** interconectadas.

*   **Região A:** Virgínia do Norte (`us-east-1`) - Rede Privada 172.31.0.0/16
*   **Região B:** Oregon (`us-west-2`) - Rede Privada 10.0.0.0/16
*   **Conectividade:** As duas redes foram interconectadas via um túnel de comunicação privada, permitindo que as instâncias se "enxerguem" via IP privado, reduzindo a sobrecarga de segurança.

## 2. Configuração das Máquinas Virtuais
Utilizamos instâncias `t2.micro` (Free Tier) com Ubuntu 24.04 LTS.
*   **Segurança (Firewall):** É necessário liberar o tráfego TCP nas portas utilizadas pelo OpenMPI (faixa dinâmica) dentro das redes privadas.
*   **Identificação:** Cada nó deve ter o arquivo `/etc/hosts` atualizado com o IP privado do nó remoto para facilitar a resolução de nomes.

## 3. Instalação do OpenMPI
Execute em ambos os nós:
```bash
sudo apt update && sudo apt install build-essential openmpi-bin libopenmpi-dev -y
```

## 4. Desafio Técnico: Latência Inter-regional
O grande desafio deste experimento é configurar o roteamento para que o OpenMPI utilize a interface de rede correta. Se o MPI tentar usar o IP público, a latência será inconsistente e o firewall poderá bloquear o tráfego.

**Comando de Execução:**
```bash
mpirun --hostfile hostfile_aws \
  --mca pml ob1 \
  --mca btl tcp,self \
  --mca btl_tcp_if_include 172.31.0.0/16,10.0.0.0/16 \
  ./osu_latency
```
*O parâmetro `btl_tcp_if_include` garante que o tráfego fique restrito às nossas redes virtuais privadas.*
