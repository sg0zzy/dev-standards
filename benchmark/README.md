# Strata UMA benchmark

An optional, self-contained Linux experiment under `benchmark/`, unrelated to
standards adoption or application compliance. It uses Python 3.11+ and its standard
library. There is no installation step, shared build dependency or service.
[Investigation findings](INVESTIGATION.md) distinguish verified upstream behavior
from the target-host facts that still need inspection.

**No full benchmark has been executed.** The implementation tests use a local
mock HTTP server, synthetic files and fake GPU counters.

The suite only attaches to a loopback server. It never launches/stops Strata,
changes BIOS/sysfs/kernel/bootloader settings, reboots, clears caches or swap,
or kills other sessions. `prepare` hashes files and counts tokens without
inference; hashing does read the model and warm filesystem cache.

## Inspect and configure on the AI395

Run from this repository root on the inference host. Do not infer that this
workspace is already the AI395. These diagnostics are read-only:

```sh
hostname
uname -a
command -v strata
strata --version
strata bench run --help
ps -eo pid,ppid,comm,args | rg -i 'strata|serve/server'
systemctl list-units --all --no-pager '*strata*'
systemctl --user list-units --all --no-pager '*strata*'
ls /sys/class/drm
cat /proc/cmdline
cat /proc/meminfo
cat /proc/swaps
```

Inspect the relevant unit with `systemctl cat UNIT` (or `--user`), container
configuration, existing Herdr session or launch script. Read the actual Strata
configuration and startup log. Do not print credentials into shared logs.
Inspect `/props`, `/v1/status` and `/metrics` on the local server, using its API
key if required. Retain the startup log as evidence of enabled kernels, prefill
tuning, cache sizing, MTP fallback, library versions and native model context.
Do not start another engine while the existing one occupies memory.

```sh
cp benchmark/config.example.json benchmark/config.json
# Edit benchmark/config.json using the installed configuration and process facts.
benchmark/benchmark --config benchmark/config.json check --offline --save /tmp/uma-inventory.json
# Offline mode deliberately exits nonzero: it has not verified Strata.
benchmark/benchmark check --profile baseline-96 --save /tmp/uma-check.json
```

Configuration requirements:

- `engine_pid` is the actual C++ inference process, not the CLI or Python HTTP
  frontend. `engine_binary` must resolve to `/proc/PID/exe`. Keep the HTTP service
  reserved for this experiment. The runner enforces concurrency one and checks
  for other requests; it cannot prevent another application from using the GPU.
- Set `strata_cli`, `launch_config`, model alias and quantization accurately.
  List **every** model, pack, dense-weight, expert, MTP and auxiliary weight file
  the engine reads in `model_files`, including split files. List all tokenizer
  vocabulary, merge, config and template files in `tokenizer_files`.
  Hashes do not prove that the operator's list is complete.
- Pin the existing explicit `--expert-cache` argument in `expected.expert_cache`,
  as a string with the same spelling/units as argv. `auto` is rejected even when
  it happens to allocate 24,576 slots. If the existing instance uses auto, this
  task does not authorize changing it; prepare the explicit common configuration
  manually for a later experiment. A setting that cannot fit is a configuration
  limitation, with skipped results, never an invitation to shrink the cache.
- `expected.context_tokens` is normally 262144; KV must match both `--kv` and
  engine INFO. `expected.engine_info` must contain the release's verified
  speculation/MTP fields and values. Replace the placeholder after inspecting
  `/metrics.engine` and the startup log. `drafting=mtp` and 24,576 slots are
  required independently. Pin spec width/window and other effective fields
  exposed by the installed release. An older release lacking these facts needs
  explicit adapter work; the suite fails rather than assuming equivalence.
- Select the AMD device's sysfs directory explicitly; `card0` is only an example.
  Set `uma_current` and `uma_options` to the actual read-only firmware attribute
  paths if available. Otherwise these remain null. **Index 8 is preserved as
  observed even though the advertised options stop at 7.** No option is written,
  and there is no assumption that sysfs can restore 96 GiB.
- Pass credentials only through `STRATA_API_KEY`. The suite does not save that
  variable. Relevant engine environment is allowlisted and credential names are
  removed. Keep result folders private and inspect metadata before sharing:
  hostname, paths, process names, argv and engine facts are local provenance.
- Keep sampling, thinking, context, KV, expert-cache, prefill, speculative
  decoding, concurrency, tuning table, runtime and optimization settings fixed.
  The example uses thinking on, unlimited reasoning budget, seed 395, output cap
  512 and explicit sampling. Do not disable options to work around a failure.

## Prepare and smoke-test

