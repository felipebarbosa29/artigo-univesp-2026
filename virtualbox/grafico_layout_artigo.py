#!/usr/bin/env python3
"""Reproduz o gráfico compacto utilizado no artigo.

Entrada: resumo_por_tamanho.csv gerado por analisar_bcast.py.
Saída: imagem PNG com as medianas das três rodadas.
"""
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path, help="caminho para resumo_por_tamanho.csv")
    parser.add_argument("saida", type=Path, help="caminho da imagem PNG de saída")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    required = {"vcpu", "size_bytes", "mediana_rodadas_us"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Colunas ausentes: {', '.join(sorted(missing))}")

    sizes = sorted(df["size_bytes"].unique())
    expected = [2**i for i in range(21)]
    if sizes != expected:
        raise SystemExit(f"Tamanhos inesperados: encontrados {sizes}; esperados {expected}")

    plt.rcParams.update({
        "font.size": 8,
        "axes.titlesize": 10,
        "axes.labelsize": 8,
        "legend.fontsize": 7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
    })

    fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=150)
    colors = {1: "#4c78a8", 2: "#f28e2b", 4: "#59a14f"}
    labels = {
        1: "1 vCPU por VM — 16 processos",
        2: "2 vCPUs por VM — 16 processos",
        4: "4 vCPUs por VM — 16 processos",
    }

    for vcpu in (1, 2, 4):
        part = df[df["vcpu"] == vcpu].sort_values("size_bytes")
        if len(part) != 21:
            raise SystemExit(f"Configuração {vcpu} vCPU(s) possui {len(part)} linhas; esperadas 21")
        ax.plot(
            part["size_bytes"],
            part["mediana_rodadas_us"],
            marker="o",
            markersize=2.8,
            linewidth=1.2,
            color=colors[vcpu],
            label=labels[vcpu],
        )

    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(expected)
    ax.set_xticklabels([rf"$2^{{{i}}}$" for i in range(21)])
    ax.set_xlabel("Tamanho da mensagem (bytes)")
    ax.set_ylabel("Latência mediana do Broadcast (µs)")
    ax.set_title("MPI Broadcast com 16 processos distribuídos em 4 VMs")
    ax.grid(True, which="major", alpha=0.25)
    ax.legend(loc="upper left", frameon=True)
    fig.tight_layout(pad=0.7)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.saida, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Gráfico salvo em: {args.saida}")


if __name__ == "__main__":
    main()
