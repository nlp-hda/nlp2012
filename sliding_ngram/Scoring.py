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
import urllib
from sliding_ngram.xgoogle.browser import Browser,BrowserError 
from sliding_ngram.xgoogle.search import GoogleSearch,SearchError
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

def getSynonyms(word) : #TODO: add known part of seech tag :)
    #TODO: wortstamm synonyme
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
                if lemma not in synonyms and len(synonyms) < 5:# skip more then 5 to reduce complexity 
                    synonyms.append(lemma)
        logging.debug(synonyms)
    return synonyms

def googleNGramViewerScores(query):
    #English: One Million Books, 
    url = "http://books.google.com/ngrams/graph?content=" + urllib.quote_plus(query) + "&year_start=1800&year_end=2008&corpus=1&smoothing=5"
    browser = Browser(debug=False)
    results = []
    for i in range(query.count(',')):
        results.append(0)
    try:
        page = browser.get_page(url)
        #[2008, 1.0942705075400738e-09, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        regex = re.compile(".*\[2008(.*)\].*")
        r = regex.search(str(page))
        if r is not None:
            logging.info("ngram result on (" + query + "): " + r.group(1))
            resultString = r.group(1)
            resultString = resultString[2:-1]
            results = resultString.split(', ')
    except BrowserError, e:
        logging.error("Failed getting %s: %s" % (e.url, e.error))
    return results

def hitScore(phrase):
    hitScore = 0
    gs = GoogleSearch("\"" + phrase + "\"")
    gs.results_per_page = 50
    matchStrings = ""
    try:
        page = gs._get_results_page()
        logging.info(gs.last_search_url)
        pageStr = str(page)
        if pageStr.find("resultStats\">") != -1 and pageStr.find("No results found for") == -1:
            m = re.search(r'resultStats\">.*bout (.*) results</div', pageStr)
            if m is not None:
                score = m.group(1)
                matchStrings += m.group(0) + " - "
                logging.info("score (" + phrase + "): " + score)
                score = score.replace(',','')
                hitScore = int(score)
            else:
                logging.warning("No match! .. no google hits? (" + phrase + ")")
        else:
            logging.warning("No google hits! (" + phrase + ")")
    except SearchError as se:
        logging.warning("Search Error on: " + phrase + " no results? " + str(se))
    return hitScore
    
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
        if pageStr.find("resultStats\">") != -1 and pageStr.find("No results found for") == -1:
            m = re.search(r'resultStats\">.*bout (.*) results</div', pageStr)
            if m is not None:
                score = m.group(1)
                matchStrings += m.group(0) + " - "
                logging.info("score (" + searchStr + "): " + score)
                score = score.replace(',','')
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
    hitScores.append(denominationScore)
    
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
                    #matchStrings += m.group(0) + " - "
                    logging.info("score (" + searchStr + "): " + score)
                    score = score.replace(',','')
                else: logging.warning("No match! .. no google hits? (" + searchStr + ")")
            else: logging.warning("No google hits! (" + searchStr + ")")
        except SearchError as se:
            logging.warning("Search Error on: " + searchStr + " no results? " + str(se))

        #relativating by general hit count
        #hitScores.append(float(score) / denominationScore)
        hitScores.append(float(score))

    #hitScores.append(matchStrings)
    #hitScores.append(unicode(pageStrings, 'utf-8', "strict"))
    logging.info(hitScores)
    return hitScores

#from: http://stackoverflow.com/questions/1883980/find-the-nth-occurrence-of-substring-in-a-string
def findnth(haystack, needle, n):
    parts= haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)

if __name__ == '__main__':
    #text = "colorless green ideas sleep furiously"
