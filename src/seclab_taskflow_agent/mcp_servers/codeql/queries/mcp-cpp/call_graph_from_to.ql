/**
 * @kind problem
 * @id mcp-cpp/definition-location-for
 * @name Call Graph reachability from a function to a function
 * @description Determines whether a source function has a path to a target function in the Call Graph
 * @tags reachable
 * @problem.severity recommendation
 */

// Based on: https://remcovermeulen.com/posts/codeql-path-graphs/
import cpp

external string sourceFunction();
external string targetFunction();

module CallGraph {
    newtype TPathNode =
        TFunction(Function f) or
        TCall(Call c)

    class PathNode extends TPathNode {

        Location getLocation() {
          result = this.asFunction().getLocation() or
          result = this.asCall().getLocation()
        }
      
        Function asFunction() {
            this = TFunction(result)
        }

        Call asCall() {
            this = TCall(result)
        }

        string toString() {
            result = this.asFunction().toString()
            or
            result = this.asCall().toString()
        }

        PathNode getASuccessor() {
            this.asFunction() = result.asCall().getEnclosingFunction()
            or
            this.asCall().getTarget() = result.asFunction()
        }
    }

    query predicate edges(PathNode pred, PathNode succ) {
            pred.getASuccessor() = succ
    }
}

import CallGraph

predicate calls(Function from_, Function to) {
        exists(Call call | call.getEnclosingFunction() = from_ |
            call.getTarget() = to
        )
}

class SourcePathNode extends PathNode {
  SourcePathNode() {
    this.asFunction().getName() = sourceFunction()
  }
}

class TargetPathNode extends PathNode {
  TargetPathNode() {
    this.asFunction().getName() = targetFunction()
  }
}

from SourcePathNode from_, TargetPathNode to
where calls+(from_.asFunction(), to.asFunction())
select "Reachable From `{0}` can be reached from `{1}`", "target, source", targetFunction(), sourceFunction()
