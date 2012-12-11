from django.http import HttpResponse
from textdomain.models import Domain, Text, Term, Word
import datetime

def home(request):
	html = "<html><body>"
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
			html += '<form action="/home/" method="GET">'
			html += '<input type="hidden" name="analyse" value="1"/>'
			html += '<input type="hidden" name="id" value="%i"/>'%(int(text.id))
			html += '<input type="submit" value="Text analysieren ">'
			html += '</form>'
		if analyse:
			html += "HAHA";
	html += "</body></html>"
	return HttpResponse(html)

def test(request):
    return HttpResponse("Test")
