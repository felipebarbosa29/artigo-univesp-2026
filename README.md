# Laboratório Didático de Computação Distribuída em EAD

Este repositório reúne os scripts, dados e códigos do artigo **"Laboratório Didático de Computação Distribuída em EAD: Estudo de Caso com VirtualBox e AWS"**, submetido ao **Congresso da UNIVESP 2026**.

O trabalho propõe dois ambientes de baixo custo para ensinar computação distribuída a distância:

- um **cluster local** com VirtualBox e Vagrant, executado em um único computador;
- um **cenário em nuvem** com AWS, usando instâncias em regiões diferentes.

Em cada ambiente, a comunicação é demonstrada com o **OSU Micro-Benchmarks**:

- `osu_bcast`: operação coletiva de broadcast no cluster local;
- `osu_latency`: latência ponto a ponto na nuvem, comparando comunicação local e inter-regional.

## Objetivo

Mostrar que é possível praticar conceitos de computação distribuída sem laboratório físico dedicado, com ênfase em dois pontos:

1. **Reprodutibilidade**: o ambiente é descrito em um `Vagrantfile` e recriado por um único comando.
2. **Economia de tempo**: a montagem manual das quatro máquinas levou de **2 a 3 horas**, enquanto a recriação com a receita pronta levou de **15 a 20 minutos**.

## Estrutura do repositório

| Diretório | Conteúdo |
|---|---|
| [`virtualbox/`](virtualbox/README.md) | Receita Vagrant, scripts de coleta e análise, dados e gráficos do cluster local. |
| [`aws_nuvem/`](aws_nuvem/README.md) | Configuração das instâncias EC2 e teste de latência entre regiões. |
| [`codigos_modificados/`](codigos_modificados/README.md) | Versões do OSU com identificação dos nós. |

## Especificações dos ambientes

| Recurso | VirtualBox (local) | AWS (nuvem) |
|---|---|---|
| Máquinas | 4 VMs | 2 instâncias |
| Processador | 1, 2 ou 4 vCPUs por VM | 1 vCPU por instância |
| Memória | 1 GB por VM | 1 GB por instância |
| Sistema operacional | Ubuntu 22.04 | Ubuntu 22.04 |
| Rede | rede interna do VirtualBox | VPC Peering entre regiões |

No cluster local, o número total de processos MPI foi fixado em 16 (quatro por VM), variando apenas a quantidade de vCPUs.

## Recursos do laboratório local

O experimento foi executado em um computador com Intel Core i7-1165G7 (quatro núcleos, oito threads), 32 GB de RAM e SSD, com Windows 11.

O consumo do laboratório foi medido comparando o computador sem VMs, com uma VM e com quatro VMs ligadas. O uso do próprio Windows foi tratado como linha de base e não atribuído ao laboratório.

| Situação | RAM adicional | Disco ocupado |
|---|---:|---:|
| 1 VM ligada | ~0,89 GB | ~9,55 GB |
| 4 VMs ligadas | ~3,57 GB | ~38,18 GB |

Cada VM acrescentou cerca de 0,89 GB de RAM e 9,55 GB de disco. O disco inclui Ubuntu, Open MPI, OSU e os scripts. A coleta pode ser reproduzida pelo script `virtualbox/scripts/coletar_recursos.ps1`.

As ferramentas de virtualização ocuparam um espaço fixo adicional: VirtualBox (~0,23 GB), Vagrant (~0,98 GB) e a imagem Ubuntu em cache (~0,61 GB).

## Como reproduzir

Cluster local:

```powershell
cd virtualbox
$env:LAB_NODES='4'; $env:VAGRANT_CPUS='1'
vagrant up --no-parallel

## Autores

Este trabalho foi desenvolvido por Felipe Barbosa da Silva sob orientação do
Prof. Dr. Mauricio G. Palma, como parte de Iniciação Científica na Universidade
Virtual do Estado de São Paulo (UNIVESP).