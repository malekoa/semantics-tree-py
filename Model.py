"""
Model semantics using semantics tree module.
"""

from typing import Set, Tuple
import inspect
from SemanticsTree import Node, SemanticsTree as Parser


class Model:
    """
    Model class for evaluating sentences.
    """

    def __init__(self):
        self.runners = set(
            [
                "a",
                "b",
            ]
        )
        self.admired = set(
            [
                ("j", "m"),
                ("s", "m"),
                ("a", "b"),
                ("b", "c"),
            ]
        )
        self.g = {
            "albert": "a",
            "betty": "b",
            "carol": "c",
            "steve": "s",
            "jane": "j",
            "mike": "m",
            "admired": self.gen_trans_verb_func(self.admired),
            "ran": self.gen_intrans_verb_func(self.runners),
        }

    def gen_intrans_verb_func(self, verb_set: Set[str]) -> lambda x: bool:
        """
        Generates a function that checks if a given argument is in the verb set.
        Generated function is of form λx.x ∈ verb_set
        """
        return lambda x: x in verb_set

    def gen_trans_verb_func(self, verb_set: Set[Tuple[str, str]]) -> lambda y, x: bool:
        """
        Generates a function that checks if a given pair of arguments is in the verb set.
        Generated function is of form λy.λx.(x, y) ∈ verb_set
        """
        return lambda y: lambda x: (x, y) in verb_set

    def traverse(self, tree_node: Node):
        """
        Traverses the parse tree and evaluates it using the model.
        """
        if tree_node.children is not None:  # if 'tree_node' is not a leaf node
            if isinstance(tree_node, Node):  # if 'tree_node' has not been evaluated
                if len(tree_node.children) == 1:  # if 'tree_node' has only one child
                    return self.traverse(tree_node.children[0])
                if len(tree_node.children) == 2:  # if 'tree_node' has two children
                    left = self.traverse(tree_node.children[0])
                    right = self.traverse(tree_node.children[1])
                    # if left is a function and right is a string, apply left to right
                    if inspect.isfunction(left) and isinstance(right, str):
                        return left(right)
                    # if right is a function and left is a string, apply right to left
                    if inspect.isfunction(right) and isinstance(left, str):
                        return right(left)
                    # it's possible that both left and right are functions.
                    # in that case, we'd have to figure out which function to apply to which
                    # if left and right are not compatible types, raise an error
                    raise ValueError(
                        f"Invalid arguments for function {tree_node.label}."
                    )
            return tree_node  # if the subtree has been evaluated
        # if 'tree_node' is a leaf node
        return self.g[tree_node.label]  # return the value of the leaf node


def evaluate(sentence: str) -> bool:
    """
    Evaluates a sentence using the model.
    """
    p = Parser(sentence)
    m = Model()
    if p.num_trees == 0:
        raise ValueError("No valid trees found.")
    pn_node = p.valid_syntax_trees[0]
    return m.traverse(pn_node)


def print_tree(sentence: str):
    """
    Prints the parse tree of a sentence in LaTeX format.
    """
    p = Parser(sentence)
    if p.num_trees == 0:
        raise ValueError("No valid trees found.")
    pn_node = p.valid_syntax_trees[0]
    print(pn_node.latex_string())


if __name__ == "__main__":
    sentences = [
        "mike ran",  # intransitive, true
        "albert ran",  # intransitive, false
        "albert admired betty",  # transitive, true
        "betty admired albert",  # transitive, false
    ]
    for s in sentences:
        print(f"{s} -> {evaluate(s)}")
