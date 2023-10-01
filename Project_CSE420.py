class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
        self.firstpos = set()
        self.lastpos = set()
        self.followpos = set()

    def __repr__(self):
        return f"Node({self.value}, {self.left}, {self.right})"

def augmentation(regex):
    idx = 1
    new_reg_ex = ""
    for i in regex:
        if i.isalpha()==False:
            new_reg_ex  += i    
        else:
            if i!="ε":
                new_reg_ex  += str(idx)
                idx+=1
    new_reg_ex  += '.#'
    return new_reg_ex 

def regex_to_syntaxtree(regex_string):
    stack = []
    oparators = []
    precedence = {"(": 0, "|": 1, ".": 2, "*": -1}
    i = 0
    while i < len(regex_string):
        char = regex_string[i]
        if char == "(":
            oparators.append(char)
        elif char == ")":
            while oparators and oparators[-1] != "(":
                right = stack.pop()
                left = stack.pop()
                op = oparators.pop()
                stack.append(Node(op, left, right))
            if not oparators:
                raise ValueError("Unbalanced parentheses")
            oparators.pop()
        elif char in "*|.":
            while oparators and oparators[-1] != "(" and precedence[char] <= precedence[oparators[-1]]:
                right = stack.pop()
                left = stack.pop()
                op = oparators.pop()
                stack.append(Node(op, left, right))
            oparators.append(char)
        else:
            if i + 1 < len(regex_string) and regex_string[i + 1] in "+*?":
                stack.append(Node(regex_string[i + 1], Node(char)))
                i += 1
            else:
                stack.append(Node(char))
        i += 1

    while oparators:
        op = oparators.pop()
        right = stack.pop() if stack else None
        left = stack.pop() if stack else None
        stack.append(Node(op, left, right))

    if len(stack) != 1 or oparators:
        raise ValueError("Syntax tree construction failed")
    print(stack)
    return stack[0]
    
def calculate_nullable(node):
    EPSILON = ""
    if node:
        if node.left is None and node.right is None:  # Leaf node
            node.nullable = True if node.value == EPSILON else False
        else:
            calculate_nullable(node.left)
            calculate_nullable(node.right)
            if node.value == '|':
                node.nullable = node.left.nullable if node.left else False or node.right.nullable if node.right else False
            elif node.value == '.':
                node.nullable = node.left.nullable if node.left else False and node.right.nullable if node.right else False
            elif node.value == '*':
                node.nullable = True



def calculate_firstpos(node):
    if node:
        if node.left is None and node.right is None:  # Leaf node
            node.firstpos = {node.value}
        elif node.value == '.':
            calculate_firstpos(node.left)
            calculate_firstpos(node.right)
            node.firstpos = node.left.firstpos
            if node.left.nullable:
                node.firstpos.update(node.right.firstpos)
        elif node.value == '|':
            calculate_firstpos(node.left)
            calculate_firstpos(node.right)
            node.firstpos = node.left.firstpos.union(node.right.firstpos)
        elif node.value == '*':
            calculate_firstpos(node.left)
            calculate_firstpos(node.right)
            node.firstpos = node.left.firstpos
            if '#' in node.left.lastpos:
                node.firstpos.update(node.right.firstpos)

def calculate_lastpos(node):
    if node:
        if node.left is None and node.right is None:  # Leaf node
            node.lastpos = {node.value}
        elif node.value == '.':
            calculate_lastpos(node.left)
            calculate_lastpos(node.right)
            node.lastpos = node.right.lastpos
            if node.right.nullable:
                node.lastpos.update(node.left.lastpos)
        elif node.value == '|':
            calculate_lastpos(node.left)
            calculate_lastpos(node.right)
            node.lastpos = node.left.lastpos.union(node.right.lastpos)
        elif node.value == '*':
            calculate_lastpos(node.left)
            calculate_lastpos(node.right)
            if node.left.nullable:
                # if the left child is nullable, the * node can match
                # after any sequence of left child matches followed by
                # a right child match
                node.lastpos = node.right.lastpos.copy()
                node.lastpos.update(node.left.lastpos)
            else:
                # if the left child is not nullable, the * node can match
                # only after a sequence of left child matches followed by
                # a right child match
                node.lastpos = node.left.lastpos.copy()


def calculate_followpos(node):
    if node:
        if node.value == '.':
            for left_pos in node.left.lastpos:
                for right_pos in node.right.firstpos:
                    left_pos_node = find_node(node, left_pos)
                    left_pos_node.followpos.add(right_pos)
        elif node.value == '*':
            for last_pos in node.lastpos:
                for first_pos in node.firstpos:
                    last_pos_node = find_node(node, last_pos)
                    last_pos_node.followpos.add(first_pos)
        calculate_followpos(node.left)
        calculate_followpos(node.right)


def find_node(node, pos):
    if node is None:
        return None
    if pos in node.firstpos or pos in node.lastpos:
        return node
    return find_node(node.left, pos) or find_node(node.right, pos)

def print_syntax_tree(node):
    if node.value == "#":
        return
    if node is None:
        return
    if node.left is not None:
        print_syntax_tree(node.left)
    if node.right is not None:
        print_syntax_tree(node.right)
    if node.left is not None:
        firstpos = "{" + ", ".join(str(x) for x in node.firstpos if x != "#") + "}"
        lastpos = "{" + ", ".join(str(x) for x in node.lastpos if x != "#") + "}"
        followpos = "{" + ", ".join(str(x) for x in node.lastpos if x != "#") + "}"
        print(f"Node: {node.value}, Nullable: {node.nullable}, FirstPos: {firstpos}, LastPos: {lastpos}, Followpos: {followpos}")
    else:
        print(f"Node: {node.value}, Nullable: {node.nullable}, FirstPos: {node.firstpos}, LastPos: {node.lastpos}")
reg_ex = "(a|b)*a.b.b"
reg_ex1 = "(a|ε)*a.b.b"
print(augmentation(reg_ex))
syntax_tree = regex_to_syntaxtree(reg_ex)
calculate_nullable(syntax_tree)
calculate_firstpos(syntax_tree)
calculate_lastpos(syntax_tree)
calculate_followpos(syntax_tree)
print_syntax_tree(syntax_tree)
print("-------------------------------------------------------------------------")
print(augmentation(reg_ex1))
syntax_tree1 = regex_to_syntaxtree(reg_ex1)
calculate_nullable(syntax_tree1)
calculate_firstpos(syntax_tree1)
calculate_lastpos(syntax_tree1)
calculate_followpos(syntax_tree1)
print_syntax_tree(syntax_tree1)