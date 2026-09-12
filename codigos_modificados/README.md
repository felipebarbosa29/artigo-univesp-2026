# Códigos-Fonte Modificados

Este diretório contém versões customizadas dos benchmarks OSU Micro-Benchmarks
(v7.3) usados nos experimentos.

## Por que modificamos

Os benchmarks originais só mostram os tempos de execução. Nós adicionamos umas
linhas de código para que, antes de rodar o teste, cada processo informe em qual
máquina está rodando. Isso ajuda a conferir se o MPI distribuiu os processos
corretamente entre os nós.

## Arquivos

### 1. `osu_bcast.c`

- **O que foi feito:** Depois do `MPI_Init`, adicionamos código que pega o nome
  da máquina (`gethostname`), sincroniza todos os processos (`MPI_Barrier`) e
  imprime o Rank e o Hostname de cada um.
- **No terminal aparece:** `[Virtual Box TOPO] Rank 0 -> node1`
- **Pra quê:** Confirmar que os processos estão distribuídos nas 4 VMs antes de
  começar a medir.

### 2. `osu_latency.c`

- **O que foi feito:** Mesma lógica de identificação de host.
- **Pra quê:** Confirmar que, no teste AWS, o Rank 0 está na Virgínia e o
  Rank 1 no Oregon (ou vice-versa).

## Importante

Essas modificações só adicionam prints no início da execução. A parte que mede
os tempos continua igual ao código original — não mexemos na lógica de medição.

## Como compilar

Substitua os arquivos originais nos diretórios do OSU Benchmark e compile:

```
./configure CC=mpicc --prefix=/usr/local
make
sudo make install
```
