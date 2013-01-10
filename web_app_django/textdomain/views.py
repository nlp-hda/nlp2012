from django.http import HttpResponse
from django.template import Context, loader
from django.utils.safestring import mark_safe

from textdomain.models import Domain, Text, Term, Word, TextHasWords, Blacklist
from textdomain.tokenize import Tokenizer, WordCount


def home(request):
	text_list = Text.objects.all()

	template = loader.get_template('home.html')

	context = Context({
       		'text_list': text_list,
	})
		
	if request.method == 'GET':

		id = request.GET.get('id', '')
		analyse = request.GET.get('analyse', '')

		if id:
			text = Text.objects.get(id=id)


			context['analyse'] = 1
			context['text_object'] = text;			
			
			if analyse:
				token=Tokenizer(text.id)
				token.analyzeWords()

			if len(text.words.all()) > 0:

				words = text.words.all()
				wordcount = []
				
				for w in words:
					texthaswords = TextHasWords.objects.get(text=text,word=w)
					wordcount.append(WordCount(w.name,texthaswords.count))

				if not len(wordcount) == 0:
					sorted(wordcount, key=lambda WordCount: WordCount.count, reverse=True)

				wordrange = 15

				if len(wordcount) < wordrange:
					wordrange = len(wordcount)
				wordname = ''
				wordcounted = ''

                                for w in range(wordrange):
                                        wordname += "'%s',"%(wordcount[w].name)

                                for w in range(wordrange):
                                        wordcounted += "%i, "%(int(wordcount[w].count))
	
				context['word_name'] = mark_safe(wordname)
				context['word_count'] = wordcounted
				context['word_range'] = wordrange

				domains = Domain.objects.all()

				counted = []
				
				for domain in domains:
					terms = domain.terms.all()
					termlist=[]
	
					counter = 0

					for term in terms:
						termlist.append(term.name)
					
					for w in range(wordrange):
						if wordcount[w].name in termlist:	
							counter += 1

					counted.append(WordCount(domain.name,counter))

				context['domains'] = counted

	return HttpResponse(template.render(context))

def sentence(request):
	template = loader.get_template('sentence.html')
	token=Tokenizer(12)
	text_list = token.getSentenceToken()
	context = Context({
       		'text_list': text_list,
	})

	return HttpResponse(template.render(context)) 



def blacklist(request):
	template = loader.get_template('blacklist.html')

	context = Context({})

	if request.method == 'GET':

		print "there we are"

		blacklistword = request.GET.get('blackword', '')
		blacklistword = blacklistword.upper()
		print blacklistword
		try:
			blackword = Blacklist.objects.get(name=blacklistword)
		except Blacklist.DoesNotExist:
			blackword = None

		if blackword is None:
			blacklist = Blacklist(name=blacklistword)
			blacklist.save()
			
			try:
                                word = Word.objects.get(name=blacklistword)
				print word.name
                        except Word.DoesNotExist:
                                word = None

                        if word is not None:
				print word.name
				word.delete()

	return HttpResponse(template.render(context))
