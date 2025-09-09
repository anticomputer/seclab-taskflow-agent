/**
 * @id mcp-cpp/declaration-location-for-variable
 * @name Function or Variable Definition Location
 * @description Finds the source code location of a variable declaration
 * @tags declaration, location, variable
 * @kind problem
 * @problem.severity recommendation
 */

import cpp
import locations

external string targetDeclaration();

class TargetVariable extends Variable {
  TargetVariable() {
    this.getName() = targetDeclaration()
  }
}

from Variable d, Function f
where
  d instanceof TargetVariable and
  d.getAnAccess().getEnclosingFunction() = f
select "Variable Declaration Location: `{0}` is declared at `{1}` in the function `{2}` at `{3}`", "declaration,location,enclosing_function,enclosing_function_location", targetDeclaration(), normalizeLocation(d.getLocation()), f,functionLocation(f)
