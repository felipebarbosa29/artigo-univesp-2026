# Análise dos resultados MPI Broadcast

## Arquivos principais

O script `analisar_bcast.py` lê os nove arquivos brutos válidos, correspondentes a três rodadas para cada configuração de 1, 2 e 4 vCPUs. A entrada esperada é uma pasta com esta estrutura:

```text
resultados_brutos/
├── vcpu1/
│   ├── bcast_*_1vcpu_*_rodada1.txt
│   ├── bcast_*_1vcpu_*_rodada2.txt
│   └── bcast_*_1vcpu_*_rodada3.txt
├── vcpu2/
└── vcpu4/
```

O script gera, entre outros arquivos, `resumo_por_tamanho.csv`, que é o CSV consolidado usado pelos gráficos. Esse é o arquivo que deve ser publicado para permitir a leitura dos dados já consolidados.

## CSVs recomendados para o repositório

| Arquivo | Uso |
|---|---|
| `resumo_por_tamanho.csv` | Principal CSV consolidado; contém as medianas por tamanho e configuração. |
| `comparacao_por_tamanho.csv` | Tabela derivada que identifica a melhor configuração em cada tamanho. |
| `resumo_global_por_vcpu.csv` | Resumo global por quantidade de vCPUs. |
| `dados_brutos_normalizados.csv` | Dados normalizados das nove rodadas; útil para auditoria. |
| `validacao_arquivos.csv` | Confirmação da quantidade de medições e iterações por arquivo. |

O arquivo `resumo_por_tamanho.csv` não é a entrada do `analisar_bcast.py`; ele é uma saída consolidada. Para reproduzir a consolidação desde os logs, é preciso publicar também os nove arquivos brutos válidos.

## Execução

Depois de instalar as dependências:

```bash
python3 -m pip install --user pandas numpy matplotlib
```

Execute:

```bash
python3 analisar_bcast.py \
  resultados_brutos \
  resultado
```

O diretório `resultados_brutos` deve conter exatamente nove arquivos válidos: três para cada configuração. O diretório `resultado` será criado automaticamente.

## Arquivo usado no gráfico do artigo

Para os gráficos e para a tabela do artigo, use:

```text
resultado/resumo_por_tamanho.csv
```

Esse arquivo possui as colunas `vcpu`, `size_bytes`, `mediana_rodadas_us`, `minimo_rodadas_us`, `maximo_rodadas_us` e outras estatísticas calculadas a partir das três rodadas.

A unidade das latências é microssegundo. Valores menores indicam menor latência de Broadcast.

## Recomendação para o GitHub

Para uma publicação completa e reproduzível, use esta estrutura:

```text
mpi-cluster/
├── Vagrantfile
├── run_bcast_mpi.sh
├── analisar_bcast.py
├── dados/
│   ├── resumo_por_tamanho.csv
│   ├── comparacao_por_tamanho.csv
│   ├── resumo_global_por_vcpu.csv
│   ├── dados_brutos_normalizados.csv
│   ├── validacao_arquivos.csv
│   └── logs_brutos/       # opcional, mas recomendado
├── figuras/
└── README.md
```

Se o objetivo for manter o repositório pequeno, publique ao menos `analisar_bcast.py` e `resumo_por_tamanho.csv`. Se o objetivo for permitir a reprodução completa da análise, publique também os nove logs brutos válidos.