```sh
# Offline implementation tests: no inference or target hardware required.
python3 -m unittest discover -s benchmark -v

# Freeze/hash the full corpus once, before any intended cold-filesystem trial.
benchmark/benchmark prepare
benchmark/benchmark check --profile baseline-96 --bundle benchmark/prepared/full

# Optional LIGHTWEIGHT INFERENCE on the selected server, later, after preflight.
benchmark/benchmark prepare --smoke --bundle benchmark/prepared/smoke
benchmark/benchmark run --profile baseline-96 --bundle benchmark/prepared/smoke
```

The smoke bundle makes six 512-token-input requests capped at 32 output tokens.
It does exercise inference when run against real Strata. It cannot be compared
to the full suite. No real inference smoke run was performed during development.

Full preparation performs exact server token counts, using the same Anthropic
request shape for count and generation, including the model's template and
special tokens. Deterministic record text and unique case prefixes use fixed
seeds. Each complete rendered input fits at or just below its target (within
0.5%); measured counts are frozen. Counts are rechecked immediately before each
request and compared to the stream's actual input count, rejecting truncation or
template drift. A configuration/template/corpus mismatch requires a new baseline.

Preparation records SHA-256 for all supplied assets, launch config and engine,
and saves the server's effective chat template. Later runs verify asset sizes
and nanosecond mtimes and rehash the engine, avoiding rereading all model data.
If content might have changed while preserving those attributes, prepare a new
bundle and baseline. Use the same intact bundle after manual host configuration
changes. Keep paths and launch-config content stable; updating `engine_pid` and
observational notes is allowed after a restart.

## Full workload and timing

| Workload | Input target | Repetitions | Output cap |
| --- | ---: | ---: | ---: |
| Short | 4096 | 5 | 512 |
| Medium | 16384 | 5 | 512 |
| Large | 65536 | 3 | 512 |
| Very large | 131072 | 3 | 512 |
| Maximum | 262144 less output and safety room | 3 | 512 |

At a 262144-token limit, the maximum input target is **261568**, including all
template overhead, reserving 512 output tokens and another 64 tokens. Early EOS
is preserved, with actual generated counts recorded. Output is never forced to
inflate throughput. These are real long input payloads, not merely context
capacity flags. The suite does not configure RoPE or extend the model's window.

There are 38 requests: 19 throughput, 12 agent, two recall, and five cache-repeat
requests. The first two requests are identical to each other; three more repeat
that same payload at the end. Their cache results stay separate from fresh-input
throughput. The initial server request count distinguishes a freshly loaded,
never-used process from an already-used process. It does not prove filesystem
coldness or measure loading time.

Agent replay grows one persistent message history through approximately
32K/64K/128K/256K tokens. Each checkpoint reserves another 1024 tokens for two
short tool-result-like user additions. Small synthetic pytest/diff results model
coding-agent work without executing tools. Fixed scripted assistant messages
separate turns so subsequent prompts stay byte-identical across configurations;
measured generated answers are saved, but are not fed into later turns. This is
a deterministic conversation replay, not an autonomous agent or a tool-use
quality test. Long added source excerpts and short incremental turns are reported
separately. Cached and freshly processed tokens, prefill, decode, wall latency
and memory growth are retained for every turn; cache reuse is observed, not
forced or guaranteed.

Recall at 128K and near 256K uses three random 128-bit values under unique keys
inserted near 10%, 50% and 90% of the record list. The requested answer is exactly
those three values, one per line. Both strict exact match (outer whitespace
ignored) and per-marker presence are recorded. Recall requests do not enter speed
summaries. Thinking that consumes the entire output budget is a failed recall,
not a reason to change generation settings.

Fresh throughput requests use distinct early prefixes. Reuse above 64 tokens
invalidates a throughput request; this conservative bound permits template and
short identifier-prefix reuse. The suite does not claim token-exact shared-prefix
analysis or flush the engine's cache. A prior run of the same fixtures can cause
rejection; use a manually freshly loaded process for comparable sessions. No
retries, cache eviction requests or fallback settings are sent.

Prefill uses only `prompt_n / prompt_ms`; decode uses the engine's accepted-token
clock and validates speculative token accounting. Raw timings and stream events
are retained. `/v1/status.last_timings` is attributed only when request counts
advance exactly once, the server is idle and resident slot counts/configuration
are unchanged. Missing metrics remain null with warnings. TTFT begins at dispatch
and includes thinking; first-answer time is also recorded. Client wall time
includes networking and small logging overhead. The request wall deadline is
1800 seconds by default, enforced even during keepalives; socket inactivity also
has a 60-second ceiling. On failure or timeout the stream closes, no further
requests are scheduled and remaining cases are marked skipped. Server-side
cancellation after disconnect depends on the installed Strata release; inspect
its idle status before further work.

## Run later in a persistent session

