# Ambiente Local (VirtualBox)

Este diretório contém os recursos para montar e testar um cluster local com
VirtualBox e Vagrant. No VirtualBox, executamos o benchmark `osu_bcast`, que faz
uso da operação coletiva Broadcast (`MPI_Bcast`).

## Requisitos de Sistema

O laboratório foi montado em uma máquina com 32 GB de RAM, SSD de 500 GB,
processador Intel Core i7-1165G7, executando Windows 11.

| Componente | RAM (GB) | Disco (GB) |
|---|---|---|
| Windows (Hospedeiro) | 4,0 | 64,0 |
| 4 VMs Ubuntu (1 GB) | 3,5 – 4,0 | 37,0 |
| Gerenciamento | 0,5 | 0,2 – 0,3 |
| **Total Estimado** | **8,0 – 8,5** | **101,2 – 101,3** |

## 1. Montagem do Cluster

O `Vagrantfile` define as 4 máquinas virtuais, configura a rede interna e
instala as dependências (OpenMPI e OSU Micro-Benchmarks). Ele também injeta os
códigos modificados durante a compilação.

### Como subir o ambiente

1. Abra o PowerShell como Administrador e navegue até esta pasta onde está o Vagranfile.
2. Execute:

```
vagrant up
```

O Vagrant vai baixar a imagem do Ubuntu e configurar tudo automaticamente.
Aguarde a conclusão dos 4 nós (node1, node2, node3, node4).

### Gerenciando o Laboratório

Principais comando para gerenciar o ambiente:

- **Ligar:** `vagrant up`
- **Desligar:** `vagrant halt`
- **Apagar tudo:** `vagrant destroy -f`

## 2. Execução do Teste

O `osu_bcast` mede o tempo médio de execução da operação Broadcast para
diferentes tamanhos de mensagem.

### Como rodar (código modificado)

1. Acesse o nó principal:

```
vagrant ssh node1
```

2. Execute o benchmark:

```
mpirun -np 4 --hostfile ~/hostfile --oversubscribe \
  --mca btl tcp,self --mca btl_tcp_if_include enp0s8 \
  --mca mpi_yield_when_idle 1 \
  /usr/local/osu/libexec/osu-micro-benchmarks/mpi/collective/osu_bcast
```

Ao rodar, o cabeçalho mostra linhas `[Virtual Box TOPO]` indicando qual VM
está processando cada Rank.

### Parâmetros do mpirun

- `-np 4`: Lança 4 processos MPI (1 por nó). Use 8 ou 16 para outros testes.
- `--hostfile ~/hostfile`: Lista de IPs das máquinas virtuais.
- `--oversubscribe`: Permite rodar mais processos do que núcleos de CPU.
- `--mca btl_tcp_if_include enp0s8`: Força o uso da rede interna do VirtualBox.
- `--mca mpi_yield_when_idle 1`: Libera a CPU quando o processo MPI está
  esperando, evitando que trave o hospedeiro.

## 3. Dados e Gráficos

Os resultados estão em `dados/dados_vbox.csv`. Para gerar o gráfico da Figura 1
do artigo:

1. Instale as dependências: `pip install matplotlib pandas`
2. Entre na pasta: `cd virtualbox/scripts/`
3. Execute: `python3 plot_latencia.py`

Os gráficos são gerados na pasta `virtualbox/graficos/`.

![Broadcast no VirtualBox](graficos/chart_osu_bcast.png)
