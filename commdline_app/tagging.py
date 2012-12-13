
import string
import re

import Tkinter
from Tkinter import *

from nltk.tokenize import word_tokenize,wordpunct_tokenize
from nltk.tokenize import TreebankWordTokenizer
from nltk.probability import FreqDist

class App:
	
	def __init__(self, master):
		frame = Frame(master)
		self.makeMenuBar(frame)
		frame.pack()

		App.label = Label(master,text="Category").pack(side=TOP,anchor='w')
		
		scroll = Scrollbar(master)	
		App.listBoxCategory = Listbox(master,height=10,width=30,)

		App.listBoxCaItems = Listbox(master,height=10,width=50,)
		App.listBoxCategory.pack(side=LEFT,fill=Y)
		App.listBoxCaItems.pack(side=RIGHT,fill=Y)
		scroll.pack(side=RIGHT, fill=Y)
		
		App.listBoxCategory.config(yscrollcommand=scroll.set)
		scroll.config(command=App.listBoxCategory.yview)

	
	
	def makeMenuBar(self,frame):
		menubar = Frame(frame,relief=RAISED,borderwidth=1)
		menubar.pack(side=LEFT)
		
		mb_file = Menubutton(menubar,text='file')
		mb_file.pack(side=LEFT)
		mb_file.menu = Menu(mb_file)
		
		mb_file.menu.add_command(label='open tag file',command=self.onLoadDBTags)
		mb_file.menu.add_command(label='open text file')
		mb_file.menu.add_command(label='close')
		
		mb_help = Menubutton(menubar,text='help')
		mb_help.pack(padx=25,side=RIGHT)
		
		mb_file['menu'] = mb_file.menu
		return


	def onLoadDBTags(self):
		readDBTags()

		#print "Test: "+categoryList[3].getCategoryName()
		for item in categoryList:
			#print item.getCategoryName()
			App.listBoxCategory.insert(END,item.getCategoryName())
			for entry in item.getCategoryItemList():
				App.listBoxCaItems.insert(END,entry)

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


class MyTreebankWordTokenizer:
	def __init__(self,read):
		self.read = read;
		self.token_word=[]

	def tokenizeInput(self):
		token = TreebankWordTokenizer()
		self.token_word = wordpunct_tokenize(self.read)	

	def getTokenWords(self):
		return self.token_word


class MyBlackList():
	def __init__(self,file):
		self.file = file
		self.blacklist=[]

	def loadBlackListFile(self,file):
		inputfile_blacklist = open('Blacklist_UTF8.txt', 'r')
		self.blacklist = inputfile_blacklist.read()	


	def getBlacklist(self):
		self.loadBlackListFile(file)
		return self.blacklist


class Filter():
	def __init__(self):
		print ""



def readDBTags():
	print "Reading DB Tags file ...... "
	file = open('tags_IT.txt')
	lines = file.readlines()

	for line in lines:
		categorySplit = line.split(';')
		category = Category(categorySplit[0])
		category.setCategoryItems(categorySplit)
		categoryList.append(category)
	#print len(categoryList)

def readDBTexte():
	print "Reading DB Text file ...... "
	file = open('texteA_M.txt')
	lines = file.readlines()

	for line in lines:
		lineSplit = line.split(';;')
		text = Text(lineSplit[0])
		if(len(lineSplit) > 2):
			print "panic"
		lineSplit.pop(0)
		text.setText(lineSplit)
		textList.append(text)
	print "Anzahl Texte: ",len(textList)


def readInputText():
	inputfile = open('it.txt', 'r')
	
	outputfile = open('output_file.txt', 'w')

	read = inputfile.read()

	myBlacklist = MyBlackList('toImpl')
	blacklist = myBlacklist.getBlacklist()

	myToken = MyTreebankWordTokenizer(read)	
	myToken.tokenizeInput()
	token_word = myToken.getTokenWords()

	

	m = re.compile(r'[0-9a-zA-Z]')
	clean_token=[]
	for t in token_word:
		if m.match(t):
			clean_token.append(t) 
			#print t

	tokenized_list=[]
	for c in clean_token:
		 if c.upper() not in blacklist:
		  	tokenized_list.append(c.upper())

	#print len(tokenized_list)

	dictionary = FreqDist(tokenized_list)

	for word in dictionary:
	    pair = word + ',' + str(dictionary[word])
	    #print pair
	    outputfile.write(pair+'\n')
	    
	highlighted_list=[]

	#print len(categoryList.getCategoryItemList())
	#for word in categoryList:
	#	print word
	#for tag in categoryList.getCategoryItemlList():
	#for tag in categoryList:
		#for word in tokenized_list:
			#for entry in tag.getCategoryItemList():
				#print entry
			# 	highlighted_list.append(tag + " -----------") #IN ROT
			# else:
			# 	highlighted_list.append(tag)
	
	for tag in categoryList:		
		for entry in tag.getCategoryItemList():
			if entry in tokenized_list:
				print entry + " +++++++++ "
			else:
				print entry + " "

#	for word in highlighted_list:
#		print word

	inputfile.close()
	outputfile.close()


categoryList = []
textList = []





readDBTags()
readInputText()

#root = Tk()
#app = App(root)
#root.mainloop()


print ""
#readDBTexte()



