from huffman.tree import Tree
from math import ceil, floor
import os
import matplotlib.pyplot as plt
import functools
import math
from bitarray import bitarray
import re


class File:
    def __init__(self, filename: str):
        self.filename = filename
        self.byteQuantities = {bytes([i]): 0 for i in range(256)}
        self.byteProbabilities: dict[bytes, int] = {}
        self.entropy = 0
        self.fileSize = 0
        self.compressedFileSize = 0
        self.curPosition = 0

    def countBytes(self):
        with open(self.filename, 'rb') as f:
            while True:
                chunk = f.read(1)
                if not chunk:
                    break

                self.byteQuantities[chunk] += 1

        self.fileSize = os.path.getsize(self.filename)

    def calculateProbabilities(self):
        total = 0.0
        for k in self.byteQuantities:
            total += self.byteQuantities[k]

        for k in self.byteQuantities:
            if self.byteQuantities[k] > 0:
                self.byteProbabilities[k] = self.byteQuantities[k] / total

        self.entropy = -functools.reduce(lambda x, y: x +
                                         self.byteProbabilities[y]*math.log(self.byteProbabilities[y], 2), self.byteProbabilities, 0)

    def probStat(self):
        plt.bar(list(map(lambda k: int.from_bytes(k, 'big'),
                         self.byteProbabilities.keys())), self.byteProbabilities.values(), align='center')
        plt.ylabel('Probability')
        plt.xlabel('Bytes')
        plt.show()

    def calculateSize(self, codebook):
        print("Entropy: " + str(self.entropy))
        for k in codebook:
            self.compressedFileSize += len(codebook[k]) * \
                self.byteQuantities[k]

        self.compressedFileSize = self.compressedFileSize // 8 + \
            ceil(self.compressedFileSize % 8 / 10)

        print(str(self.fileSize) + ' bytes')
        print(str(self.compressedFileSize) + ' bytes')
        print(str(round(self.compressedFileSize / self.fileSize * 100)) + '%')

    def compress(self, rawCodebook, codebook):
        buffer = bitarray()
        with open(self.filename, 'rb') as rf:
            with open(self.filename + '.compressed', 'wb') as wf:
                wf.write(self.fileSize.to_bytes(8, 'big'))
                wf.write(bytes([len(rawCodebook[0])]))

                wf.write(bytes(rawCodebook[0]))
                for e in rawCodebook[1]:
                    wf.write(e)

                while True:
                    label = rf.read(1)
                    if not label:
                        break

                    buffer.extend(codebook[label])

                    while len(buffer) >= 8:
                        buffer[:8].tofile(wf)
                        del buffer[:8]

                buffer.tofile(wf)

    def readHeader(self):
        with open(self.filename, 'rb') as f:
            self.fileSize = int.from_bytes(f.read(8), 'big')
            alphabetLength = int.from_bytes(f.read(1), 'big')
            codebookSize = 0
            codebook = [[], []]

            for i in range(alphabetLength):
                temp = int.from_bytes(f.read(1), 'big')
                codebook[0].append(temp)
                codebookSize += temp

            for i in range(codebookSize):
                codebook[1].append(f.read(1))

            self.curPosition = f.tell()

        return codebook

    def decompress(self, tree: Tree):
        curNode = tree.root

        with open(self.filename, 'rb') as rf:
            with open(re.sub('.compressed$', '', self.filename), 'wb') as wf:
                rf.seek(self.curPosition, 0)

                while True:
                    try:
                        code = bitarray()
                        code.fromfile(rf, 1)
                        curNode = tree.decompress(wf, curNode, code)
                    except:
                        break

        with open(re.sub('.compressed$', '', self.filename), 'ab') as f:
            f.truncate(self.fileSize)
