# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

from pathlib import Path


TESTS_DIR = Path(__file__).parent
DATA_DIR = TESTS_DIR / "data"
ROOT_DIR = TESTS_DIR.parent
PRIVATE_KEY = DATA_DIR / "private-key"
TESTING_DB = f"sqlite:////{ROOT_DIR}/access_tokens.db"
