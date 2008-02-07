
__all__ = [
    "Parent",
    ]

class Parent(object):
    def __init__(self):
        self.children = []

    def _attach(self, child):
        self.children.append(child)

    def _detach(self, child):
        self.children.remove(child)

    def traverse(self):
        for c in self.children:
            c.traverse()
