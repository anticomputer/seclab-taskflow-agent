/**
 * @id mcp-cpp/stmt-location
 * @name Location of a statment
 * @description Finds the source code location of a statement.
 * @tags declaration, location, statement
 * @kind problem
 * @problem.severity recommendation
 */

import cpp
import locations

external string targetStmt();

class TargetStmt extends Stmt {
  TargetStmt() {
    this.toString().matches(targetStmt())
  }
}

from TargetStmt d, Function f
where
  d instanceof TargetStmt and
  f = d.getEnclosingFunction()
  select "Statement Location: `{0}` is at `{1}` in the function `{2}` at `{3}`", "statement,location,enclosing_function,enclosing_function_location", targetStmt(), normalizeLocation(d.getLocation()), f,functionLocation(f)
