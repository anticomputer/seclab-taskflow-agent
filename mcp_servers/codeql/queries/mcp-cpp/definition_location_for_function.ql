/**
 * @id mcp-cpp/definition-location-for-function
 * @name Function Definition Location
 * @description Finds the source code location of a function definition.
 * @tags definition, location, function
 * @kind problem
 * @problem.severity recommendation
 */

import cpp
import locations

external string targetDefinition();

class TargetFunction extends Function {
  TargetFunction() {
    this.getName() = targetDefinition()
  }
}

from TargetFunction d
// XXX: because CodeQL doesn't include closing brace as its last statement we guess a +1 line offset for it
// 0 in our region extractor returns max value possible
select "Function Definition Location: `{0}` is defined at `{1}`", "definition,location", targetDefinition(), functionLocation(d)