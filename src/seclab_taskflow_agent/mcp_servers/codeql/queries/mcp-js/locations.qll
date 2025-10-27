import javascript

string functionLocation(Function d) {
    result =  "file://" + "/" + d.getFile().getRelativePath() + ":" + d.getBody().getLocation().getStartLine() + ":" + "0" + ":" + (d.getBody().getLastToken().getLocation().getEndLine() + 1) + ":" + "0"
}

string normalizeLocation(Location l) {
    result = "file://" + "/" + l.getFile().getRelativePath() + ":" + l.getStartLine().toString() + ":" + l.getStartColumn().toString() + ":"
    + ":" + l.getEndLine().toString() + ":" + l.getEndColumn().toString()
}
