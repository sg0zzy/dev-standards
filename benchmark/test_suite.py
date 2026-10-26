"""Offline smoke and regression tests. No Strata/model/GPU/admin access needed."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import suite as b


class Handler(BaseHTTPRequestHandler):
    requests = 0
    mode = 'ok'
    timing = None
    expert_slots = 24576

    def log_message(self, *args):
        pass

    def send_json(self, value):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(value).encode())

    def do_GET(self):
        if self.path == '/props':
            return self.send_json({'chat_template': 'MOCK TEMPLATE', 'total_slots': 1,
                'default_generation_settings': {'n_ctx': 262144}})
        if self.path == '/v1/status':
            return self.send_json({'loaded': True, 'engine': 'mock',
                'activity': {'requests': type(self).requests, 'in_flight': 0}, 'last_timings': type(self).timing})
        if self.path == '/metrics':
            return self.send_json({'engine': {'version': 'mock', 'drafting': 'mtp', 'spec': 4, 'kv': 'int8',
                'expert_slots': type(self).expert_slots}, 'live': {'state': 'idle'}})
        self.send_error(404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        n = sum(len(m['content'].split()) for m in body['messages']) + 8
        if self.path == '/v1/messages/count_tokens':
            return self.send_json({'input_tokens': n})
        if self.path != '/v1/messages':
            return self.send_error(404)
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.end_headers()
        def event(value):
            self.wfile.write(b'data: ' + json.dumps(value).encode() + b'\n\n')
            self.wfile.flush()
        event({'type': 'message_start', 'message': {'usage': {'input_tokens': n + (1 if self.mode == 'truncate' else 0)}}})
        if self.mode == 'timeout':
            time.sleep(.15)
            return
        event({'type': 'content_block_delta', 'delta': {'type': 'thinking_delta', 'thinking': 'reason'}})
        event({'type': 'content_block_delta', 'delta': {'type': 'text_delta', 'text': 'answer'}})
        if self.mode == 'broken':
            return
        type(self).requests += 2 if self.mode == 'concurrent' else 1
        type(self).timing = {'prompt_n': n, 'cache_n': 0, 'prompt_ms': 100,
                            'predicted_n': 32, 'predicted_ms': 500, 'predicted_per_second': 64}
        event({'type': 'message_delta', 'delta': {'stop_reason': 'max_tokens'}, 'usage': {'output_tokens': 32}})
        event({'type': 'message_stop'})


class SuiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        Handler.requests, Handler.mode, Handler.expert_slots = 0, 'ok', 24576
        Handler.timing = None
        self.cfg = json.loads((Path(__file__).parent / 'config.example.json').read_text())
        self.cfg.update(url=f'http://127.0.0.1:{self.server.server_port}', engine_pid=os.getpid(), engine_binary=sys.executable,
                        strata_cli=None, engine_arg_notes='mock')
        self.cfg['expected']['expert_cache'] = '70000'
        self.cfg['expected']['engine_info'] = {'drafting': 'mtp', 'spec': 4}
        self.dev = self.root / 'gpu'
        self.dev.mkdir()
        for name, n in {'mem_info_vram_total': 96*2**30, 'mem_info_vram_used': 68*2**30,
                        'mem_info_gtt_total': 16*2**30, 'mem_info_gtt_used': 0}.items():
            (self.dev / name).write_text(str(n))
        self.cfg['gpu_device'] = str(self.dev)
        for key in ['model_files', 'tokenizer_files']:
            path = self.root / key
            path.write_text('mock bytes ' + key)
            self.cfg[key] = [str(path)]
        path = self.root / 'launch.json'
        path.write_text('{}')
        self.cfg['launch_config'] = str(path)
        self.bundle = self.root / 'bundle'
        self.args = [sys.executable, '--expert-cache', '70000', '--kv', 'int8', '--mtp', 'pack', '--spec', '4']
        self.argpatch = patch.object(b, 'argv_for', return_value=self.args)
        self.argpatch.start()
        b.STOP.clear()
        self.handlers = {s: signal.getsignal(s) for s in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGALRM]}

    def tearDown(self):
        signal.setitimer(signal.ITIMER_REAL, 0)
        for signum, handler in self.handlers.items():
            signal.signal(signum, handler)
        self.argpatch.stop()
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()
        b.STOP.clear()

    def prepared(self):
        with contextlib.redirect_stdout(io.StringIO()):
            b.prepare(self.cfg, self.bundle, smoke=True)
        return b.load_bundle(self.cfg, self.bundle)

    def test_exact_fit_and_context_headroom(self):
        api = b.API(self.cfg)
        for target in [512, 4096, 131072, 261568]:
            messages, n, needles = b.fit_prompt(api.count, [], target, 395, 'case\n', '\nrecall', True)
            self.assertLessEqual(n, target)
            self.assertGreaterEqual(n, target * .995)
            self.assertEqual(api.count(messages), n)
            self.assertEqual(len(needles), 3)
        cases = b.plan(self.cfg)
        self.assertEqual(len([c for c in cases if c['kind'] == 'throughput']), 19)
        self.assertTrue(all(c['target'] + 512 + 64 <= 262144 for c in cases))

    def test_preparation_frozen_and_tampering_rejected(self):
        manifest, cases = self.prepared()
        self.assertEqual(len(cases), 6)
        self.assertEqual(cases[0]['prompt_sha256'], cases[1]['prompt_sha256'])
        self.assertEqual(cases[0]['prompt_sha256'], cases[-1]['prompt_sha256'])
        (self.bundle / 'cases.jsonl').write_text('{}\n')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            b.load_bundle(self.cfg, self.bundle)

    def test_changed_model_rejected(self):
        self.prepared()
        Path(self.cfg['model_files'][0]).write_text('new model')
        with self.assertRaisesRegex(ValueError, 'File changed'):
            b.load_bundle(self.cfg, self.bundle)

    def test_auto_and_slot_reduction_rejected(self):
        Handler.expert_slots = 100
        self.cfg['expected']['expert_cache'] = 'auto'
        _, errors = b.effective(b.API(self.cfg), self.cfg, 'baseline-96')
        self.assertTrue(any('configuration limitation' in e for e in errors))
        self.assertTrue(any('explicit' in e for e in errors))

    def test_mock_end_to_end_and_report_and_compare(self):
        self.prepared()
        # Hardware inventory subprocesses are unnecessary in offline fixtures.
        with patch.object(b, 'inventory', return_value={'process_identity': b.proc_stat(os.getpid())}), \
             patch.object(b, 'kernel_events', return_value={'coverage': 'mock', 'events': []}), \
             contextlib.redirect_stdout(io.StringIO()):
            b.run(self.cfg, self.bundle, 'baseline-96', self.root / 'results', True)
        result = next((self.root / 'results').iterdir())
        records = [json.loads(s) for s in (result / 'runs.jsonl').read_text().splitlines()]
        self.assertEqual(len(records), 6)
        self.assertTrue(all(r['status'] == 'ok' for r in records))
        self.assertTrue(all(r['decode_tps'] == 64 for r in records))
        self.assertTrue(all(r['ttft_s'] <= r['first_answer_s'] for r in records))
        self.assertTrue((result / 'telemetry.jsonl').is_file())
        self.assertIn('Complete configuration', (result / 'report.md').read_text())
        candidate = self.root / 'candidate'
        candidate.mkdir()
        for name in ['session.json', 'runs.jsonl', 'report.md']:
            (candidate / name).write_bytes((result / name).read_bytes())
        s = json.loads((candidate / 'session.json').read_text())
        s['profile'] = 'uma-64'
        b.write(candidate / 'session.json', s)
        with contextlib.redirect_stdout(io.StringIO()):
            b.compare([result, candidate], self.root / 'comparison')
        self.assertIn('0.000', (self.root / 'comparison/comparison.md').read_text())
        s['identity']['seed'] += 1
        b.write(candidate / 'session.json', s)
        with contextlib.redirect_stdout(io.StringIO()):
            b.compare([result, candidate], self.root / 'mismatch')
        self.assertIn('mismatch', (self.root / 'mismatch/comparison.md').read_text())

    def test_failed_stream_preserves_partial_and_skips(self):
        self.prepared()
        Handler.mode = 'broken'
        with patch.object(b, 'inventory', return_value={'process_identity': b.proc_stat(os.getpid())}), \
             patch.object(b, 'kernel_events', return_value={'coverage': 'mock'}), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, 'Partial session'):
                b.run(self.cfg, self.bundle, 'baseline-96', self.root / 'results', True)
        result = next((self.root / 'results').iterdir())
        records = [json.loads(s) for s in (result / 'runs.jsonl').read_text().splitlines()]
        self.assertEqual(records[0]['status'], 'failed')
        self.assertEqual(records[0]['answer'], 'answer')
        self.assertTrue(all(r['status'] == 'skipped' for r in records[1:]))
        self.assertEqual(b.summary(records), {})

    def test_concurrency_and_truncation_rejected(self):
        for mode in ['concurrent', 'truncate']:
            Handler.mode = mode
            r = {}
            api = b.API(self.cfg)
            n_before = api.get('/v1/status')['activity']['requests']
            case = {'id': 'case', 'messages': [{'role': 'user', 'content': 'hi'}], 'output_tokens': 32}
            b.stream(api, case, r, self.root / 'events.jsonl')
            if mode == 'concurrent':
                self.assertNotEqual(api.get('/v1/status')['activity']['requests'], n_before + 1)
            else:
                self.assertNotEqual(r['input_tokens'], api.count(case['messages']))

    def test_deadline_and_decode_accounting(self):
        Handler.mode = 'timeout'
        b.signal_setup()
        signal.setitimer(signal.ITIMER_REAL, .05)
        with self.assertRaises(TimeoutError):
            b.stream(b.API(self.cfg), {'id': 'timeout', 'messages': [{'role': 'user', 'content': 'hi'}], 'output_tokens': 32}, {}, self.root / 'events')
        signal.setitimer(signal.ITIMER_REAL, 0)
        metrics = b.timing_metrics({'predicted_n': 100, 'predicted_ms': 1000, 'predicted_per_second': 45})
        self.assertEqual(metrics['decode_tps'], 45)
        self.assertTrue(metrics['token_accounting_note'])
        self.assertIsNone(b.timing_metrics({})['prefill_tps'])

    def test_full_agent_and_recall_bundle_is_deterministic_and_safe(self):
        def count(_api, messages):
            return sum(len(m['content'].split()) for m in messages) + 8
        with patch.object(b.API, 'count', count), contextlib.redirect_stdout(io.StringIO()):
            b.prepare(self.cfg, self.bundle, smoke=False)
            other = self.root / 'other'
            b.prepare(self.cfg, other, smoke=False)
        manifest, cases = b.load_bundle(self.cfg, self.bundle)
        self.assertEqual(manifest['cases_sha256'], json.loads((other / 'manifest.json').read_text())['cases_sha256'])
        self.assertEqual(len(cases), 38)
        agents = [c for c in cases if c['kind'] in ('agent', 'agent-tool')]
        self.assertEqual(len(agents), 12)
        self.assertTrue(all(c['input_tokens'] + c['output_tokens'] + 64 <= 262144 for c in cases))
        self.assertEqual(agents[1]['messages'][:-1], agents[0]['messages'] +
                         [{'role': 'assistant', 'content': 'I will inspect the files and run the focused tests.'}])
        for case in cases:
            if case['kind'] == 'recall':
                for key, value in case['needles']:
                    self.assertEqual(case['messages'][0]['content'].count(value), 1)
                    self.assertIn(key, case['messages'][0]['content'])

    def test_configuration_limitation_is_saved_without_inference(self):
        self.prepared()
        Handler.expert_slots = 100
        with patch.object(b, 'inventory', return_value={}), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, 'configuration limitation'):
                b.run(self.cfg, self.bundle, 'baseline-96', self.root / 'results', False)
        result = next((self.root / 'results').iterdir())
        self.assertEqual(json.loads((result / 'session.json').read_text())['status'], 'configuration-limitation')
        self.assertEqual(Handler.requests, 0)

    def test_partial_repetition_groups_are_not_compared(self):
        base, partial = self.root / 'base', self.root / 'partial'
        base.mkdir(); partial.mkdir()
        rows = [{'id': f'throughput-4096-{i}', 'kind': 'throughput', 'status': 'ok',
                 'prefill_tps': 1000, 'decode_tps': 48, 'ttft_s': 4, 'wall_s': 15} for i in range(5)]
        for path, profile, records in [(base, 'baseline-96', rows), (partial, 'uma-64', rows[:4])]:
            b.write(path / 'session.json', {'schema': b.SCHEMA, 'protocol': b.PROTOCOL, 'profile': profile,
                'identity': {'test': True}, 'status': 'partial', 'planned_cases': rows})
            for r in records:
                b.append(path / 'runs.jsonl', r)
        with contextlib.redirect_stdout(io.StringIO()):
            b.compare([base, partial], self.root / 'comparison')
        import csv
        with open(self.root / 'comparison/comparison.csv') as f:
            rows = list(csv.DictReader(f))
        self.assertTrue(all(r['delta_percent_vs_baseline'] == '' and r['comparable'] == 'False'
                            for r in rows if r['profile'] == 'uma-64'))

    def test_interruption_and_journal_permission_and_recovery(self):
        self.prepared()
        with patch.object(b, 'inventory', return_value={'process_identity': b.proc_stat(os.getpid())}), \
             patch.object(b, 'kernel_events', return_value={'coverage': 'mock'}), \
             patch.object(b, 'stream', side_effect=KeyboardInterrupt('requested')), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, 'Partial session'):
                b.run(self.cfg, self.bundle, 'baseline-96', self.root / 'results', True)
        result = next((self.root / 'results').iterdir())
        records, warning = b.read_jsonl(result / 'runs.jsonl')
        self.assertEqual(records[0]['status'], 'interrupted')
        self.assertEqual(records[-1]['status'], 'skipped')
        with open(result / 'runs.jsonl', 'a') as f:
            f.write('{"torn":')
        recovered, warning = b.read_jsonl(result / 'runs.jsonl')
        self.assertEqual(len(recovered), len(records))
        self.assertIn('torn', warning)
        with patch.object(b, 'command', return_value={'returncode': 0, 'stdout': '', 'stderr': 'Permission denied'}):
            self.assertEqual(b.kernel_events(b.utc())['coverage'], 'unavailable')

    def test_load_observer_refuses_occupied_port_and_preserves_timeout(self):
        with self.assertRaisesRegex(ValueError, 'Endpoint already serves'):
            b.watch_load(self.cfg, 'baseline-96', self.root / 'results',
                         'cold-process-warm-fs', self.root / 'pid', True)
        self.cfg['url'] = 'http://127.0.0.1:1'
        self.cfg['request_timeout'] = .01
        with patch.object(b, 'inventory', return_value={}), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, 'Partial load observation'):
                b.watch_load(self.cfg, 'baseline-96', self.root / 'results',
                             'manual-cold-fs', self.root / 'pid', True)
        result = next((self.root / 'results').iterdir())
        doc = json.loads((result / 'load.json').read_text())
        self.assertEqual(doc['status'], 'partial')
        self.assertIn('telemetry', doc)
        self.assertEqual(Handler.requests, 0)

    def test_telemetry_and_secret_redaction(self):
        s = b.telemetry(self.cfg)
        self.assertEqual(s['gtt_used_bytes'], 0)
        self.assertIsNone(s['gpu_busy_percent'])
        self.assertIn('read_bytes', s['process_io'])
        self.assertEqual(b.redacted_argv(['--api-key', 'secret', '--tokenizer', '/tok', '--password=x']),
                         ['--api-key', '<redacted>', '--tokenizer', '/tok', '--password=<redacted>'])
        with self.assertRaises(ValueError):
            b.API({'url': 'http://remote.example:8080'})


if __name__ == '__main__':
    unittest.main()
