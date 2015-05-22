calculate_match_score <- function(queries, texts) {
  scores <- list(length=length(queries))
  for (i in 1:length(queries)) {
    query <- queries[i]
    text <- texts[i]
    # Remove leading and trailing whitespaces, then split string by whitespaces.
    query_nodes <- unique(strsplit(gsub("^\\s+|\\s+$", "",
                                        gsub("\\s+", " ", query)), " ")[[1]])
    text_nodes <- unique(strsplit(gsub("^\\s+|\\s+$", "",
                                       gsub("\\s+", " ", text)), " ")[[1]])
    score <- 0
    for(query_node in query_nodes) {
      score <- score + length(grep(query_node, text_nodes))
    }
    the_score <- score / length(query_nodes)
    if(the_score > 1) {the_score <- 1}
    scores[[i]] <- (the_score)
  }
  return(as.numeric(scores))
}

# Testing function calculate_match_score
queries <- c("first query",
             "second query ",
             "third query",
             " this fourth query should",
             "led christma light",
             "soda stream")
texts <- c(
  "first one should  return 0.5",
  "this one should return 0",
  "this third query   should return 1 third",
  "this fourth one should return 0.75",
  "set  10 batteri oper multi led train christma light  clear wire",
  "sodastream home soda maker kit")
scores <- calculate_match_score(queries, texts)
stopifnot(all.equal(scores[[1]], 0.5) &&
          all.equal(scores[[2]], 0) &&
          all.equal(scores[[3]], 1) &&
          all.equal(scores[[4]], 0.75) &&
          all.equal(scores[[5]], 1) &&
          all.equal(scores[[6]], 1))