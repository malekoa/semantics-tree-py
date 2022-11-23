from __future__ import annotations
from copy import deepcopy
from typing import Dict, List, Optional, Tuple

default_rewrite_rules = {
    'S coord S': 'S',
    'NP VP': 'S',
    'NP coord NP': 'NP',
    'PN': 'NP',
    'Det N': 'NP',
    'VP Adv': 'VP',
    'Adv VP': 'VP',
    'VP coord VP': 'VP',
    'V_T NP': 'VP',
    'V_I': 'VP',
    'supported': 'V_T',
    'criticized': 'V_T',
    'admired': 'V_T',
    'yawned': 'V_I',
    'slept': 'V_I',
    'Jojo': 'PN',
    'Rosa': 'PN',
    'and': 'coord',
    'or': 'coord',
    'the': 'Det',
    'a': 'Det',
    'linguist': 'N',
    'psychologist': 'N',
    'loudly': 'Adv',
    'enthusiastically': 'Adv',
    'secretly': 'Adv',
}

class Node:
    def __init__(self, label: str, children: Optional[List[Node]] = None) -> None:
        self.label = label
        self.children = children
        self.data = None
    
    def latex_str(self) -> str:
        if self.children:
            return f'[ {self.label} {" ".join([child.latex_str() for child in self.children])} ]'
        else:
            return f'[ {self.label} ]'

    def __repr__(self) -> str:
        return f'<Node label={{{self.label}}} children={{{self.children}}}>'

    # TODO: define an __eq__ and __hash__ function so you can use sets directly in the backtracking part <--

class State: # used for backtracking algorithm for finding valid syntax trees
    def __init__(self, constituents: List[Node], rewrite_rules: Dict[str, str]) -> None:
        self.constituents = constituents
        self.valid_rules = self.get_valid_rules(rewrite_rules)
    
    def get_valid_rules(self, rewrite_rules: Dict[str, str]) -> List[Tuple[int, int]]:
        valid_rules = []
        for i in range(3 if len(self.constituents) >= 3 else len(self.constituents)): # There are rules of length 1, 2, and 3. This gets all of them
            for j in range(i, len(self.constituents) + 1):
                possible_rule = " ".join(node.label for node in self.constituents[j - (i + 1) : j])
                if possible_rule in rewrite_rules:
                    valid_rules.append((j - ( i + 1 ), j))
        return valid_rules

    def apply_rule(self, rewrite_rules: Dict[str, str]):
        i, j = self.valid_rules.pop()
        rewritten = " ".join(node.label for node in self.constituents[i:j])
        new_constituents = deepcopy(self.constituents)
        new_constituents[i:j] = [Node(rewrite_rules[rewritten], children=self.constituents[i:j])]
        return State(new_constituents, rewrite_rules=rewrite_rules)
    
    def has_valid_rules(self) -> bool:
        return len(self.valid_rules) > 0

    def __repr__(self) -> str:
        return f'<State constituents={{{",".join([constituent.label for constituent in self.constituents])}}}>'

class SemanticsTree:
    def __init__(self, sentence: str) -> None:
        self.valid_syntax_trees = self.generate_all_valid_syntax_trees(sentence, pre_percolate=True)

    def pre_percolate(self, noded_sentence: List[Node], rewrite_rules: Dict[str, str]) -> None:
        for i in range(len(noded_sentence)):
            while noded_sentence[i].label in rewrite_rules:
                noded_sentence[i] = Node(label=rewrite_rules[noded_sentence[i].label], children=[noded_sentence[i]])

    def generate_all_valid_syntax_trees(self, sentence: str, pre_percolate: bool = False) -> List[Node]:
        tokenized_sentence = sentence.split(' ')
        noded_sentence = [Node(token) for token in tokenized_sentence]

        if pre_percolate:
            self.pre_percolate(noded_sentence, rewrite_rules=default_rewrite_rules)

        state_0 = State(noded_sentence, rewrite_rules=default_rewrite_rules)

        found_trees = set()
        dead_ends = set()
        valid_trees = []
        Z = [state_0]
        
        while len(Z) > 0:
            top = Z[-1]
            dead_end_test = ''.join([node.latex_str() for node in top.constituents])
            if dead_end_test not in dead_ends and top.has_valid_rules():
                new_state = top.apply_rule(rewrite_rules=default_rewrite_rules)
                Z.append(new_state)
                continue
            elif len(top.constituents) == 1:
                contender = top.constituents[0]
                latex_str = contender.latex_str()
                if latex_str not in found_trees:
                    valid_trees.append(contender)
                    found_trees.add(latex_str)
            elif len(top.constituents) > 1:
                dead_ends.add(dead_end_test)

            Z.pop()

        return valid_trees

if __name__ == '__main__':
    sentence = "Jojo and the psychologist or the linguist and the psychologist or Rosa and the linguist supported Rosa enthusiastically or Rosa yawned loudly"
    sem = SemanticsTree(sentence)
    print('\nTrees found:')
    for tree in sem.valid_syntax_trees:
        print(tree.latex_str())
