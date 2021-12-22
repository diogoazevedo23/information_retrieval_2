"""

    Autores:
    Diogo Azevedo nº 104654 / Ricardo Madureira nº 104624
    19/11/2021

"""

# Imports
import sys
import json
import math
from testeTokenizer import Tokenizer    # Import of Tokenizer
import time

from operator import methodcaller

""" Main Class """


class Ranked:

    lenDocs = {}
    tfDict = {}
    tokens = []
    finalTF = {}
    array_queries = []
    numDocs = 0
    tfidfDocs = {}
    tfidfQuery = {}
    bm25Final = {}
    line2 = ""

    full_path1 = "extras/dicionario.txt"
    dictionario_palavras = json.load(open(full_path1))
    full_path2 = "finalBlock/completeText.txt"
    dictionary_final = json.load(open(full_path2))
    full_path3 = "extras/lenDocs.txt"
    lenDocs = json.load(open(full_path3))

    def __init__(self, query, tokenizer_mode, steemer, ranker):
        self.query = query
        self.ranker = ranker
        self.tokenizer = Tokenizer("4", tokenizer_mode, steemer)

    def readQuery(self):
        print("\n\t* Reading Queries / Tokenizer *\n")
        with open(self.query, 'r') as f:
            for line in f:
                self.line2 = line
                #print("line -->", line)
                self.tokens = self.tokenizer.tokenize2(line)
                self.array_queries.append(line)

                #print("\nFinals Tokens -->", self.tokens)

                self.things()
                self.tfidf_Queries()
                if self.ranker == 'tfidf':
                    #print("\n\tself.ranker ->", self.ranker, "\n")
                    self.tf_idfFinal()
                elif self.ranker == 'bm25':
                    #print("\n\tself.ranker ->", self.ranker, "\n")
                    self.bm25()
                else:
                    print("Choose a valid ranker")
                    exit(0)

                self.tokens.clear()

    def things(self):
        start = time.time()
        print("\n\t\t* Things *\n")
        for x in self.tokens:
            for i in self.lenDocs:
                if x not in self.tfDict:
                    self.tfDict[x] = {i: 0}
                else:
                    self.tfDict[x].update({i: 0})

        self.numDocs = len(self.lenDocs)

        #print("\nself.tfDict -->", self.tfDict)
        end = time.time()
        print("Time things =", end - start)

    def tfidf_Docs(self):
        start = time.time()
        print("\t\t* TFIDF Docs *")
        self.things()

        for k, v in self.dictionary_final.items():
            for x in v.items():
                #print("k", k, "| x[0]", x[0], "| x[1]", x[1], "| dictionario_palavras[k]", self.dictionario_palavras[k], "| Mult =", x[1] * self.dictionario_palavras[k])
                if k not in self.tfidfDocs:
                    self.tfidfDocs[k] = {x[0]: x[1] * 1}
                else:
                    if x not in self.tfidfDocs[k]:
                        self.tfidfDocs[k].update({x[0]: x[1] * 1})
                    else:
                        self.tfidfDocs[k][x[0]].update(x[1] * 1)

        #print("\nself.tfidfDocs ->", self.tfidfDocs, "\n")
        
        sumVals2 = 0
        for k in self.tfidfDocs.values():
            for x in k.values():
                sumVals2 += math.pow(x, 2)

        sumVals2 = math.sqrt(sumVals2)
        #print("sumVals2", sumVals2, "\n")

        #print("Afer Cosine")
        for k, v in self.tfidfDocs.items():
            #print("k:", k, "| v:", v)
            for x in v.items():
                #print("x:", x)
                self.tfidfDocs[k].update({x[0]: x[1] / sumVals2})

        #print("\nself.tfidfDocs ->", self.tfidfDocs, "\n")
        end = time.time()
        print("Time TFIDFDocs =", end - start)

    def tfidf_Queries(self):
        start = time.time()
        print("\n\t\t* TFIDF Queries *\n")
        tfQuery = {}
        idfQuery = {}

        for k, v in self.dictionario_palavras.items():
            #print("k:", k, "| v:", v)
            tfQuery[k] = 0

        for k in self.tokens:
            if k not in tfQuery:
                tfQuery[k] = 1
            else:
                tfQuery[k] += 1

        #print("tfQuery ->", tfQuery)

        for k, v in self.dictionary_final.items():
            #print("k:", k, "| v:", v, "| len(v):", len(v))
            idfQuery[k] = math.log10(self.numDocs / len(v))

        for k in self.tokens:
            if k not in idfQuery:
                #print(k, "is not")
                idfQuery[k] = 0
            else:
                #print(k, "is in")
                pass

        #print("\nidfQuery ->", idfQuery, "\n")

        for k, v in tfQuery.items():
            #print("self.tfidfQuery[k] = v", v , "* idfQuery[k]", idfQuery[k])
            self.tfidfQuery[k] = v * idfQuery[k]

        #print("\nself.tfidfQuery ->", self.tfidfQuery, "\n")

        sumVals = 0
        for x in self.tfidfQuery.values():
            sumVals += math.pow(x, 2)
        sumVals = math.sqrt(sumVals)

        #print("\nAfter Cosine")

        for x, v in self.tfidfQuery.items():
            self.tfidfQuery.update({x: v / sumVals})
        
        #print("\nself.tfidfQuery ->", self.tfidfQuery, "\n")
        end = time.time()
        print("Time TFIDFQueries =", end - start)

    def tf_idfFinal(self):
        start = time.time()

        print("\n\t\t* TFIDF Final *")

        tdidfFinal = {}

        for key, value in self.tfidfQuery.items():
            for key2, value2 in self.tfidfDocs.items():
                if key == key2:
                    #print("key:", key, "value:", value, "key2:", key2, "value2:", value2)
                    for k, v in value2.items():
                        #print("key:", key, "value:", value, "key2:", key2, "k:", k, "v:")
                        #print("key:", key, "value:", value, "value2:", v, "result =", value * v, "k:", k)
                        if key not in tdidfFinal:
                            tdidfFinal[key] = {k: value * v}
                        else:
                            if k not in tdidfFinal[key]:
                                tdidfFinal[key].update({k: value * v})
                            else:
                                tdidfFinal[key][k].update(value * v)

        #print("\ntdidfFinal ->", tdidfFinal, "\n")
        print("\nFinalSum")

        finalSum = {}
        for key, subdict in tdidfFinal.items():
            for k, v in subdict.items():
                finalSum[k] = finalSum.get(k, 0) + v

        #print("\ntdidfFinal ->", finalSum, "\n")
        print("\ntop5Results")

        top5Results = {k: v for k, v in sorted(
            finalSum.items(), key=lambda item: item[1], reverse=True)[0:100]}
        print("\n\n\t** Top 100 documentos **")
        with open('finalResult/resultsTFIDF.txt', 'a') as f:
            line = "Q:", self.line2
            f.write(f'{line}\n')
            for k, v in top5Results.items():
                f.write(f'{k}\n')
        
        end = time.time()
        print("Time TFIDFFinal =", end - start)

    def bm25(self, k1=1.2, b=0.75):
        start = time.time()

        print("\n\t\t* BM25 *\n")

        idfQuery = {}
        tfQuery = {}
        self.bm25Final = {}
        finalSum = {}
        top5Results = {}
        idfWord = 0
        numerator = 0
        denominator = 0
        bm25Doc = 0


        #print("\nself.tfDict -->", self.tfDict, "\n")

        for k, v in self.dictionario_palavras.items():
            #print("k:", k, "| v:", v)
            tfQuery[k] = 0

        for k in self.tokens:
            if k not in tfQuery:
                tfQuery[k] = 1
            else:
                tfQuery[k] += 1

        #print("tfQuery ->", tfQuery, "\n")

        #print("self.lenDocs:", self.lenDocs, "\n")
        avdl = sum(self.lenDocs.values()) / self.numDocs
        #print("self.numDocs:", self.numDocs, "SUM:", avdl)

        for k, v in self.dictionary_final.items():
            #print("k:", k, "| v:", v, "| len(v):", len(v))
            idfQuery[k] = math.log10(self.numDocs / len(v))

        #print("\nidfQuery ->", idfQuery, "\n")

        for k, v in self.dictionary_final.items():
            #print("Termo(k):", k, "IDF(v):", v)
            for x in v.items():
                idfWord = idfQuery[k]
                numerator = ((k1 + 1) * x[1])
                denominator = ((k1 * ( (1 - b) + (b*(self.lenDocs[x[0]]/avdl)))) + x[1])
                #print("x[0]:", x[0], "x[1]:", x[1], "idfQuery[k]:", idfQuery[k], "idfWord:", idfWord, "numerator:", numerator, "self.lenDocs[x[0]]", self.lenDocs[x[0]])
                bm25Doc = (idfWord * (numerator / denominator))
                #print("bm25Doc:", bm25Doc)

                if k not in self.bm25Final:
                    self.bm25Final[k] = {x[0]: bm25Doc}
                else:
                    if x[0] not in self.bm25Final[k]:
                        self.bm25Final[k].update({x[0]: bm25Doc})
                    else:
                        self.bm25Final[k][x[0]].update(bm25Doc)

        print("\n\n\t ** Final ** \n")
        #print("self.bm25Final ->", self.bm25Final, "\n")

        for key, subdict in self.bm25Final.items():
            for k, v in subdict.items():
                finalSum[k] = finalSum.get(k, 0) + v

        #print("\nBM25FinalSum ->", finalSum, "\n")

        top5Results = {k: v for k, v in sorted(
            finalSum.items(), key=lambda item: item[1], reverse=False)[0:100]}
        print("\n\n\t** Top 100 documentos **")
        with open('finalResult/resultsBM25.txt', 'a') as f:
            line = "Q:", self.line2
            f.write(f'{line}\n')
            for k, v in top5Results.items():
                f.write(f'{k}\n')

        end = time.time()
        print("Time Bm25 =", end - start)

    def writeToFile(self, finalDict):
        start = time.time()

        print("\nWrinting To File")
        with open('finalResult/writeToFile.txt', 'w') as f:
            for key, value in finalDict.items():
                string = ""
                for x, y in value.items():
                    string += str((x, y))
                line2 = key+"|"+str(self.dictionario_palavras[key])+"|"+string
                f.write(f'{line2}\n')

        end = time.time()
        print("Time writeToFile =", end - start)


""" Main """

if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("Usage: py ranked.py ('path to queries.txt') ('yes') ('yes') ('tfidf')"
              + "\n** CHOICES **"
              + "\npath = queries.txt"
              + "\ntokenizer = yes/no"
              + "\nstemmer = yes/no"
              + "\nranker = tfidf/bm25")
        sys.exit(1)

    try3 = Ranked(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    start = time.time()
    try3.tfidf_Docs()
    try3.readQuery()
    try3.writeToFile(try3.tfidfDocs)
    end = time.time()
    print("Total Time Spent was =", end - start)
