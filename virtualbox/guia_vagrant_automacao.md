# Guia de automação do laboratório MPI

Este guia descreve a criação do cluster local com quatro VMs Ubuntu 22.04. A configuração da nuvem está documentada separadamente em `aws_nuvem/`.

## Nós do cluster

| Nó | Hostname | IP host-only | Slots MPI |
|---:|---|---|---:|
| 1 | `mpi-node1` | `192.168.56.101` | 4 |
| 2 | `mpi-node2` | `192.168.56.102` | 4 |
| 3 | `mpi-node3` | `192.168.56.103` | 4 |
| 4 | `mpi-node4` | `192.168.56.104` | 4 |

O protocolo usa 16 processos MPI, quatro por nó.

## Pré-requisitos

Instale VirtualBox e Vagrant no Windows. Desligue as VMs manuais antigas antes de iniciar este ambiente, pois elas usam a mesma faixa `192.168.56.101`–`192.168.56.104`.

## Criar o cluster

Abra o PowerShell na pasta `virtualbox/`:

```powershell
$env:LAB_NODES="4"
$env:VAGRANT_CPUS="1"
$env:VAGRANT_MEMORY="1024"
$env:VAGRANT_CPU_CAP="40"
$env:MPI_PROCS_PER_NODE="4"
vagrant up --no-parallel
```

O `Vagrantfile` instala Open MPI e OSU Micro-Benchmarks 7.3, configura a rede host-only, cria o `hostfile` e prepara o SSH entre os nós.

## Validar o cluster

```powershell
vagrant status
vagrant ssh mpi-node1 -c "hostname; hostname -I; nproc"
vagrant ssh mpi-node1
```

Dentro de `mpi-node1`:

```bash
cat ~/hostfile
mpirun -np 16 --hostfile ~/hostfile --map-by ppr:4:node --bind-to none --oversubscribe hostname
```

O resultado deve apresentar quatro processos em cada nó.

## Configurações de vCPU

A coleta é realizada separadamente com 1, 2 e 4 vCPUs por VM:

```powershell
$env:VAGRANT_CPUS="2"
vagrant reload --provision --no-parallel

$env:VAGRANT_CPUS="4"
vagrant reload --provision --no-parallel
```

O valor de `VAGRANT_CPU_CAP` deve ser o mesmo nas três configurações e no artigo.

## Executar o benchmark

A infraestrutura e o protocolo de medição são separados. O `Vagrantfile` prepara o cluster; o script `scripts/run_bcast_mpi.sh` executa a coleta.

Dentro de `mpi-node1`:

```bash
cp /vagrant_data/run_bcast_mpi.sh "$HOME/run_bcast_mpi.sh"
chmod +x "$HOME/run_bcast_mpi.sh"
"$HOME/run_bcast_mpi.sh" 1
"$HOME/run_bcast_mpi.sh" 2
"$HOME/run_bcast_mpi.sh" 4
```

O script executa três rodadas, 21 tamanhos de mensagem de 1 byte a 1 MiB, 100 iterações por tamanho e 20 iterações de aquecimento. Os resultados são salvos em `~/resultados_ic/`.

## Gerenciamento

```powershell
vagrant halt
vagrant destroy -f
```

`vagrant destroy -f` remove somente as VMs gerenciadas por esta pasta.
