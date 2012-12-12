from nltk.tokenize import word_tokenize,wordpunct_tokenize
from nltk.tokenize import TreebankWordTokenizer
from nltk.probability import FreqDist

from textdomain.models import Blacklist, Text, Word, TextHasWords

import re
import string


class WordCount(object):
	def __init__(self, name, count):
		self.name = name
		self.count = count

class Tokenizer(object):
	def __init__(self,id):
		self.textid = id
		self.textobject = Text.objects.get(id=id)
		self.text = self.textobject.text
		self.blacklist = Blacklist.objects.all()
	
	def analyzeWords(self):
		token = TreebankWordTokenizer()
		token_word = wordpunct_tokenize(self.text)
		tokenized_list=[]
		m = re.compile(r'[0-9a-zA-Z]')
		
		black=[]
		for b in self.blacklist:
				black.append(b.name)
		
		for t in token_word:
			if m.match(t) and t.upper() not in black:
				tokenized_list.append(t.upper()) 

		dictionary = FreqDist(tokenized_list)

		words=[]
		for w in dictionary:
			words.append(WordCount(w,dictionary[w]))    	
			print(w)
		for w in words:
			
			try:
    				word = Word.objects.get(name=w.name)
			except Word.DoesNotExist:
    				word = None

			if word is None:
				word = Word(name=w.name)
				word.save()

			try:
				texthasword = TextHasWords.objects.get(text=self.textobject, word=word)
			except TextHasWords.DoesNotExist:
				texthasword = None

			if texthasword is None:	
				texthasword = TextHasWords(text=self.textobject, word=word,count=w.count)
				texthasword.save()
