/**
 * @name Call Graph for a Given Function
 * @description Displays the call graph for a given function name, including the locations of calls and the fully qualified names of the callers.
 * @kind problem
 * @problem.severity recommendation
 * @id mcp-javascript/call-graph-to
 */

import javascript
import locations

external string targetFunction();

from CallExpr call
where
  call.getCalleeName() = targetFunction() and
select
  "Call to `{0}` from `{1}` at `{2}`", "target, caller, location", targetFunction(), 
  call.getEnclosingFunction() != null ? call.getEnclosingFunction().getName() : "Top-level", 
  normalizeLocation(call.getLocation())