Use an existing persistent SSH/Herdr session, or create a dedicated tmux session
if tmux is installed. No session-management program is required by the suite.

```sh
tmux new -s uma-benchmark
benchmark/benchmark check --profile baseline-96 --bundle benchmark/prepared/full
benchmark/benchmark run --profile baseline-96
# Detach with Ctrl-b d. Reattach later with: tmux attach -t uma-benchmark

# Only AFTER the operator independently establishes and verifies each host state:
benchmark/benchmark check --profile uma-64 --bundle benchmark/prepared/full
benchmark/benchmark run --profile uma-64
benchmark/benchmark check --profile uma-512m --bundle benchmark/prepared/full
benchmark/benchmark run --profile uma-512m
```

Each `run` requires typing `RUN`. For a reviewed unattended invocation, `--yes`
records the operator's decision to start the selected workload. SIGHUP is ignored;
use persistent terminal output or redirection as appropriate. Ctrl-C/SIGTERM
interrupt only this client, close its stream and finalize partial results. Do not
send signals to Strata. The runner holds a per-user local lock against overlapping
suite clients, not against other applications.

JSONL records are flushed/fsynced per completed request and every telemetry
sample; stream events are batched approximately once per second. Session/report
JSON is replaced atomically. Abrupt power loss/SIGKILL can leave an unfinished
request or torn last line; recover a readable report without rerunning inference:

```sh
benchmark/benchmark report benchmark/results/SESSION
```

Recovery preserves original JSONL. It labels missing planned cases skipped and
can ignore a torn final record with a warning. It does not resume a measured
conversation or merge partial sessions into a full run. Keep completed evidence,
then run a new session if a complete comparison is needed.

## Filesystem-cache and process-load experiments

[Manual host actions](MANUAL_HOST_ACTIONS.md) explains the boundaries. There is no
cache-clearing command in the implementation, including the optional cold mode.
Use `watch-load` to observe an externally started fresh engine:

```sh
# In terminal A; PID path must not yet exist, and selected HTTP endpoint must be free.
benchmark/benchmark watch-load --profile baseline-96 \
  --condition cold-process-warm-fs --pid-file /tmp/uma-fresh-engine.pid
# Terminal B: manually use your VERIFIED normal startup mechanism, then write the
# actual new C++ engine PID to /tmp/uma-fresh-engine.pid. No launcher is supplied.
```

The observer reuses the prepared full bundle by default (`--bundle` can select another),
checks asset metadata without rereading model data, and verifies the loaded
configuration. It never starts or terminates a process. It records baseline/peak/end
memory and I/O while waiting, then process-start-to-loaded duration using the
kernel PID start time and server readiness, with up to roughly one polling
interval plus HTTP delay. Start it before launch; process counters prior to PID
publication are unavailable and identified by the time series. Final process-lifetime
read counters and major faults are also saved for the fresh PID; system-level
load I/O remains separate. Ensure the PID
belongs to the engine behind the observed endpoint; matching executable alone
cannot prove this when multiple engines exist. If the process already answered
requests, the observation is rejected. The deadline defaults to 1800 seconds.

Use `--condition manual-cold-fs` only after separately establishing cold
filesystem state. It prompts with a warning and records operator attestation;
it does not establish or verify coldness. Capture a cold-filesystem load, a fresh
process with warm filesystem, then inference against a warm process, using the
same assets/settings. Pair each observer directory with its subsequent inference
session; compare load durations separately from inference. Observer directories
have `load.json`, not `session.json`, and do not enter the inference comparison
command. Their JSON/Markdown contains the observed duration and counters for
manual load comparison.

A larger MemAvailable and lower physical reads on repeated loads may support the
page-cache hypothesis. Linux's `Cached` value alone does not prove model residency
or cache effectiveness. Uncontrolled background I/O, storage layers and memory
pressure can confound it. Hashing the model immediately before a cold trial
invalidates that trial's premise.

## Results and comparison

Each invocation creates `benchmark/results/UTC-PROFILE-RANDOM/`:

| File | Contents |
| --- | --- |
| `session.json` | Requested/effective configuration, hardware, software, source notes, kernel events and status |
| `runs.jsonl` | One terminal record per planned request, including failures/skips and telemetry summary |
| `progress.jsonl` | Started-case records useful after abrupt interruption |
| `events.jsonl` | Raw response events and monotonic offsets |
| `telemetry.jsonl` | Timestamped read-only counters, normally sampled every two seconds |
| `summary.json` | Successful measurements grouped by case, median/min/max/SD/CV and sample counts |
| `report.md` | Full metadata, per-test tables, summaries, resource observations and errors |

```sh
benchmark/benchmark compare \
  benchmark/results/SESSION_96 benchmark/results/SESSION_64 benchmark/results/SESSION_512M \
  --output benchmark/results/comparison-01
```

