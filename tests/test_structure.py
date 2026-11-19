import ast
import json
from pathlib import Path
import unittest
from labs.shared.core import Run,seed_data
from labs.ch18.ingest import normalize

class StructureTests(unittest.TestCase):
    def test_all_chapters_have_entrypoint(self):
        for i in range(1,19):
            module=Path(f'labs/ch{i:02}/exercise.py')
            tree=ast.parse(module.read_text())
            self.assertTrue(any(isinstance(n,ast.FunctionDef) and n.name=='main' for n in tree.body))
    def test_seed_preservation(self):
        self.assertEqual(len(seed_data('books')),5)
        self.assertEqual(len(seed_data('courses')),3)
        self.assertEqual(len(seed_data('orders')),10)
    def test_known_book_price_baseline(self):
        old=[b for b in seed_data('books') if b['year']<2010]
        self.assertEqual([(b['title'],b['price']) for b in old],[('Clean Code',39.99)])
    def test_sources_and_classroom_labels(self):
        records=json.loads(Path('data/threats.json').read_text())
        self.assertEqual(len({r['_id'] for r in records}),12)
        self.assertEqual({r['status'] for r in records},{'Active','Anticipated','Evolving','Resolved'})
        for r in records:self.assertTrue(r['classroom_observation']['fictional'])
    def test_source_is_provider_not_one_partition_per_document(self):
        record=normalize('CVE-test','https://nvd.nist.gov/vuln/detail/CVE-test','2024-01-01','Summary')
        self.assertEqual(record['source'],'nvd.nist.gov')
        self.assertFalse(record['synthetic'])

if __name__=='__main__':unittest.main()
