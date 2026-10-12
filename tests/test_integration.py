import shutil
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from media_forge.engine import execute_plan
from media_forge.jobs import JobStore, JobWorker
from media_forge.probe import inspect_media


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
class MediaIntegrationTests(unittest.TestCase):
    def make_sample(self, path):
        subprocess.run([
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
            '-f', 'lavfi', '-i', 'testsrc2=size=160x96:rate=12:duration=2',
            '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=16000:duration=2',
            '-c:v', 'mpeg4', '-q:v', '4', '-c:a', 'aac', '-shortest', str(path)
        ], check=True, timeout=30)

    def test_preserve_convert_both(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d, 'source.mp4')
            self.make_sample(source)
            original = inspect_media(str(source))
            results = execute_plan('testjob12345678', {'source': str(source), 'output_dir': d, 'mode': 'both', 'preset': 'balanced', 'container': 'mp4'}, lambda *a: None, threading.Event(), Path(d, 'logs'))
            self.assertEqual(len(results), 2)
            archived = inspect_media(results[0]['path'])
            converted = inspect_media(results[1]['path'])
            self.assertEqual(archived['streams'][0]['codec'], original['streams'][0]['codec'])
            self.assertEqual(converted['streams'][0]['codec'], 'h264')
            self.assertTrue(Path(results[0]['path']).is_file())
            self.assertTrue(Path(results[1]['path']).is_file())

    def test_queue_processing(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d, 'queue-source.mp4')
            self.make_sample(source)
            store = JobStore(Path(d, 'queue.sqlite3'))
            worker = JobWorker(store, Path(d, 'logs'))
            worker.start()
            try:
                job = store.submit({'source': str(source), 'output_dir': d, 'mode': 'convert', 'container': 'mkv', 'preset': 'compact'})
                import time
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    current = store.get(job['id'])
                    if current['state'] in ('completed', 'failed', 'canceled'):
                        break
                    time.sleep(0.1)
                self.assertEqual(current['state'], 'completed', current['error'])
                self.assertEqual(len(current['outputs']), 1)
            finally:
                worker.stop()

    def test_failed_conversion_retains_verified_archive(self):
        from unittest.mock import patch
        from media_forge import engine
        with tempfile.TemporaryDirectory() as d:
            src = Path(d, 'source.mp4')
            self.make_sample(src)
            store = JobStore(Path(d, 'jobs.sqlite3'))
            worker = JobWorker(store, Path(d, 'logs'))
            original_builder = engine.build_ffmpeg_args
            def builder(kind, source, target, plan):
                if kind == 'convert':
                    return ['ffmpeg', '-an_invalid_option', str(target)]
                return original_builder(kind, source, target, plan)
            with patch('media_forge.engine.build_ffmpeg_args', side_effect=builder):
                worker.start()
                try:
                    job = store.submit({'source': str(src), 'output_dir': d, 'mode': 'both', 'preset': 'balanced', 'container': 'mp4'})
                    import time
                    deadline = time.monotonic() + 30
                    while time.monotonic() < deadline:
                        current = store.get(job['id'])
                        if current['state'] in ('partial_success', 'failed', 'completed'):
                            break
                        time.sleep(.1)
                    self.assertEqual(current['state'], 'partial_success', current['error'])
                    self.assertEqual(len(current['outputs']), 1)
                    self.assertTrue(Path(current['outputs'][0]['path']).exists())
                finally:
                    worker.stop()

    def test_no_overwrite_on_duplicate_job_id(self):
        from media_forge.probe import MediaError
        with tempfile.TemporaryDirectory() as d:
            src = Path(d, 'source.mp4')
            self.make_sample(src)
            plan = {'source': str(src), 'output_dir': d, 'mode': 'preserve', 'preset': 'balanced', 'container': 'mp4'}
            first = execute_plan('duplicate987654', plan, lambda *a: None, threading.Event(), Path(d, 'logs'))
            old_size = Path(first[0]['path']).stat().st_size
            with self.assertRaises(MediaError):
                execute_plan('duplicate987654', plan, lambda *a: None, threading.Event(), Path(d, 'logs'))
            self.assertEqual(Path(first[0]['path']).stat().st_size, old_size)


if __name__ == '__main__':
    unittest.main()
