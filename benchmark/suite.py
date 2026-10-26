"""Optional, local Strix Halo experiment. Python stdlib only; no service control."""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import re
import shutil
import signal
import socket
import statistics
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

SCHEMA = 1
PROTOCOL = 'strata-uma-local-v1'
MATRIX = [(4096, 5), (16384, 5), (65536, 3), (131072, 3), (262144, 3)]
PROFILES = {'baseline-96': 96 * 2**30, 'uma-64': 64 * 2**30, 'uma-512m': 512 * 2**20}
METRICS = ['prefill_tps', 'decode_tps', 'ttft_s', 'wall_s']
RESOURCE_METRICS = ['peak_vram_bytes', 'peak_gtt_bytes', 'min_mem_available_bytes', 'peak_rss_bytes',
                    'peak_pss_bytes', 'peak_swap_bytes', 'process_disk_read_bytes', 'process_read_syscalls',
                    'swap_in_pages', 'swap_out_pages', 'process_major_faults', 'process_cpu_percent_one_core',
                    'system_cpu_busy_percent']
STOP = threading.Event()


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(8 * 2**20), b''):
            h.update(b)
    return h.hexdigest()


def read(path):
    try:
        return Path(path).read_text().strip()
    except (OSError, UnicodeError):
        return None


def number(path):
    try:
        return int(read(path))
    except (TypeError, ValueError):
        return None


