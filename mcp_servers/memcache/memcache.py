import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/mcp_memcache.log',
    filemode='a'
)
from mcp.server.fastmcp import FastMCP
import json
from pathlib import Path
import os
from typing import Any
from memcache_backend.dictionary_file import MemcacheDictionaryFileBackend
from memcache_backend.sqlite import SqliteBackend

mcp = FastMCP("Memcache")

backends = {
    'dictionary_file': MemcacheDictionaryFileBackend,
    'sqlite': SqliteBackend,
}

# if MEMCACHE_STATE_DIR contains an absolute path we WANT the user to be able
# to override the relative path in that case this path join will return
# /MEMCACHE_STATE_DIR/memory.json
MEMORY = Path(__file__).parent.resolve() / Path(os.getenv('MEMCACHE_STATE_DIR', default='./'))
BACKEND = os.getenv('MEMCACHE_BACKEND', default='sqlite')

backend = backends.get(BACKEND)(str(MEMORY))

@mcp.tool()
def memcache_set_state(key: str, value: Any) -> str:
    """Set or override a value for a key into the memory cache. This acts as your memory."""
    return backend.set_state(key, value)

@mcp.tool()
def memcache_get_state(key: str) -> str:
    """Get a value for a key from the memory cache. Returned values are JSON serialized object strings."""
    return json.dumps(backend.get_state(key))


@mcp.tool()
def memcache_list_keys() -> str:
    """List all available keys in your memory cache."""
    return backend.list_keys()

@mcp.tool()
def memcache_get_all_entries() -> str:
    """Get all entries in your memory cache. Returned values are JSON serialized object strings."""
    return json.dumps(backend.get_all_entries())

@mcp.tool()
def memcache_add_state(key: str, value: Any) -> str:
    """Add to the existing value for an existing key in your memory cache. Supports lists and strings."""
    return backend.add_state(key, value)

@mcp.tool()
def memcache_delete_state(key: str) -> str:
    """Delete a key from the memory cache."""
    return backend.delete_state(key)

@mcp.tool()
def memcache_clear_cache():
    """Clear the memory cache, invalidating all stored key value pairs."""
    return backend.clear_cache()

if __name__ == "__main__":
    mcp.run()
