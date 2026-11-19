"""Runnable activity entrypoint; shared chapter setup keeps seeds repeatable."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from labs.run import main
if __name__ == '__main__':
    sys.argv[1:1] = ['ch16', '--activity', '1']
    raise SystemExit(main())
