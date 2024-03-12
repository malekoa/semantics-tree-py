from __future__ import annotations
from copy import deepcopy
from typing import Callable, Dict, List, Optional, Tuple

default_rewrite_rules = {
    "NP VP": "S",
    "V_I": "VP",
    "V_T NP": "VP",
    "Q N'": "NP",
    "PN": "NP",
    "Adj N'": "N'",
    "N": "N'",
    "S XP": "S",
    "XP S": "S",
    "subord S": "XP",
    "albert": "PN",
    "betty": "PN",
    "carol": "PN",
    "steve": "PN",
    "oscar": "PN",
    "mike": "PN",
    "jane": "PN",
    "john": "PN",
    "alligator": "N",
    "dog": "N",
    "people": "N",
    "person": "N",
    "boy": "N",
    "cat": "N",
    "anxious": "Adj",
    "big": "Adj",
    "caring": "Adj",
    "ran": "V_I",
    "run": "V_I",
    "swam": "V_I",
    "cried": "V_I",
    "admired": "V_T",
    "kissed": "V_T",
    "insulted": "V_T",
    "scratched": "V_T",
    "if": "subord",
    "and": "coord",
    "or": "coord",
    "every": "Q",
    "all": "Q",
    "some": "Q",
    "no": "Q",
    "most": "Q",
    "an": "Q",
    "a": "Q",
    "one": "Q",
    "two": "Q",
    "three": "Q",
}


def build_coordination_rules(rewrite_rules: Dict[str, str]):
    coordinatables = "S,XP,NP,VP,Adj,N,V_I,V_T,N'".split(",")
    for coordinatable in coordinatables:
        rewrite_rules[f"{coordinatable} coord {coordinatable}"] = coordinatable


class Model:
    def __init__(
        self,
        domain: Optional[List[str]] = None,
        interpretation_function: Optional[Dict[str, Callable]] = None,
    ) -> None:
        self.domain = domain if domain != None else []
        self.interpretation_function = (
            interpretation_function if interpretation_function != None else dict()
        )

    def add_domain_item(self, item: str):
        self.domain.append(item)

    def add_interpretation_mapping(self, value: str, mapping: Callable):
        self.interpretation_function[value] = mapping


class Node:
    def __init__(self, label: str, children: Optional[List[Node]] = None) -> None:
        self.label = label
        self.children = children
        self.data = None  # hold meaning values

    def latex_string(self) -> str:
        if self.children:
            return f'[ {self.label} {" ".join([child.latex_string() for child in self.children])} ]'
        else:
            return f"[ {self.label} ]"

    def inorder_string(self) -> str:
        if self.children:
            return f'{self.label},{",".join(child.inorder_string() for child in self.children)}'
        else:
            return f"{self.label}"

    def struct_string(self) -> str:
        if self.children:
            return f'[{"".join(child.struct_string() for child in self.children)}]'
        else:
            return "[]"

    def __repr__(self) -> str:
        return f"<Node label={{{self.label}}} children={{{self.children}}}>"

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Node):
            if self.label != __o.label:
                return False  # unequal labels

            # one has children but other doesn't
            if (self.children and not __o.children) or (
                not self.children and __o.children
            ):
                return False

            # both have children...
            elif self.children and __o.children:
                if len(self.children) != len(__o.children):
                    return False  # unequal number of children
                else:  # equal number of children
                    # returns true if all children are equal, false otherwise
                    return all(
                        [
                            self.children[i] == __o.children[i]
                            for i in range(len(self.children))
                        ]
                    )
            # both have no children and same label, must be true
            return True
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.struct_string())


