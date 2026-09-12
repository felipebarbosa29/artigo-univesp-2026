# Automação do Cluster Local (VirtualBox + Vagrant)

Este guia descreve como utilizar o Vagrant para criar um cluster de 4 nós de forma automática, garantindo que o ambiente de estudo seja idêntico ao descrito no artigo.

## 1. Por que usar Automação (IaC)?
A configuração manual de 4 máquinas virtuais é demorada e sujeita a erros (IPs errados, falta de bibliotecas). O Vagrant resolve isso através de um script (`Vagrantfile`) que define toda a infraestrutura como código.

## 2. Gerenciamento de Recursos
Este laboratório foi projetado para rodar em computadores comuns de alunos da UNIVESP. O cálculo de viabilidade é:
*   **Sistema Hospedeiro (Windows):** 2,0 GB
*   **Cluster (4 VMs x 1 GB):** 4,0 GB
*   **Software de Virtualização:** 0,5 GB
*   **Total:** **6,5 GB**

Isso deixa uma margem de segurança de **1,5 GB** em máquinas com 8 GB de RAM, permitindo que o aluno navegue no material de aula enquanto o cluster executa.

## 3. Comandos:
Para subir o cluster completo:
```bash
vagrant up
```

Para acessar o nó mestre:
```bash
vagrant ssh node1
```

## 4. Experimento de Broadcast
Dentro do cluster, o teste de broadcast avalia como o tempo de comunicação cresce com o aumento de processos:
```bash
mpirun --hostfile hostfile -np 4 ./osu_bcast
```
