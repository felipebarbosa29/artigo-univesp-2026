# Laboratório Didático de Computação Distribuída em EAD

Este repositório contém os scripts, dados e códigos referentes ao artigo
"Laboratório Didático de Computação Distribuída em EAD: Estudo de Caso com
VirtualBox e AWS", submetido à Escola Regional de Alto Desempenho de São Paulo
(ERAD-SP 2026).

O artigo apresenta dois ambientes para o ensino de computação distribuída em
cursos a distância: um cluster local com VirtualBox e um cenário em nuvem com
AWS. Demonstramos o uso de cada ambiente com um benchmark da OSU
Micro-Benchmarks: o `osu_bcast` para uma operação coletiva no cluster local, e o
`osu_latency` para medir latência ponto a ponto na nuvem, comparando comunicação
local e inter-regional.

## Estrutura do Repositório

1. [Ambiente Local (VirtualBox)](virtualbox/README.md): Scripts de provisionamento
   (Vagrantfile) para criar um cluster de 4 nós e executar o teste de Broadcast.
2. [Ambiente em Nuvem (AWS)](aws_nuvem/README.md): Instruções para configurar
   instâncias EC2 em regiões distintas e executar o teste de latência.
3. [Códigos Modificados](codigos_modificados/README.md): Versões customizadas dos
   benchmarks OSU com identificação dos nós.

## Especificações dos Ambientes

| Recurso | VirtualBox (Local) | AWS (Nuvem) |
|---|---|---|
| Quantidade | 4 máquinas virtuais | 2 máquinas virtuais |
| Processador | 1 vCPU por máquina | 1 vCPU por máquina |
| Memória | 1 GB por máquina | 1 GB por máquina |
| Sistema Operacional | Ubuntu 22.04 Server | Ubuntu 22.04 Server |

### Requisitos para o Laboratório Local (VirtualBox)

| Componente | RAM (GB) | Disco (GB) |
|---|---|---|
| Windows 11 (base) | 4,0 | 64,0 |
| 4 VMs Ubuntu (1 GB cada) | 3,5 – 4,0 | 37,0 |
| Gerenciamento VBox/Rede | 0,5 | 0,2 – 0,3 |
| **Total Estimado** | **8,0 – 8,5** | **101,2 – 101,3** |

O laboratório foi montado em uma máquina com 32 GB de RAM, SSD de 500 GB,
processador Intel Core i7-1165G7, executando Windows 11.

## Autores

Este trabalho foi desenvolvido por Felipe Barbosa da Silva sob orientação do
Prof. Dr. Mauricio G. Palma, como parte de Iniciação Científica na Universidade
Virtual do Estado de São Paulo (UNIVESP).