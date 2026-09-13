# Ambiente local com VirtualBox e Vagrant

Esta pasta contém a configuração e os resultados do laboratório local usado no experimento MPI Broadcast. A nuvem está documentada separadamente em `aws_nuvem/` e não faz parte deste cenário.

## Estrutura do cluster

| Nó | Hostname | IP host-only | Processos MPI |
|---:|---|---|---:|
| 1 | `mpi-node1` | `192.168.56.101` | 4 |
| 2 | `mpi-node2` | `192.168.56.102` | 4 |
| 3 | `mpi-node3` | `192.168.56.103` | 4 |
| 4 | `mpi-node4` | `192.168.56.104` | 4 |

O teste usa 16 processos MPI, quatro em cada VM. A quantidade de vCPUs é alterada entre 1, 2 e 4 por VM.

## Requisitos

O laboratório foi executado em um computador com Windows 11, processador Intel Core i7-1165G7, oito processadores lógicos, 32 GB de RAM, VirtualBox e Vagrant. As VMs manuais antigas devem estar desligadas para não ocupar os mesmos endereços IP.

A imagem usada é Ubuntu 22.04 (`ubuntu/jammy64`). Cada VM recebe 1 GB de RAM por padrão. O limite de execução do VirtualBox é controlado pela variável `VAGRANT_CPU_CAP`.

## Criar o ambiente

Abra o PowerShell na pasta `virtualbox/` e execute:

```powershell
$env:LAB_NODES="4"
$env:VAGRANT_CPUS="1"
$env:VAGRANT_MEMORY="1024"
$env:VAGRANT_CPU_CAP="40"
$env:MPI_PROCS_PER_NODE="4"
vagrant up --no-parallel
```

Use `VAGRANT_CPU_CAP="50"` somente se esse for o valor definido no protocolo da coleta. O mesmo valor deve aparecer no artigo e ser mantido nas três configurações.

O provisionamento instala Open MPI, compila o OSU Micro-Benchmarks 7.3, configura a rede privada, cria o `hostfile` e prepara o acesso SSH entre os nós. Em redes com inspeção HTTPS, o download do OSU usa a alternativa prevista no `Vagrantfile`.

## Alterar a quantidade de vCPUs

Depois de criar o ambiente, altere a variável no PowerShell e reprovisione as VMs:

```powershell
$env:VAGRANT_CPUS="2"
vagrant reload --provision --no-parallel

$env:VAGRANT_CPUS="4"
vagrant reload --provision --no-parallel
```

## Validar a configuração

```powershell
vagrant status
vagrant ssh mpi-node1 -c "hostname; hostname -I; nproc"
vagrant ssh mpi-node2 -c "hostname; hostname -I; nproc"
vagrant ssh mpi-node3 -c "hostname; hostname -I; nproc"
vagrant ssh mpi-node4 -c "hostname; hostname -I; nproc"
```

Dentro de `mpi-node1`, confirme a distribuição dos processos:

```bash
cat ~/hostfile
mpirun -np 16 \
  --hostfile ~/hostfile \
  --map-by ppr:4:node \
  --bind-to none \
  --oversubscribe \
  hostname
```

O resultado deve apresentar quatro processos em cada nó.

## Executar o experimento

O `Vagrantfile` prepara a infraestrutura. O protocolo de coleta está separado em `scripts/run_bcast_mpi.sh`.

Dentro de `mpi-node1`, execute:

```powershell
vagrant ssh mpi-node1
```

Na VM:

```bash
cp /vagrant_data/run_bcast_mpi.sh "$HOME/run_bcast_mpi.sh"
chmod +x "$HOME/run_bcast_mpi.sh"
```

Execute uma configuração por vez:

```bash
"$HOME/run_bcast_mpi.sh" 1
"$HOME/run_bcast_mpi.sh" 2
"$HOME/run_bcast_mpi.sh" 4
```

O script executa três rodadas, 21 tamanhos de mensagem de 1 byte a 1 MiB, 100 iterações por tamanho e 20 iterações de aquecimento. Cada tamanho é executado em uma chamada MPI separada. Os parâmetros de rede e de distribuição são os mesmos usados no protocolo manual: `pml ob1`, `self,vader,tcp`, rede `192.168.56.0/24`, portas 20000–20999, quatro processos por nó, `--bind-to none` e `--oversubscribe`.

Os logs ficam em:

```text
$HOME/resultados_ic/grupo5_broadcast_vcpu_vagrant/vcpu1/
$HOME/resultados_ic/grupo5_broadcast_vcpu_vagrant/vcpu2/
$HOME/resultados_ic/grupo5_broadcast_vcpu_vagrant/vcpu4/
```

## Análise dos resultados

O script `scripts/analisar_bcast.py` consolida nove logs válidos, três rodadas para cada configuração, e gera as medianas por tamanho de mensagem.

Os CSVs consolidados estão em `dados/consolidado/`. O principal arquivo é:

```text
dados/consolidado/resumo_por_tamanho.csv
```

Para gerar novamente o gráfico compacto usado no artigo:

```bash
python3 scripts/grafico_layout_artigo.py \
  dados/consolidado/resumo_por_tamanho.csv \
  graficos/grafico_broadcast_vcpu_medianas.png
```

Os arquivos `comparacao_por_tamanho.csv`, `resumo_global_por_vcpu.csv`, `dados_brutos_normalizados.csv` e `validacao_arquivos.csv` apoiam a conferência dos resultados.

## Gerenciamento

```powershell
vagrant halt
vagrant destroy -f
```

`vagrant destroy -f` remove somente as VMs gerenciadas por esta pasta. Ele não remove VMs antigas criadas manualmente no VirtualBox.
