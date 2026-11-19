from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from labs.shared.core import Run
run=Run('ch01','quick','extension-gap')
run.emit('rubric_gap',reason='Extension definition absent from pinned faculty materials')
run.finish('blocked','Faculty activity definition missing')
raise SystemExit(2)
