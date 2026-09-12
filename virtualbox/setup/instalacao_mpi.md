# Guia de Instalação e Configuração: OpenMPI

Este documento descreve os procedimentos técnicos para a instalação e a execução dos experimentos de computação distribuída.

## 1. Dependências do Sistema
A instalação deve ser realizada em todos os nós do cluster (Master e Workers). O ambiente base utilizado foi Ubuntu 22.04 LTS / 24.04 LTS.

```bash
# Atualização de repositórios e instalação do compilador e bibliotecas MPI
sudo apt update
sudo apt install -y build-essential openmpi-bin openmpi-common libopenmpi-dev
```

## 2. Verificação da Instalação
Para validar se o ambiente está operacional e reconhecendo os compiladores MPI:

```bash
mpicc --version
mpirun --version
```

## 3. Configuração de Chaves SSH (Inter-node Communication)
O OpenMPI utiliza SSH para o lançamento de processos remotos. É mandatório que o nó Master possua acesso sem senha a todos os Workers.

1. Gerar par de chaves no Master:
   ```bash
   ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa
   ```
2. Distribuir a chave pública para os Workers:
   ```bash
   ssh-copy-id usuario@<IP_DO_WORKER>
   ```

## 4. Compilação dos Benchmarks
Os benchmarks da suíte OSU devem ser compilados nativamente para garantir o uso das bibliotecas do sistema:

```bash
mpicc -O3 osu_latency.c -o osu_latency
mpicc -O3 osu_bcast.c -o osu_bcast
```
*Nota: A flag `-O3` é utilizada para otimização de performance do binário.*