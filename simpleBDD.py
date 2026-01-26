import re

class simpleBDD:
    def __init__(self, formula: str):
        self.formula = formula
        # 1.split formula into words
        self.tokens = self._tokenize(formula)
        #select only the variables, remove duplicates and sort them
        self.variables = sorted(list(set(t for t in self.tokens if t.isalnum() and t not in {'and', 'or', 'not','xor', 'True', 'False'})))
        
        #Setup Unique Table {(var_index, low_id, high_id): node_id}
        self.unique_table = {}
        self.nodes = {} # {node_id: (var_index, low_id, high_id)}-for reverse lookup
        self.next_id = 2
        
        # 3. Define Terminal Nodes
        # ID 0 = False, ID 1 = True
        self.FALSE = 0
        self.TRUE = 1
        
        # 4. Build the BDD
        self.root = self._build(self.tokens, 0)

    def _tokenize(self, formula):
        f = formula.replace('(', ' ( ').replace(')', ' ) ')
        f = f.replace('xor', ' ^ ') 
        return f.split()

    def _simplify_and_eval(self, tokens, var, val):
        #replace the variable with a value(true/false)
        new_tokens = [str(val) if t == var else t for t in tokens]
        
        #convert operators to python equivalents(and join them)
        expr = " ".join(new_tokens).replace('and', '&').replace('or', '|').replace('not', '~').replace('xor', '^')
        
        try:
            #evaluate to check if there are no variables left
            result = eval(expr)
            return result
        except NameError:
            #else, return the modified tokens
            return new_tokens

    def _get_node(self, var_idx, low, high):
        """The 'Reduced' part: Returns existing node or creates a new one."""
        #if both branches are identical, reducing the BDD on this node
        if low == high:
            return low
        
        #use an existing subtree if exists
        key = (var_idx, low, high)
        if key in self.unique_table:
            return self.unique_table[key]
        
        # Otherwise, create new
        node_id = self.next_id
        self.unique_table[key] = node_id
        self.nodes[node_id] = key
        self.next_id += 1
        return node_id

    def _build(self, current_tokens, var_idx):
        """Recursive Shannon Expansion build."""
        #if the formula is a constant we finished
        if current_tokens == True or current_tokens == [ 'True' ]: return self.TRUE
        if current_tokens == False or current_tokens == [ 'False' ]: return self.FALSE
        
        #if there are no more variables, evaluate the expression
        if var_idx >= len(self.variables):
            res = eval(" ".join(current_tokens).replace('and', '&').replace('xor', '^').replace('or', '|').replace('not', '~'))
            return self.TRUE if res else self.FALSE

        var = self.variables[var_idx]
        
        # skip the variable if not in the formula
        if var not in current_tokens:
            return self._build(current_tokens, var_idx + 1)

        # f = (var & f_high) | (!var & f_low)
        low_tokens = self._simplify_and_eval(current_tokens, var, False)
        high_tokens = self._simplify_and_eval(current_tokens, var, True)
        
        #recursively build low and high branches
        low_branch = self._build(low_tokens, var_idx + 1)
        high_branch = self._build(high_tokens, var_idx + 1)
        
        return self._get_node(var_idx, low_branch, high_branch)
# my example
bdd = simpleBDD("(x and not y) and (z or x)")
print(f"Variables: {bdd.variables}")
print(f"Root Node ID: {bdd.root}")
print(f"Nodes Created (var_idx, low, high): {bdd.nodes}")

# execise examples:
bdd1a = simpleBDD("(a and not c) or (b xor d)")
print(f"1a Variables: {bdd1a.variables}")
print(f"1a Root Node ID: {bdd1a.root}")
print(f"1a Nodes Created (var_idx, low, high): {bdd1a.nodes}")
bdd1b = simpleBDD("(x1 and x2 and x3) or (x1 and x2 and x4) or (x1 and x2 and x5) or (x1 and x3 and x4) or (x1 and x3 and x5) or (x1 and x4 and x5) or (x2 and x3 and x4) or (x2 and x3 and x5) or (x2 and x4 and x5) or (x3 and x4 and x5)")
print(f"1b Variables: {bdd1b.variables}")
print(f"1b Root Node ID: {bdd1b.root}")
print(f"1b Nodes Created (var_idx, low, high): {bdd1b.nodes}")
bdd1c = simpleBDD("(x3 and not y3) or (not (x3 xor y3) and (x2 and not y2)) or (not (x3 xor y3) and not (x2 xor y2) and (x1 and not y1))")
print(f"1c Variables: {bdd1c.variables}")
print(f"1c Root Node ID: {bdd1c.root}")
print(f"1c Nodes Created (var_idx, low, high): {bdd1c.nodes}")
""" 
Variables: ['x', 'y', 'z']
Root Node ID: 3
Nodes Created (var_idx, low, high): {2: (1, 1, 0), 3: (0, 0, 2)}
1a Variables: ['a', 'b', 'c', 'd']
1a Root Node ID: 8
1a Nodes Created (var_idx, low, high): {2: (3, 0, 1), 3: (3, 1, 0), 4: (1, 2, 3), 5: (2, 1, 2), 6: (2, 1, 3), 7: (1, 5, 6), 8: (0, 4, 7)}
1b Variables: ['x1', 'x2', 'x3', 'x4', 'x5']
1b Root Node ID: 10
1b Nodes Created (var_idx, low, high): {2: (4, 0, 1), 3: (3, 0, 2), 4: (2, 0, 3), 5: (3, 2, 1), 6: (2, 3, 5), 7: (1, 4, 6), 8: (2, 5, 1), 9: (1, 6, 8), 10: 
(0, 7, 9)}
1c Variables: ['x1', 'x2', 'x3', 'y1', 'y2', 'y3']
1c Root Node ID: 15
1c Nodes Created (var_idx, low, high): {2: (5, 1, 0), 3: (2, 0, 2), 4: (4, 2, 0), 5: (4, 1, 2), 6: (2, 4, 5), 7: (1, 3, 6), 8: (3, 4, 0), 9: (3, 5, 2), 10: 
(2, 8, 9), 11: (3, 2, 4), 12: (3, 1, 5), 13: (2, 11, 12), 14: (1, 10, 13), 15: (0, 7, 14)}
"""
