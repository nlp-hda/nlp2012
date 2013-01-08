from textdomain.models import Domain, Blacklist, Text, Word, Term 
from django.contrib import admin

class DomainAdmin(admin.ModelAdmin):
	fields = ['name', 'terms']

admin.site.register(Domain, DomainAdmin)

class TextAdmin(admin.ModelAdmin):
	fields = ['name', 'text']

admin.site.register(Text, TextAdmin)

class BlacklistAdmin(admin.ModelAdmin):
	fields = ['name']

admin.site.register(Blacklist, BlacklistAdmin)
admin.site.register(Word)
admin.site.register(Term)
