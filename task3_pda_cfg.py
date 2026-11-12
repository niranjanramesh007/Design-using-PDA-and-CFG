import os
from graphviz import Digraph

# =====================================================================
# 1. PUSHDOWN AUTOMATA SIMULATORS
# =====================================================================

class BalancedBracketsPDA:
    def __init__(self):
        self.stack = []
        self.state = 'q0'
    def reset(self):
        self.stack = ['Z']
        self.state = 'q0'
    def step_by_step_trace(self, input_str):
        self.reset()
        steps = [f"Initial State: {self.state}, Stack: {list(self.stack)}"]
        self.state = 'q1'
        steps.append(f"Transition (epsilon-move): State -> {self.state}, Stack: {list(self.stack)}")
        for i, char in enumerate(input_str):
            if char not in ['(', ')']:
                return False, steps + [f"Rejected: Invalid character '{char}'"]
            top = self.stack[-1]
            if char == '(':
                self.stack.append('(')
                steps.append(f"Read '(': Push. Stack: {list(self.stack)}")
            elif char == ')':
                if top == '(':
                    self.stack.pop()
                    steps.append(f"Read ')': Pop. Stack: {list(self.stack)}")
                else:
                    return False, steps + ["Rejected: Mismatched closing parenthesis"]
        if self.stack == ['Z']:
            self.state = 'q2'
            self.stack.pop()
            steps.append("Accepted: Stack is empty (Z popped)")
            return True, steps
        return False, steps + ["Rejected: Stack not empty at EOF"]

class ArithmeticExpressionPDA:
    def __init__(self):
        self.stack = []
        self.parsing_table = {
            ('E', 'id'): ['T', "E'"], ('E', '('): ['T', "E'"],
            ("E'", '+'): ['+', 'T', "E'"], ("E'", ')'): [], ("E'", '$'): [],
            ('T', 'id'): ['F', "T'"], ('T', '('): ['F', "T'"],
            ("T'", '+'): [], ("T'", '*'): ['*', 'F', "T'"], ("T'", ')'): [], ("T'", '$'): [],
            ('F', 'id'): ['id'], ('F', '('): ['(', 'E', ')']
        }
    def tokenize(self, s):
        tokens, i = [], 0
        while i < len(s):
            if s[i:i+2] == 'id': tokens.append('id'); i += 2
            elif s[i] in ['+', '*', '(', ')']: tokens.append(s[i]); i += 1
            elif s[i].isspace(): i += 1
            else: return None
        return tokens + ['$']
    def step_by_step_trace(self, input_str):
        tokens = self.tokenize(input_str)
        if not tokens: return False, ["Rejected: Tokenization failed"]
        self.stack = ['$', 'E']
        steps = [f"Stack: {list(self.stack)}"]
        ip = 0
        while len(self.stack) > 0:
            top = self.stack[-1]
            current = tokens[ip]
            if top == current:
                self.stack.pop(); ip += 1
                steps.append(f"Match terminal '{top}'. Stack: {list(self.stack)}")
            elif top in ['id', '+', '*', '(', ')', '$']:
                return False, steps + [f"Mismatch: Expected {top} but found {current}"]
            else:
                lookup = (top, current)
                if lookup in self.parsing_table:
                    prod = self.parsing_table[lookup]
                    self.stack.pop()
                    for sym in reversed(prod):
                        self.stack.append(sym)
                    steps.append(f"Expand {top} -> {' '.join(prod) if prod else 'epsilon'}. Stack: {list(self.stack)}")
                else:
                    return False, steps + ["Parsing table error"]
        return ip == len(tokens), steps

class PalindromeNPDA:
    def step_by_step_trace(self, input_str):
        queue = [(0, 'q0', ('Z',), ["Initial State q0, Stack: ['Z']"])]
        while len(queue) > 0:
            idx, state, stack, hist = queue.pop(0)
            if idx == len(input_str) and state == 'q1' and stack == ('Z',):
                return True, hist + ["Accepted: Correct midpoint choice & balanced matching"]
            if state == 'q1' and idx < len(input_str):
                if input_str[idx] == stack[-1]:
                    queue.append((idx + 1, 'q1', stack[:-1], hist + [f"q1: Match & pop {input_str[idx]}"]))
                continue
            if state == 'q0':
                queue.append((idx, 'q1', stack, hist + ["q0 -> q1 (Epsilon transition: Guessing midpoint)"]))
                if idx < len(input_str) and input_str[idx] in ['a', 'b']:
                    queue.append((idx + 1, 'q0', stack + (input_str[idx],), hist + [f"q0: Push {input_str[idx]}"]))
        return False, ["Rejected: No computational path matched as palindrome."]
