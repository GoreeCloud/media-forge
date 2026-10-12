import tempfile
import unittest
from pathlib import Path
from media_forge.engine import PRESETS, build_ffmpeg_args, safe_stem, validate_plan
from media_forge.jobs import JobStore
from media_forge.probe import MediaError, validate_preservation


class PlanTests(unittest.TestCase):
    def test_safe_stem(self):
        self.assertEqual(safe_stem('hi there:really?.mp4'), 'hi-there-really')
        self.assertEqual(safe_stem('....'), 'media')

    def test_validate_plan(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d, 'input.mp4')
            source.write_bytes(b'1')
            plan = validate_plan({'source': str(source), 'output_dir': d, 'mode': 'both', 'preset': 'balanced', 'container': 'mp4'})
            self.assertEqual(plan['mode'], 'both')
            with self.assertRaises(MediaError):
                validate_plan({**plan, 'mode': 'delete-all'})

    def test_commands_are_shell_free(self):
        plan = {'preset': 'balanced', 'container': 'mp4'}
        command = build_ffmpeg_args('preserve', Path('/input with space.mp4'), Path('/tmp/out.mkv'), plan)
        self.assertEqual(command[command.index('-i') + 1], '/input with space.mp4')
        self.assertIn('-c', command)
        self.assertIn('copy', command)
        command = build_ffmpeg_args('convert', Path('/tmp/in.mkv'), Path('/tmp/out.mp4'), plan)
        self.assertIn('libx264', command)

    def test_preservation_detects_missing_audio(self):
        first = {'streams': [{'type': 'video', 'codec': 'h264'}, {'type': 'audio', 'codec': 'aac'}], 'chapters': 0}
        second = {'streams': [{'type': 'video', 'codec': 'h264'}], 'chapters': 0}
        with self.assertRaises(MediaError):
            validate_preservation(first, second)


class StoreTests(unittest.TestCase):
    def test_persist_and_cancel(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d, 'input.mp4')
            src.write_bytes(b'sample')
            path = Path(d, 'jobs.sqlite3')
            store = JobStore(path)
            job = store.submit({'source': str(src), 'output_dir': d, 'mode': 'preserve', 'preset': 'balanced', 'container': 'mp4'})
            self.assertEqual(job['state'], 'queued')
            self.assertEqual(JobStore(path).get(job['id'])['state'], 'queued')
            self.assertTrue(store.cancel_queued(job['id']))
            self.assertEqual(store.get(job['id'])['state'], 'canceled')

    def test_running_jobs_marked_interrupted(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, 'jobs.sqlite3')
            src = Path(d, 'source.mp4')
            src.write_bytes(b'a')
            store = JobStore(path)
            job = store.submit({'source': str(src), 'output_dir': d, 'mode': 'convert'})
            store.update(job['id'], state='running')
            self.assertEqual(JobStore(path).get(job['id'])['state'], 'interrupted')


class RecoveryRegressionTests(unittest.TestCase):
    def test_processing_job_recovery(self):
        import sqlite3, json
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, 'recover.sqlite3')
            JobStore(path)
            with sqlite3.connect(path) as db:
                db.execute("INSERT INTO jobs(id,created_at,updated_at,state,plan_json,outputs_json) VALUES (?,?,?,?,?,?)",
                           ('kept', 'x', 'x', 'processing', '{}', json.dumps([{'kind':'preserve'}])))
            self.assertEqual(JobStore(path).get('kept')['state'], 'partial_success')


if __name__ == '__main__':
    unittest.main()
