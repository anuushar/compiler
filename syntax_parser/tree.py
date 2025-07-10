class TreeNode:
    def __init__(self, value, is_terminal=False):
        self.value = value
        self.is_terminal = is_terminal
        self.children = []
        self.parent = None
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def is_leaf(self):
        return len(self.children) == 0 