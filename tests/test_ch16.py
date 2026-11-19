"""Mongo insertion must not leak its generated IDs into Neo4j parameters."""
import importlib.util
import sys
import types
import unittest
from unittest.mock import Mock, patch


class EnrollmentTests(unittest.TestCase):
    def test_graph_receives_only_enrollment_fields_after_mongo_insert(self):
        back = Mock()
        stub = types.ModuleType('labs.shared.polyglot')
        stub.Backends = Mock(return_value=back)
        spec = importlib.util.spec_from_file_location('ch16_under_test', 'labs/ch16/exercise.py')
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'labs.shared.polyglot': stub}):
            spec.loader.exec_module(module)

        def insert(db, name, documents):
            # PyMongo insert_many adds _id to each supplied dictionary in place.
            for document in documents:
                document['_id'] = object()
            return Mock()

        class ReachedGraph(Exception):
            pass

        def cypher(query, **params):
            if query.startswith('MERGE'):
                self.assertEqual(set(params), {'student', 'course', 'instructor'})
                self.assertTrue(all(isinstance(value, str) for value in params.values()))
                raise ReachedGraph()

        back.cypher.side_effect = cypher
        with patch.object(module, 'reset', side_effect=insert):
            with self.assertRaises(ReachedGraph):
                module.main(Mock())
        back.close.assert_called_once()
