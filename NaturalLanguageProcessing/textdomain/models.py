from django.db import models

# Create your models here.

class Term(models.Model):
	name = models.CharField(max_length=50)

class Word(models.Model):
	name = models.CharField(max_length=100)

class Text(models.Model):
	name = models.CharField(max_length=50)
	text = models.TextField()
	words = models.ManyToManyField(Word, through='TextHasWords')

class TextHasWords(models.Model):
	text = models.ForeignKey(Text)
	word = models.ForeignKey(Word)
	count = models.IntegerField()	

class Domain(models.Model):
	name = models.CharField(max_length=50)
	terms = models.ManyToManyField(Term)
	texts = models.ManyToManyField(Text)
	
class Blacklist(models.Model):
	name = models.CharField(max_length=100)
