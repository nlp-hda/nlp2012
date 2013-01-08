'''
Created on 30.12.2012

@author: andreas
'''

import logging

logging.basicConfig(format='%(levelname)s:%(message)s')

class SlidingNGram(object):
    '''
    representing a text by sliding n-grams
    '''

    text = "colorless green ideas sleep furiously"
    ngramSize = 2
    slidingNGrams = []

    def __init__(self,text,size):
        '''
        Constructor: split text into n-grams by n-gram size
        text should be only with white space seperated words
        '''
        self.text = text
        self.ngramSize = size
        words = self.text.split()
        logging.debug(self.text)
        
        for i in range(len(words) - self.ngramSize + 1) :
            ngram = words[i: i + self.ngramSize]
            self.slidingNGrams.append(ngram)
            logging.debug(ngram)