The output directory must be new. `comparison.md` and `comparison.csv` show
medians, spread, sample counts and percentage differences from exactly one
`baseline-96`. Throughput and resource metrics are separate; there is no weighted
winner score. Positive throughput change is better; negative latency/I/O/swap is
usually better; higher MemAvailable is better. A percentage from a zero baseline
is undefined and remains empty/null.

Fingerprints include the corpus, model/engine/config/tokenizer hashes, effective
version, generation settings, expected engine fields, actual argv/environment,
template, host, CPU/GPU identity and kernel version. Intentional UMA/GTT and
MemTotal changes are outside this fingerprint. Mismatched fingerprints, missing
metrics or incomplete repetition groups receive no percentage comparison. Failed
runs never enter summaries; partial sessions and recall failures are explicit.
Kernel fault evidence is flagged for stability review. See each linked session
report for full metadata and baseline/peak/end memory and disk observations.

## Resource interpretation and limitations

- DRM sysfs gives device-wide VRAM/GTT totals and usage, not process-exclusive
  allocation. On UMA these pools, host RAM, mappings and RSS overlap: never sum
  them. PSS is sampled when permitted. Process RSS/PSS/CPU/I/O are for the selected
  engine PID; Python frontend/tokenizer memory is visible in system memory and
  background-process inventory but is not aggregated into engine RSS.
- Process `read_bytes` is storage-read accounting; `syscr` is read syscall count,
  **not physical IOPS**. `/proc/diskstats` gives per-device read bytes (512-byte
  sectors) and completed operations. Device, partition and dm rows overlap and
  are not summed. Loop/RAM disks are omitted. Choose the actual backing device
  using recorded `lsblk`; unrelated system activity stays visible separately.
- Swap-in/out counters are pages, with the system page size recorded in metadata.
  CPU utilization is process percent of one core (can exceed 100%) and system busy
  percent. GPU utilization is the driver's sampled percentage. Clock strings are
  preserved; HWMON units are temperature m°C, power µW, frequency Hz. Missing
  power, clock, temperature, HIP version or PSS is unavailable, not zero.
- Two-second sampling misses short peaks and is an observation, not an exact
  allocation trace. PSS sampling and logging can add overhead; keep the same
  interval/output filesystem across configurations. No benchmark overhead has
  been calibrated on the AI395.
- Kernel OOM/reset/fault evidence comes only from accessible journal entries.
  Restricted/empty journals are labeled unavailable; no evidence is not proof of
  stability. Sudden host crashes can prevent finalization; retain JSONL and
  inspect prior-boot logs manually. This is a workload stability probe, not a
  long-duration burn-in.
- BIOS-reported UMA, observed VRAM and OS RAM are recorded independently. Profiles
  validate approximate VRAM, allowing driver reservations. GTT capacity is
  recorded rather than increased. A 512 MiB carve-out with the current small GTT
  may not fit; report that limitation and do not silently reduce cache/KV/context.
- Native model-window metadata and tokenizer behavior must be confirmed on the
  installed target. Exact request counts and reported effective context protect
  request sizing, but do not prove recall quality or validate RoPE behavior.
- Runtime/library paths and versions are captured where readable; they are not
  fully reproducible build attestations. Retain the same installation and startup
  evidence. External clients, power limits and unexposed adaptive engine settings
  can still invalidate an otherwise matching fingerprint.

## Estimated time and space

These are estimates, not AI395 measurements. At 45–50 output tok/s, 38 full caps
require roughly 6.5–7.2 minutes of decoding. The sweep ingests about 1.5 million
fresh prompt tokens; agent growth, recall and cache checks bring the uncached
upper workload to roughly 2.2 million tokens. At an assumed 500–1300 prefill tok/s,
allow **40–100 minutes per configuration**, plus model loading, hashing,
preparation and interruptions. With the 1800-second per-request ceiling, the
worst scheduled request time is 19 hours for all 38 requests; failures stop the
schedule early. Check measured short/medium prefill before committing to the rest.

Preparation can take minutes to tens of minutes because exact counting repeats
large tokenizations and all weight files are read once. Allow 100–300 MiB for
fixtures/results initially, and at least 1 GiB free for longer telemetry/logs;
actual usage scales with devices and runtime. Models/packs remain in place and
are not copied. The suite itself uses roughly tens to hundreds of MiB during
large fixture preparation; the engine's existing approximately 68 GiB usage,
context growth, CPU arena and required OS headroom dominate. No automatic memory
capacity guarantee is possible from this development host. A second loaded engine
could exhaust the 128 GiB pool and must be accounted for manually.

[Example output](example-output/README.md) contains synthetic, explicitly labeled
report data. No standards, version, tags, releases or application compliance
claims are changed by this experiment.
