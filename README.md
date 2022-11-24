# semantics-tree

## Main Idea

This project is meant to evaluate the semantic values of sentences by following
the semantics model theory rules outlined in LING 371.

Essentially, a user of this software should provide a set of rewrite rules, a
sentence, and a model that maps each constituent in all generatable syntax trees
to a semantic value.

The software should produce all valid syntax trees by using the rewrite rules.
Then, it should apply the model's rules to each constituent node in the valid
syntax trees it generates to evaluate the semantic values of each sentence.

### Project Requirements

- [x] Generate syntax trees following a set of rewrite rules.
- [x] Allow for user-defined rewrite rules.
- [x] Generate ALL valid syntax trees, not just the first valid one.
- [x] Increase algorithm efficiency.
- [ ] Improve robustness of algorithm.
- [ ] Apply model rules to generated syntax trees.
- [ ] Figure out if there is a way to allow greater freedom for user defined models.

### Current State

- Optimizations have been made to the backtracking algorithm, it is now relatively
efficient.
- All valid trees are now generated.
- User defined rewrite rules are supported.
