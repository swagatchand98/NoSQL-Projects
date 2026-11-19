import unittest
from unittest.mock import Mock
from labs.ch16.service import CircuitBreaker,CircuitOpen,FraudQueryService

class ServiceTests(unittest.TestCase):
    def test_circuit_opens_and_isolated(self):
        breaker=CircuitBreaker(threshold=2)
        bad=Mock(side_effect=ConnectionError())
        for _ in range(2):
            with self.assertRaises(ConnectionError):breaker.call(bad)
        with self.assertRaises(CircuitOpen):breaker.call(bad)
        self.assertEqual(bad.call_count,2)
        self.assertEqual(CircuitBreaker().call(lambda:42),42)
    def test_merged_investigation(self):
        mongo=Mock();mongo.transactions.find_one.return_value={'_id':'T','user_id':'U'}
        cs=Mock();cs.execute.return_value.one.return_value={'user_id':'U'}
        graph=Mock(return_value=[{'id':'V'}]);service=FraudQueryService(mongo,cs,graph)
        result=service.investigate('T')
        self.assertEqual(result['transaction']['_id'],'T')
        self.assertEqual(result['ring_candidates'],[{'id':'V'}])
        with self.assertRaises(ValueError):service.detect_fraud_rings('U',max_depth=100)
    def test_missing_transaction_does_not_query_others(self):
        mongo=Mock();mongo.transactions.find_one.return_value=None;cs=Mock();graph=Mock()
        self.assertIsNone(FraudQueryService(mongo,cs,graph).investigate('absent'))
        cs.execute.assert_not_called();graph.assert_not_called()

if __name__=='__main__':unittest.main()
