"""Bounded connection retries with a fresh client after failed initialization."""
import time


def connect_fresh(factory, probe, close, timeout, retry_errors):
    deadline = time.monotonic() + timeout
    while True:
        client = factory()
        try:
            result = probe(client)
            return client, result
        except retry_errors:
            close(client)
            if time.monotonic() >= deadline:
                raise
            time.sleep(3)
        except Exception:
            close(client)
            raise
