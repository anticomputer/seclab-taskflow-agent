/**
 * @name absolute_to_relative
 * @description Get root directory of source archive
 * @kind problem
 * @problem.severity recommendation
 * @id mcp-javascript/absolute_to_relative
 */

import javascript

external string absPath();

from File file
where file.getAbsolutePath() = absPath()
select "Relative path {0}", "relative_path", file.getRelativePath().toString()