"""
Logger module.
Duplicates all terminal output to a timestamped log file in the logs/ folder.
"""

import os
import re
import sys
from datetime import datetime


class TeeOutput:
    """Duplicates output to both terminal and a log file."""

    def __init__(self, log_path: str):
        self.terminal = sys.__stdout__
        self.log_file = open(log_path, "w", encoding="utf-8")

    def write(self, message: str):
        self.terminal.write(message)
        clean = re.sub(r'\x1b\[[0-9;]*m', '', message)
        self.log_file.write(clean)
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        self.log_file.close()


def setup_logging() -> str:
    """Setup dual output to terminal and log file. Returns log file path."""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"unlock_{timestamp}.log")

    tee = TeeOutput(log_path)
    sys.stdout = tee
    sys.stderr = tee
    return log_path
