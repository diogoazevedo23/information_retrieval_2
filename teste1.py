"""

    Autores:
    Diogo Azevedo nº 104654 / Ricardo Madureira nº 104624
    19/11/2021

"""

# Imports
from testeTokenizer import Tokenizer    # Import of Tokenizer
from index1 import Merger               # Import of Merger
import json                             # Json Functions
import time                             # Time functions
import sys
from collections import OrderedDict     # Order dictionaries
import csv                              # Ler ficheiros csv


""" Main class """


class teste1:

    PostingList = {}            # Dicionario das postings lists
    Sorted_PostingList = {}     # Dicionario das postings lists ordenadas
    d = {}                      # para testes
    BlockFilesNumber = 0        # Numero de blocos temporarios criados
    total_mem_size = 0          # Total de memoria usada no final da indexação
    nTokens = 0
    len_doc = {}

    """ Initialize some functions/variables """

    # def __init__(self, min_tamanho, tokenizer_mode, steemer, chunksize, file='files/amazon_reviews_us_Digital_Video_Games_v1_00.tsv'):
    def __init__(self, min_tamanho, tokenizer_mode, steemer, chunksize, file='files/testFile.tsv'):
        self.tokenizer_mode = tokenizer_mode
        self.tokenizer = Tokenizer(min_tamanho, tokenizer_mode, steemer)
        self.file = file
        self.chunksize = chunksize
        self.merger = Merger()

    """ Function to send chunks of data to processing """

    def gen_chunks(self, reader):
        chunk = []
        for i, line in enumerate(reader):
            if (i % self.chunksize == 0 and i > 0):
                # print("\n Inside line -->", line)
                # print("Inside Chunk -->", chunk)
                yield chunk
                del chunk[:]
            chunk.append(line)
        # print("\n Outside Line -->", line)
        # print("Outside Chunk -->", chunk)
        yield chunk

    """ Processing of data with SPIMI implementation """

    def SPIMIChunk(self):
        num = 0
        num1 = 0

        with open(self.file, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(
                csvfile, delimiter="\t", quoting=csv.QUOTE_NONE)    # Reading csv/tsv files
            """ If you want to switch from tsv to csv files, change the  delimiter="\t", to  delimiter="," """
            print("Reading tsv")

            for chunk in self.gen_chunks(reader):
                tokens = []    # Words
                # len_doc = {}
                print("\n\t\t** ITERATION Nº", num1, "**\n")
                for row in chunk:
                    index = row['review_id']
                    appended_string = row['product_title'] + " " + \
                        row['review_headline'] + " " + \
                        row['review_body']                  # Join title, headline and body rows
                    tokens += self.tokenizer.tokenize(
                        appended_string, index)             # Apply tokenizer of the tokens

                    #len_doc.update({index: len(tokens)})
                    #print("Tokens ->", tokens)
                    #print("Dict -> ", len_doc.items())

                # print("\nFinal Tokens --> ", tokens)
                print("\nIndexing block ", num)
                num += 1
                self.criarBlocos(tokens)
                num1 += 1

        # print(" ")

    """ Indexing of datachunks that were already processed """

    def criarBlocos(self, tokens):
        for token in tokens:
            term = token[0]
            docID = token[1]
            if term not in self.PostingList:
                self.PostingList[term] = {docID: 1}
            else:
                if docID not in self.PostingList[term]:
                    self.PostingList[term].update({docID: 1})
                else:
                    self.PostingList[term][docID] += 1

            # ---------------------------------------------------

            if docID not in self.len_doc:
                self.len_doc[docID] = 1
            else:
                self.len_doc[docID] += 1

        # print("\nPostingList -->", self.PostingList)
        self.Sorted_PostingList = sorted(self.PostingList)
        # print("\nSorted_PostingList -->", self.Sorted_PostingList)

        self.writeToBlock()

    """ Sort the chunks that were already processed and indexed and write them to a block """

    def writeToBlock(self):

        print("\nWriting to block")

        sorted_dictionary = OrderedDict()
        with open('blocks/' + str(self.BlockFilesNumber) + '.txt', 'w') as f:
            for i in self.Sorted_PostingList:
                sorted_dictionary[i] = self.PostingList[i]
            #print("\nsorted_dictionary -->", sorted_dictionary.items())
            json.dump(sorted_dictionary, f)
            self.BlockFilesNumber += 1

        # print("\nPostingList -> ", self.PostingList)
        # print("\nSorted_PostingList -> ", self.Sorted_PostingList)

        self.PostingList.clear()
        self.Sorted_PostingList.clear()
        print("\nFinished writing block")

    """ Merge and save the merged block """

    def pos_index(self):
        self.merger.merge_docs(self.len_doc)
        self.merger.save_merge()

    """ Get size of final dictionary """

    def pos_index2(self):
        return self.merger.print_results()

    """ Size of final dictionary(Gb) """

    def sizeOfDictInGb(self):
        return self.merger.calculate_dict_size()

    """ Print final answers to a file """

    def printToFile(self, messageA, messageB, messageC, messageD):
        with open('finalResult/finalAnswers.txt', 'w') as f:
            print("File ==", self.file, file=f)
            print("\n\t**Answers**\n\n", file=f)
            print("a) Total indexing time ==", messageA, "s.", file=f)
            messageB2 = (f"{messageB/float(1<<30):,.3f} GB")
            print("b) Total index size on disk ==", messageB2, file=f)
            print("c) Vocabulary size(number of terms) ==",
                  messageC, "terms", file=f)
            print("d) Number of temporary index segments written to disk (before merging) ==",
                  messageD, "blocks", file=f)

    """ Saving to File """

    def saveTF(self, dictTf):
        print("\nSaving TF to file")
        with open('extras/lenDocs.txt', 'w') as f:
            json.dump(dictTf, f)
        print("Saved")

    """
    def saveIDF(self):
        dictIDF = {}
        print("\nSaving IDF to file")
        self.merger.idf(len(self.len_doc))
        # with open('extras/IDF.txt', 'w') as f:
        #    json.dump(dictIDF, f)
        # print("Saved")"""


""" Main """

if __name__ == "__main__":

    if len(sys.argv) < 5:
        print("Usage: py teste1.py min_tamanho_palavra(no/4) Stopwords('yes/no/filepath') stemmer('yes/no') chunksize(4)"
              + "\n** CHOICES **"
              + "\nmin_tamanho_palavra: Can be choosen with a number or desativacted with 'no'"
              + "\nstopwords: 'yes', 'no' or pathfile to the file that u want to use"
              + "\nstemmer: 'yes' or 'no'"
              + "\nchunkzise: integer")
        sys.exit(1)

    try1 = teste1(
        sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))

    totalIndexingTimeStart = time.time()
    try1.SPIMIChunk()

    print("\n\nStarging to Merge")
    mergeStartTime = time.time()
    try1.pos_index()
    mergeEndTime = time.time()
    print("\nFinished Merging ==", mergeEndTime - mergeStartTime, "segundos")
    totalIndexingTimeEnd = time.time()
    totalIndexingTimeFinal = totalIndexingTimeEnd - totalIndexingTimeStart
    try1.printToFile(totalIndexingTimeFinal, try1.sizeOfDictInGb(),
                     try1.pos_index2(), try1.BlockFilesNumber)

    # print("Doc_Len -->", try1.len_doc.items())
    try1.saveTF(try1.len_doc)
    # try1.saveIDF()
