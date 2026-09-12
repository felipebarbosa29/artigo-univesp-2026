import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import os

# Funcao para formatar os ticks do Eixo X (B, KB, MB)
def formatador_bytes(x, pos):
    if x < 1024:
        return f"{int(x)} B"
    elif x < 1048576:
        return f"{int(x/1024)} KB"
    else:
        return f"{int(x/1048576)} MB"

# Funcao para formatar os ticks do Eixo Y (Numeros Inteiros com separador de milhar)
def formatador_microssegundos(x, pos):
    return f"{int(x):,}".replace(",", ".")

def gerar_graficos():
    # Caminho do CSV consolidado
    csv_path = '../dados/dados_vbox.csv'
    
    if not os.path.exists(csv_path):
        print(f"Erro: O arquivo {csv_path} nao foi encontrado.")
        return

    # Lendo os dados via Pandas
    df = pd.read_csv(csv_path)
    tamanhos = df['Tamanho_Bytes']
    tempo_4 = df['NP_4_us']
    tempo_8 = df['NP_8_us']
    tempo_16 = df['NP_16_us']

    plt.figure(figsize=(10, 6))
    
    # Plotagem com estilos idênticos ao artigo
    plt.plot(tamanhos, tempo_4, marker='o', markersize=5, linestyle='-', linewidth=1.5, color='#1f77b4', label='4 Processos')
    plt.plot(tamanhos, tempo_8, marker='s', markersize=5, linestyle='--', linewidth=1.5, color='#ff7f0e', label='8 Processos')
    plt.plot(tamanhos, tempo_16, marker='^', markersize=5, linestyle='-.', linewidth=1.5, color='#2ca02c', label='16 Processos')

    plt.xscale('log', base=2)
    plt.yscale('log', base=10)

    # Configuração dos eixos
    ax = plt.gca()
    
    # Formatação Eixo X
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(formatador_bytes))
    plt.xticks(rotation=45, fontsize=10)

    # Formatação Eixo Y (Numeros Legiveis em vez de 10^x)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatador_microssegundos))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter()) # Remove labels menores para nao poluir
    plt.yticks(fontsize=10)

    # Ajuste de limites para focar nos dados (removendo espaco vazio antes de 1000)
    plt.ylim(1000, 1000000)

    plt.xlabel('Tamanho da Mensagem', fontsize=12, fontweight='bold')
    plt.ylabel('Tempo de Execucao (Microssegundos)', fontsize=12, fontweight='bold')
    plt.title('Desempenho de Broadcast no VirtualBox (4 VMs)', fontsize=14, fontweight='bold', pad=15)
    
    plt.legend(loc='upper left', fontsize=10)
    
    # Grid principal e secundaria para facilitar a leitura dos valores logaritmicos
    plt.grid(True, which="major", ls="-", alpha=0.3, color='gray')
    plt.grid(True, which="minor", ls=":", alpha=0.2, color='gray')

    plt.tight_layout()

    # Garantir que a pasta graficos existe
    os.makedirs('../graficos', exist_ok=True)

    # Salvando na pasta correta
    plt.savefig('../graficos/chart_osu_bcast.png', dpi=300)
    plt.savefig('../graficos/chart_osu_bcast.pdf', format='pdf')

    print(f"Sucesso! Grafico gerado com Eixo Y legivel a partir de {csv_path}.")

if __name__ == '__main__':
    gerar_graficos()
