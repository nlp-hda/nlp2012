from django.conf.urls import patterns, url

from textdomain import views

urlpatterns = patterns('',
    # ex: /polls/
    url(r'^$', views.home, name='home'),
    url(r'^blacklist/$', views.blacklist, name='blacklist')

    # ex: /polls/5/
    #url(r'^(?P<text_id>\d+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
    # url(r'^(?P<text_id>\d+)/results/$', views.results, name='results'),
    # ex: /polls/5/vote/
    # url(r'^(?P<text_id>\d+)/vote/$', views.vote, name='vote'),
)
