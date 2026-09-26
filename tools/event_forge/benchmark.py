"""CLI for the clean-room Event Forge benchmark."""

import json
from .engine import benchmark


if __name__ == "__main__":
    print(json.dumps(benchmark(), sort_keys=True))
