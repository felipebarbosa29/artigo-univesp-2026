# Guia rápido do laboratório VirtualBox

O laboratório local usa quatro VMs Ubuntu 22.04 conectadas por uma rede host-only:

| Nó | IP | vCPUs |
|---:|---|---:|
| `mpi-node1` | `192.168.56.101` | 1, 2 ou 4 |
| `mpi-node2` | `192.168.56.102` | 1, 2 ou 4 |
| `mpi-node3` | `192.168.56.103` | 1, 2 ou 4 |
| `mpi-node4` | `192.168.56.104` | 1, 2 ou 4 |

São utilizados 16 processos MPI, quatro por nó.

## Subir as VMs

Na pasta `virtualbox/`, execute no PowerShell:

```powershell
$env:VAGRANT_CPUS="1"
$env:VAGRANT_MEMORY="1024"
$env:VAGRANT_CPU_CAP="40"
vagrant up --no-parallel
```

## Conferir a distribuição

```powershell
vagrant ssh mpi-node1
```

Dentro da VM:

```bash
cat ~/hostfile
mpirun -np 16 --hostfile ~/hostfile --map-by ppr:4:node --bind-to none --oversubscribe hostname
```

## Executar a coleta

```bash
cp /vagrant_data/run_bcast_mpi.sh "$HOME/run_bcast_mpi.sh"
chmod +x "$HOME/run_bcast_mpi.sh"
"$HOME/run_bcast_mpi.sh" 1
```

Para repetir com 2 ou 4 vCPUs, altere `VAGRANT_CPUS` no PowerShell e execute `vagrant reload --provision --no-parallel` antes de chamar o script com o número correspondente.

O script testa mensagens de 1 byte a 1 MiB em três rodadas, com 100 iterações por tamanho. A análise posterior gera `dados/consolidado/resumo_por_tamanho.csv`.
