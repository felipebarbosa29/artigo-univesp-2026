# Resultados Experimentais: AWS Cloud (Inter-regional)

Medições de latência transcontinental utilizando instâncias EC2.

## 1. Topologia de Rede
*   **Nó 1:** `us-east-1` (Virgínia do Norte)
*   **Nó 2:** `us-west-2` (Oregon)
*   **Distância Estimada:** ~4.000 km.

## 2. Latência Ponto-a-Ponto (osu_latency)
Comparação entre execução local (processos na mesma instância na Virgínia) e execução distribuída entre as regiões da Virgínia do Norte e Oregon.

| Tamanho (Bytes) | Latência Local (µs) | Latência Inter-regional (µs) |
| :--- | :--- | :--- |
| 1 | 1,22 | 28270,00 |
| 16 | 0,96 | 28275,00 |
| 256 | 0,97 | 28280,00 |
| 4096 | 3,45 | 28310,00 |
| 65536 | 10,88 | 85120,00 |
| 1048576 | 202,66 | 87170,00 |

**Notas Técnicas:**
*   **Latência Inter-regional:** Os valores variam entre **28,27 ms** e **87,17 ms**, refletindo o tempo de trânsito dos pacotes através do backbone da AWS entre as costas Leste e Oeste dos EUA.
*   **Latência Local:** Valores baixos (< 1 µs para mensagens pequenas).