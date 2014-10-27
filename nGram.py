# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 02:54:36 2014

@author: Carlos Manuel Pacheco Soares
@StudentNumber: 67518
@Course: Processamento Computacional da Linguagem (NLP)
@Degree: Master in Computer Engineering
@University: ISCTE, Lisbon
"""

# Imports used:
import sys, getopt, os, re
from collections import Counter
from pandas import DataFrame

# Globals:
## Unchangeable:
normExt = ".norm"
## Changeable:
dirName = "./data"
ext = ".txt"
### Number of chars used for the n-Gram:
num = 3
### Phrase for testing:
testPhrase = "Olá tudo bem?\nChamo-me Carlos Soares."
smoothing = False
testFile = "./test.csv"
fileToTest = False

def normalizeText (n, text):
    temp = ''
    wordBegin = ''
    wordEnd = ''
    for word in re.split('\W+', text, flags=re.UNICODE):
        if word != '':
            if n == 1 :
                wordBegin += "<"
                wordEnd += ">"
            else:
                for i in range(n-1):
                    wordBegin += "<"
                    wordEnd += ">"
            temp += wordBegin + word + wordEnd + "\n"
            wordBegin = wordEnd = ''
    return temp;

def normalizeFilesInDirectory (n, dir, fileExt, newExt):

    for file in os.listdir(dir):
        if file.endswith(fileExt):
            if os.path.splitext(file)[0] != "sources":
                tempFile = open(dir+'/'+os.path.splitext(file)[0]+os.path.splitext(file)[1], 'r', encoding="utf8")
                temp = re.sub("\d+", " ", tempFile.read().lower())
                tempFile.close()
                
                tempFile = open(dir+'/'+os.path.splitext(file)[0]+newExt, 'w', encoding="utf8")
                tempFile.write(normalizeText(n, temp))
                tempFile.close()

def ngram (n, text):
    gram = ""
    gramArray = []
    for i in range(len(text)-n):
        for j in range(n):
            if (i+j) == len(text):
                break
            if text[i+j] == "\n":
                if j == 0 :
                    break
                else:
                    i += 1
                    gram += text[i+j]
            else:
                gram += text[i+j]
        if ("\n" not in gram) & (gram != "") & (len(gram) == n):
            # print(gram)
            # This is where I have to add the gram to the counter...
            gramArray.append(gram)
        gram = ""
    count = Counter(gramArray)
    return sorted(count.items());
            
def createNGramFile (n, dir, ext):
    gramExt = '.' + str(n) + 'gr'
    
    for file in os.listdir(dir):
        if file.endswith(ext):
            if os.path.splitext(file)[0] != "sources":
                fileName = os.path.splitext(file)[0]
                file = open(dir+'/'+fileName+ext, 'r', encoding="utf8")
                normFile = file.read()
                file.close()
                
                tempGram = ngram (n, normFile)
                df = DataFrame(tempGram)
                df.columns = [str(n) + '-gram', 'count']

                df.to_csv(dir+'/'+fileName+gramExt, sep='\t', encoding='utf-8', header=False, index=False)

def testSentence (n, phrase):
    tempPhrase = normalizeText(n, phrase)

### Changeable:
#dirName = "./data"
#ext = ".txt"
#### Number of chars used for the n-Gram:
#num = 3
#### Phrase for testing:
#testPhrase = "Olá tudo bem?\nChamo-me Carlos Soares."
#smoothing = False
#testFile = "./test.csv"
#fileToTest = False

def main(argv):
   try:
      opts, args = getopt.getopt(argv,"hd:e:n:t:c:s",["dir=", "dirName=", "ext=", "extention=", "num=", "number=", "test=", "testPhrase=", "testCSV="])
   except getopt.GetoptError:
      print('nGram.py <options>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h', "--help"):
         print('nGram.py <options>')
         # Add missing options
         sys.exit()
      elif opt in ("-d", "--dir", "--dirName"):
         global dirName
         dirName = arg
      elif opt in ("-e", "--ext", "--extention"):
         global ext
         ext = arg
      elif opt in ("-n", "--num", "--number"):
         if int(arg) > 0 :
             global num
             num = int(arg)
      elif opt in ("-t", "--test", "--testPhrase"):
         global testPhrase
         testPhrase = arg
         
         # Needs to be refined in order to recieve a full sentence:
         print(testPhrase)
      elif opt in ("-c", "--testCSV"):
         global testFile
         testFile = arg
         global fileToTest
         fileToTest = True
      elif opt in ('-s', "--smoothing", "--smooth"):
         global smoothing
         smoothing = True

   normalizeFilesInDirectory (num, dirName, ext, normExt);
   createNGramFile (num, dirName, normExt);
   
   #Here do the testing

if __name__ == "__main__":
   main(sys.argv[1:])