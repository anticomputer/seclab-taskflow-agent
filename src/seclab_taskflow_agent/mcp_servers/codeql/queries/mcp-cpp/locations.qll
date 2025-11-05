import cpp

// file:// uris are always absolute syntax paths, even for relative locations

string functionLocation(Function d) {
    result =  "file://" + "/" + d.getFile().getRelativePath() + ":" + d.getDefinitionLocation().getStartLine() + ":" + "0" + ":" + (d.getBlock().getLastStmt().getLocation().getEndLine() + 1) + ":" + "0"
}

string normalizeLocation(Location l) {
    result = "file://" + "/" + l.getFile().getRelativePath() + ":" + l.getStartLine().toString() + ":" + l.getStartColumn().toString() + ":"
    + ":" + l.getEndLine().toString() + ":" + l.getEndColumn().toString()
}
