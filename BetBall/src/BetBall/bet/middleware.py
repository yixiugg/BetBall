'''
Created on Apr 11, 2011

@author: e511125
'''
from django.http import HttpResponseRedirect 
from django.contrib.auth import SESSION_KEY 
from urllib import quote 
from django.template import Context, loader,RequestContext
from django.db.models import Q
from django.http import *
from BetBall.bet.timer import *
from BetBall.bet.models import *  

class AuthMiddleware(object): 
    def process_request(self, request):
        #print request.path 
        if request.path == '/' or request.path == '/mybet/' or request.path == '/myaccount/': 
            gambler =  request.session.get('gambler')
            if gambler is None:
                c = Context({}) 
                t = loader.get_template('login.htm')
                return HttpResponse(t.render(c))
            else:
                pass
        else:
            pass