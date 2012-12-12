from django.http import HttpResponse
from textdomain.models import Domain, Text, Term, Word, TextHasWords
from textdomain.tokenize import Tokenizer, WordCount

def home(request):
	html = "<html>"
	html += "<head>"
	html += '<script src="/media/jquery.js"></script>'
	html += '<script src="http://code.highcharts.com/highcharts.js"></script>'
	html += "</head>"
	html += "<body>"
	html += '<form action="/home/" method="GET">'
	html += '<select name="id" onChange="this.form.submit()">'
	texts = Text.objects.all()
	html += "<option></option>"

	for i in texts:
		html += "<option value='%i'>%s</option>"%(int(i.id),i.name)

	html += "</select>"
	html += '</form>'
	
	id = 0
	
	if request.method == 'GET':
		id = request.GET.get('id', '')
		analyse = request.GET.get('analyse', '')
		if id:
			text = Text.objects.get(id=id)
			html += "<h4>%s</h4>"%(text.name);
			html += text.text
			
			if analyse:
				token=Tokenizer(text.id)
				token.analyzeWords()
		
			if len(text.words.all()) == 0:
				html += '<form action="/home/" method="GET">'
				html += '<input type="hidden" name="analyse" value="1"/>'
				html += '<input type="hidden" name="id" value="%i"/>'%(int(text.id))
				html += '<input type="submit" value=" Analyze text ">'
				html += '</form>'

			else:
				words = text.words.all()
				wordcount = []
				
				for w in words:
					texthaswords = TextHasWords.objects.get(text=text,word=w)
					wordcount.append(WordCount(w.name,texthaswords.count))

				if not len(wordcount) == 0:
					sorted(wordcount, key=lambda WordCount: WordCount.count, reverse=True)

				html += '<script type="text/javascript">'
				html += "var chart; $(document).ready(function() { chart = new Highcharts.Chart({ chart: { renderTo: 'container', type: 'column', margin: [ 50, 50, 100, 80]}, title: { text: 'Text Analysis' }, xAxis: { categories: ["

				wordrange = 15

				if len(wordcount) < wordrange:
					wordrange = len(wordcount)
				
				for w in range(wordrange):
					html += "'%s',"%(wordcount[w].name)

				html += "], labels: { rotation: -45, align: 'right', style: { fontSize: '15px', fontFamily: 'Verdana, sans-serif' } } }, yAxis: { min: 0, title: { text: 'Counted Words' } }, legend: { enabled: false }, tooltip: { formatter: function() { return '<b>'+ this.x +'</b><br/>'+ this.y; } }, series: [{ name: 'Counted Words', data: ["
				
				for w in range(wordrange):
					html += "%i, "%(int(wordcount[w].count))

				html += "] }] }); });"
 				html += "</script>"
				html += '<div id="container" style="min-width: 400px; height: 400px; margin: 0 auto"></div>'
	html += "</body></html>"
	return HttpResponse(html)
