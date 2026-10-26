# UMA comparison

**SIMULATED EXAMPLE: invented numbers, not measured performance.**

Percent change is (candidate / baseline - 1) × 100. Negative latency changes are improvements. Missing percentages are withheld, not zero.

| Profile | Test | Metric | n | Median | Min–max | Δ vs 96+32 % | Comparable |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| baseline-96 | throughput-4096 | prefill_tps | 5 | 1000.000 | 998.000–1002.000 | 0.000 | True |
| baseline-96 | throughput-4096 | decode_tps | 5 | 48.000 | 47.800–48.200 | 0.000 | True |
| baseline-96 | throughput-4096 | ttft_s | 5 | 4.220 | 4.200–4.240 | 0.000 | True |
| baseline-96 | throughput-4096 | wall_s | 5 | 15.200 | 15.000–15.400 | 0.000 | True |
| uma-64 | throughput-4096 | prefill_tps | 5 | 1020.000 | 1018.000–1022.000 | 2.000 | True |
| uma-64 | throughput-4096 | decode_tps | 5 | 47.500 | 47.300–47.700 | -1.042 | True |
| uma-64 | throughput-4096 | ttft_s | 5 | 4.220 | 4.200–4.240 | 0.000 | True |
| uma-64 | throughput-4096 | wall_s | 5 | 15.200 | 15.000–15.400 | 0.000 | True |
| uma-512m | throughput-4096 | prefill_tps | 5 | 980.000 | 978.000–982.000 | -2.000 | True |
| uma-512m | throughput-4096 | decode_tps | 5 | 46.000 | 45.800–46.200 | -4.167 | True |
| uma-512m | throughput-4096 | ttft_s | 5 | 4.220 | 4.200–4.240 | 0.000 | True |
| uma-512m | throughput-4096 | wall_s | 5 | 15.200 | 15.000–15.400 | 0.000 | True |

## Warnings and failures

- benchmark/example-output/baseline-96: SIMULATED EXAMPLE; numbers are invented, not measured
- benchmark/example-output/baseline-96 / recall-131072: ok; recall exact=False
- benchmark/example-output/uma-64: SIMULATED EXAMPLE; numbers are invented, not measured
- benchmark/example-output/uma-64 / recall-131072: ok; recall exact=False
- benchmark/example-output/uma-512m: SIMULATED EXAMPLE; numbers are invented, not measured
- benchmark/example-output/uma-512m / recall-131072: ok; recall exact=False

## Session metadata

Configuration, memory, disk I/O, correctness and kernel evidence are in each linked report.

- [benchmark/example-output/baseline-96](../baseline-96/report.md): complete
```json
{
  "profile": "baseline-96",
  "identity": {
    "synthetic_example": true,
    "workload": "example-only"
  },
  "kernel_events": {
    "coverage": "unavailable",
    "events": []
  }
}
```

- [benchmark/example-output/uma-64](../uma-64/report.md): complete
```json
{
  "profile": "uma-64",
  "identity": {
    "synthetic_example": true,
    "workload": "example-only"
  },
  "kernel_events": {
    "coverage": "unavailable",
    "events": []
  }
}
```

- [benchmark/example-output/uma-512m](../uma-512m/report.md): complete
```json
{
  "profile": "uma-512m",
  "identity": {
    "synthetic_example": true,
    "workload": "example-only"
  },
  "kernel_events": {
    "coverage": "unavailable",
    "events": []
  }
}
```
