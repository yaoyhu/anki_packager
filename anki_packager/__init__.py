__version__ = "0.9.5"

from .utils import initialize_config

try:
    initialize_config()
except Exception as e:
    import sys

    print(f"Warning: Unable to initialize configuration: {e}", file=sys.stderr)
