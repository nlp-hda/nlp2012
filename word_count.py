#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib2
import tempfile
import tokenize
import HTMLParser

# Sample URLs with text
'http://archive.org/stream/Dissertation.Der_Mensch_und_die_KI/Mensch_und_KI_djvu.txt'
'http://archive.org/stream/illinoisappellat2120illi/illinoisappellat2120illi_djvu.txt'


class MyHtmlParser(HTMLParser.HTMLParser):
	""" Simple HTML parser that extracts text from the given data """
	
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self) # must be like this, due to old class style of HTMLParser!
		self.text = list()
		self.cur = ''

	def handle_starttag(self, tag, attrs):
		self.cur = ''

	def handle_endtag(self, tag):
		# Calling strip() is IMPORTANT, otherwise: IndentationError: unindent does not match any outer indentation level
		self.text.append(self.cur.strip())

	def handle_data(self, data):
		self.cur += data


def readFromUrl(url):
	""" Read text from the given URL """
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	return opener.open(url).read()


def countWordFrequency(wordList):
	""" Returns a lower case dictionary with words as keys and integers as values, representing their occurence in the given text """
	words = dict()
	for w in wordList:
		word = w.lower() # convert to lower case
		if words.has_key(word):
			words[word] += 1
		else:
			words[word] = 1
	return words


__blacklist__ = ['after', 'about', 'between', 'but', 'only', 'been', 'both', 'did', "n't", "it's", "'s", 's', 'its', 'may', 'no', 'yes', 'not', 'have', 'has', 'all', 'also', 'so', 'other', 'from', 'can', 'it', 'an', 'into', 'by', 'with', 'had', 'such', 'be', 'on', 'are', 'my', 'new', 'at', 'that', 'for', 'as', 'or', 'in', 'is', 'he', 'she', 'and', 'to', 'of', 'a', 'his', 'how', 'the', 'do', 'much', 'most', 'could', 'now', 'ca', 'we', 'well', 'were', 'when', 'which', 'who', 'what', 'will', 'would', 'you', 'your', 'than', 'their', 'there', 'these', 'they', 'this', 'those', 'through', 'me', 'more', 'became', 'because', 'see', 'very', 'use', 'was', 'year', 'many', 'used', 'first']


def filterCommonWords(words):
	""" Filter common words - compare lower case! """
	return filter(lambda w: w.lower() not in __blacklist__, words)


def filterSmallWords(words):
	""" Filter small (non-relevant) words """
	return filter(lambda w: len(w) > 3, words)
	

def tokenizeIt(data):
	""" Extracts words from the given input file handle's readline method """
	words = list()

	def collectWords(tokenType, token, c, d, sentence):
		if tokenType == 1:
			words.append(token)

	# Since content must be read from a file handle (see tokenize module), the data is stored in a tmp file
	f = tempfile.TemporaryFile(mode='w+r')	
	f.write(data)

	# Reset file position for reading...
	f.seek(0)

	# IMPORTANT, otherwise: raise TokenError, ("EOF in multi-line statement", (lnum, 0))
	try:
		tokenize.tokenize(f.readline, collectWords)
	except tokenize.TokenError:
		pass # ignore errors and continue

	f.close()

	return words


def getTopWords(wordDict, n):
	""" Return 'n' words with the highest frequency in the text """
	def compareCount(a, b):
		if wordDict[a] < wordDict[b]:
			return -1
		elif wordDict[a] > wordDict[b]:
			return 1
		elif wordDict[a] == wordDict[b]:
			return 0

	return sorted(wordDict, cmp=compareCount, reverse=True)[:n]	


def main():
	""" Start program with configuration """

	if len(sys.argv) < 2:
		print 'USAGE: word_count.py <URL>'
		sys.exit(0)

	urlsFile = sys.argv[1]
	f = open(urlsFile, 'r')
	urls = f.readlines()
	f.close()

	results = list()

	maxTopWords = 30

	for url in urls:

		print 'Read ' + url + ' and parse HTML...'

		parser = MyHtmlParser()

		parser.feed(readFromUrl(url))

		# Convert from list-of-strings to string
		print 'Tokenize...'

		tmp = countWordFrequency(filterCommonWords(filterSmallWords(tokenizeIt(''.join(parser.text)))))

		results.extend(getTopWords(tmp, maxTopWords))

		print getTopWords(tmp, 10)

	#
	#
	# Dictionaries zusammen mergen und nicht in Liste speichern!!!
	#
	#


	#print results

	#print countWordFrequency(results)

	print getTopWords(countWordFrequency(results), maxTopWords)

	#uniqueResults = sorted(list(set(map(lambda w: w.lower(), results))))

	#f = open('results.txt', 'w')
	#f.write(' '.join(uniqueResults))
	#f.close()
	
	#print uniqueResults


# start script
if __name__ == "__main__":
    main()
