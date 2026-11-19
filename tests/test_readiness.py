import unittest
from unittest.mock import Mock, patch
from labs.shared.readiness import connect_fresh


class ReadinessTests(unittest.TestCase):
    @patch('labs.shared.readiness.time.sleep')
    def test_failed_client_is_closed_and_replaced(self, sleep):
        first, second = object(), object()
        factory = Mock(side_effect=[first, second])
        probe = Mock(side_effect=[ConnectionError(), 'session'])
        close = Mock()
        self.assertEqual(connect_fresh(factory, probe, close, 150, (ConnectionError,)),
                         (second, 'session'))
        close.assert_called_once_with(first)

    def test_configuration_error_is_not_retried(self):
        client = object()
        factory, close = Mock(return_value=client), Mock()
        with self.assertRaises(ValueError):
            connect_fresh(factory, Mock(side_effect=ValueError()), close, 150,
                          (ConnectionError,))
        factory.assert_called_once()
        close.assert_called_once_with(client)

    @patch('labs.shared.readiness.time.monotonic', side_effect=[0, 151])
    def test_timeout_closes_failed_client(self, clock):
        client, close = object(), Mock()
        with self.assertRaises(ConnectionError):
            connect_fresh(lambda: client, Mock(side_effect=ConnectionError()), close,
                          150, (ConnectionError,))
        close.assert_called_once_with(client)
