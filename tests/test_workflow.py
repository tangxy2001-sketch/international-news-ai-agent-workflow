import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
spec = importlib.util.spec_from_file_location('workflow',Path(__file__).resolve().parents[1]/'scripts/workflow.py')
workflow = importlib.util.module_from_spec(spec); spec.loader.exec_module(workflow)
class WorkflowTests(unittest.TestCase):
    def test_init_preserves_existing_run(self):
        with tempfile.TemporaryDirectory() as folder:
            args = SimpleNamespace(path=folder,topic='测试',keywords='条件甲,方案乙',start='2030-01-01',end='2030-01-31')
            workflow.initialize(args)
            original = (Path(folder)/'request.json').read_bytes()
            with self.assertRaises(ValueError): workflow.initialize(args)
            self.assertEqual(original,(Path(folder)/'request.json').read_bytes())
    def test_reversed_dates_rejected_before_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'run'
            with self.assertRaises(ValueError):
                workflow.initialize(SimpleNamespace(path=path,topic='测试',keywords='词',start='2030-02-02',end='2030-02-01'))
            self.assertFalse(path.exists())
    def test_mapping_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)
            (path/'报告初稿.md').write_text('正文[^1]\n\n[^1]: https://example.com/a\n',encoding='utf-8')
            (path/'articles.json').write_text(json.dumps([{'footnote':1,'url':'https://example.com/b'}]),encoding='utf-8')
            with self.assertRaises(ValueError): workflow.validate(path)
    def test_orphan_footnote_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)
            (path/'报告初稿.md').write_text('正文\n\n[^1]: https://example.com/a\n',encoding='utf-8')
            (path/'articles.json').write_text(json.dumps([{'footnote':1,'url':'https://example.com/a'}]),encoding='utf-8')
            with self.assertRaises(ValueError): workflow.validate(path)

    def test_region_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            selected = workflow.REGIONS[0]
            workflow.initialize(SimpleNamespace(path=folder,topic='测试',keywords='词',start='2030-01-01',end='2030-01-31',regions=selected))
            request = json.loads((Path(folder)/'request.json').read_text())
            self.assertEqual(request['regions'],[selected])
            self.assertEqual([p.name for p in (Path(folder)/'原始素材').iterdir()],[selected])
    def test_unknown_region_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'run'
            with self.assertRaises(ValueError):
                workflow.initialize(SimpleNamespace(path=path,topic='测试',keywords='词',start='2030-01-01',end='2030-01-31',regions='invalid-group'))
            self.assertFalse(path.exists())
