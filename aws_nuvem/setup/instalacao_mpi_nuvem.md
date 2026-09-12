## Guia de Configuração do Ambiente OpenMPI
Este documento fornece um guia passo a passo para configurar o ambiente necessário para executar cargas de trabalho MPI. Garantir uma configuração adequada é crítico para a reprodutibilidade, permitindo que os benchmarks rodem em diferentes ambientes de teste (WSL2, VirtualBox e AWS EC2) sob configurações idênticas.

## 1. Requisitos do Sistema
Sistema Operacional: Ubuntu 24.04 LTS (versão Server é preferível para VMs/Nuvem).

Middleware MPI: OpenMPI v4.1.x.

Topologia do Cluster: Um mínimo de 2 a 4 nós conectados à mesma sub-rede privada.

## 2. Instalando os Pacotes Base
Execute estes comandos em todos os nós do seu cluster para atualizar os repositórios do sistema, instalar as ferramentas de compilação necessárias e configurar as bibliotecas de desenvolvimento do OpenMPI.

```Bash
sudo apt update && sudo apt install build-essential openmpi-bin openmpi-common libopenmpi-dev -y
```
## 3. Configuração de SSH sem Senha
O orquestrador do OpenMPI (mpirun) utiliza SSH para criar processos remotos nos nós trabalhadores (worker nodes). Para evitar que o sistema solicite senhas durante a execução, você deve estabelecer uma relação de confiança via SSH do nó mestre (master node, ex: server1) para todos os outros nós.

No nó mestre, gere um par de chaves SSH (pressione Enter para aceitar os valores padrão):

```Bash
ssh-keygen -t rsa
```
Em seguida, distribua a chave pública para todos os nós do cluster (incluindo o próprio nó mestre, para permitir o mapeamento de execução local).

Nota: Os comandos abaixo são um exemplo usando o utilitário padrão do Linux ssh-copy-id, que é comum em ambientes Bash. Dependendo do seu sistema operacional, terminal ou provedor de nuvem (como a AWS, que desativa a autenticação por senha por padrão), este comando pode falhar. Nesses casos, você deve copiar manualmente o conteúdo de ~/.ssh/id_rsa.pub do nó mestre e anexá-lo ao arquivo ~/.ssh/authorized_keys em cada nó trabalhador.

Exemplo (Abordagem padrão Linux/Bash):

```Bash
ssh-copy-id username@server1
ssh-copy-id username@server2
ssh-copy-id username@server3
ssh-copy-id username@server4
```
Verificação: Teste a conexão executando ssh username@server2. Se o login for feito sem solicitar uma senha, sua configuração de SSH está correta.

## 4. Definindo o Hostfile
O hostfile informa ao OpenMPI quais nós estão disponíveis e quantos slots de processo (núcleos de CPU) estão alocados para cada máquina. Crie um arquivo chamado hostfile ou mpi_hosts no diretório raiz do seu projeto no nó mestre:

Plaintext
server1 slots=2
server2 slots=2
server3 slots=2
server4 slots=2

## 5. Verificando o Cluster
Antes de executar os testes principais, compile e rode um programa simples hello_world.c para garantir que o roteamento de rede e o mapeamento de processos estejam funcionando corretamente em todas as instâncias.

```hello_world.c
C
#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) {
    // Inicializa o ambiente MPI
    MPI_Init(&argc, &argv);

    // Pega o número total de processos e o ID (rank) deste processo
    int world_rank, world_size;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    // Pega o nome da máquina (hostname)
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;
    MPI_Get_processor_name(processor_name, &name_len);

    // Imprime o resultado formatado
    printf("Executando na máquina: %s | Rank %d de %d\n", processor_name, world_rank, world_size);
    
    // Sincroniza os processos
    MPI_Barrier(MPI_COMM_WORLD);

    // Finaliza o MPI
    MPI_Finalize();
    return 0;
}
```
Compile o código de verificação:

```Bash
mpicc hello_world.c -o hello_world
```
Execute através dos nós, forçando o tráfego pela rede entre eles:

```Bash
mpirun --hostfile hostfile --map-by node -np 4 ./hello_world
```
Nota: Se a execução travar em ambientes de nuvem, exclua a interface de loopback anexando --mca btl_tcp_if_exclude lo --mca oob_tcp_if_exclude lo ao seu comando.

Se a saída exibir as mensagens padrão de "hello" contendo os diferentes números de rank vinculados com sucesso aos seus respectivos hostnames (server1, server2, etc.), o ambiente do seu cluster está validado e pronto para os benchmarks.