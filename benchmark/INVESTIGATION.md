# Investigation before implementation

Inspected on 2026-10-26, before writing the suite. This checkout is on
`a5900x`, kernel `7.2.9+deb13-amd64`, with approximately 62.6 GiB MemTotal.
It is not the described 128 GiB AI395. `command -v strata` returned no binary;
process inspection found no Strata process, and system and user systemd queries
found no Strata units. The existing Ollama process was left alone. No SSH
credentials or access to the AI395 were supplied or used.

Consequently the installed Strata release, engine hash, launch configuration,
startup mechanism, actual tokenizer, context, expert-cache sizing, HIP runtime,
and enabled optimizations on **the AI395 remain unverified**. The hardware,
96 GiB carve-out, index 8, 15.5 GiB GTT, TTM count and 45–50 tok/s in the task are
operator-provided observations, not measurements made by this suite.

## Official sources

Read current official documentation and relevant server/benchmark source at
Strata commit `4b9e05a2a806a3fe24f7b2560d98626c37dade35`:

- [Strix Halo](https://github.com/Niko1221/Strata/blob/4b9e05a2a806a3fe24f7b2560d98626c37dade35/docs/STRIX_HALO.md)
- [Benchmark protocol](https://github.com/Niko1221/Strata/blob/4b9e05a2a806a3fe24f7b2560d98626c37dade35/docs/BENCHMARK_PROTOCOL.md)
- [Community benchmarks](https://github.com/Niko1221/Strata/blob/4b9e05a2a806a3fe24f7b2560d98626c37dade35/docs/COMMUNITY_BENCHMARKS.md)
- [Server](https://github.com/Niko1221/Strata/blob/4b9e05a2a806a3fe24f7b2560d98626c37dade35/serve/server.py)
- [Frontend conversion](https://github.com/Niko1221/Strata/blob/4b9e05a2a806a3fe24f7b2560d98626c37dade35/serve/frontend.py)
- [Official runner](https://github.com/Niko1221/Strata/blob/4b9e05a2a806a3fe24f7b2560d98626c37dade35/strata_cli/bench_standard.py)
- [Drafting facts](https://github.com/Niko1221/Strata/blob/4b9e05a2a806a3fe24f7b2560d98626c37dade35/strata_control/drafting.py)

`strata bench run` has a frozen workload and rejects workload-changing flags.
It cannot express this context sweep. This utility implements a separate,
nonstandard UMA experiment; it does not claim official-protocol conformance.
For an optional official baseline, use the installed CLI's documented
`strata bench run --url http://127.0.0.1:8080 --no-start` separately. The suite
does not run it automatically or import version-sensitive Strata internals.

The server's `/v1/messages/count_tokens` renders and tokenizes without inference.
Using the same `/v1/messages` dialect avoids approximating the chat template.
`/props` exposes effective context/template; `/metrics.engine` exposes engine
INFO and drafting facts. Anthropic streams do not carry the chat endpoint's
`timings`; `/v1/status.last_timings` carries them. The suite attributes these only
when the server request counter advances exactly once and returns idle.

Engine `prompt_n / (prompt_ms/1000)` measures fresh prefill. Cache reuse is
separate. Decode accounting checks `predicted_n` against the engine's rounded
`predicted_per_second` and timer, preserving any discrepancy and its derivation.
No throughput comes from client token counts divided by total time. TTFT uses
the first nonempty thinking, text or JSON delta; first-answer latency excludes
thinking.

The Strix Halo guide describes experimental support, architecture defaults,
hipBLASLt tuning and explicit cache budgets for RAM-budgeted quantizations.
Auto sizing can change with available RAM. The guide also lists opt-ins such as
`STRATA_PF_FUSED`, `STRATA_IGPU_PROMPT_SET`, `STRATA_PREFILL_STREAM_MIN`,
`STRATA_REFILL_PARTS` and MTP-window tuning; some alter numerical behavior.
The suite records environment/argv and changes none of them. The installed
release's startup log remains necessary evidence of resolved defaults and tuning
table acceptance; do not infer them solely from environment variables.

For telemetry, use read-only DRM sysfs, HWMON, `/proc/meminfo`, `vmstat`,
`diskstats`, and the selected engine PID's `stat`, `status`, `io` and
`smaps_rollup`. These need no GPU-management commands or privileged performance
counters. Kernel journal access may be restricted; coverage is reported.

## Target-host investigation still required

Before preparing fixtures, inspect the actual host using the commands in
[README.md](README.md), fill the configuration from real evidence, retain a
redacted launch/startup log alongside results, then run `check`. The suite blocks
inference on unverified/mismatched context, expert cache, KV, drafting, selected
engine fields, PID or profile memory. It cannot certify unknown release-specific
fields or model-file completeness without that operator inspection.
