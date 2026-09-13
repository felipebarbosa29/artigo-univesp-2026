#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

EXPECTED_SIZES = [2**i for i in range(21)]
LINE_RE = re.compile(
    r"^\s*(\d+)\s+([0-9]+(?:\.[0-9]+)?)\s+([0-9]+(?:\.[0-9]+)?)\s+([0-9]+(?:\.[0-9]+)?)\s+(\d+)\s*$"
)


def parse_file(path: Path) -> pd.DataFrame:
    rows = []
    vcpu_match = re.search(r"(\d+)vcpu", path.name)
    rodada_match = re.search(r"rodada(\d+)", path.name)
    if not vcpu_match or not rodada_match:
        raise ValueError(f"Nome de arquivo inesperado: {path.name}")
    vcpu = int(vcpu_match.group(1))
    rodada = int(rodada_match.group(1))
    for line in path.read_text(encoding="utf-8").splitlines():
        m = LINE_RE.match(line)
        if m:
            size, avg, minimum, maximum, iterations = m.groups()
            rows.append({
                "vcpu": vcpu,
                "rodada": rodada,
                "size_bytes": int(size),
                "avg_us": float(avg),
                "min_us": float(minimum),
                "max_us": float(maximum),
                "iterations": int(iterations),
                "arquivo": str(path),
            })
    df = pd.DataFrame(rows)
    if len(df) != 21 or df["size_bytes"].tolist() != EXPECTED_SIZES:
        raise ValueError(
            f"Arquivo inválido: {path}; encontrados {len(df)} tamanhos; "
            f"esperados {EXPECTED_SIZES}"
        )
    if not (df["iterations"] == 100).all():
        raise ValueError(f"Iterações diferentes de 100 em {path}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(args.input_dir.glob("vcpu*/bcast_*_rodada*.txt"))
    if len(files) != 9:
        raise SystemExit(f"Esperados 9 arquivos válidos; encontrados {len(files)}")

    frames = [parse_file(p) for p in files]
    raw = pd.concat(frames, ignore_index=True)
    raw.to_csv(args.output_dir / "dados_brutos_normalizados.csv", index=False)

    validation = (
        raw.groupby(["vcpu", "rodada"], as_index=False)
        .agg(medicoes=("size_bytes", "size"), iteracoes_min=("iterations", "min"), iteracoes_max=("iterations", "max"))
    )
    validation.to_csv(args.output_dir / "validacao_arquivos.csv", index=False)

    summary = (
        raw.groupby(["vcpu", "size_bytes"], as_index=False)
        .agg(
            media_rodadas_us=("avg_us", "mean"),
            mediana_rodadas_us=("avg_us", "median"),
            minimo_rodadas_us=("avg_us", "min"),
            maximo_rodadas_us=("avg_us", "max"),
            media_min_us=("min_us", "mean"),
            media_max_us=("max_us", "mean"),
            n_rodadas=("rodada", "nunique"),
        )
    )
    summary["amplitude_rodadas_us"] = summary["maximo_rodadas_us"] - summary["minimo_rodadas_us"]
    summary["size_kib"] = summary["size_bytes"] / 1024
    summary.to_csv(args.output_dir / "resumo_por_tamanho.csv", index=False)

    # Gráfico principal: mediana e faixa min-max entre as três rodadas.
    plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.25})
    colors = {1: "#1f77b4", 2: "#ff7f0e", 4: "#2ca02c"}
    labels = {1: "1 vCPU", 2: "2 vCPUs", 4: "4 vCPUs"}

    fig, ax = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    for vcpu in [1, 2, 4]:
        part = summary[summary.vcpu == vcpu].sort_values("size_bytes")
        x = part["size_bytes"].to_numpy()
        y = part["mediana_rodadas_us"].to_numpy()
        low = part["minimo_rodadas_us"].to_numpy()
        high = part["maximo_rodadas_us"].to_numpy()
        ax.plot(x, y, marker="o", markersize=3.5, linewidth=2, color=colors[vcpu], label=labels[vcpu])
        ax.fill_between(x, low, high, color=colors[vcpu], alpha=0.12)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("Tamanho da mensagem (bytes)")
    ax.set_ylabel("Latência de broadcast (µs)")
    ax.set_title("MPI Broadcast: mediana e faixa mínimo–máximo entre rodadas")
    ax.set_xticks(EXPECTED_SIZES)
    ax.set_xticklabels([str(x) if x < 1024 else f"{x//1024} KiB" for x in EXPECTED_SIZES], rotation=45, ha="right")
    ax.legend(title="Configuração")
    fig.savefig(args.output_dir / "grafico_broadcast_mediana_faixa.png", dpi=220)
    fig.savefig(args.output_dir / "grafico_broadcast_mediana_faixa.svg")
    plt.close(fig)

    # Gráfico complementar sem escala logarítmica no eixo Y, útil para evidenciar a dispersão.
    fig, ax = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    for vcpu in [1, 2, 4]:
        part = summary[summary.vcpu == vcpu].sort_values("size_bytes")
        ax.plot(part["size_bytes"], part["mediana_rodadas_us"], marker="o", markersize=3.5, linewidth=2, color=colors[vcpu], label=labels[vcpu])
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Tamanho da mensagem (bytes)")
    ax.set_ylabel("Latência mediana de broadcast (µs)")
    ax.set_title("MPI Broadcast: latência mediana por tamanho")
    ax.set_xticks(EXPECTED_SIZES)
    ax.set_xticklabels([str(x) if x < 1024 else f"{x//1024} KiB" for x in EXPECTED_SIZES], rotation=45, ha="right")
    ax.legend(title="Configuração")
    fig.savefig(args.output_dir / "grafico_broadcast_mediana_linear.png", dpi=220)
    plt.close(fig)

    # Tabela de síntese: medianas globais por configuração e faixa observada.
    overall = (
        raw.groupby("vcpu", as_index=False)
        .agg(
            mediana_global_us=("avg_us", "median"),
            media_global_us=("avg_us", "mean"),
            menor_latencia_us=("avg_us", "min"),
            maior_latencia_us=("avg_us", "max"),
        )
    )
    overall.to_csv(args.output_dir / "resumo_global_por_vcpu.csv", index=False)

    # Texto de validação e resumo para facilitar a documentação.
    with (args.output_dir / "relatorio_validacao.txt").open("w", encoding="utf-8") as f:
        f.write(f"Arquivos válidos: {len(files)}\n")
        f.write("Cada arquivo deve conter 21 medições e 100 iterações.\n\n")
        f.write(validation.to_string(index=False))
        f.write("\n\nResumo global:\n")
        f.write(overall.to_string(index=False))


if __name__ == "__main__":
    main()
