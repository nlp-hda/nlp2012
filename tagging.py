#!/usr/bin/python

import string
import re

import Tkinter
from Tkinter import *

dbFileName = "db.txt"

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
#		for item in categoryList:
#			print item.getCategoryName()
#			App.listBoxCategory.insert(END,item.getCategoryName())
#			for entry in item.getCategoryItemList():
#				App.listBoxCaItems.insert(END,entry)



class Category:
	name = ""
	itemList = []

	def __init__(self,str):
		Category.name = str

	def setCategoryItems(self,itemList):
		Category.itemList = itemList

	def getCategoryName(self):
		return Category.name

	def getCategoryItemList(self):
		return Category.itemList


class Text:
	name = ""
	text = []

	def __init__(self,str):
		Text.name = str

	def setText(self,text):
		Text.text = text

	def getText(self):
		return Text.text


def readDBTags():
	print "Reading DB Tags file ...... "
	file = open('db.txt')
	lines = file.readlines()

	for line in lines:
		categorySplit = line.split(';')

		category = Category(categorySplit[0])
		category.setCategoryItems(categorySplit)
		print category.getCategoryName()
		print categoryList.append(category)

	print "Anzahl Tag items: ",len(categoryList)
	for item in categoryList:
		print item.getCategoryName()
	


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





categoryList = []
textList = []

root = Tk()
app = App(root)
root.mainloop()

readDBTags()
print ""
readDBTexte()


