/**
 * @name Call Graph for a Given Function
 * @description Displays the call graph for a given function name, including the locations of calls and the fully qualified names of the callers.
 * @kind problem
 * @problem.severity recommendation
 * @id mcp-cpp/call-graph-to
 */

import cpp
import locations

external string targetFunction();

/**
 * Specify the function name for which you want to generate the call graph.
 * Replace "targetFunctionName" with the desired function name.
 */
class TargetFunction extends Function {
  TargetFunction() {
    this.getName() = targetFunction()
  }
}

from FunctionCall call, TargetFunction target, Function caller
where
  call.getTarget() = target and
  call.getEnclosingFunction() = caller
select
  "Call to `{0}` from `{1}` at `{2}`", "target, caller, location", target.getQualifiedName(), caller.getQualifiedName(), normalizeLocation(call.getLocation())
