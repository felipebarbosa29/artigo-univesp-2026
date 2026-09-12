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

# Funcao para formatar os ticks do Eixo Y (Numeros Inteiros)
def formatador_inteiro(x, pos):
    if x >= 1:
        return f"{int(x):,}".replace(",", ".")
    else:
        return f"{x:.2f}"

def gerar_grafico_aws():
    # Caminho do CSV
    csv_path = '../dados/dados_aws_interregional.csv'
    
    if not os.path.exists(csv_path):
        print(f"Erro: O arquivo {csv_path} nao foi encontrado.")
        return

    # Lendo os dados via Pandas
    df = pd.read_csv(csv_path)
    tamanhos = df['Tamanho_Bytes']
    tempo_local = df['Local_Virginia_us']
    tempo_inter = df['Interregional_OR_VA_us']

    plt.figure(figsize=(10, 6))
    
    # Plotagem com estilos e legendas idênticas ao artigo
    plt.plot(tamanhos, tempo_local, marker='o', markersize=6, linestyle='-', linewidth=1.5, color='#1f77b4', 
             label='2 processos na Virgínia do Norte')
    plt.plot(tamanhos, tempo_inter, marker='s', markersize=6, linestyle='-', linewidth=1.5, color='#ff7f0e', 
             label='1 processo no Oregon e 1 processo na Virgínia do Norte')

    plt.xscale('log', base=2)
    plt.yscale('log', base=10)

    # Configuração dos eixos
    ax = plt.gca()
    
    # FORCAR EIXO X A TER APENAS OS PONTOS DE DADOS (Igual ao Artigo)
    ax.set_xticks(tamanhos)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(formatador_bytes))
    plt.xticks(rotation=45, fontsize=10)

    # Formatação Eixo Y (Numeros Legiveis em vez de 10^x)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatador_inteiro))
    plt.yticks(fontsize=10)

    # Ajuste de limites para focar nos dados
    plt.ylim(0.5, 200000)

    plt.xlabel('Tamanho da Mensagem', fontsize=12, fontweight='bold')
    plt.ylabel('Latência (µs)', fontsize=12, fontweight='bold')
    plt.title('OSU Micro-Benchmarks: LATÊNCIA (Ponto-a-Ponto)', fontsize=14, fontweight='bold', pad=15)
    
    plt.legend(loc='center left', fontsize=10)
    
    # Grid principal e secundaria
    plt.grid(True, which="major", ls="-", alpha=0.3, color='gray')
    plt.grid(True, which="minor", ls=":", alpha=0.2, color='gray')

    plt.tight_layout()

    # Garantir que a pasta graficos existe
    os.makedirs('../graficos', exist_ok=True)

    # Salvando na pasta correta
    plt.savefig('../graficos/grafico_latencia_aws.png', dpi=300)
    plt.savefig('../graficos/grafico_latencia_aws.pdf', format='pdf')

    print(f"Sucesso! Grafico AWS atualizado com Eixo X alinhado aos dados em '../graficos/'.")

if __name__ == '__main__':
    gerar_grafico_aws()
