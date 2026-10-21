import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
for path in (PROJECT.parents[1] / "lib", PROJECT / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
