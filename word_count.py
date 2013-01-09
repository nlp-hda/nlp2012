#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Author: Tobias Daub """

import sys
import copy
import urllib2
import tempfile
import tokenize
import HTMLParser

# Sample URLs with ASCII text - at the moment there's a problem when parsing non-ASCII content
'http://archive.org/stream/Dissertation.Der_Mensch_und_die_KI/Mensch_und_KI_djvu.txt'
'http://archive.org/stream/illinoisappellat2120illi/illinoisappellat2120illi_djvu.txt'

#
# NOTE: Verbs, adjectives and adverbs lists were taken from http://www.linguanaut.com/verbs.htm
#

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


__blacklist__ = ["'s", 'a', 'able', 'about', 'accept', 'accidentally', 'account', 'achieve', 'acidic', 'act', 'add', 'admire', 'admit', 'adorable', 'adventurous', 'affect', 'afford', 'afraid', 'after', 'afterwards', 'aggressive', 'agree', 'agreeable', 'aim', 'alert', 'alive', 'all', 'allow', 'almost', 'also', 'always', 'amazing', 'amused', 'amusing', 'an', 'ancient', 'and', 'angrily', 'annually', 'answer', 'anxiously', 'appear', 'apply', 'approve', 'are', 'argue', 'arrange', 'arrive', 'as', 'ashamed', 'ask', 'at', 'attack', 'attractive', 'average', 'avoid', 'awesome', 'awful', 'awkwardly', 'bad', 'badly', 'base', 'be', 'beat', 'beautiful', 'became', 'because', 'become', 'been', 'begin', 'believe', 'belong', 'beneficial', 'best', 'better', 'between', 'big', 'bite-sized', 'bitter', 'black', 'black-and-white', 'blindly', 'blushing', 'boiling', 'boldly', 'both', 'bouncy', 'brave', 'bravely', 'break', 'breakable', 'brief', 'briefly', 'bright', 'brightly', 'broken', 'brown', 'build', 'bumpy', 'burn', 'bustling', 'busy', 'but', 'buy', 'by', 'ca', 'calculating', 'call', 'calm', 'calmly', 'can', 'care', 'careful', 'carefully', 'careless', 'carelessly', 'caring', 'carry', 'catch', 'cause', 'cautiously', 'change', 'charge', 'charming', 'cheap', 'check', 'cheerful', 'cheerfully', 'choose', 'chubby', 'claim', 'clean', 'clear', 'clearly', 'climb', 'close', 'closed', 'cloudy', 'clumsy', 'cluttered', 'cold', 'collect', 'colorful', 'come', 'comfortable', 'commit', 'compare', 'complain', 'complete', 'concern', 'concerned', 'confirm', 'connect', 'consider', 'consist', 'contact', 'contain', 'continue', 'contribute', 'control', 'cook', 'cool', 'cooperative', 'coordinated', 'copy', 'correct', 'correctly', 'cost', 'could', 'count', 'courageous', 'courageously', 'cover', 'crazy', 'create', 'creepy', 'crooked', 'cross', 'crowded', 'cruelly', 'cry', 'cuddly', 'cumbersome', 'curly', 'curvy', 'cut', 'cute', 'daily', 'damage', 'damaged', 'dance', 'dangerous', 'dark', 'dazzling', 'dead', 'deal', 'decide', 'deep', 'defiant', 'defiantly', 'deliberately', 'delicious', 'delightful', 'delirious', 'deliver', 'demand', 'deny', 'depend', 'describe', 'descriptive', 'deserted', 'design', 'destroy', 'develop', 'did', 'die', 'different', 'difficult', 'dirty', 'disappear', 'disastrous', 'discover', 'discuss', 'disgusting', 'distinct', 'divide', 'dizzy', 'do', 'doubtfully', 'drab', 'draw', 'dress', 'drink', 'drive', 'drop', 'dry', 'dull', 'during', 'eager', 'early', 'easily', 'easy', 'eat', 'elated', 'elderly', 'elegant', 'elegantly', 'embarrassed', 'empty', 'enable', 'enchanted', 'enchanting', 'encourage', 'energetic', 'enjoy', 'enormously', 'enthusiastically', 'envious', 'equal', 'equally', 'even', 'eventually', 'evil', 'exactly', 'examine', 'excellent', 'excited', 'exciting', 'exist', 'expect', 'expensive', 'experience', 'explain', 'express', 'extend', 'extra-large', 'extra-small', 'face', 'fail', 'fair', 'faithfully', 'fall', 'familiar', 'famous', 'fancy', 'far', 'far-flung', 'fast', 'fasten', 'fat', 'fatally', 'fearful', 'fearless', 'feed', 'feel', 'fiercely', 'fight', 'fill', 'filthy', 'find', 'fine', 'finish', 'first', 'fit', 'flaky', 'flat', 'flimsy', 'fluffy', 'fly', 'fold', 'follow', 'foolish', 'foolishly', 'for', 'force', 'forget', 'forgive', 'form', 'fortunately', 'found', 'frail', 'frantically', 'free', 'fresh', 'friendly', 'frightened', 'frightening', 'from', 'full', 'fumbling', 'funny', 'fuzzy', 'gain', 'gently', 'get', 'giant', 'gifted', 'gigantic', 'give', 'gladly', 'glamorous', 'gleaming', 'glistening', 'glorious', 'go', 'good', 'gorgeous', 'graceful', 'gracefully', 'grateful', 'gray', 'great', 'greedily', 'greedy', 'green', 'grotesque', 'grow', 'gruesome', 'grumpy', 'gullible', 'had', 'handle', 'handy', 'happen', 'happily', 'happy', 'hard', 'hard-to-find', 'has', 'hastily', 'hate', 'hateful', 'have', 'he', 'head', 'healthy', 'hear', 'heavenly', 'heavy', 'help', 'helpful', 'helpless', 'hide', 'hideous', 'high', 'his', 'hit', 'hold', 'homely', 'honestly', 'hope', 'horrible', 'hot', 'hourly', 'how', 'however', 'hungrily', 'hungry', 'hurt', 'husky', 'icky', 'icy', 'identify', 'ignorant', 'ill-fated', 'ill-informed', 'imagine', 'impolite', 'important', 'improve', 'in', 'include', 'increase', 'incredible', 'indicate', 'infamous', 'influence', 'inform', 'innocently', 'inquisitively', 'insidious', 'intelligent', 'intend', 'interesting', 'into', 'introduce', 'invite', 'involve', 'irritably', 'irritating', 'is', 'it', "it's", 'itchy', 'its', 'jealous', 'jittery', 'join', 'jolly', 'joyous', 'joyously', 'juicy', 'jump', 'jumpy', 'justly', 'keen', 'keep', 'kick', 'kill', 'kind', 'kindly', 'knock', 'know', 'lame', 'large', 'last', 'late', 'laugh', 'lay', 'lazily', 'lazy', 'lead', 'lean', 'learn', 'leave', 'lend', 'less', 'let', 'lie', 'light', 'like', 'limit', 'limping', 'link', 'listen', 'little', 'live', 'long', 'long-term', 'look', 'loose', 'loosely', 'lose', 'loud', 'loudly', 'love', 'lovely', 'loving', 'low', 'lucky', 'lumpy', 'made', 'madly', 'magnificent', 'make', 'mammoth', 'manage', 'many', 'mark', 'marvelous', 'massive', 'matter', 'may', 'me', 'mean', 'measure', 'meaty', 'meek', 'meet', 'mellow', 'melodic', 'mention', 'messy', 'might', 'milky', 'mind', 'miniature', 'miss', 'misty', 'modern', 'monthly', 'more', 'mortally', 'most', 'motionless', 'mountainous', 'move', 'much', 'muddy', 'mundane', 'murky', 'mushy', 'must', 'my', 'mysterious', 'mysteriously', "n't", 'narrow', 'natural', 'naughty', 'near', 'nearly', 'neat', 'neatly', 'need', 'nervously', 'never', 'new', 'next', 'nice', 'nimble', 'nippy', 'no', 'noisily', 'noisy', 'normal', 'not', 'notice', 'now', 'nutritious', 'nutty', 'obedient', 'obediently', 'obese', 'obtain', 'occur', 'odd', 'of', 'offer', 'often', 'old', 'old-fashioned', 'on', 'only', 'open', 'or', 'orange', 'order', 'ordinary', 'other', 'ought', 'outgoing', 'outrageous', 'outstanding', 'own', 'painfully', 'pale', 'paltry', 'pass', 'pay', 'perfect', 'perfectly', 'perform', 'pick', 'place', 'plain', 'plan', 'plastic', 'play', 'pleasant', 'point', 'poised', 'polite', 'politely', 'poor', 'poorly', 'powerful', 'powerfully', 'precious', 'prefer', 'prepare', 'present', 'press', 'pretty', 'prevent', 'previous', 'pricey', 'prickly', 'produce', 'promise', 'promptly', 'protect', 'proud', 'prove', 'provide', 'publish', 'pull', 'punctually', 'puny', 'purple', 'push', 'pushy', 'put', 'puzzled', 'puzzling', 'quaint', 'quick', 'quickly', 'quiet', 'quietly', 'quirky', 'raise', 'rapid', 'rapidly', 'rare', 'rarely', 'reach', 'read', 'real', 'realize', 'really', 'receive', 'recklessly', 'recognize', 'record', 'red', 'reduce', 'refer', 'reflect', 'refuse', 'regard', 'regularly', 'relate', 'release', 'reluctantly', 'remain', 'remarkable', 'remember', 'remove', 'repeat', 'repeatedly', 'replace', 'reply', 'report', 'represent', 'require', 'rest', 'result', 'return', 'reveal', 'rich', 'right', 'rightfully', 'rigid', 'ring', 'ripe', 'rise', 'roasted', 'robust', 'roll', 'rotten', 'rough', 'roughly', 'round', 'rude', 'rudely', 'run', 's', 'sad', 'sadly', 'safe', 'safely', 'save', 'say', 'scared', 'scary', 'scrawny', 'second', 'second-hand', 'see', 'seem', 'seldom', 'selfish', 'selfishly', 'sell', 'send', 'separate', 'serious', 'seriously', 'serve', 'set', 'settle', 'shake', 'shaky', 'shall', 'share', 'sharp', 'sharply', 'she', 'shiny', 'shoot', 'short', 'should', 'shout', 'show', 'shrill', 'shut', 'shy', 'shyly', 'sick', 'silent', 'silently', 'silky', 'silly', 'simple', 'simplistic', 'sing', 'sit', 'skinny', 'sleep', 'sleepy', 'slim', 'slimy', 'slippery', 'slow', 'slowly', 'small', 'smart', 'smile', 'smoggy', 'smooth', 'smoothly', 'so', 'soft', 'softly', 'solemnly', 'solid', 'some', 'sometimes', 'soon', 'sophisticated', 'sore', 'sort', 'sound', 'sour', 'sparkling', 'speak', 'speedily', 'spicy', 'spiffy', 'spiteful', 'spotless', 'spotted', 'square', 'stale', 'stand', 'start', 'state', 'stay', 'stealthily', 'steep', 'sternly', 'stick', 'sticky', 'stingy', 'stop', 'stormy', 'straight', 'strange', 'striped', 'strong', 'study', 'stupendous', 'stupid', 'sturdy', 'substantial', 'succeed', 'successfully', 'such', 'suddenly', 'suffer', 'suggest', 'suit', 'super', 'superb', 'superficial', 'supply', 'support', 'suppose', 'survive', 'suspiciously', 'sweet', 'swiftly', 'take', 'talk', 'tall', 'tame', 'tan', 'tart', 'tasty', 'teach', 'tedious', 'tell', 'tend', 'tender', 'tenderly', 'tense', 'tensely', 'terrific', 'test', 'testy', 'than', 'thank', 'thankful', 'that', 'the', 'their', 'there', 'these', 'they', 'thin', 'think', 'third', 'thirsty', 'this', 'those', 'thoughtful', 'thoughtfully', 'through', 'throw', 'tidy', 'tight', 'tightly', 'tiny', 'tired', 'to', 'tomorrow', 'too', 'touch', 'tough', 'train', 'travel', 'treat', 'tremendous', 'tricky', 'troubled', 'truthful', 'truthfully', 'try', 'turn', 'ugly', 'understand', 'unequal', 'uneven', 'unexpectedly', 'unhealthy', 'unique', 'unkempt', 'unknown', 'unnatural', 'unruly', 'unsightly', 'untidy', 'unused', 'unusual', 'unwieldy', 'unwritten', 'upset', 'use', 'used', 'used to', 'useful', 'useless', 'valuable', 'vast', 'very', 'victorious', 'victoriously', 'violently', 'violet', 'visit', 'vivacious', 'vote', 'wait', 'walk', 'want', 'warm', 'warmly', 'warn', 'was', 'wash', 'watch', 'watery', 'we', 'weak', 'weakly', 'wealthy', 'wear', 'weary', 'well', 'well-groomed', 'well-made', 'well-off', 'well-to-do', 'were', 'wet', 'what', 'when', 'which', 'white', 'who', 'whole', 'wicked', 'wide', 'wide-eyed', 'wiggly', 'wild', 'wildly', 'will', 'win', 'windy', 'wish', 'with', 'witty', 'wonder', 'wonderful', 'wooden', 'work', 'worried', 'worry', 'would', 'write', 'wrong', 'year', 'yearly', 'yellow', 'yes', 'yesterday', 'you', 'young', 'your', 'yummy', 'zany', 'zealous', 'zesty']


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
	""" Return a sorted list with the 'n' highest frequend words from the given dictionary """
	def compareCount(a, b):
		if wordDict[a] < wordDict[b]:
			return -1
		elif wordDict[a] > wordDict[b]:
			return 1
		elif wordDict[a] == wordDict[b]:
			return 0

	return sorted(wordDict, cmp=compareCount, reverse=True)[:n]	


