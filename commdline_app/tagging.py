
import string
import re
import codecs

from nltk.tokenize import wordpunct_tokenize
from nltk.tokenize import TreebankWordTokenizer
from nltk.probability import FreqDist
import nltk.data

import Tkinter
from Tkinter import *
from tk_app import App


class Category:
	def __init__(self,str):
		self.name = str

	def setCategoryItems(self,itemList):
		self.itemList = itemList

	def getCategoryName(self):
		return self.name

	def getCategoryItemList(self):
		return self.itemList

class Text:
	name = ""
	text = []

	def __init__(self,str):
		Text.name = str

	def setText(self,text):
		Text.text = text

	def getText(self):
		return Text.text

class MyTokenizer:
	def __init__(self,inputText):
		self.inputText = inputText

	def getWordToken(self):
		token = TreebankWordTokenizer()
		token_word = wordpunct_tokenize(self.inputText)
		return token_word

	def getSentenceToken(self):
		sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
		sent_list = '\n'.join(sent_detector.tokenize(self.inputText.strip(), realign_boundaries=True)).split('\n')
		return sent_list

# blacklist/filter class
class MyBlackList():
	def __init__(self,balckListFile,token_word):
		self.token_word = token_word
		self.balckListFile = balckListFile
		self.loadBlackListFile()
		self.cleanToken()
		self.blackListTokens()

	def loadBlackListFile(self):
		inputfile_blacklist = open(self.balckListFile, 'r')
		self.blacklist = inputfile_blacklist.read()	

	def cleanToken(self):
		m = re.compile(r'[0-9a-zA-Z]')
		self.clean_token=[]
		for t in self.token_word:
			if m.match(t):
				self.clean_token.append(t) 
			#print t

	def blackListTokens(self):
		self.tokenListBlacklist=[]
		for c in self.clean_token:
			 if c.upper() not in self.blacklist:
			  	self.tokenListBlacklist.append(c.upper())

	def getBlacklist(self):
		return self.tokenListBlacklist



class ReadInput():
	def __init__(self,textFile):
		self.textFile = textFile
		self.readText()

	def readText(self):
		inputfile = open(self.textFile, 'r')	
		self.text = inputfile.read()
		inputfile.close()

	def getText(self):
		return self.text


class WordCounter():
	def __init__(self,tokenList):
		self.tokenList = tokenList
		self.count()

	def count(self):
		self.dictionary = FreqDist(self.tokenList)

	def getWordCount(self):
		return self.dictionary








def readDBTags():
	print "Reading DB Tags file ...... "
	file = open('tags_IT.txt')
	lines = file.readlines()

	for line in lines:
		categorySplit = line.split(';')
		category = Category(categorySplit[0])
		category.setCategoryItems(categorySplit)
		categoryList.append(category)


categoryList = []
readDBTags()

inputText = ReadInput('it.txt')
	
myToken = MyTokenizer(inputText.getText())	
token_word = myToken.getWordToken()

token_sentences = myToken.getSentenceToken()

myBlacklist = MyBlackList('Blacklist_UTF8.txt',token_word)
tokenAfterBlacklist = myBlacklist.getBlacklist()

wordCounter = WordCounter(tokenAfterBlacklist)
dictionary = wordCounter.getWordCount()





for sentence in token_sentences:
	print sentence

# for word in dictionary:
# 	pair = word + ',' + str(dictionary[word])
# 	#print pair

# for tag in categoryList:		
# 	for entry in tag.getCategoryItemList():
# 		if entry in tokenAfterBlacklist:
# 			print entry + " +++++++++ "
# 	 	else:
# 	 		print entry



#root = Tk()
#app = App(root)
#root.mainloop()



