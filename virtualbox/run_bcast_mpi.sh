#!/usr/bin/env bash
set -Eeuo pipefail

# Executa o protocolo usado no experimento MPI Broadcast.
# Uso: ./run_bcast_mpi.sh 1|2|4 [diretorio_de_saida]

VCPU="${1:-}"
BASE_OUT="${2:-$HOME/resultados_ic/grupo5_broadcast_vcpu_vagrant}"

if [[ ! "$VCPU" =~ ^(1|2|4)$ ]]; then
  echo "Uso: $0 1|2|4 [diretorio_de_saida]" >&2
  exit 2
fi

HOSTFILE="${HOSTFILE:-$HOME/hostfile}"
OSU_BIN="${OSU_BIN:-$HOME/osu_benchmark/osu-micro-benchmarks-7.3/c/mpi/collective/blocking/osu_bcast}"
ITERACOES="${ITERACOES:-100}"
AQUECIMENTO="${AQUECIMENTO:-20}"
RODADAS="${RODADAS:-3}"
TIMEOUT_TAMANHO="${TIMEOUT_TAMANHO:-15m}"
PAUSA_TAMANHO="${PAUSA_TAMANHO:-5}"

TAMANHOS=(1 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384 32768 65536 131072 262144 524288 1048576)

for arquivo in "$HOSTFILE" "$OSU_BIN"; do
  if [[ ! -e "$arquivo" ]]; then
    echo "ERRO: arquivo não encontrado: $arquivo" >&2
    exit 1
  fi
done

if [[ ! -x "$OSU_BIN" ]]; then
  echo "ERRO: executável sem permissão de execução: $OSU_BIN" >&2
  exit 1
fi

mkdir -p "$BASE_OUT/vcpu${VCPU}"

MPI_BASE=(
  --hostfile "$HOSTFILE"
  --bind-to none
  --oversubscribe
  --mca pml ob1
  --mca btl self,vader,tcp
  --mca btl_tcp_if_include 192.168.56.0/24
  --mca btl_tcp_port_min_v4 20000
  --mca btl_tcp_port_range_v4 1000
  --mca oob_tcp_if_include 192.168.56.0/24
  --mca mpi_preconnect_mpi 0
  --mca mpi_yield_when_idle 1
)

for rodada in $(seq 1 "$RODADAS"); do
  ARQUIVO="$BASE_OUT/vcpu${VCPU}/bcast_16proc_${VCPU}vcpu_100iter_1mib_rodada${rodada}.txt"
  RAW_DIR="$BASE_OUT/vcpu${VCPU}/logs_brutos/rodada${rodada}"
  mkdir -p "$RAW_DIR"

  {
    echo "# Protocolo MPI Broadcast"
    echo "# Configuração: ${VCPU} vCPU(s) por VM"
    echo "# Processos: 16; processos por nó: 4"
    echo "# Rodada: ${rodada}/${RODADAS}"
    echo "# Iterações: ${ITERACOES}; aquecimento: ${AQUECIMENTO}"
    echo "# CPU cap informado no Vagrant: ${VAGRANT_CPU_CAP:-não informado}"
    echo "# Tamanho       Avg Latency(us)   Min Latency(us)   Max Latency(us)   Iterations"
  } > "$ARQUIVO"

  echo "============================================================"
  echo "RODADA ${rodada}/${RODADAS} — ${VCPU} vCPU(s)"
  echo "Saída: $ARQUIVO"
  echo "============================================================"

  for tamanho in "${TAMANHOS[@]}"; do
    RAW="$RAW_DIR/tamanho_${tamanho}.log"
    echo "[$(date '+%F %T')] Medindo ${tamanho} bytes..."

    set +e
    timeout --signal=INT --kill-after=60s "$TIMEOUT_TAMANHO" \
      mpirun -np 16 \
        "${MPI_BASE[@]}" \
        --map-by ppr:4:node \
        nice -n 10 "$OSU_BIN" \
        -i "$ITERACOES" -x "$AQUECIMENTO" -m "${tamanho}:${tamanho}" -f \
        > "$RAW" 2>&1
    status=$?
    set -e

    linha="$(awk -v alvo="$tamanho" '$1 == alvo && $2 ~ /^[0-9]+([.][0-9]+)?$/ && $3 ~ /^[0-9]+([.][0-9]+)?$/ && $4 ~ /^[0-9]+([.][0-9]+)?$/ {print; exit}' "$RAW")"

    if [[ "$status" -ne 0 || -z "$linha" ]]; then
      echo "ERRO no tamanho ${tamanho}; status ${status}." >&2
      echo "Consulte: $RAW" >&2
      exit 1
    fi

    echo "$linha" | tee -a "$ARQUIVO"
    sleep "$PAUSA_TAMANHO"
  done

  echo "Rodada ${rodada} validada: ${#TAMANHOS[@]} medições até 1 MiB."
  if [[ "$rodada" -lt "$RODADAS" ]]; then
    echo "Aguardando 120 segundos antes da próxima rodada..."
    sleep 120
  fi
done

echo "CONFIGURAÇÃO ${VCPU} vCPU(s) CONCLUÍDA COM SUCESSO"
find "$BASE_OUT/vcpu${VCPU}" -maxdepth 1 -type f -name '*rodada*.txt' -printf '%f\n' | sort