class State:  # used for backtracking algorithm for finding valid syntax trees
    def __init__(self, constituents: List[Node], rewrite_rules: Dict[str, str]) -> None:
        self.constituents = constituents
        self.valid_rules = self.get_valid_rules(rewrite_rules)

    def get_valid_rules(self, rewrite_rules: Dict[str, str]) -> List[Tuple[int, int]]:
        valid_rules = []
        for i in range(
            3 if len(self.constituents) >= 3 else len(self.constituents)
        ):  # There are rules of length 1, 2, and 3. This gets all of them
            for j in range(i, len(self.constituents) + 1):
                possible_rule = " ".join(
                    node.label for node in self.constituents[j - (i + 1) : j]
                )
                if possible_rule in rewrite_rules:
                    valid_rules.append((j - (i + 1), j))
        return valid_rules

    def apply_rule(self, rewrite_rules: Dict[str, str]):
        i, j = (
            self.valid_rules.pop()
        )  # valid_rules is a list of tuples that contain the start and end index of a valid transformation
        rewritten = " ".join(node.label for node in self.constituents[i:j])
        new_constituents = deepcopy(self.constituents)
        new_constituents[i:j] = [
            Node(rewrite_rules[rewritten], children=self.constituents[i:j])
        ]
        return State(new_constituents, rewrite_rules=rewrite_rules)

    def has_valid_rules(self) -> bool:
        return len(self.valid_rules) > 0

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, State) and len(self.constituents) == len(__o.constituents):
            return all(
                [
                    self.constituents[i] == __o.constituents[i]
                    for i in range(len(self.constituents))
                ]
            )
        return False

    def __hash__(self) -> int:
        return hash(
            ",".join(
                [constituent.inorder_string() for constituent in self.constituents]
            )
        )

    def __repr__(self) -> str:
        return f'<State constituents={{{",".join([constituent.label for constituent in self.constituents])}}}>'


class SemanticsTree:
    def __init__(self, sentence: str) -> None:
        build_coordination_rules(default_rewrite_rules)
        self.valid_syntax_trees = self.generate_all_valid_syntax_trees(
            sentence, pre_percolate=True
        )
        self.num_trees = len(self.valid_syntax_trees)

    # performs all possible percolations on tokenized sentence
    def pre_percolate(
        self, noded_sentence: List[Node], rewrite_rules: Dict[str, str]
    ) -> None:
        for i in range(len(noded_sentence)):
            while noded_sentence[i].label in rewrite_rules:
                noded_sentence[i] = Node(
                    label=rewrite_rules[noded_sentence[i].label],
                    children=[noded_sentence[i]],
                )

    def generate_all_valid_syntax_trees(
        self, sentence: str, pre_percolate: bool = True
    ) -> List[Node]:
        tokenized_sentence = sentence.split(" ")  # Tokenize the sentence
        noded_sentence = [
            Node(token) for token in tokenized_sentence
        ]  # convert list of tokens to list of nodes

        # perform pre-percolation
        if pre_percolate:
            self.pre_percolate(noded_sentence, rewrite_rules=default_rewrite_rules)

        # create initial state
        state_0 = State(noded_sentence, rewrite_rules=default_rewrite_rules)

        found_trees = set()
        dead_ends = set()
        valid_trees = []
        Z = [state_0]

        # while there is an unexhausted state in the stack
        while len(Z) > 0:
            top = Z[-1]  # get the top state from the stack
            if (
                top not in dead_ends and top.has_valid_rules()
            ):  # if this structure hasn't been seen yet and it has a valid rule (S has no valid rules)
                new_state = top.apply_rule(
                    rewrite_rules=default_rewrite_rules
                )  # apply one of the valid rules
                Z.append(
                    new_state
                )  # append the newly created state to the top of the stack
                continue  # continue from the newly created state
            elif (
                len(top.constituents) == 1
            ):  # else if the top only has one constituent (it is the root of the tree)
                contender = top.constituents[0]
                if (
                    contender not in found_trees
                ):  # add it to the list if it hasn't been found yet
                    valid_trees.append(contender)
                    found_trees.add(contender)
            else:
                # else add it to the list of dead ends that don't need to be checked anymore
                dead_ends.add(top)

            Z.pop()

        return valid_trees


if __name__ == "__main__":
    # build_coordination_rules(
    #     default_rewrite_rules
    # )  # builds 'X coord X' rules where X is a coordinatable node
    SENTENCE = "albert and betty or john and oscar admired an alligator"
    print(f"sentence: {SENTENCE}")
    sem = SemanticsTree(SENTENCE)
    print(f"Found {sem.num_trees} trees:\n")
    for tree in sem.valid_syntax_trees:
        print(tree.latex_string())
        print()
    print(f"Found {sem.num_trees} trees:\n")
