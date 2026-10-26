# Strata UMA experiment

Profile: uma-512m; status: complete.

Custom protocol; concurrency 1. Higher throughput is better; lower latency is better.

| Test | Status | Actual input | Output | Fresh | Cached | Expert slots | Prefill tok/s | Decode tok/s | TTFT s | Wall s | Recall exact |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| throughput-4096-0 | ok | 4096 | 512 | 4080 | 16 | 24576 | 978.000 | 45.800 | 4.200 | 15.000 | unavailable |
| throughput-4096-1 | ok | 4096 | 512 | 4080 | 16 | 24576 | 979.000 | 45.900 | 4.210 | 15.100 | unavailable |
| throughput-4096-2 | ok | 4096 | 512 | 4080 | 16 | 24576 | 980.000 | 46.000 | 4.220 | 15.200 | unavailable |
| throughput-4096-3 | ok | 4096 | 512 | 4080 | 16 | 24576 | 981.000 | 46.100 | 4.230 | 15.300 | unavailable |
| throughput-4096-4 | ok | 4096 | 512 | 4080 | 16 | 24576 | 982.000 | 46.200 | 4.240 | 15.400 | unavailable |
| recall-131072 | ok | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | False |

## Statistics

| Test | Metric | n | Median | Min | Max | Sample SD | CV % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| throughput-4096 | prefill_tps | 5 | 980.000 | 978.000 | 982.000 | 1.581 | 0.161 |
| throughput-4096 | decode_tps | 5 | 46.000 | 45.800 | 46.200 | 0.158 | 0.344 |
| throughput-4096 | ttft_s | 5 | 4.220 | 4.200 | 4.240 | 0.016 | 0.375 |
| throughput-4096 | wall_s | 5 | 15.200 | 15.000 | 15.400 | 0.158 | 1.040 |

## Memory, I/O and cache observations

Baseline, end, sampled minima/maxima, per-device I/O and process deltas follow. MemAvailable minimum is the memory-pressure peak. VRAM/GTT/RSS overlap and must not be added. Process syscr counts read syscalls, not physical IOPS. /proc/diskstats counts block operations; partition, device-mapper and physical device rows overlap, so they are not summed. Cached/Buffers and reduced read_bytes are cache observations, not a measured cache-hit ratio. Sampling can miss brief peaks. HWMON temperature is millidegrees C, power microwatts, freq Hz.

## Errors and warnings

- SIMULATED EXAMPLE ONLY. All rates, timings, settings and outcomes are invented to demonstrate formatting.
- No system, memory, I/O or model metadata was measured. Fields are omitted rather than fabricated.
- throughput-4096-0: SIMULATED EXAMPLE; NOT MEASURED
- throughput-4096-1: SIMULATED EXAMPLE; NOT MEASURED
- throughput-4096-2: SIMULATED EXAMPLE; NOT MEASURED
- throughput-4096-3: SIMULATED EXAMPLE; NOT MEASURED
- throughput-4096-4: SIMULATED EXAMPLE; NOT MEASURED
- recall-131072: SIMULATED FAILURE; NOT A MODEL EVALUATION

## Complete configuration and provenance

```json
{
  "schema": 1,
  "protocol": "strata-uma-local-v1",
  "profile": "uma-512m",
  "status": "complete",
  "synthetic_example": true,
  "identity": {
    "synthetic_example": true,
    "workload": "example-only"
  },
  "planned_cases": [
    {
      "id": "throughput-4096-0",
      "kind": "throughput",
      "target": 4096
    },
    {
      "id": "throughput-4096-1",
      "kind": "throughput",
      "target": 4096
    },
    {
      "id": "throughput-4096-2",
      "kind": "throughput",
      "target": 4096
    },
    {
      "id": "throughput-4096-3",
      "kind": "throughput",
      "target": 4096
    },
    {
      "id": "throughput-4096-4",
      "kind": "throughput",
      "target": 4096
    },
    {
      "id": "recall-131072",
      "kind": "recall"
    }
  ],
  "warnings": [
    "SIMULATED EXAMPLE ONLY. All rates, timings, settings and outcomes are invented to demonstrate formatting.",
    "No system, memory, I/O or model metadata was measured. Fields are omitted rather than fabricated."
  ],
  "kernel_events": {
    "coverage": "unavailable",
    "events": []
  }
}
```
