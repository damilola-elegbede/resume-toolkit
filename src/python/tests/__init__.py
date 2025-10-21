"""Test suite for Python modules."""

import sys
from pathlib import Path

# Add src/python to path for imports
src_python = Path(__file__).parent.parent
if str(src_python) not in sys.path:
    sys.path.insert(0, str(src_python))
