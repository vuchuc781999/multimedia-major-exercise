from __future__ import annotations


class Node:
    def __init__(self, **data):
        self.parent: Node = None
        self.children: list[Node] = []
        self.data = data

    def addNode(self, nodes: list[Node]):
        self.children.extend(nodes)
