from typing import List, Optional, Union
from copy import deepcopy


rewrite_rules = {
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

"""
Each state contains a list of constituents and a list of valid rewrite rules that 
can be applied to them. If the list of valid rewrite rule reversals is of length 
0 and len(constituents) != 1, the state is invalid and can be thrown away.
"""
class SemanticsTree:

    class ConstituentNode:
        def __init__(self, title: str, children: Optional[List] = None) -> None:
            self.title = title
            self.children = children

        def __repr__(self) -> str:
            return f'<ConstituentNode title="{self.title}" children="{self.children}">'

        @classmethod
        def traverse(cls, root) -> None:
            if root.children:
                for child in root.children:
                    cls.traverse(child)
            else:
                print(root.title)


    def __init__(self, sentence: Union[str, List[ConstituentNode]]) -> None:
        if isinstance(sentence, str):
            self.constituents = [self.ConstituentNode(title=i) for i in sentence.split(" ")]
        elif isinstance(sentence, list):
            self.constituents = sentence
        self.valid_rules = self.get_valid_rules()

    def apply_rule(self):
        if self.valid_rules:
            i, j = self.valid_rules.pop()
            rewritten = " ".join(node.title for node in self.constituents[i:j])
            new_constituents = deepcopy(self.constituents)
            new_constituents[i:j] = [self.ConstituentNode(rewrite_rules[rewritten], children=self.constituents[i:j])]
            return SemanticsTree(new_constituents)

    def has_valid_rules(self) -> bool:
        return self.valid_rules != None and len(self.valid_rules) > 0

    def __repr__(self) -> str:
        return " ".join(node.title for node in self.constituents)
    
    """
    Valid rewrite rule reversals can be of length 1 to 3. Therefore, all subsets
    of lengths 1, 2, and 3 should be checked to see if they form a valid rewrite
    rule reversal. The valid rules themselves are a list of tuples containing 
    index ranges in self.constituents that form a valid rule reversal.
    """
    def get_valid_rules(self) -> Optional[List]:
        valid_rules = []
        for i in range(3): # There are rules of length 1, 2, and 3. This gets all of them
            for j in range(i, len(self.constituents) + 1):
                possible_rule = " ".join(node.title for node in self.constituents[j - (i + 1) : j])
                print(f'possible_rule: {possible_rule}')
                if possible_rule in rewrite_rules:
                    valid_rules.append((j - ( i + 1 ), j))
        if len(valid_rules) > 0:
            return valid_rules
        return None


valid_trees = []
Z = [SemanticsTree("Rosa secretly admired the linguist and the psychologist and Jojo criticized Rosa")]

while len(Z) > 0:
    print(Z)
    top = Z[-1]
    if top.has_valid_rules():
        new_state = top.apply_rule()
        if new_state != None:
            Z.append(new_state)
            continue
    else:
        if len(top.constituents) == 1:
            valid_trees.append(top.constituents[0])
            break
        Z.pop()

if len(valid_trees) == 0:
    print('found no valid trees')
else:
    print('\nTree found!')
    root = (valid_trees[0])
    SemanticsTree.ConstituentNode.traverse(root)

