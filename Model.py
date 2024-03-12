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
        self.domain = set(
            [
                "a",
                "b",
                "c",
                "j",
                "m",
                "s",
                "x",
                "y",
                "z",
            ]
        )
        self.runners = set(["x", "y", "j"])
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
            "people": self.gen_noun_func({"a", "b", "c", "s", "j", "m"}),
            "person": self.gen_noun_func({"a", "b", "c", "s", "j", "m"}),
            "cat": self.gen_noun_func({"x", "y", "z"}),
            "admired": self.gen_trans_verb_func(self.admired),
            "ran": self.gen_intrans_verb_func(self.runners),
            "a": self.gen_quant_func_num(1),
            "three": self.gen_quant_func_num(3),
        }

    def gen_noun_func(self, noun_set: Set[str]) -> lambda x: bool:
        """
        Generates a function that checks if a given argument is in the noun set.
        Generated function is of form λx.x ∈ noun_set
        """
        return lambda x: x in noun_set

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

    def gen_quant_func_num(self, num: int) -> lambda s1, s2: bool:
        """
        Generates a function that checks if a given pair of arguments is in the verb set.
        Generated function is of form λf.λg.(|CH(f) ∩ CH(g)| > num).
        This is useful for quantifiers like "an", "a", "one", "two", "three", etc.
        """

        def ch(f: callable) -> Set[str]:
            """
            Returns the set of individuals that are in the extension of the noun phrase.
            """
            return {x for x in self.domain if f(x)}

        return lambda s1: lambda s2: len(ch(s1).intersection(ch(s2))) >= num

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
                    # This is quite a hacky way to do this, but it works.
                    # It will try to apply the left child to the right child,
                    # and if that fails, it will try to apply the right child
                    # on the left child.
                    try:
                        return left(right)
                    except Exception as _:
                        try:
                            return right(left)
                        except Exception as e2:
                            raise ValueError(
                                f"Invalid arguments for function {tree_node.label}. Left: {left}, Right: {right}"
                            ) from e2
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


def main():
    """
    Demonstrates the use of the model.
    """
    sentences = [
        "jane ran",  # intransitive, true
        "mike ran",  # intransitive, false
        "albert admired betty",  # transitive, true
        "betty admired albert",  # transitive, false
        "a person ran",  # quantified subject, true
        "three people ran",  # quantified subject, false
    ]
    for s in sentences:
        print(f"{s} -> {evaluate(s)}")


if __name__ == "__main__":
    main()