def mergeWordCountDictionaries(a, b):
	""" Merge the two dictionaries, add the counters and return a new dictionary containing all the words """
	aCopy = copy.deepcopy(a)
	for word in b.keys():
		if aCopy.has_key(word):
			aCopy[word] += b[word]
		else:
			aCopy[word] = b[word]
	return aCopy


def readUrls(urlsFile):
	""" Reads the URL file and does some error checking... """
	f = open(urlsFile, 'r')
	urls = map(lambda url: url.replace('\n', ''), filter(lambda line: (line != '') and (line.find('http://') != -1), f.readlines()))
	f.close()
	return urls


def main():
	""" Start program with configuration """

	if len(sys.argv) < 2:
		print 'USAGE: word_count.py <URL>'
		sys.exit(0)

	maxTopWords = 30

	urls = readUrls(sys.argv[1])

	def collectWordFrequenciesFromUrls(): # Closure

		wordFrequencies = dict()

		for i in range(len(urls)):

			url = urls[i]

			print i+1, 'Read', url, 'and collect words...'

			# Because the parser holds a state, initialize a new parser for each URL
			parser = MyHtmlParser()

			parser.feed(readFromUrl(url))

			curWordFrequencies = countWordFrequency(filterCommonWords(filterSmallWords(tokenizeIt(''.join(parser.text)))))

			wordFrequencies = mergeWordCountDictionaries(wordFrequencies, curWordFrequencies)

		return wordFrequencies

	print getTopWords(collectWordFrequenciesFromUrls(), maxTopWords)


# start script
if __name__ == "__main__":
    main()
