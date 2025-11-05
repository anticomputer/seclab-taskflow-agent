/**
 * @id mcp-cpp/list-functions
 * @name List all defined functions
 * @description Lists all defined functions in the codebase by their qualified name
 * @tags function
 */

import cpp
import locations

from Function f
select "Function {0} is defined at {1}", "function,location", f.getQualifiedName(), normalizeLocation(f.getLocation())
