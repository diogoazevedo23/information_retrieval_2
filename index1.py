"""

    Autores:
    Diogo Azevedo nº 104654 / Ricardo Madureira nº 104624
    19/11/2021

"""

# Imports
import sys
import os
import json  # Json functions
import time  # Time functions
import math


""" Main Class """


class Merger:

    result = {}     # Final dictionary with the merged blocks
    contagem = []   # Array with documents in which the term searched will appear

    def __init__(self, path="blocks/"):
        self.path = path

    """ Merge the blocks into a final block """

    def merge_docs(self, len_doc):
        # print("A ler ficheiros")
        files = [f for f in os.listdir(
            self.path) if f.endswith(".txt")]  # Get all blocks
        print("\n* Merging *")

        for file in files:
            full_path = self.path + file
            d = json.load(open(full_path))
            for word in d:
                if word not in self.result:
                    self.result[word] = dict()
                for doc in d[word]:
                    if doc not in self.result[word]:
                        self.result[word][doc] = d[word][doc]
                    else:
                        self.result[word][doc] += d[word][doc]

        #print("sorted Dict -->", self.result)
        print("\n")

        dicionarioWords = {}

        for k, v in self.result.items():
            #print("k ->", k, "v ->", v, "len(v) ->", len(v), "len(len_doc) ->", len(len_doc))
            for x, y in v.items():
                #print("x ->", x, "y ->", y)
                dicionarioWords[k] = (math.log10(len(len_doc)) / len(v))
        #print("\nIDF ->", dicionarioWords)

        with open('extras/dicionario.txt', 'w') as f:
            json.dump(dicionarioWords, f)
        print("\nSaved")

        for k, v in self.result.items():
            for x, y in v.items():
                # print("k:", k, "x:", x, "y:", y, "len(x)", len_doc[x])
                self.result[k][x] = (1 + (math.log10(y / len_doc[x])))

        print("\n")
        #print("sorted Dict -->", self.result)
        print("\n\n")

    """ Save the merged dictionary """

    def save_merge(self):
        with open('finalBlock/completeText.txt', 'w') as f:
            json.dump(self.result, f)
        print("\nSaved")

    """ Search for a word """

    def index_searcher(self, termo_final):
        dictionary_final = {}

        full_path2 = "finalBlock/completeText.txt"
        dictionary_final = json.load(open(full_path2))
        if termo_final in dictionary_final:
            self.contagem.append(dictionary_final[termo_final].keys())

        # print("Contagem -> ", self.contagem)
        # print("C2 -->", len(self.contagem[0]))

    """ Get size of nested dictionary """

    def calculate_dict_size(self):
        mem_size = 0
        for key, value in self.result.items():
            mem_size += sys.getsizeof(value)

        return mem_size + sys.getsizeof(self.result)

    """ Get nº of terms """

    def print_results(self):
        # print("\n\nresult ->", self.result.items())
        return (len(self.result))


""" Main """

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: py teste1.py term('diogo')"
              + "\n** CHOICES **"
              + "\nterm = term you need to search on index")
        sys.exit(1)

    try2 = Merger()

    indexSearchStart = time.time()
    try2.index_searcher(sys.argv[1])
    indexSearchEnd = time.time()
    indexSearchFinal = indexSearchEnd - indexSearchStart

    with open("finalResult/finalAnswers.txt", "a") as f:
        print("\ne) Amount of time taken to start up an index searcher, after the final index is written to disk ==",
              indexSearchFinal, "s.", file=f)
        print("\nThe term", sys.argv[1], "is in", len(
            try2.contagem[0]), "documents", file=f)
