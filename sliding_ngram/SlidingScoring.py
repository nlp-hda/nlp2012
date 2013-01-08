'''
Created on 30.12.2012

@author: andreas
'''

import re
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', 
                    filename='slidingScoring-testChomsky.log',
                    filemode='w', 
                    level=logging.INFO)
delimiter = ";"

from SlidingNGram import SlidingNGram

from DomainIdentification import identifyDomain 

#google
from xgoogle.search import GoogleSearch,SearchError
from time import sleep

searchSleepTime = 0
domains = ["information technology", "medical"]

#synonyms
import nltk
from nltk.corpus import wordnet
import itertools

#see http://nltk.googlecode.com/svn/trunk/doc/book/ch05.html#tab-syntax-verbs
print "init corpus"
#buid corpus tree
wsj = nltk.corpus.treebank.tagged_words(simplify_tags=True)
#build fequency distributions
cfd1 = nltk.ConditionalFreqDist(wsj)

def getSynonyms(word) : #TODO add known part of seech tag :)
    #TODO wortstamm synonyme
    #get word related possible parts of speech    
    possiblePartsOfSpeech = cfd1[word].keys()
    synonyms = [word]
    for partOfSpeech in possiblePartsOfSpeech :
        #reducing Part of Speech Tag to synonym position levels
        #see http://nltk.googlecode.com/svn/trunk/doc/book/ch05.html#tab-simplified-tagset
        #see http://nltk.googlecode.com/svn/trunk/doc/api/nltk.corpus.reader.wordnet.Synset-class.html
        #ignoring difference between ADJ and ADJ_SAT
        #ADJ, ADJ_SAT, ADV, NOUN, VERB = 'a', 's', 'r', 'n', 'v' see class WordNetCorpusReader(CorpusReader)
        partTag = 's'
        if partOfSpeech == "ADJ":
            partTag = 'a'
        elif partOfSpeech == "ADV":
            partTag = 'r'
        elif partOfSpeech == "N" or partOfSpeech == "NP":
            partTag = 'n'
        elif partOfSpeech[0:1] == 'V':
            partTag = 'v'
        else: #ignore other parts of speech, they may be assumed to be without synonym ambiguity
            break
        logging.debug("partTag ('" + word + "'): " + partTag)
        #lookup every synonym, if it is new, add it - corpus: wordnet
        for synset in wordnet.synsets(word, partTag) :#eclipse meldet hier einen Fehler, bitte ignorieren, das muss wirklich so...
            for lemma in synset.lemma_names :
                lemma = lemma.replace("_", " ")
                if lemma not in synonyms : 
                    synonyms.append(lemma)
        logging.debug(synonyms)
    return synonyms

def proximateScoring(phrase):
    score = [0,0] #dummy
    #google it and get first page proximate words -> proximate text
    gs = GoogleSearch("\"" + phrase + "\"")
    gs.results_per_page = 50
    sleep(searchSleepTime)
    proximateText = ""
    try:
        results = gs.get_results()
        logging.info(gs.last_search_url)
        for result in results:
            proximateText += result.desc + " "
        logging.info("proximate text (" + phrase + "):" + proximateText)
        
        #domain identification of the text
        domainScores = identifyDomain(proximateText)
        score = domainScores
        score.append(proximateText)
    except SearchError as se:
        logging.error("Search Error on proximate scoring: " + str(se))
        print "Search Error on proximate scoring: " + str(se)
        score.append(proximateText)
    return score

