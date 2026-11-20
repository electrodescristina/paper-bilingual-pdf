"""Behavior checks for coverage, rendered geometry, and CLI exit codes."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'audit_layout.py'
spec = importlib.util.spec_from_file_location('audit_layout', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LayoutAuditTests(unittest.TestCase):
    def setUp(self):
        self.source = {'units': [{'id': u, 'kind': 'paragraph'} for u in ('a', 'b')]}
        self.layout = {
            'units': [{'id': u, 'status': 'translated', 'translation': '测试译文。',
                       'reviewed': True} for u in ('a', 'b')],
            'items': [{'id': 'en', 'unit_ids': ['a', 'b'], 'page': 1, 'side': 'en',
                       'kind': 'page', 'bbox': [0, 0, 600, 800],
                       'panel_bbox': [0, 0, 600, 800]}] + [
                {'id': u, 'unit_ids': [u], 'page': 1, 'side': 'zh', 'kind': 'text',
                 'bbox': [650, y, 1100, y + 20], 'panel_bbox': [620, 0, 1220, 800]}
                for u, y in [('a', 60), ('b', 100)]]}

    def assertIssue(self, layout, text):
        result = module.audit(self.source, layout)
        self.assertFalse(result['passed'])
        self.assertTrue(any(text in e for e in result['errors']), result)

    def test_clean_layout(self):
        self.assertTrue(module.audit(self.source, self.layout)['passed'])

    def test_overlap_despite_both_items_fitting_panel(self):
        self.layout['items'][2]['bbox'] = [650, 70, 1100, 90]
        self.assertIssue(self.layout, 'Overlap')

    def test_outside_panel(self):
        self.layout['items'][1]['bbox'] = [610, 60, 1100, 80]
        self.assertIssue(self.layout, 'outside panel')

    def test_missing_translation(self):
        self.layout['units'].pop()
        self.assertIssue(self.layout, 'Missing output unit')

    def test_preserved_prose_is_not_translation(self):
        self.layout['units'][0]['status'] = 'preserved'
        self.assertIssue(self.layout, 'Prose cannot')

    def test_unreviewed_content(self):
        self.layout['units'][0]['reviewed'] = False
        self.assertIssue(self.layout, 'review unfinished')

    def test_missing_chinese_placement(self):
        self.layout['items'].pop()
        self.assertIssue(self.layout, 'Missing zh placement')

    def test_independent_pagination(self):
        self.layout['items'][1]['page'] = 2
        self.assertIssue(self.layout, 'No shared comparison page')

    def test_reversed_panels(self):
        self.layout['items'][0]['panel_bbox'] = [620, 0, 1220, 800]
        self.assertIssue(self.layout, 'panels are reversed')

    def test_duplicate_rendered_item(self):
        self.layout['items'].append(copy.deepcopy(self.layout['items'][1]))
        self.assertIssue(self.layout, 'Duplicate rendered item')

    def test_explicit_figure_label_overlap(self):
        self.source['units'][0]['kind'] = 'figure'
        self.source['units'][1]['kind'] = 'identifier'
        self.layout['items'][1]['kind'] = 'figure'
        self.layout['items'][2]['bbox'] = [650, 70, 1100, 90]
        self.layout['allowed_overlaps'] = [
            {'items': ['a', 'b'], 'reason': 'Translated label inside its figure'}]
        self.assertTrue(module.audit(self.source, self.layout)['passed'])

    def test_nonfinite_geometry(self):
        self.layout['items'][1]['bbox'][2] = float('nan')
        with self.assertRaises(ValueError):
            module.audit(self.source, self.layout)

    def test_cli_exit_codes(self):
        broken = copy.deepcopy(self.layout)
        broken['items'][2]['bbox'] = [650, 70, 1100, 90]
        invalid = copy.deepcopy(self.layout)
        invalid['items'][1]['bbox'] = [0, 0, 0, 0]
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            original = base / 'source.json'
            original.write_text(json.dumps(self.source), encoding='utf-8')
            for data, expected in [(self.layout, 0), (broken, 1), (invalid, 2)]:
                with self.subTest(expected=expected):
                    target = base / 'layout.json'
                    target.write_text(json.dumps(data), encoding='utf-8')
                    process = subprocess.run(
                        [sys.executable, str(SCRIPT), str(original), str(target)],
                        capture_output=True)
                    self.assertEqual(process.returncode, expected, process.stderr)


if __name__ == '__main__':
    unittest.main()
