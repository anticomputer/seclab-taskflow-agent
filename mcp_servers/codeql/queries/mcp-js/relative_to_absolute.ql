/**
 * @name relative_to_absolute
 * @description Get root directory of source archive
 * @kind problem
 * @problem.severity recommendation
 * @id mcp-javascript/relative_to_absolute
 */

import javascript

external string relPath();

from File file
where file.getRelativePath() = relPath()
select "absolute path {0}", "absolute_path", file.getAbsolutePath().toString()