#    text = "he has a large heart"
    texts = [#IT
             #"not because it has a big heart but these phones",
             #"brilliant man with a large heart Steve Jobs passed",
             #"Cordy is a little blue robot with a large heart and an even larger",
             #"It features a big heart that rotates and changes",
             ##Medical
             #"a person with a large heart can suddenly die",
             #"medicine as for his large heart unique compassion",
             #"frail frame but her big heart and wide smile have the ability",
             #"A big heart may be hazardous to one's health",
             ##general
             #"loving with a large heart for the poor",
             #"when we have a big heart We are never"
#             "a big heart but",
#             "a large heart Steve",
#             "a large heart and",
#             "a big heart that",
             #Medical
#             "a large heart can",
             "his large heart unique",
#             "her big heart and",
#             "A big heart may",
             #general
#             "a large heart for",
#             "a big heart We"
             ]
    
    csv = open('slidingNGram.csv', 'w')
    for text in texts:
        ngramSize = 2
        print "get sliding ngrams"
        unigram = SlidingNGram(text, 1)
        slidingNGram = SlidingNGram(text, ngramSize)
        #csv.write('ngram' + delimiter + 'syn' + delimiter + 'ngramScore' + delimiter + 'result count' + delimiter + 'proxScoreIT' + delimiter + 'proxScoreMed' + delimiter + 'augScoreIT' + delimiter + 'augScoreMed' + delimiter + 'augMatchStrings' + delimiter + 'proxText\n')
        csv.write(text + '\n')
        
        ngramPos = -1
        for ngram in slidingNGram.slidingNGrams :
            ngramPos = ngramPos + 1
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
                ngramViewerSearchStr += phrase + ','
            ngramViewerSearchStr = ngramViewerSearchStr[: - len(delimiter)]
            #max. query size: 240
            maxNGramViewerQuerySize = 150
            maxQeurysAtOneTime = 12
            ngramViewerSearches = len(ngramViewerSearchStr) / maxNGramViewerQuerySize + 1
            ngramScores = []
            startPos = 0
            i = 0
            while startPos <= len(ngramViewerSearchStr) :
                maxRange = (i + 1) * maxNGramViewerQuerySize
                i = i + 1
                if maxRange > len(ngramViewerSearchStr) :
                    maxRange = len(ngramViewerSearchStr)
                endPos = startPos + ngramViewerSearchStr[startPos:maxRange].rfind(',') #(len(ngramViewerSearchStr[startPos:maxRange]) - 1) - ngramViewerSearchStr[startPos:maxRange][::-1].index(',')#ngramViewerSearchStr.find(',', startPos, maxRange) 
                if endPos == -1 or maxRange == len(ngramViewerSearchStr) : endPos = maxRange
                queryCountsInRage = ngramViewerSearchStr[startPos : endPos].count(',')
                if queryCountsInRage >= maxQeurysAtOneTime : 
                    endPos = startPos + findnth(ngramViewerSearchStr[startPos : endPos], ',', maxQeurysAtOneTime - 1)
                ngramQuery = ngramViewerSearchStr[startPos : endPos]
                ngramResults = googleNGramViewerScores(ngramQuery)
                startPos = endPos + 1
                for score in ngramResults : 
                    ngramScores.append(float(score))
            ngramCounter = 0
            logging.info(str(len(ngramScores)) + " <-> " + str(len (synonymNGrams)))
            if len(ngramScores) != len (synonymNGrams) : 
                logging.error("Not enough ngrams passed through ngram viewer!")
                print "Not enough ngrams passed through ngram viewer!"
                print str(len(ngramScores)) + " <-> " + str(len (synonymNGrams))
            
            augDomainPhraseScores = []
            for d in domains : augDomainPhraseScores.append([])
            augGoodPhrases = []
            augPhraseDeonominators = []
            denominatorScoreSum = 0
            csv.write('ngram' + delimiter + 'syn' + delimiter + 'ngramScore' + delimiter + 'result count' + delimiter + 'prioriTrigram'  + delimiter + 'priori count' + delimiter + 'posterioriTrigram' + delimiter + 'posteriori count' + delimiter + 'augScoreIT' + delimiter + 'augScoreMed\n')
            for synNGram in synonymNGrams :
                phrase = " ".join(synNGram)
                synLine = line + phrase + delimiter
                logging.info(phrase)
                
                #(0) check ngram score
                ngramViewerScore = ngramScores[ngramCounter]
                logging.info("ngramViewerScore:"+str(ngramViewerScore))
                ngramCounter = ngramCounter + 1
                #if ngramCounter > 10 : break
                synLine += ('%.15f' % ngramViewerScore).replace('.', ',') + delimiter
                if ngramViewerScore != 0.0 :
                    #Test Trigrams
                    hitScoreSum = 0
                    hitsPriori = 0
                    strPriori = ""
                    if ngramPos > 0 : 
                        prioriTrigram = " ".join(unigram.slidingNGrams[ngramPos - 1]) + " " + phrase
                        hitScoreSum += hitScore(prioriTrigram)
                        hitsPriori = hitScoreSum
                        strPriori = prioriTrigram 

                    hitsPosteri = 0
                    strPosteri = ""
                    if ngramPos < len(unigram.slidingNGrams) - ngramSize : 
                        posteroriTrgram = phrase + " " + " ".join(unigram.slidingNGrams[ngramPos - ngramSize])
                        hitScoreSum += hitScore(posteroriTrgram)
                        hitsPosteri = hitScoreSum - hitsPriori
                        strPosteri = posteroriTrgram
                    
                    logging.info("priori:"+str(hitsPriori) + " posteriori:"+str(hitsPosteri))
                    
                    #if too few results for 3gram -> discard
                    if hitScoreSum < 1000 : continue
                    
                    #(1) proximate scoring
                    #proximateScore = proximateScoring(phrase)
                    #(2) augmented scoring
                    
                    #TODO: check  augmented Trigram instead
                    augmentedScores = augmentedScoring(phrase)
                    denominator = augmentedScores[0]
                    denominatorScoreSum += denominator
                    synLine += str(denominator) + delimiter + strPriori + delimiter + str(hitsPriori) + delimiter + strPosteri + delimiter + str(hitsPosteri) + delimiter
                    #evaluation of survived aug scores
                    domainCnt = 0
                    for domain in domains :
                        augDomainPhraseScores[domainCnt].append(augmentedScores[domainCnt + 1])
                        if domainCnt == 0 : augGoodPhrases.append(phrase)
                        if domainCnt == 0 : augPhraseDeonominators.append(denominator)
                        synLine += str(augmentedScores[domainCnt + 1]) + delimiter
                        domainCnt = domainCnt + 1
                synLine += '\n'
                csv.write(synLine.encode('ascii', 'ignore'))#ignoring special web characters 
            csv.write(synLine.encode('ascii', 'ignore'))#ignoring special web characters
            csvLine = '\n'+"Given a phrase, which is in general more likely?" + '\n'
            csvLine += "syn ngram" + delimiter + "general"+'\n'
            phraseCnt = 0
            for goodPhrase in augGoodPhrases :
                score = augPhraseDeonominators[phraseCnt] / denominatorScoreSum
                csvLine += goodPhrase + delimiter + str(score).replace('.', ',') + '\n'
                phraseCnt = phraseCnt + 1
            
            csvLine += '\n'+"Given a phrase, which domain is more likely?" + '\n'
            csvLine += "domain/phrase (given)" + delimiter
            domainCnt = 0
            augDomainPhraseCumulativeScores = []
            augDomainDenominator = [0] * len(augGoodPhrases)
            sumCumulativeScores = [0] * len(domains)
            for domain in domains :
                augDomainPhraseCumulativeScores.append([])
                phraseCnt = 0
                for phrase in augGoodPhrases :
                    cumulativeScore = augDomainPhraseScores[domainCnt][phraseCnt] * augPhraseDeonominators[phraseCnt]
                    sumCumulativeScores[domainCnt] += cumulativeScore
                    augDomainPhraseCumulativeScores[domainCnt].append(cumulativeScore)
                    augDomainDenominator[phraseCnt] += cumulativeScore
                    if domainCnt == 0 : csvLine += phrase + delimiter
                    phraseCnt = phraseCnt + 1 
                domainCnt = domainCnt + 1
            
            csvLine += '\n'
            domainCnt = 0
            augScores = []
            for domain in domains :
                augScores.append([])
                phraseCnt = 0
                csvLine += domain + delimiter
                for phrase in augGoodPhrases :
                    score = augDomainPhraseCumulativeScores[domainCnt][phraseCnt] / augDomainDenominator[phraseCnt]
                    augScores.append(score)
                    phraseCnt = phraseCnt + 1
                    csvLine += str(score).replace('.', ',') + delimiter
                domainCnt = domainCnt + 1
                csvLine += '\n'
                
            csvLine += '\n' + "Given a domain, which phrase is more likely?" + '\n'
            csvLine += "phrase/domain (given)" + delimiter
            for domain in domains : 
                csvLine += domain + delimiter
            csvLine += '\n'
            phraseCnt = 0
            for phrase in augGoodPhrases :
                csvLine += phrase + delimiter
                domainCnt = 0
                for domain in domains :
                    score = augDomainPhraseCumulativeScores[domainCnt][phraseCnt] / sumCumulativeScores[domainCnt]
                    domainCnt = domainCnt + 1
                    csvLine += str(score).replace('.', ',') + delimiter
                phraseCnt = phraseCnt + 1
                csvLine += "\n"
            #write content end
            csvLine += "\n"
            csv.write(csvLine.encode('ascii', 'ignore'))#ignoring special web characters
    csv.close()
    print "done."
    pass
