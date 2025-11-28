# SPDX-FileCopyrightText: 2025 GitHub
# SPDX-License-Identifier: MIT

import logging
import platformdirs
import os
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def mcp_data_dir(packagename: str, mcpname: str, env_override: str | None):
    """
    Create a directory for an MCP to store its data.
    env_override is the name of an environment variable that
    can be used to override the default location.
    """
    if env_override:
        p = os.getenv(env_override)
        if p:
            return Path(p)
    # Use [platformdirs](https://pypi.org/project/platformdirs/) to
    # choose an appropriate location.
    d = platformdirs.user_data_dir(appname = "seclab-taskflow-agent",
                                   appauthor = "GitHubSecurityLab",
                                   ensure_exists = True)
    # Each MCP server gets its own sub-directory
    p = Path(d).joinpath(packagename).joinpath(mcpname)
    p.mkdir(parents = True, exist_ok = True)
    return p
