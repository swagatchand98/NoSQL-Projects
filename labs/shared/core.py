"""Small shared helpers. Every run records observations, never expected results as measurements."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import random
import time

ROOT = Path(__file__).resolve().parents[2]

class Blocked(RuntimeError):
    pass

class Run:
    def __init__(self, chapter, mode, activity='all'):
        self.chapter, self.mode, self.activity = chapter, mode, activity
        self.events = []
        self.directory = ROOT / 'results' / chapter / dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        self.directory.mkdir(parents=True, exist_ok=True)
        self.started = time.perf_counter()
        self.random = random.Random(42)

    def emit(self, name, **values):
        event = dict(name=name, mode=self.mode, **values)
        self.events.append(event)
        print(json.dumps(event, default=str), flush=True)

    def wants(self, *activities):
        return self.activity == "all" or self.activity in {str(a) for a in activities}

    def count(self, full, quick=1000):
        return full if self.mode == 'full' else min(full, quick)

    def save(self, name, value):
        (self.directory / name).write_text(json.dumps(value, default=str, indent=2))

    def finish(self, status, error=None):
        self.save('result.json', dict(chapter=self.chapter, activity=self.activity, mode=self.mode,
                  status=status, error=error, elapsed_seconds=time.perf_counter()-self.started,
                  events=self.events))


def connect(uri=None):
    from pymongo import MongoClient
    client = MongoClient(uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
                         serverSelectionTimeoutMS=5000, connectTimeoutMS=5000, socketTimeoutMS=15000)
    client.admin.command('ping')
    return client


def database(run):
    client = connect()
    run.emit('server', version=client.server_info()['version'])
    return client[f'college_{run.chapter}']


def reset(db, name, documents=(), validator=None):
    if not db.name.startswith('college_'):
        raise ValueError('Reset limited to college_ lab databases')
    db.drop_collection(name)
    col = db.create_collection(name, **({'validator': validator} if validator else {}))
    docs = list(documents)
    if docs:
        col.insert_many(docs)
    return col


def seed_data(name):
    return json.loads((ROOT / 'labs' / 'shared' / 'seeds' / (name + '.json')).read_text())


def timed(call):
    start = time.perf_counter()
    value = call()
    return value, time.perf_counter() - start


def explain(col, query, projection=None):
    return col.database.command('explain', {'find': col.name, 'filter': query, 'projection': projection or {}}, verbosity='executionStats')


def stages(value):
    found = []
    if isinstance(value, dict):
        if 'stage' in value:
            found.append(value['stage'])
        for item in value.values():
            found.extend(stages(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(stages(item))
    return sorted(set(found))


def plot(run, name, x, y, xlabel, ylabel):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o')
    ax.set(xlabel=xlabel, ylabel=ylabel, title=f'{run.chapter} — {run.mode}')
    fig.tight_layout()
    fig.savefig(run.directory / name)
    plt.close(fig)
