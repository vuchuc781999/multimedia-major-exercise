from __future__ import annotations
from .node import Node
from bitarray import bitarray


class Tree:
    def __init__(self):
        self.root = None

    def build(self, alphabet={}):
        externals: list[Node] = []
        internals: list[Node] = []
        extsLen = 0
        intsLen = 0

        for k in alphabet:
            externals.append(Node(l=k, p=alphabet[k]))

        externals.sort(key=(lambda e: e.data['p']))

        extsLen = len(externals)

        while extsLen + intsLen > 1:
            if intsLen == 0:
                node = Node(p=externals[0].data['p'] + externals[1].data['p'])
                node.addNode(externals[:2])
                internals.append(node)
                del externals[:2]
            elif extsLen == 0:
                node = Node(p=internals[0].data['p'] + internals[1].data['p'])
                node.addNode(internals[:2])
                internals.append(node)
                del internals[:2]
            else:
                if extsLen > 1 and externals[1].data['p'] < internals[0].data['p']:
                    node = Node(
                        p=externals[0].data['p'] + externals[1].data['p'])
                    node.addNode(externals[:2])
                    internals.append(node)
                    del externals[:2]
                elif intsLen > 1 and internals[1].data['p'] < externals[0].data['p']:
                    node = Node(
                        p=internals[0].data['p'] + internals[1].data['p'])
                    node.addNode(internals[:2])
                    internals.append(node)
                    del internals[:2]
                else:
                    node = Node(
                        p=internals[0].data['p'] + externals[0].data['p'])
                    node.addNode([externals[0], internals[0]])
                    internals.append(node)
                    del externals[0]
                    del internals[0]

            extsLen = len(externals)
            intsLen = len(internals)

        if len(internals) == 1:
            self.root = internals[0]
        else:
            self.root = externals[0]

    def countLabelRecur(self, node: Node, quantities: dict[int, list], length: int, avrLen: list[int]):
        if len(node.children) == 0:
            if length in quantities:
                quantities[length][0] += 1
                quantities[length][1].append(node.data['l'])
            else:
                quantities[length] = [1, [node.data['l']]]

            avrLen[0] += node.data['p'] * length
        else:
            for i in range(len(node.children)):
                self.countLabelRecur(
                    node.children[i], quantities, length + 1, avrLen)

    def countLabelByLength(self) -> list[list]:
        quantities = {}
        averageCodeLength = [0, 0]
        self.countLabelRecur(self.root, quantities, 0, averageCodeLength)

        print('ACL    : ' + str(averageCodeLength[0]))

        sortedQuantities = {k: v for k, v in sorted(
            quantities.items(), key=lambda e: e[0])}

        codebook = [[0] * (list(sortedQuantities.keys())[0] - 1), []]

        for k in sortedQuantities:
            codebook[0].append(sortedQuantities[k][0])
            codebook[1].extend(sortedQuantities[k][1])

        return codebook

    def addToCanonicalTree(self, node: Node, label, length, depth, maxWidth, codeword: bitarray) -> bool:
        if depth >= 0:
            if depth < length - 1:
                if len(node.children) == 0:
                    node.children.append(Node())

                codeword.append(bool(len(node.children) - 1))
                added = self.addToCanonicalTree(
                    node.children[-1], label, length, depth + 1, maxWidth, codeword)

                while not added:
                    if len(node.children) >= maxWidth:
                        if len(codeword) > 0:
                            codeword.pop()

                        return False

                    node.children.append(Node())
                    codeword.append(bool(len(node.children) - 1))

                    added = self.addToCanonicalTree(
                        node.children[-1], label, length, depth + 1, maxWidth, codeword)
            else:
                if len(node.children) >= maxWidth:
                    if len(codeword) > 0:
                        codeword.pop()

                    return False

                node.children.append(Node(l=label))
                codeword.append(bool(len(node.children) - 1))

            return True

        return False

    def canonicallyBuild(self, codebook: list[list]):
        quantities = codebook[0]
        alphabet = codebook[1]
        i = len(alphabet) - 1
        canonicalCodebook = {k: bitarray() for k in alphabet}

        self.root = Node()

        for length in reversed(range(len(quantities))):
            for j in range(quantities[length]):
                self.addToCanonicalTree(
                    self.root, alphabet[i], length + 1, 0, 2, canonicalCodebook[alphabet[i]])
                i -= 1

        return canonicalCodebook

    def decompress(self, file, curNode: Node, code: bitarray) -> Node:
        if len(curNode.children) == 0:
            file.write(curNode.data['l'])

            if len(code) == 0:
                return self.root
            else:
                return self.decompress(file, self.root, code)
        else:
            if len(code) == 0:
                return curNode
            else:
                return self.decompress(file, curNode.children[int(code[0])], code[1:])

    def printRecur(self, node: Node, path: bitarray = bitarray(), length=0, point: bool = None):
        if not (node is None):
            if not (point is None):
                if len(path) <= length:
                    path.append(point)
                else:
                    path[length] = point

                length += 1

            if len(node.children) == 0:
                print(node.data['l'])
                print(path[:length])
            else:
                for i in range(len(node.children)):
                    self.printRecur(
                        node.children[i], path, length, bool(i))

    def print(self):
        self.printRecur(self.root)
