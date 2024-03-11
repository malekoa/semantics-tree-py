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
        }

    def gen_trans_verb_func(self, verb_set: Set[Tuple[str, str]]) -> lambda y, x: bool:
        """
        Generates a function that checks if a given pair of arguments is in the verb set.
        Generated function is of form λy.λx.(x, y) ∈ verb_set
        """
        return lambda y: lambda x: (x, y) in verb_set

    def traverse(self, tree: Node):
        """
        Traverses the parse tree and evaluates it using the model.
        """
        if tree.children is not None:  # if 'tree' is not a leaf node
            if isinstance(tree, Node):  # if 'tree' has not been evaluated
                if len(tree.children) == 1:  # if 'tree' has only one child
                    return self.traverse(tree.children[0])
                if len(tree.children) == 2:  # if 'tree' has two children
                    left, right = self.traverse(tree.children[0]), self.traverse(
                        tree.children[1]
                    )
                    # if left is a function and right is a string, apply left to right
                    if inspect.isfunction(left) and isinstance(right, str):
                        return left(right)
                    # if right is a function and left is a string, apply right to left
                    if inspect.isfunction(right) and isinstance(left, str):
                        return right(left)
                    # if left and right are not compatible types, raise an error
                    raise ValueError(f"Invalid arguments for function {tree.label}.")
            elif isinstance(tree, str):  # if 'tree' has been evaluated
                return tree
        else:  # if 'tree' is a leaf node
            return self.g[tree.label]  # return the value of the leaf node
        return None


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
        "albert admired betty",
        "betty admired albert",
    ]
    for s in sentences:
        print(f"{s} -> {evaluate(s)}")