def augmentedScoring(phrase) :
    #TODO hit count ist nicht ganz korrekt
    #=> more like: about .* results kann ueber die ganze seite gehen...
    #=> investigate regex/google site!
    hitScores = []
    #without domains -> denominator
    searchStr = "\"" + phrase + "\""
    gs = GoogleSearch(searchStr)
    gs.results_per_page = 50
    sleep(searchSleepTime)
    score = 0
    matchStrings = ""
    pageStrings = ""
    try:
        page = gs._get_results_page()
        logging.info(gs.last_search_url)
        pageStr = str(page)
        pageStrings += pageStr
        if pageStr.find("resultStats\">") != -1 or pageStr.find("No results found for") > -1:
            m = re.search(r'resultStats\">.*bout (.*) results</div', pageStr)
            if m is not None:
                score = m.group(1)
                matchStrings += m.group(0) + " - "
                logging.info("score (" + searchStr + "): " + score)
                score = score.replace(',','')
                hitScores.append(int(score))
            else:
                logging.warning("No match! .. no google hits? (" + searchStr + ")")
                hitScores.append(0)
                for _ in domains: hitScores.append(0)
                hitScores.append("first: no match")
                hitScores.append(unicode(pageStrings, 'utf-8', "strict"))
                logging.info(hitScores) 
                return hitScores
        else:
            logging.warning("No google hits! (" + searchStr + ")")
            hitScores.append(0)
            for _ in domains: hitScores.append(0)
            hitScores.append("first: no match")
            hitScores.append(unicode(pageStrings, 'utf-8', "strict"))
            logging.info(hitScores) 
            return hitScores
    except SearchError as se:
        logging.warning("Search Error on: " + searchStr + " no results? " + str(se))
        hitScores.append(0)
        for _ in domains: hitScores.append(0)
        hitScores.append("first: search error: " + str(se))
        hitScores.append(unicode(pageStrings, 'utf-8', "strict"))
        logging.info(hitScores)
        return hitScores
    denominationScore = float(score)
    logging.info("denominator (" + searchStr + "): " + str(denominationScore))
    
    #augmented with domains
    for domain in domains :
        searchStr = "\"" + phrase + "\" \"" + domain + "\""
        gs = GoogleSearch(searchStr)
        gs.results_per_page = 50
        sleep(searchSleepTime)
        score = 0
        try:
            page = gs._get_results_page()
            logging.info(gs.last_search_url)
            pageStr = str(page)
            pageStrings += pageStr
            if pageStr.find("resultStats\">") != -1 :
                m = re.search(r'resultStats">.*bout (.*) results</div', pageStr)
                if m is not None:
                    score = m.group(1)
                    matchStrings += m.group(0) + " - "
                    logging.info("score (" + searchStr + "): " + score)
                    score = score.replace(',','')
                else: logging.warning("No match! .. no google hits? (" + searchStr + ")")
            else: logging.warning("No google hits! (" + searchStr + ")")
        except SearchError as se:
            logging.warning("Search Error on: " + searchStr + " no results? " + str(se))

        #relativating by general hit count
        hitScores.append(float(score) / denominationScore)

    hitScores.append(matchStrings)
    hitScores.append(unicode(pageStrings, 'utf-8', "strict"))
    logging.info(hitScores)
    return hitScores

if __name__ == '__main__':
    text = "colorless green ideas sleep furiously"
    ngramSize = 2
    print "get sliding ngrams"
    slidingNGram = SlidingNGram(text, ngramSize)
    csv = open('slidingNGram.csv', 'w')
    csv.write('ngram' + delimiter + 'syn' + delimiter + 'ngramScore' + delimiter + 'result count' + delimiter + 'proxScoreIT' + delimiter + 'proxScoreMed' + delimiter + 'augScoreIT' + delimiter + 'augScoreMed' + delimiter + 'augMatchStrings' + delimiter + 'proxText\n')
    for ngram in slidingNGram.slidingNGrams :
        ngramStr = " ".join(ngram)
        print "get synonym ngrams for: " + ngramStr  
        #(0) get synonyms
        synonyms = []
        for word in ngram : 
            synonyms.append(getSynonyms(word))
        synonymNGrams = list(itertools.product(*synonyms))
        logging.info(synonymNGrams)
        
        print "score all " + str(len(synonymNGrams)) + " synNGrams for: " + ngramStr
        line = ngramStr + delimiter
        ngramViewerSearchStr = ""
        for synNGram in synonymNGrams :
            phrase = " ".join(synNGram)
            ngramViewerSearchStr += phrase + delimiter
        ngramViewerSearchStr = ngramViewerSearchStr[: - len(delimiter)]
        #TODO (3) NGramViewer scoring
        for synNGram in synonymNGrams :
            phrase = " ".join(synNGram)
            synLine = line + phrase + delimiter
            logging.info(phrase)
            #(1) proximate scoring
            proximateScore = proximateScoring(phrase)
            #(2) augmented scoring
            augmentedScores = augmentedScoring(phrase)
            #write content
            #TODO add ngram Score instead of 0
            synLine += "0" + delimiter + str(augmentedScores[0]) + delimiter
            synLine += str(proximateScore[0]).replace('.', ',') + delimiter + str(proximateScore[1]).replace('.', ',') + delimiter
            synLine += str(augmentedScores[1]).replace('.', ',') + delimiter + str(augmentedScores[2]).replace('.', ',') + delimiter
            synLine += augmentedScores[3].replace("\"", "\"\"") + delimiter + "\"" + proximateScore[2].replace("\"", "\"\"") + "\"" + "\n"
            csv.write(synLine.encode('ascii', 'ignore'))#ignoring special web characters
    csv.close()
    pass
