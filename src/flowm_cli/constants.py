"""Static constants for the Flow Maestro CLI."""
from __future__ import annotations

import os

APP_NAME = "flowm"
OWNER = os.getenv("FLOWM_REPO_OWNER", "ethras")
REPO = os.getenv("FLOWM_REPO_NAME", "flow-maestro")

__all__ = ["APP_NAME", "OWNER", "REPO"]