def command(args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=10)
        return {'returncode': p.returncode, 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {'error': str(e)}


def write(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    os.replace(tmp, path)


def append(path, value):
    with open(path, 'a') as f:
        f.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + '\n')
        f.flush()
        os.fsync(f.fileno())


def append_events(path, events):
    if not events:
        return
    with open(path, 'a') as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
        f.flush()
        os.fsync(f.fileno())


def redacted_argv(args):
    out, hide = [], False
    for a in args:
        secret = bool(re.search(r'^--(?:api[-_]?key|access[-_]?token|token|secret|password)(?:=|$)', a, re.I)) and a.startswith('--')
        out.append('<redacted>' if hide else (a.split('=')[0] + '=<redacted>' if secret and '=' in a else a))
        hide = secret and '=' not in a
    return out


def env_for(pid):
    try:
        raw = Path(f'/proc/{pid}/environ').read_bytes().split(b'\0')
        env = dict(x.decode(errors='replace').split('=', 1) for x in raw if b'=' in x)
        return {k: v for k, v in env.items()
                if k.startswith(('STRATA_', 'HIP_', 'ROCM_', 'HSA_', 'GGML_'))
                and not re.search('KEY|TOKEN|SECRET|PASSWORD|AUTH|CREDENTIAL', k)}
    except OSError:
        return None


def argv_for(pid):
    try:
        return Path(f'/proc/{pid}/cmdline').read_bytes().decode().strip('\0').split('\0')
    except OSError:
        return []


def option(args, name):
    for i, a in enumerate(args):
        if a.startswith(name + '='):
            return a.split('=', 1)[1]
        if a == name and i + 1 < len(args):
            return args[i + 1]
    return None


class API:
    def __init__(self, cfg):
        self.cfg = cfg
        self.url = cfg['url'].rstrip('/')
        u = urllib.parse.urlsplit(self.url)
        if u.scheme != 'http' or u.hostname not in ('127.0.0.1', 'localhost', '::1') or u.path not in ('', '/') or u.username:
            raise ValueError('Use a loopback HTTP server on the inference host, without a /v1 suffix or credentials in URL')

    def request(self, path, body=None, timeout=15):
        headers = {'Content-Type': 'application/json', 'anthropic-version': '2023-06-01'}
        if os.environ.get('STRATA_API_KEY'):
            headers['Authorization'] = 'Bearer ' + os.environ['STRATA_API_KEY']
        return urllib.request.urlopen(urllib.request.Request(self.url + path,
            data=canonical(body) if body is not None else None, headers=headers), timeout=timeout)

    def get(self, path):
        with self.request(path) as f:
            return json.load(f)

    def body(self, messages, output=None):
        return {**self.cfg['sampling'], 'seed': self.cfg['seed'], 'model': self.cfg['model'],
                'messages': messages, 'max_tokens': output or self.cfg['output_tokens']}

    def count(self, messages):
        with self.request('/v1/messages/count_tokens', self.body(messages), timeout=120) as f:
            n = json.load(f)['input_tokens']
        if type(n) is not int or n <= 0:
            raise ValueError('Invalid exact token count')
        return n

    def snapshot(self):
        snap = {p: self.get(p) for p in ['/props', '/v1/status', '/metrics']}
        snap['/metrics'] = {k: v for k, v in snap['/metrics'].items() if k in ('engine', 'live', 'totals', 'hardware_static')}
        return snap


def proc_stat(pid):
    s = read(f'/proc/{pid}/stat')
    if not s:
        return {}
    parts = s[s.rfind(')') + 2:].split()
    return {'major_faults': int(parts[9]), 'cpu_ticks': int(parts[11]) + int(parts[12]),
            'start_ticks': int(parts[19])}


def kvfile(path, scale=1):
    text = read(path)
    if text is None:
        return None
    result = {}
    for line in text.splitlines():
        parts = line.replace(':', '').split()
        if len(parts) >= 2:
            try:
                result[parts[0]] = int(parts[1]) * scale
            except ValueError:
                pass
    return result


def telemetry(cfg):
    dev = Path(cfg['gpu_device'])
    mem = kvfile('/proc/meminfo', 1024) or {}
    vm = kvfile('/proc/vmstat') or {}
    pid = cfg.get('engine_pid')
    p = Path(f'/proc/{pid}')
    st = kvfile(p / 'status', 1024) if pid else None
    # Status contains non-byte fields too: select only byte-valued entries.
    sm = kvfile(p / 'smaps_rollup', 1024) if pid else None
    sample = {'utc': utc(), 'monotonic_s': time.monotonic(),
        'vram_total_bytes': number(dev / 'mem_info_vram_total'),
        'vram_used_bytes': number(dev / 'mem_info_vram_used'),
        'gtt_total_bytes': number(dev / 'mem_info_gtt_total'),
        'gtt_used_bytes': number(dev / 'mem_info_gtt_used'),
        'mem_total_bytes': mem.get('MemTotal'), 'mem_available_bytes': mem.get('MemAvailable'),
        'cached_bytes': mem.get('Cached'), 'buffers_bytes': mem.get('Buffers'),
        'swap_used_bytes': mem['SwapTotal'] - mem['SwapFree'] if 'SwapTotal' in mem and 'SwapFree' in mem else None,
        'swap_in_pages': vm.get('pswpin'), 'swap_out_pages': vm.get('pswpout'),
        'system_major_faults': vm.get('pgmajfault'),
        'rss_bytes': (st or {}).get('VmRSS'), 'pss_bytes': (sm or {}).get('Pss'),
        'process': proc_stat(pid) if pid else None,
        'process_io': kvfile(p / 'io') if pid else None,
        'gpu_busy_percent': number(dev / 'gpu_busy_percent'),
        'system_cpu_ticks': read('/proc/stat').splitlines()[0] if read('/proc/stat') else None,
        'disks': {}, 'sensors': {}}
    for line in (read('/proc/diskstats') or '').splitlines():
        x = line.split()
        if len(x) >= 14 and not x[2].startswith(('loop', 'ram')):
            sample['disks'][x[2]] = {'reads': int(x[3]), 'read_bytes': int(x[5]) * 512,
                                   'writes': int(x[7]), 'write_bytes': int(x[9]) * 512}
    for hw in sorted(dev.glob('hwmon/hwmon*')):
        for pattern in ('temp*_input', 'power*_average', 'power*_cap', 'freq*_input'):
            for f in hw.glob(pattern):
                sample['sensors'][f.name] = number(f)
    sample['gpu_sclk'] = read(dev / 'pp_dpm_sclk')
    sample['gpu_mclk'] = read(dev / 'pp_dpm_mclk')
    return sample


class Sampler:
    def __init__(self, cfg, path, case):
        self.cfg, self.path, self.case = cfg, path, case
        self.samples = []
        self.errors = []
        self.done = threading.Event()

    def take(self):
        try:
            s = telemetry(self.cfg)
            self.samples.append(s)
            append(self.path, {'case': self.case, **s})
        except Exception as e:
            self.errors.append(str(e))

    def __enter__(self):
        self.take()
        def loop():
            while not self.done.wait(self.cfg['sample_interval']):
                self.take()
        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.done.set()
        self.thread.join()
        self.take()

    def summary(self):
        if not self.samples:
            return {'errors': self.errors}
        first, last = self.samples[0], self.samples[-1]
        duration = last['monotonic_s'] - first['monotonic_s']
        out = {'baseline': first, 'end': last, 'errors': self.errors, 'extrema': {}}
        for k in first:
            values = [s[k] for s in self.samples if isinstance(s.get(k), (float, int))]
            if values:
                out['extrema'][k] = {'min': min(values), 'max': max(values)}
        def delta(a, b):
            return b - a if a is not None and b is not None and b >= a else None
        out['delta'] = {k: delta(first[k], last[k]) for k in
                        ['swap_in_pages', 'swap_out_pages', 'system_major_faults']}
        out['delta']['process'] = {k: delta((first['process'] or {}).get(k), (last['process'] or {}).get(k))
                                   for k in ['major_faults', 'cpu_ticks']}
        process_changed = (first['process'] or {}).get('start_ticks') != (last['process'] or {}).get('start_ticks')
        if process_changed:
            out['errors'].append('PID identity changed; process deltas invalid')
            out['delta']['process'] = {}
        ticks = out['delta']['process'].get('cpu_ticks')
        out['process_cpu_percent_one_core'] = ticks / os.sysconf('SC_CLK_TCK') / duration * 100 if ticks is not None and duration > 0 else None
        out['delta']['process_io'] = {k: delta((first['process_io'] or {}).get(k), (last['process_io'] or {}).get(k))
                                       for k in ['read_bytes', 'write_bytes', 'syscr', 'syscw', 'rchar', 'wchar']}
        if process_changed:
            out['delta']['process_io'] = {}
        out['delta']['disks'] = {d: {k: delta(first['disks'][d].get(k), last['disks'].get(d, {}).get(k))
                                    for k in first['disks'][d]} for d in first['disks']}
        def cpu_ticks(value):
            return [int(x) for x in value.split()[1:]] if value else None
        ca, cb = cpu_ticks(first['system_cpu_ticks']), cpu_ticks(last['system_cpu_ticks'])
        if ca and cb:
            total = sum(cb[:8]) - sum(ca[:8])
            idle = cb[3] + cb[4] - ca[3] - ca[4]
            out['system_cpu_busy_percent'] = (total-idle)/total*100 if total > 0 else None
        return out


def runtime_libraries(pid):
    paths = set()
    for line in (read(f'/proc/{pid}/maps') or '').splitlines():
        parts = line.split(maxsplit=5)
        if len(parts) == 6 and re.search(r'(amdhip|hipblas|rocblas|hsa-runtime|hiprtc|rocsolver).*\.so', parts[5]):
            paths.add(parts[5])
    result = {}
    for p in paths:
        try:
            st = Path(p).stat()
            result[p] = {'bytes': st.st_size, 'mtime_ns': st.st_mtime_ns}
        except OSError:
            result[p] = None
    return result


def inventory(cfg):
    pid = cfg.get('engine_pid')
    binpath = cfg.get('engine_binary')
    return {'utc': utc(), 'hostname': socket.gethostname(), 'kernel': platform.release(),
        'os_release': read('/etc/os-release'),
        'firmware_identity': {k: read(Path('/sys/class/dmi/id') / k) for k in ['sys_vendor', 'product_name', 'board_name', 'bios_vendor', 'bios_version', 'bios_date']},
        'kernel_cmdline': read('/proc/cmdline'), 'cpu': read('/proc/cpuinfo'), 'page_size_bytes': os.sysconf('SC_PAGE_SIZE'),
        'gpu': {k: read(Path(cfg['gpu_device']) / k) for k in ['vendor', 'device', 'revision', 'uevent']},
        'uma': {'current_path': cfg.get('uma_current'), 'index': read(cfg['uma_current']) if cfg.get('uma_current') else None,
                'options_path': cfg.get('uma_options'), 'options': read(cfg['uma_options']) if cfg.get('uma_options') else None},
        'ttm': {p.name: read(p) for p in Path('/sys/module/ttm/parameters').glob('*')},
        'amdgpu_parameters': {p.name: read(p) for p in Path('/sys/module/amdgpu/parameters').glob('*')},
        'memory': telemetry(cfg), 'swap': read('/proc/swaps'),
        'strata_cli_version': command([cfg['strata_cli'], '--version']) if cfg.get('strata_cli') else None,
        'engine_binary_sha256': sha(binpath) if binpath and Path(binpath).is_file() else None,
        'effective_argv': redacted_argv(argv_for(pid)), 'relevant_environment': env_for(pid),
        'process_identity': proc_stat(pid), 'process_cgroup': read(f'/proc/{pid}/cgroup'),
        'startup_units': command(['systemctl', 'list-units', '--all', '--no-pager', '*strata*']),
        'user_startup_units': command(['systemctl', '--user', 'list-units', '--all', '--no-pager', '*strata*']),
        'rocm': {str(p): read(p) for p in Path('/opt/rocm/.info').glob('version*')},
        'hipconfig': command(['hipconfig', '--version']), 'runtime_libraries': runtime_libraries(pid), 'pci': command(['lspci', '-nn']),
        'background_processes': command(['ps', '-eo', 'pid,ppid,comm,%cpu,%mem,rss']),
        'disk_free': shutil.disk_usage('.')._asdict(), 'lsblk': command(['lsblk', '-J', '-o', 'NAME,TYPE,SIZE,MOUNTPOINTS']),
        'launch_config_sha256': sha(cfg['launch_config']) if Path(cfg.get('launch_config', '')).is_file() else None,
        'notes': {k: cfg.get(k) for k in ['background_notes', 'startup_notes']}}


def kernel_events(since):
    journal_since = dt.datetime.fromisoformat(since).strftime('%Y-%m-%d %H:%M:%S UTC')
    r = command(['journalctl', '-k', '--since', journal_since, '--no-pager', '-o', 'short-iso'])
    text = r.get('stdout', '')
    r['events'] = [line for line in text.splitlines() if re.search(
        r'out of memory|oom.kill|killed process|amdgpu.*(fault|reset|timeout|failed)|gpu reset', line, re.I)]
    # Permission denials can return exit status zero; never equate absence of access with no events.
    r['coverage'] = 'unavailable' if r.get('returncode') != 0 or r.get('stderr') or 'No journal files' in text or text == '-- No entries --' else 'journal-visible-only'
    r.pop('stdout', None)
    return r


def config(path):
    c = json.loads(Path(path).read_text())
    if c['sample_interval'] < 1 or c['request_timeout'] <= 0 or c['context_margin'] < 32:
        raise ValueError('Use sample_interval >= 1, positive timeout and context_margin >= 32')
    if c['output_tokens'] != 512:
        raise ValueError('Protocol v1 requires output_tokens=512 (smoke overrides separately)')
    if c['expected']['context_tokens'] < 256000 or c['expected']['expert_slots'] != 24576:
        raise ValueError('This protocol requires a ~256K context and 24,576 resident expert slots')
    if not c.get('model_files') or not c.get('tokenizer_files'):
        raise ValueError('List every model/pack/MTP and tokenizer file explicitly')
    API(c)
    return c


def effective(api, cfg, profile=None):
    snap = api.snapshot()
    errors = []
    eng = snap['/metrics']['engine']
    props, status = snap['/props'], snap['/v1/status']
    expected = cfg['expected']
    args = argv_for(cfg.get('engine_pid'))
    if not eng.get('version'):
        errors.append('Effective engine version unavailable')
    slots = eng.get('expert_slots')
    if slots != expected['expert_slots']:
        errors.append(f'configuration limitation: expert_slots={slots}, required={expected["expert_slots"]}')
    if props.get('default_generation_settings', {}).get('n_ctx') != expected['context_tokens']:
        errors.append('Effective context differs from requested context')
    if props.get('total_slots') != 1:
        errors.append('Protocol requires server capacity 1')
    if option(args, '--expert-cache') != expected['expert_cache'] or expected['expert_cache'] in ('auto', '', None) or 'REPLACE' in expected['expert_cache']:
        errors.append('An explicit, matching --expert-cache size is required in engine argv')
    spec = option(args, '--spec')
    if spec is None or not spec.isdigit() or int(spec) <= 0:
        errors.append('An explicit enabled --spec argument is required for this comparison')
    if option(args, '--kv') != expected['kv']:
        errors.append('Effective --kv differs or is unavailable')
    if eng.get('drafting') != 'mtp':
        errors.append('Effective drafting must report mtp; no silent fallback permitted')
    if eng.get('kv') != expected['kv']:
        errors.append('Engine INFO kv differs or unavailable')
    checks = expected.get('engine_info', {})
    if not checks or any('REPLACE' in k for k in checks):
        errors.append('Pin verified MTP/speculation engine INFO fields in expected.engine_info')
    for k, v in checks.items():
        if eng.get(k) != v:
            errors.append(f'Effective engine field {k}: {eng.get(k)!r}, required {v!r}')
    if status.get('activity', {}).get('in_flight') != 0 or snap['/metrics'].get('live', {}).get('state') != 'idle':
        errors.append('Server must be loaded and idle with no queued clients')
    try:
        exe = Path(f'/proc/{cfg["engine_pid"]}/exe').resolve(strict=True)
        if not os.path.samefile(exe, cfg['engine_binary']):
            errors.append('engine_pid does not execute engine_binary')
    except (OSError, TypeError):
        errors.append('Readable local engine PID and matching binary required')
    if env_for(cfg.get('engine_pid')) is None:
        errors.append('Engine environment unavailable')
    if profile:
        total = number(Path(cfg['gpu_device']) / 'mem_info_vram_total')
        if total is None or abs(total - PROFILES[profile]) > max(128 * 2**20, PROFILES[profile] * .03):
            errors.append(f'Profile VRAM mismatch: {total}; requested {PROFILES[profile]} bytes')
    return snap, errors


WORDS = 'alpha beta gamma delta epsilon zeta eta theta lambda matrix buffer commit function pointer cache kernel record result'.split()


def fit_prompt(count, messages, target, seed, prefix, suffix, markers=False):
    """Fit measured rendered tokens, never a chars/token estimate. Whole deterministic records."""
    rng = random.Random(seed)
    records = [f'file{i:06d}: ' + ' '.join(rng.choices(WORDS, k=12)) + '.\n' for i in range(target // 6 + 128)]
    needles = [(f'lookup_{seed}_{i}', f'VALUE_{rng.getrandbits(128):032x}') for i in range(3)] if markers else []
    def build(n, padding=0):
        rows = records[:n]
        for fraction, (key, value) in zip([.1, .5, .9], needles):
            rows.insert(int(n * fraction), f'CRITICAL {key} = {value}\n')
        tail = suffix
        if needles:
            tail += '\nReturn only the values for ' + ', '.join(k for k, _ in needles) + ', in order, one per line.'
        return messages + [{'role': 'user', 'content': prefix + ''.join(rows) + ' x' * padding + tail}]
    lo, hi, best, size = 0, len(records), None, None
    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = build(mid)
        n = count(candidate)
        if n <= target:
            best, size, lo = candidate, n, mid + 1
            best_records = mid
        else:
            hi = mid - 1
    if best is not None:
        low_pad, high_pad = 0, 128
        while low_pad <= high_pad:
            pad = (low_pad + high_pad) // 2
            candidate = build(best_records, pad)
            n = count(candidate)
            if n <= target:
                best, size, low_pad = candidate, n, pad + 1
            else:
                high_pad = pad - 1
    if best is None or size < target * .995:
        raise ValueError(f'Cannot fit target {target}: measured {size}')
    return best, size, needles


def plan(cfg, smoke=False):
    maximum = cfg['expected']['context_tokens'] - cfg['output_tokens'] - cfg['context_margin']
    matrix = [(512, 1)] if smoke else MATRIX
    cases = []
    for target, reps in matrix:
        for rep in range(reps):
            cases.append({'id': f'throughput-{target}-{rep}', 'kind': 'throughput', 'target': min(target, maximum)})
    if not smoke:
        for target in [32768, 65536, 131072, 262144]:
            cases.append({'id': f'agent-{target}', 'kind': 'agent', 'target': min(target, maximum)})
            for i in range(2):
                cases.append({'id': f'agent-{target}-tool-{i}', 'kind': 'agent-tool', 'target': min(target, maximum)})
        for target in [131072, 262144]:
            cases.append({'id': f'recall-{target}', 'kind': 'recall', 'target': min(target, maximum)})
    for i in range(3):
        cases.append({'id': f'repeat-{i}', 'kind': 'repeat', 'target': 512 if smoke else 4096})
    # Two identical early requests distinguish first observed inference from repeat inference.
    return [{'id': 'repeat-first', 'kind': 'repeat', 'target': 512 if smoke else 4096},
            {'id': 'repeat-second', 'kind': 'repeat', 'target': 512 if smoke else 4096}] + cases


def prepare(cfg, directory, smoke=False):
    api = API(cfg)
    directory.mkdir(parents=True, exist_ok=False)
    files = {}
    started = time.monotonic()
    for p in [cfg['engine_binary'], cfg['launch_config'], *cfg['model_files'], *cfg['tokenizer_files']]:
        files[str(Path(p).resolve())] = {'sha256': sha(p), 'bytes': Path(p).stat().st_size, 'mtime_ns': Path(p).stat().st_mtime_ns}
    if not cfg['model_files'] or not cfg['tokenizer_files']:
        raise ValueError('Explicit complete model and tokenizer file lists required')
    props = api.get('/props')
    template = props.get('chat_template')
    if not template:
        raise ValueError('Server must expose effective chat_template')
    (directory / 'chat_template.jinja').write_text(template)
    cases, history, repeat = plan(cfg, smoke), [], None
    for index, case in enumerate(cases):
        print('Preparing', case['id'], flush=True)
        kind = case['kind']
        base = history if kind in ('agent', 'agent-tool') else []
        if kind == 'agent-tool':
            candidate = base + [{'role': 'user', 'content': f'Tool result {case["id"]}: pytest: 42 passed. git diff: +3 -1. Summarize next steps.'}]
            n = api.count(candidate)
            if n + cfg['output_tokens'] + cfg['context_margin'] > cfg['expected']['context_tokens']:
                # Reserve space for short additions at the maximum checkpoint during preparation below.
                raise ValueError('Agent tool turn does not fit context')
            needles = []
        elif kind == 'repeat' and repeat:
            candidate, n, needles = repeat
        else:
            target = case['target'] - (1024 if kind == 'agent' else 0)
            candidate, n, needles = fit_prompt(api.count, base, target, cfg['seed'] + index,
                f'[case {case["id"]}]\n', '\nExplain the record structure and propose a lookup implementation.', kind == 'recall')
        case.update(messages=candidate, input_tokens=n, needles=needles,
                    output_tokens=32 if smoke else cfg['output_tokens'])
        case['prompt_sha256'] = digest(canonical(candidate))
        if kind in ('agent', 'agent-tool'):
            history = candidate + [{'role': 'assistant', 'content': 'I will inspect the files and run the focused tests.'}]
        if kind == 'repeat':
            repeat = candidate, n, needles
        append(directory / 'cases.jsonl', case)
    manifest = {'schema': SCHEMA, 'protocol': PROTOCOL, 'smoke': smoke, 'files': files,
                'template_sha256': digest(template.encode()), 'config': cfg, 'hashing_and_preparation_s': time.monotonic() - started,
                'cases_sha256': sha(directory / 'cases.jsonl'), 'case_count': len(cases)}
    write(directory / 'manifest.json', manifest)
    print(directory)


def load_bundle(cfg, directory):
    manifest = json.loads((directory / 'manifest.json').read_text())
    if manifest['schema'] != SCHEMA or manifest['protocol'] != PROTOCOL:
        raise ValueError('Unsupported bundle schema/protocol')
    # PID and observational notes may change after manual restarts; workload settings may not.
    keys = ['model', 'quantization', 'sampling', 'seed', 'output_tokens', 'expected', 'context_margin',
            'model_files', 'tokenizer_files', 'engine_binary', 'launch_config']
    if any(cfg[k] != manifest['config'][k] for k in keys):
        raise ValueError('Configuration drift: prepare a new bundle and baseline')
    if sha(directory / 'cases.jsonl') != manifest['cases_sha256']:
        raise ValueError('Frozen workload hash mismatch')
    for p, info in manifest['files'].items():
        stat = Path(p).stat()
        if stat.st_size != info['bytes'] or stat.st_mtime_ns != info['mtime_ns']:
            raise ValueError(f'File changed since prepare: {p}; re-prepare and baseline')
    if sha(cfg['engine_binary']) != manifest['files'][str(Path(cfg['engine_binary']).resolve())]['sha256']:
        raise ValueError('Engine binary hash changed')
    cases = [json.loads(s) for s in (directory / 'cases.jsonl').read_text().splitlines()]
    if len(cases) != manifest['case_count']:
        raise ValueError('Incomplete bundle')
    return manifest, cases


def confirm(yes, message):
    if yes:
        return
    if not sys.stdin.isatty() or input(message + '\nType RUN to continue: ') != 'RUN':
        raise ValueError('Not confirmed; use --yes only after reviewing check output')


def stream(api, case, record, event_path):
    body = api.body(case['messages'], case['output_tokens'])
    body['stream'] = True
    started = time.monotonic()
    record.update(ttft_s=None, first_answer_s=None, answer='', thinking='', usage=None, input_tokens=None)
    complete = False
    pending = []
    flushed_at = started
    try:
        with api.request('/v1/messages', body, timeout=min(60, api.cfg['request_timeout'])) as response:
            # SIGALRM enforces the entire wall deadline, even with endless keepalives.
            for raw in response:
                if STOP.is_set():
                    raise InterruptedError('Interrupted')
                if not raw.startswith(b'data:'):
                    continue
                event = json.loads(raw[5:].strip())
                elapsed = time.monotonic() - started
                pending.append({'case': case['id'], 'elapsed_s': elapsed, 'event': event})
                if time.monotonic() - flushed_at >= 1:
                    append_events(event_path, pending)
                    pending.clear()
                    flushed_at = time.monotonic()
                typ = event.get('type')
                if typ == 'error':
                    raise ValueError('Server stream error: ' + json.dumps(event))
                if typ == 'message_start':
                    record['input_tokens'] = event['message']['usage']['input_tokens']
                if typ == 'content_block_delta':
                    delta = event['delta']
                    value = delta.get('text') or delta.get('thinking') or delta.get('partial_json')
                    if value:
                        if record['ttft_s'] is None:
                            record['ttft_s'] = elapsed
                        if delta.get('type') in ('text_delta', 'input_json_delta') and record['first_answer_s'] is None:
                            record['first_answer_s'] = elapsed
                        if delta.get('text'):
                            record['answer'] += delta['text']
                        if delta.get('thinking'):
                            record['thinking'] += delta['thinking']
                if typ == 'message_delta':
                    record['usage'] = event.get('usage')
                    record['finish_reason'] = event.get('delta', {}).get('stop_reason')
                if typ == 'message_stop':
                    complete = True
    finally:
        wall = time.monotonic() - started
        record['wall_s'] = wall
        append_events(event_path, pending)
    if not complete:
        raise ValueError('Truncated stream: no message_stop')
    record['wall_s'] = wall


def timing_metrics(timing):
    timing = timing or {}
    prompt_n, prompt_ms = timing.get('prompt_n'), timing.get('prompt_ms')
    decode_n, decode_ms, rate = timing.get('predicted_n'), timing.get('predicted_ms'), timing.get('predicted_per_second')
    note = None
    if decode_ms and rate is not None:
        implied = rate * decode_ms / 1000
        if decode_n is None or abs(decode_n - implied) > .05 * decode_ms / 1000 + 1:
            decode_n = implied
            note = 'Decode numerator inferred from engine rate and timer; predicted_n differs (speculative accounting).'
    return {'prefill_tps': prompt_n / (prompt_ms / 1000) if prompt_n and prompt_ms and prompt_ms > 0 else None,
            'decode_tps': decode_n / (decode_ms / 1000) if decode_n and decode_ms and decode_ms > 0 else None,
            'fresh_input_tokens': prompt_n, 'cached_tokens': timing.get('cache_n'),
            'decode_timer_tokens': decode_n, 'token_accounting_note': note}


def stable_identity(cfg, manifest, snap):
    return {'protocol': PROTOCOL, 'schema': SCHEMA, 'workload': manifest['cases_sha256'],
        'smoke': manifest['smoke'], 'files': {p: v['sha256'] for p, v in manifest['files'].items()},
        'model': cfg['model'], 'quantization': cfg['quantization'], 'expected': cfg['expected'],
        'sampling': cfg['sampling'], 'seed': cfg['seed'], 'template': manifest['template_sha256'],
        'engine_version': snap['/metrics']['engine'].get('version'),
        'effective_pinned_info': {k: snap['/metrics']['engine'].get(k) for k in cfg['expected']['engine_info']},
        'argv': redacted_argv(argv_for(cfg['engine_pid'])), 'environment': env_for(cfg['engine_pid']),
        'launch_config_sha256': sha(cfg['launch_config']),
        'host': socket.gethostname(), 'kernel': platform.release(),
        'cpu_model': next((line.split(':', 1)[1].strip() for line in (read('/proc/cpuinfo') or '').splitlines() if line.startswith('model name')), None),
        'gpu_pci': {k: read(Path(cfg['gpu_device']) / k) for k in ['vendor', 'device', 'revision']}}


def new_session(root, profile):
    root.mkdir(parents=True, exist_ok=True)
    path = root / (dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + profile + '-' + uuid.uuid4().hex[:8])
    path.mkdir(mode=0o700)
    return path


def signal_setup():
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    def interrupt(signum, frame):
        STOP.set()
        raise KeyboardInterrupt('Safe interruption requested')
    def timeout(signum, frame):
        raise TimeoutError('Request wall-clock deadline exceeded; client connection closed')
    signal.signal(signal.SIGINT, interrupt)
    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGALRM, timeout)


def run(cfg, bundle, profile, root, yes):
    manifest, cases = load_bundle(cfg, bundle)
    api = API(cfg)
    try:
        initial, errors = effective(api, cfg, profile)
    except (OSError, ValueError, KeyError) as e:
        initial, errors = {}, ['Strata unavailable: ' + str(e)]
    if initial and digest(initial['/props']['chat_template'].encode()) != manifest['template_sha256']:
        errors.append('Effective chat template changed')
    if errors:
        out = new_session(root, profile)
        rejected = {'schema': SCHEMA, 'protocol': PROTOCOL, 'profile': profile, 'started': utc(),
            'status': 'configuration-limitation', 'requested': cfg, 'initial_server': initial,
            'inventory': inventory(cfg), 'identity': {'rejected': True}, 'warnings': errors}
        skipped = [{**{k: v for k, v in c.items() if k != 'messages'},
                    'status': 'skipped', 'error': 'Preflight configuration limitation'} for c in cases]
        for r in skipped:
            append(out / 'runs.jsonl', r)
        write(out / 'session.json', rejected)
        report(out, rejected, skipped)
        raise ValueError('\n'.join(errors) + f'\nEvidence saved at {out}')
    confirm(yes, f'{len(cases)} requests, including long-context work; no other clients may use this server.\n'
            'This can take hours and exhaust memory. Attach-only: services and host settings are never changed.')
    out = new_session(root, profile)
    print('Results:', out, flush=True)
    session = {'schema': SCHEMA, 'protocol': PROTOCOL, 'profile': profile, 'started': utc(),
        'requested': cfg, 'inventory': inventory(cfg), 'initial_server': initial,
        'first_request_state': 'fresh-process-no-prior-requests' if initial['/v1/status']['activity']['requests'] == 0 else 'previously-used-process',
        'identity': stable_identity(cfg, manifest, initial), 'status': 'running',
        'warnings': ['Custom UMA experiment, not the official Strata standard benchmark.',
            'Null telemetry means unavailable; permissions/driver/version may limit collection.',
            'RSS includes shared/mapped pages; VRAM/GTT/RAM overlap on UMA and must not be summed.',
            'File hashes verified at prepare; run checks size/mtime and binary hash. Rehash if files may be modified preserving metadata.',
            'Filesystem warmth uncontrolled; first request is not evidence of a cold filesystem.',
            'Kernel journal coverage may be partial. Inspect kernel_events.coverage.'],
        'planned_cases': [{k: v for k, v in c.items() if k != 'messages'} for c in cases]}
    write(out / 'session.json', session)
    signal_setup()
    records = []
    try:
        for case in cases:
            r = {k: v for k, v in case.items() if k != 'messages'}
            r.update(status='running', started=utc(), warnings=[], prefill_tps=None, decode_tps=None,
                     ttft_s=None, wall_s=None, effective_expert_slots=None)
            append(out / 'progress.jsonl', {'case': case['id'], 'event': 'started', 'utc': utc()})
            timer = time.monotonic()
            sampler = None
            try:
                before, errors = effective(api, cfg, profile)
                r['effective_expert_slots'] = before['/metrics']['engine'].get('expert_slots')
                if proc_stat(cfg['engine_pid']) != session['inventory']['process_identity']:
                    # CPU/fault counters evolve; only start ticks identify the process.
                    if proc_stat(cfg['engine_pid']).get('start_ticks') != session['inventory']['process_identity'].get('start_ticks'):
                        errors.append('Engine process restarted')
                if stable_identity(cfg, manifest, before) != session['identity']:
                    errors.append('Effective configuration drift')
                if errors:
                    raise ValueError('; '.join(errors))
                actual = api.count(case['messages'])
                r['verified_input_tokens'] = actual
                if actual != case['input_tokens'] or actual + case['output_tokens'] + cfg['context_margin'] > cfg['expected']['context_tokens']:
                    raise ValueError('Token count drift or unsafe context budget')
                with Sampler(cfg, out / 'telemetry.jsonl', case['id']) as sampler:
                    signal.setitimer(signal.ITIMER_REAL, cfg['request_timeout'])
                    timer = time.monotonic()
                    try:
                        stream(api, case, r, out / 'events.jsonl')
                    finally:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                after = api.snapshot()
                r['server_after'] = after
                r['effective_expert_slots_after'] = after['/metrics']['engine'].get('expert_slots')
                before_status, after_status = before['/v1/status'], after['/v1/status']
                a, b = before_status['activity']['requests'], after_status['activity']['requests']
                if b != a + 1 or after_status['activity']['in_flight'] != 0:
                    raise ValueError('Timing attribution unsafe: concurrent requests or server still busy')
                r['generated_tokens'] = (r.get('usage') or {}).get('output_tokens')
                r['timings'] = after_status.get('last_timings')
                r.update(timing_metrics(r['timings']))
                r['timing_source'] = '/v1/status.last_timings, guarded by request counter +1 and idle state'
                if r['input_tokens'] != actual:
                    raise ValueError('Server input token count differs: truncation or template drift')
                if after['/metrics']['engine'].get('expert_slots') != cfg['expected']['expert_slots']:
                    raise ValueError('Resident expert slots changed during request')
                if stable_identity(cfg, manifest, after) != session['identity']:
                    raise ValueError('Effective configuration changed during request')
                if case['kind'] == 'throughput' and (r.get('cached_tokens') is None or r['cached_tokens'] > 64):
                    raise ValueError('Fresh-payload throughput requires known cache reuse <=64 template/prefix tokens')
                r['status'] = 'ok'
                if case['kind'] == 'recall':
                    expected = '\n'.join(v for _, v in case['needles'])
                    r['exact_match'] = r['answer'].strip() == expected
                    r['marker_matches'] = {k: v in r['answer'] for k, v in case['needles']}
                for key in METRICS:
                    if r.get(key) is None:
                        r['warnings'].append(f'{key} unavailable: server did not supply usable timing or content')
            except (Exception, KeyboardInterrupt) as e:
                r['status'] = 'interrupted' if isinstance(e, KeyboardInterrupt) else 'failed'
                r['error'] = f'{type(e).__name__}: {e}'
                r['wall_s'] = r.get('wall_s') or time.monotonic() - timer
                # Close the stream and stop scheduling; do not control/cancel unrelated server work.
                STOP.set()
            finally:
                if sampler:
                    r['telemetry'] = sampler.summary()
                    r.update(resource_metrics(r['telemetry']))
                r['ended'] = utc()
                append(out / 'runs.jsonl', r)
                records.append(r)
                report(out, session, records)
            print(case['id'], r['status'], flush=True)
            if STOP.is_set():
                break
    finally:
        completed = {r['id'] for r in records}
        for case in cases:
            if case['id'] not in completed:
                r = {k: v for k, v in case.items() if k != 'messages'}
                r.update(status='skipped', error='Scheduling stopped after failure or interruption')
                append(out / 'runs.jsonl', r)
                records.append(r)
        session.update(ended=utc(), status='complete' if all(r['status'] == 'ok' for r in records) else 'partial',
                       kernel_events=kernel_events(session['started']))
        session['final_memory'] = telemetry(cfg)
        write(out / 'session.json', session)
        report(out, session, records)
    if session['status'] != 'complete':
        raise ValueError(f'Partial session preserved at {out}')


def resource_metrics(t):
    extrema, delta = t.get('extrema', {}), t.get('delta', {})
    out = {}
    for key, source, which in [
        ('peak_vram_bytes', 'vram_used_bytes', 'max'), ('peak_gtt_bytes', 'gtt_used_bytes', 'max'),
        ('min_mem_available_bytes', 'mem_available_bytes', 'min'), ('peak_rss_bytes', 'rss_bytes', 'max'),
        ('peak_pss_bytes', 'pss_bytes', 'max'), ('peak_swap_bytes', 'swap_used_bytes', 'max')]:
        out[key] = extrema.get(source, {}).get(which)
    out.update(process_disk_read_bytes=delta.get('process_io', {}).get('read_bytes'),
               process_read_syscalls=delta.get('process_io', {}).get('syscr'),
               swap_in_pages=delta.get('swap_in_pages'), swap_out_pages=delta.get('swap_out_pages'),
               process_major_faults=delta.get('process', {}).get('major_faults'),
               process_cpu_percent_one_core=t.get('process_cpu_percent_one_core'),
               system_cpu_busy_percent=t.get('system_cpu_busy_percent'))
    for disk, values in delta.get('disks', {}).items():
        for k in ['read_bytes', 'reads']:
            out[f'system_disk:{disk}:{k}'] = values.get(k)
    return out


def summary(records):
    groups = {}
    for r in records:
        if r['status'] != 'ok' or r['kind'] == 'recall':
            continue
        # Keep agent checkpoints and repeat-cache phases separate.
        key = re.sub(r'-\d+$', '', r['id']) if r['kind'] == 'throughput' else r['id']
        groups.setdefault(key, []).append(r)
    result = {}
    for key, rows in groups.items():
        result[key] = {}
        available_metrics = METRICS + RESOURCE_METRICS + sorted({k for r in rows for k in r if k.startswith('system_disk:')})
        for metric in available_metrics:
            values = [r[metric] for r in rows if isinstance(r.get(metric), (int, float)) and math.isfinite(r[metric])]
            if values:
                mean = statistics.mean(values)
                result[key][metric] = {'n': len(values), 'median': statistics.median(values),
                    'min': min(values), 'max': max(values), 'stdev': statistics.stdev(values) if len(values) > 1 else None,
                    'cv_percent': statistics.stdev(values) / mean * 100 if len(values) > 1 and mean else None}
    return result


def display(value):
    return 'unavailable' if value is None else f'{value:.3f}' if isinstance(value, float) else str(value)


def report(out, session, records):
    stats = summary(records)
    write(out / 'summary.json', stats)
    lines = ['# Strata UMA experiment', '', f'Profile: {session["profile"]}; status: {session["status"]}.', '',
        'Custom protocol; concurrency 1. Higher throughput is better; lower latency is better.', '',
        '| Test | Status | Actual input | Output | Fresh | Cached | Expert slots | Prefill tok/s | Decode tok/s | TTFT s | Wall s | Recall exact |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for r in records:
        values = [r['id'], r['status'], r.get('input_tokens'), r.get('generated_tokens'), r.get('fresh_input_tokens'), r.get('cached_tokens'),
                  r.get('effective_expert_slots'), r.get('prefill_tps'), r.get('decode_tps'), r.get('ttft_s'), r.get('wall_s'), r.get('exact_match')]
        lines.append('| ' + ' | '.join(display(v) for v in values) + ' |')
    lines += ['', '## Statistics', '', '| Test | Metric | n | Median | Min | Max | Sample SD | CV % |',
              '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for test, metrics in stats.items():
        for metric, values in metrics.items():
            lines.append('| ' + ' | '.join([test, metric] + [display(values[k]) for k in ['n', 'median', 'min', 'max', 'stdev', 'cv_percent']]) + ' |')
    lines += ['', '## Memory, I/O and cache observations', '',
        'Baseline, end, sampled minima/maxima, per-device I/O and process deltas follow. '
        'MemAvailable minimum is the memory-pressure peak. VRAM/GTT/RSS overlap and must not be added. '
        'Process syscr counts read syscalls, not physical IOPS. /proc/diskstats counts block operations; '
        'partition, device-mapper and physical device rows overlap, so they are not summed. '
        'Cached/Buffers and reduced read_bytes are cache observations, not a measured cache-hit ratio. '
        'Sampling can miss brief peaks. HWMON temperature is millidegrees C, power microwatts, freq Hz.', '']
    for r in records:
        if r.get('telemetry'):
            lines += [f'### {r["id"]}', '', '```json', json.dumps(r['telemetry'], indent=2), '```', '']
    lines += ['## Errors and warnings', ''] + ['- ' + w for w in session.get('warnings', [])]
    for r in records:
        if r.get('error'):
            lines.append(f'- {r["id"]}: {r["error"]}')
        lines += [f'- {r["id"]}: {w}' for w in r.get('warnings', [])]
    lines += ['', '## Complete configuration and provenance', '', '```json', json.dumps(session, indent=2), '```', '']
    (out / 'report.md').write_text('\n'.join(line.rstrip() for line in lines))


def compare(paths, out):
    docs = []
    for path in paths:
        s = json.loads((path / 'session.json').read_text())
        if s.get('schema') != SCHEMA or s.get('protocol') != PROTOCOL or 'identity' not in s:
            raise ValueError(f'Unsupported session: {path}')
        records, torn = read_jsonl(path / 'runs.jsonl')
        if torn:
            s = {**s, 'recovery_warning': torn, 'status': 'recovered-partial'}
        docs.append((path, s, records))
    baselines = [x for x in docs if x[1]['profile'] == 'baseline-96']
    if len(baselines) != 1:
        raise ValueError('Supply exactly one baseline-96 session')
    baseline = baselines[0]
    base_stats = summary(baseline[2])
    rows, warnings = [], []
    for path, session, records in docs:
        valid_identity = session['identity'] == baseline[1]['identity']
        if session.get('synthetic_example'):
            warnings.append(f'{path}: SIMULATED EXAMPLE; numbers are invented, not measured')
        if session.get('recovery_warning'):
            warnings.append(f'{path}: {session["recovery_warning"]}')
        if not valid_identity:
            warnings.append(f'{path}: configuration/workload mismatch; percentage comparisons withheld')
        if session.get('kernel_events', {}).get('events'):
            warnings.append(f'{path}: kernel OOM/GPU events detected; inspect session report for stability evidence')
        if session['status'] != 'complete':
            warnings.append(f'{path}: PARTIAL session; no full-suite ranking')
        for test, metrics in summary(records).items():
            # Never compute a cell comparison from a reduced subset of repetitions.
            planned = [r for r in session.get('planned_cases', records) if (re.sub(r'-\d+$', '', r['id']) if r['kind'] == 'throughput' else r['id']) == test]
            base_planned = [r for r in baseline[1].get('planned_cases', baseline[2]) if (re.sub(r'-\d+$', '', r['id']) if r['kind'] == 'throughput' else r['id']) == test]
            for metric, values in metrics.items():
                b = base_stats.get(test, {}).get(metric)
                eligible = (valid_identity and b and len(planned) == values['n'] and len(base_planned) == b['n']
                            and all(r['status'] == 'ok' for r in records if (re.sub(r'-\d+$', '', r['id']) if r['kind'] == 'throughput' else r['id']) == test)
                            and all(r['status'] == 'ok' for r in baseline[2] if (re.sub(r'-\d+$', '', r['id']) if r['kind'] == 'throughput' else r['id']) == test))
                pct = (values['median'] / b['median'] - 1) * 100 if eligible and b['median'] else None
                rows.append({'session': str(path), 'profile': session['profile'], 'test': test, 'metric': metric,
                             **values, 'delta_percent_vs_baseline': pct, 'comparable': bool(eligible)})
        for r in records:
            if r['status'] != 'ok' or r.get('exact_match') is False:
                warnings.append(f'{path} / {r["id"]}: {r["status"]}; recall exact={r.get("exact_match")} {r.get("error", "")}')
    out.mkdir(parents=True, exist_ok=False)
    fields = ['session', 'profile', 'test', 'metric', 'n', 'median', 'min', 'max', 'stdev', 'cv_percent', 'delta_percent_vs_baseline', 'comparable']
    with open(out / 'comparison.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        writer.writerows(rows)
    lines = ['# UMA comparison', '', 'Percent change is (candidate / baseline - 1) × 100. '
             'Negative latency changes are improvements. Missing percentages are withheld, not zero.', '',
             '| Profile | Test | Metric | n | Median | Min–max | Δ vs 96+32 % | Comparable |',
             '| --- | --- | --- | ---: | ---: | --- | ---: | --- |']
    if any(s.get('synthetic_example') for _, s, _ in docs):
        lines[2:2] = ['**SIMULATED EXAMPLE: invented numbers, not measured performance.**', '']
    for r in rows:
        lines.append('| ' + ' | '.join([r['profile'], r['test'], r['metric'], str(r['n']), display(r['median']),
                     f'{display(r["min"])}–{display(r["max"])}', display(r['delta_percent_vs_baseline']), str(r['comparable'])]) + ' |')
    lines += ['', '## Warnings and failures', ''] + ['- ' + w for w in warnings]
    lines += ['', '## Session metadata', '', 'Configuration, memory, disk I/O, correctness and kernel evidence are in each linked report.', '']
    for path, session, _ in docs:
        lines += [f'- [{path}]({os.path.relpath(path.resolve() / "report.md", out.resolve())}): {session["status"]}',
                  '```json', json.dumps({'profile': session['profile'], 'identity': session['identity'],
                                        'kernel_events': session.get('kernel_events')}, indent=2), '```', '']
    (out / 'comparison.md').write_text('\n'.join(line.rstrip() for line in lines))
    print(out)


def watch_load(cfg, profile, root, condition, pid_file, yes, bundle=None):
    """Observe only: operator starts the process separately and writes its PID."""
    manifest = load_bundle(cfg, bundle)[0] if bundle is not None else None
    confirm(yes, 'Start this observer BEFORE manually launching a fresh process. No existing service is stopped.\n'
            'Only declare manual-cold-fs after independently establishing cold filesystem state.\n'
            'Do not hash model files between that action and loading. Press Ctrl-C to end observation.')
    if pid_file.exists():
        raise ValueError('PID file must be absent initially; use a new path')
    api = API(cfg)
    endpoint = urllib.parse.urlsplit(cfg['url'])
    try:
        with socket.create_connection((endpoint.hostname, endpoint.port or 80), timeout=2):
            pass
    except OSError:
        pass
    else:
        raise ValueError('Endpoint already serves: observer requires a fresh external process on a free port')
    out = new_session(root, profile + '-load')
    signal_setup()
    observation = {'schema': SCHEMA, 'protocol': PROTOCOL, 'profile': profile, 'condition': condition,
                   'started': utc(), 'status': 'waiting', 'requested': cfg.copy(), 'inventory': inventory(cfg),
                   'prepared_files': manifest['files'] if manifest else None,
                   'warnings': ['Filesystem condition is operator attested, not independently verified.',
                                'Process counters before PID publication are unavailable; observed readiness includes polling delay.']}
    write(out / 'load.json', observation)
    deadline = time.monotonic() + cfg['request_timeout']
    try:
        with Sampler(cfg, out / 'telemetry.jsonl', 'load') as sampler:
            while time.monotonic() < deadline:
                if pid_file.exists():
                    pid = number(pid_file)
                    if pid and proc_stat(pid):
                        cfg['engine_pid'] = pid
                        try:
                            if not os.path.samefile(f'/proc/{pid}/exe', cfg['engine_binary']):
                                raise ValueError('Observed PID does not execute engine_binary')
                            s = api.get('/v1/status')
                            if s.get('loaded'):
                                resolved, errors = effective(api, cfg, profile)
                                observation['effective_configuration'] = resolved
                                observation['effective_argv'] = redacted_argv(argv_for(pid))
                                observation['relevant_environment'] = env_for(pid)
                                if errors:
                                    raise ValueError('Load configuration limitation: ' + '; '.join(errors))
                                uptime = float(read('/proc/uptime').split()[0])
                                start_s = proc_stat(pid)['start_ticks'] / os.sysconf('SC_CLK_TCK')
                                observation.update(status='observed', process_start_to_ready_s=uptime-start_s,
                                    pid=pid, server=s, memory=telemetry(cfg),
                                    process_lifetime_io_at_ready=kvfile(f'/proc/{pid}/io'),
                                    process_lifetime_faults_at_ready=proc_stat(pid).get('major_faults'),
                                    prior_requests=s.get('activity', {}).get('requests'),
                                    effective_expert_slots=api.get('/metrics')['engine'].get('expert_slots'))
                                if observation['prior_requests'] != 0:
                                    raise ValueError('Process has already served requests; fresh-load evidence invalid')
                                break
                        except urllib.error.URLError:
                            pass
                STOP.wait(1)
            else:
                raise TimeoutError('Load observation deadline expired')
        observation['telemetry'] = sampler.summary()
    except (Exception, KeyboardInterrupt) as e:
        observation.update(status='partial', error=str(e))
    finally:
        if 'sampler' in locals():
            observation['telemetry'] = sampler.summary()
        observation['ended'] = utc()
        observation['kernel_events'] = kernel_events(observation['started'])
        write(out / 'load.json', observation)
        (out / 'report.md').write_text('# External model-load observation\n\n```json\n' + json.dumps(observation, indent=2) + '\n```\n')
    print(out)
    if observation['status'] != 'observed':
        raise ValueError('Partial load observation preserved at ' + str(out))


def read_jsonl(path):
    raw = Path(path).read_text() if Path(path).exists() else ''
    rows, warning = [], None
    lines = raw.splitlines()
    for index, line in enumerate(lines):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            if index != len(lines)-1 or raw.endswith('\n'):
                raise ValueError('Corrupt JSONL before end of file: ' + str(path))
            warning = 'Ignored torn final JSONL row after abrupt termination; original file preserved.'
    return rows, warning


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('benchmark/config.json'))
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('prepare', help='Hash files and freeze exact-token fixtures; no inference')
    p.add_argument('--bundle', type=Path, default=Path('benchmark/prepared/full'))
    p.add_argument('--smoke', action='store_true')
    p = sub.add_parser('check', help='Read-only target-host preflight; no inference')
    p.add_argument('--bundle', type=Path)
    p.add_argument('--profile', choices=PROFILES)
    p.add_argument('--save', type=Path)
    p.add_argument('--offline', action='store_true', help='Capture host inventory without contacting Strata')
    p = sub.add_parser('run')
    p.add_argument('--profile', choices=PROFILES, required=True)
    p.add_argument('--bundle', type=Path, default=Path('benchmark/prepared/full'))
    p.add_argument('--results', type=Path, default=Path('benchmark/results'))
    p.add_argument('--yes', action='store_true')
    p = sub.add_parser('compare')
    p.add_argument('results', nargs='+', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('report', help='Regenerate report after abrupt client termination')
    p.add_argument('result', type=Path)
    p = sub.add_parser('watch-load')
    p.add_argument('--profile', choices=PROFILES, required=True)
    p.add_argument('--bundle', type=Path, default=Path('benchmark/prepared/full'))
    p.add_argument('--condition', choices=['cold-process-warm-fs', 'manual-cold-fs'], required=True)
    p.add_argument('--pid-file', type=Path, required=True)
    p.add_argument('--results', type=Path, default=Path('benchmark/results'))
    p.add_argument('--yes', action='store_true')
    args = parser.parse_args()
    try:
        if args.action == 'compare':
            compare(args.results, args.output)
            return
        if args.action == 'report':
            s = json.loads((args.result / 'session.json').read_text())
            records, warning = read_jsonl(args.result / 'runs.jsonl')
            if warning:
                s.setdefault('warnings', []).append(warning)
            seen = {r['id'] for r in records}
            records += [{**c, 'status': 'skipped', 'error': 'No completed record recovered'}
                        for c in s.get('planned_cases', []) if c['id'] not in seen]
            s['status'] = 'recovered-partial' if s['status'] == 'running' else s['status']
            report(args.result, s, records)
            return
        cfg = config(args.config)
        if args.action == 'prepare':
            prepare(cfg, args.bundle, args.smoke)
        elif args.action == 'check':
            snap, errors = None, []
            if args.offline:
                errors.append('Offline inventory only: Strata effective configuration unverified')
            else:
                try:
                    snap, errors = effective(API(cfg), cfg, args.profile)
                except (OSError, ValueError, KeyError) as e:
                    errors.append('Strata preflight unavailable: ' + str(e))
            if args.bundle:
                load_bundle(cfg, args.bundle)
            value = {'inventory': inventory(cfg), 'server': snap, 'errors': errors,
                     'note': 'Hashes in bundle were computed by prepare; check does not read model data or run inference.'}
            if args.save:
                write(args.save, value)
            print(json.dumps(value, indent=2))
            if errors:
                raise ValueError('Preflight failed: ' + '; '.join(errors))
        elif args.action == 'watch-load':
            watch_load(cfg, args.profile, args.results, args.condition, args.pid_file, args.yes, args.bundle)
        else:
            # Prevent overlapping suite clients on this host. Never lock or control the engine itself.
            lock_path = Path('/tmp') / f'strata-uma-benchmark-{os.getuid()}.lock'
            with open(lock_path, 'a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                run(cfg, args.bundle, args.profile, args.results, args.yes)
    except (OSError, ValueError, KeyError) as e:
        parser.exit(1, f'benchmark: {e}\n')


if __name__ == '__main__':
    main()
