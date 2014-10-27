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
import sys, getopt, os, re, numpy
import matplotlib.pyplot as plt
from collections import Counter
from pandas import DataFrame, Series

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
outFile = "./resultados.txt"
writeOutput = False
plot = False

def normalizeText (n, text):
    temp = ''
    wordBegin = ''
    wordEnd = ''
    text = re.sub("\d+", " ", text.lower())
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
                temp = tempFile.read()
                tempFile.close()
                
                tempFile = open(dir+'/'+os.path.splitext(file)[0]+newExt, 'w', encoding="utf8")
                tempFile.write(normalizeText(n, temp))
                tempFile.close()

def grams (n, text):
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
    return gramArray;

def ngram (n, text):
    
    count = Counter(grams(n, text))
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
                
def div(a, b):
    return a / b;
    
def getCount(gram, df):
    try:
        temp = df.loc[gram, 1]
    except:
        temp = 0
    return temp;

def testSentence (n, phrase):
    tempPhrase = normalizeText(n, phrase)
    gram = grams(n, tempPhrase)
    #print(gram)
    
    fileExt1 = '.' + str(n) + 'gr'
    fileExt2 = '.' + str(n-1) + 'gr'
    language = []
    probsArray = []
    
    for file in os.listdir(dirName):
        if file.endswith(fileExt1):
            script_dir = os.path.dirname(__file__)
            path = os.path.join(script_dir, dirName+'/'+os.path.splitext(file)[0]+fileExt1)
            #print(path)
            df1 = DataFrame.from_csv(path, sep='\t', encoding='utf-8', header=None, index_col=0)
            #df1 = Series(df1[1], index=df1.index.values)
            #print(df1)
            script_dir = os.path.dirname(__file__)
            path = os.path.join(script_dir, dirName+'/'+os.path.splitext(file)[0]+fileExt2)
            #print(path)
            df2 = DataFrame.from_csv(path, sep='\t', encoding='utf-8', header=None, index_col=0)
            
            prob = 1
            for i in gram:
                if smoothing:
                    #with smoothing
                    vol = len(list(set(''.join(str(elem) for elem in df2.index.values))))
                    temp = div(getCount(i, df1)+1, getCount(i[:-1], df2)+vol)
                    prob *= temp
                    #print(str(getCount(i, df1)+1), ' / ', str(getCount(i[:-1], df2)+vol), ' = ', temp)
                else:
                    #print(df1[[i]])
                    try:
                        temp = div(getCount(i, df1), getCount(i[:-1], df2))
                        prob *= temp
                        #print(str(getCount(i, df1)), ' / ', str(getCount(i[:-1], df2)), ' = ', temp)
                    except:
                        print("Unknown chars used... Please use '-s' option.")
                        sys.exit(2)
            
            language.append(os.path.splitext(file)[0])
            probsArray.append(prob)
            
    title = str(n)+"-gram result for \"" + phrase + "\":\n"
    print(title)
    testResults = DataFrame({"Language": Series(language), "Probability": Series(probsArray)})
    testResults = testResults.set_index('Language')
    
    testResults = numpy.log10(testResults)
    testResults = testResults.sort(['Probability'], ascending=False)
    print(testResults)
    
    resultDescription = "\nWe estimate that " + testResults['Probability'].argmax() + " is the sentence's language.\n"
    print(resultDescription)
    
    if writeOutput:
        print("Updating file with results...")
        tempFile = open(outFile, 'a', encoding="utf8")
        tempFile.write(title+'\n')
        tempFile.flush()
        testResults.to_csv(outFile, sep='\t', encoding='utf-8', mode='a')
        tempFile.write(resultDescription+'\n')
        tempFile.flush()
        tempFile.close()

    if plot:
        plt.figure();
        testResults.plot(kind='bar');
        plt.title(title)
        plt.show()

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
#outFile = "./resultados.txt"
#writeOutput = False

def main(argv):
   try:
      opts, args = getopt.getopt(argv,"hd:e:n:t:f:sow:p",["dir=", "dirName=", "ext=", "extention=", "num=", "number=", "test=", "testPhrase=", "testFile=", "writeOutputTo="])
   except getopt.GetoptError:
      print('nGram.py <options>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h', "--help"):
         print('nGram.py <options>\nAnd the options need to be added here...')
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
         # print(testPhrase)
      elif opt in ("-f", "--testFile"):
         global testFile
         testFile = arg
         global fileToTest
         fileToTest = True
      elif opt in ('-s', "--smoothing", "--smooth"):
         global smoothing
         smoothing = True
      elif opt in ('-o', '--output'):
         global writeOutput
         global outFile
         writeOutput = True
         tempFile = open(outFile, 'w', encoding="utf8")
         tempFile.write(str(num) + "-Gram Test Results:\n")
         tempFile.close()
      elif opt in ('-w', '--writeOutputTo'):
         writeOutput = True
         if arg != '':
             outFile = arg
         tempFile = open(outFile, 'w', encoding="utf8")
         tempFile.write(str(num) + "-Gram Test Results:\n")
         tempFile.close()
      elif opt in ('-p', '--plot'):
         global plot
         plot = True

   normalizeFilesInDirectory (num, dirName, ext, normExt);
   createNGramFile (num, dirName, normExt);
   createNGramFile (num-1, dirName, normExt);
   
   #Here do the testing
   if fileToTest :
       tempFile = open(testFile, 'r', encoding="utf8")
       temp = tempFile.read()
       tempFile.close()
       temp = temp.split(';\n')
       for i in temp:
           testSentence(num, i)
   else:
       testSentence(num, testPhrase)

if __name__ == "__main__":
   main(sys.argv[1:])