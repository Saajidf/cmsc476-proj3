import os
from bs4 import BeautifulSoup
import timeit
import math

# define punctuation
punctuations = '''1234567890!`()+-[]{};:'"\=,<>./?@#$%^&*_~'''

numOfDocs = 0
tf = {}  # dictionary of dictionaries each one is word count of each file
l1 = []  # stopwords from stopwords.txt
docFreq = {}  # key is word, value is num of documents its in
location = {}  # this will be dic of key = word val = line of posting file of first occurrence
doc_weights = {}  # dictionary of dictionaries all the weights for each doc


def sort_dict_by_key(unsorted_dict):
    sorted_keys = sorted(unsorted_dict.keys(), key=lambda x: x.lower())

    sorted_dict = {}
    for key in sorted_keys:
        sorted_dict.update({key: unsorted_dict[key]})

    return sorted_dict

def calc_weight(word, total, freq, docfreq):
    idf = math.log(float(numOfDocs) / float(docfreq[word]))
    return float(freq / total) * float(idf)


if __name__ == '__main__':
    # start timer
    start = timeit.default_timer()

    stop_file = open('stopwords.txt', 'r')
    for line in stop_file.readlines():
        for i in line.split('\n'):
            l1.append(i)
    stop_file.close()

    files = os.listdir("html_files")

    # get term frequency, number of files, and doc frequency of each word
    for x in files:
        # if numOfDocs == 10:
        #     break

        wordCount = {}
        numOfDocs += 1

        currFile = "html_files/" + x

        # opens file and strips html
        file = open(currFile, encoding="utf8", errors='ignore')
        soup = BeautifulSoup(file.read(), "html.parser")
        file.close()
        justText = soup.get_text()
        # remove punctuation from the string
        no_punct = ""
        for char in justText:
            if char not in punctuations:
                no_punct = no_punct + char

        newFile = os.path.splitext(x)[0]

        for y in no_punct.lower().split():
            if y[0].isnumeric():
                continue
            if y in wordCount:
                # Increment count of word by 1
                wordCount[y] = wordCount[y] + 1
            else:
                # Add the word to dictionary with count 1
                wordCount[y] = 1
                # add to total doc frequency only once per document
                if y in docFreq:
                    docFreq[y] = docFreq[y] + 1
                else:
                    docFreq[y] = 1

        # clean up wordcount
        for k, v in list(wordCount.items()):
            if v == 1:
                del wordCount[k]
        for k, v in list(wordCount.items()):
            if k in l1:
                del wordCount[k]
        for k, v in list(wordCount.items()):
            if len(k) == 1:
                del wordCount[k]

        # add term frequency of current file to dictionary of all tf dictionaries
        tf[newFile] = wordCount

    # loop through dic of tf dic and create doc weights
    for t in tf:
        weights = {}

        # only look at current tf
        name = t
        curr = tf[t]
        numOfWords = sum(curr.values())

        # calc weight of each word in each doc
        for x in curr:
            weights[x] = calc_weight(x, numOfWords, curr[x], docFreq)

        doc_weights[name] = weights

    lineCount = 0
    postings = open("postings.txt","a")
    # create postings file
    for w in doc_weights:

        # only look at curr doc
        name = w
        weights = doc_weights[w]

        for word in weights:
            lineCount = lineCount + 1
            if word not in location:
                location[word] = lineCount
            postings.write(str(name) + ", " + str(weights[word]))
            postings.write("\n")

    postings.close()

    sortedAlpha = sort_dict_by_key(location)
    # create dictionary file
    dic = open("dictionary.txt","a")
    for word in sortedAlpha:
        name = word;
        num = docFreq[word]
        loc = sortedAlpha[word]
        dic.write(name)
        dic.write("\n")
        dic.write(str(num))
        dic.write("\n")
        dic.write(str(loc))
        dic.write("\n")

    dic.close()

    print(timeit.default_timer() - start)
