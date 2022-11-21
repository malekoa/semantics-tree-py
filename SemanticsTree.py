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


if __name__ == '__main__':
    sentence = "Rosa secretly admired the linguist and the psychologist and Jojo criticized Rosa"
    tokenized_sentence = sentence.split(' ')
    noded_sentence = [Node(token) for token in tokenized_sentence]
    state_0 = State(noded_sentence, rewrite_rules=default_rewrite_rules)

    valid_trees = []
    Z = [state_0]
    
    while len(Z) > 0:
        top = Z[-1]
        if top.has_valid_rules():
            new_state = top.apply_rule(rewrite_rules=default_rewrite_rules)
            Z.append(new_state)
            continue
        elif len(top.constituents) == 1:
            valid_trees.append(top.constituents[0])
            break
        Z.pop()

    if len(valid_trees) == 1:
        print('Tree found!')
        print(valid_trees[0].latex_str())

