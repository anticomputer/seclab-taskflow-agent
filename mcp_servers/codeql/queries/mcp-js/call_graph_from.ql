/**
 * @name Call Graph for a Given Function
 * @description Displays the call graph for a given function name, including the locations of calls and the fully qualified names of the callers.
 * @kind problem
 * @problem.severity recommendation
 * @id mcp-js/call-graph-from
 */

import javascript
import locations

external string sourceFunction();

/**
 * Specify the function name for which you want to generate the call graph.
 * Replace "sourceFunctionName" with the desired function name.
 */
class SourceFunction extends Function {
  SourceFunction() {
    this.getName() = sourceFunction()
  }
}

from CallExpr call, SourceFunction source
where
  call.getEnclosingFunction() = source
select
  "Call from `{0}` to `{1}` at `{2}`", "source, callee, location", source.getName(), call.getCalleeName(), normalizeLocation(call.getLocation())
