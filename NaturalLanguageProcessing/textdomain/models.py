from django.db import models

# Create your models here.

class Term(models.Model):
	name = models.CharField(max_length=50)

	def __unicode__(self):
        	return self.name

class Word(models.Model):
	name = models.CharField(max_length=100)

	def __unicode__(self):
        	return self.name

class Text(models.Model):
	name = models.CharField(max_length=50)
	text = models.TextField()
	words = models.ManyToManyField(Word, through='TextHasWords')

	def __unicode__(self):
        	return self.name

class TextHasWords(models.Model):
	text = models.ForeignKey(Text)
	word = models.ForeignKey(Word)
	count = models.IntegerField()	

class Domain(models.Model):
	name = models.CharField(max_length=50)
	terms = models.ManyToManyField(Term)
	texts = models.ManyToManyField(Text)

	def __unicode__(self):
        	return self.name
	
class Blacklist(models.Model):
	name = models.CharField(max_length=100)

	def __unicode__(self):
        	return self.name
