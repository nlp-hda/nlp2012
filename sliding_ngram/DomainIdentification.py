'''
Created on 02.01.2013

@author: andreas

from domain identification group's code
'''

import logging

logging.basicConfig(format='%(levelname)s:%(message)s')

from tagging import Category,MyTokenizer,MyBlackList,ReadInput,WordCounter

#needs to be in the same order and logical meaning as in SlidingScoring!
#values cannot be changed due to they are file dependent...
domains = ["IT", "MEDICAL"]

def readDBTags(domain):
    logging.info("Reading DB Tags file ...... ")
    domainTags = open('tags_' + domain + '.txt')
    lines = domainTags.readlines()

    categoryList = []
    for line in lines:
        categorySplit = line.split(';')
        category = Category(categorySplit[0])
        category.setCategoryItems(categorySplit)
        categoryList.append(category)
    return categoryList

def identifyDomain(text):
    myToken = MyTokenizer(text)    
    token_word = myToken.getWordToken()
    #token_sentences = myToken.getSentenceToken()
    #for sentence in token_sentences: print sentence
    myBlacklist = MyBlackList('Blacklist_UTF8.txt',token_word)
    tokenAfterBlacklist = myBlacklist.getBlacklist()
    wordCounter = WordCounter(tokenAfterBlacklist)
    totalWords = 0
    dictionary = wordCounter.getWordCount()
    for word in dictionary:
        totalWords += dictionary[word]
    #    pair = word + ',' + str(dictionary[word])
    #    print pair
    
    scores = []
    for domain in domains:
        categoryList = readDBTags(domain)
        counts = 0
        for tag in categoryList:        
            for entry in tag.getCategoryItemList():
                if entry.upper() in tokenAfterBlacklist:
                    logging.info("entry of " + domain + " found: " + entry)
                    counts += 1
                #else: print entry
        prob = float(counts) / totalWords
        scores.append(prob)
        logging.info("count(" + domain + ")\t= " + str(counts) + " => " + str(prob))
        #print "count(" + domain + ")\t= " + str(counts) + " => " + str(prob)
        
    return scores

if __name__ == '__main__':
    #test script
    #inputText = ReadInput('texteA_M.txt')
    inputText = ReadInput('it.txt')
    identifyDomain(inputText.getText())