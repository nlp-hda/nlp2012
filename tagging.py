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

		#master.minsize(500,500)
		#master.maxsize(1000,1000)
		text = Text(master)
		scroll = Scrollbar(master)
		scroll.pack(side=RIGHT, fill=Y)
		#self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
		#self.button.pack(side=LEFT)

		#self.readDBTags = Button(frame, text="Read DB Tags", command=self.onLoadDBTags)
		#self.readDBTags.pack(side=LEFT)

		App.listBox = Listbox(master)
		App.listBox.pack()
		App.listBox.insert(END,"Category")
		

		#self.readDBTexte = Button(frame, text="Read DB Texte", command=readDBTexte)
		#self.readDBTexte.pack(side=LEFT)



	
	def makeMenuBar(self,frame):
		menubar = Frame(frame,relief=RAISED,borderwidth=1)
		menubar.pack()
		
		#A menu in Tk is a combination of a Menubutton (the title of the
  	    #menu) and the Menu (what drops down when the Menubutton is pressed)
       		
		mb_file = Menubutton(menubar,text='file')
		mb_file.pack(side=LEFT)
		mb_file.menu = Menu(mb_file)
		
		#Once we've specified the menubutton and the menu, we can add
        #different commands to the menu
		
		mb_file.menu.add_command(label='open tag file')
		mb_file.menu.add_command(label='open text file')
		mb_file.menu.add_command(label='close')
		
		mb_edit = Menubutton(menubar,text='edit')
		mb_edit.pack(side=LEFT)
		mb_edit.menu = Menu(mb_edit)
		mb_edit.menu.add_command(label='copy')
		mb_edit.menu.add_command(label='paste')
		
		mb_help = Menubutton(menubar,text='help')
		mb_help.pack(padx=25,side=RIGHT)
		
		mb_file['menu'] = mb_file.menu
		mb_edit['menu'] = mb_edit.menu
		return



	def onLoadDBTags(self):
		readDBTags()
		i=0
		App.listBox.insert(END,"=================")
		for item in categoryList:
			App.listBox.insert(END,item.getCategoryName())
			for entry in item.getCategoryItemList():
				App.listBox.insert(END,"-"+entry)



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
		categoryList.append(category)
	print "Anzahl Tag items: ",len(categoryList)
	


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


