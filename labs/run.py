import argparse
import importlib
import sys
import traceback
from labs.shared.core import Run, Blocked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('chapter', choices=[f'ch{i:02}' for i in range(1, 19)])
    parser.add_argument('--mode', choices=['quick', 'full'], default='quick')
    parser.add_argument('--activity', default='all')
    args = parser.parse_args()
    run = Run(args.chapter, args.mode, args.activity)
    try:
        module = importlib.import_module(f'labs.{args.chapter}.exercise')
        module.main(run)
        run.finish('partial' if any(e['name'] in ('external_check_blocked','rubric_gap') for e in run.events) else 'passed')
    except (Blocked, ModuleNotFoundError) as exc:
        run.emit('blocked', reason=str(exc))
        run.finish('blocked', str(exc))
        return 2
    except Exception as exc:
        # Do not serialize connection strings or exception messages containing credentials.
        run.emit('failed', error_type=type(exc).__name__,
                 frames=[dict(file=frame.filename, line=frame.lineno, function=frame.name)
                         for frame in traceback.extract_tb(exc.__traceback__)])
        run.finish('failed', type(exc).__name__)
        return 1
    finally:
        print(f'Evidence: {run.directory}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
