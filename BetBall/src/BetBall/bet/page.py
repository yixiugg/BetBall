'''
Created on 2011-3-20

@author: yixiugg
'''
#coding=utf-8
import datetime    
import getpass
import os
import md5
from django.template import Context, loader
from django.http import *
from BetBall.bet.timer import *
from BetBall.bet.models import *  
    
def listTodayMatches(request):    
    gambler =  request.session.get('gambler')
    if gambler is None:
        c = Context({}) 
        t = loader.get_template('login.htm')
        return HttpResponse(t.render(c))
    else:
        gettime = datetime.date.today()  
        list = Match.objects.filter(state='1', gettime=gettime)     
        c = Context({'list':list}) 
        t = loader.get_template('index.htm')
        return HttpResponse(t.render(c))
    
def viewMatches(request,year,month,date):
    year=int(year)    
    month=int(month)    
    date=int(date)    
    matchdate = datetime.date(year,month,date)  
    list = Match.objects.filter(state='1', matchdate=matchdate)      
    c = Context({'list':list,'matchdate':matchdate}) 
    t = loader.get_template('matches.htm')
    return HttpResponse(t.render(c))

def listTodayAllMatches(request):    
    gettime = datetime.date.today()    
    list = Match.objects.filter(gettime=gettime)      
    c = Context({'list':list}) 
    t = loader.get_template('index.htm')
    return HttpResponse(t.render(c))

def openMatch(request,id): 
    id=int(id)
    match = Match.objects.get(id=id)
    match.state='1'
    match.save()
    return adminresult("Match open!")

def closeMatch(request,id):   
    id=int(id)
    match = Match.objects.get(id=id)
    match.state='0'
    match.save()
    return adminresult("Match close!")

def openGambler(request,id): 
    id=int(id)
    gambler = Gambler.objects.get(id=id)
    gambler.state='1'
    gambler.save()
    return adminresult("Gambler open!")

def closeGambler(request,id):   
    id=int(id)
    gambler = Gambler.objects.get(id=id)
    gambler.state='0'
    gambler.save()
    return adminresult("Gambler close!")

def viewMatch(request):   
    matchdate = datetime.date.today()    
    list = Match.objects.filter(matchdate=matchdate)      
    c = Context({'list':list}) 
    t = loader.get_template('index.htm')
    return HttpResponse(t.render(c))

def gologin(request):
    c = Context({}) 
    t = loader.get_template('login.htm')
    return HttpResponse(t.render(c))

def login(request):  
    m = Gambler.objects.filter(eid=request.POST['username'])      
    pwd = md5.new(request.POST['password'])
    pwd.digest()
    if len(m)!=0:
        if  m[0].password == pwd.hexdigest():
            if m[0].state=='0':
                return result("Account not active, please contact admin.")
            else:
                request.session['gambler'] = m[0]
                return myaccount(request)
        else:
            return result("Your username and password didn't match.")
    else:
        return result("Your username and password didn't match.")

def register(request):  
    c = Context({}) 
    t = loader.get_template('register.htm')
    return HttpResponse(t.render(c))
    
def saveRegister(request):  
    username = request.POST['username']
    if username is None:
        c = Context({}) 
        t = loader.get_template('register.htm')
        return HttpResponse(t.render(c))      
    pwd = md5.new(request.POST['password'])
    if request.POST['password']!=request.POST['password1']:
        return result("Password didn't match.")
    u = Gambler.objects.filter(eid=username)
    if len(u)>0:
        return result("Username exsited.")
    else:
        name = request.POST['name']
        gambler = Gambler(name=name,eid=username,password=pwd.hexdigest(),state='0',regtime=datetime.datetime.now(),balance=0)
        gambler.save()
        return result("Please wait for admin to approve your register.")

def recharge(request):  
    c = Context({}) 
    t = loader.get_template('recharge.htm')
    return HttpResponse(t.render(c))
 
def adminLogin(request):  
    m = Admin.objects.filter(username=request.POST['username'])      
    pwd = md5.new(request.POST['password'])
    pwd.digest()
    if len(m)!=0:
        if  m[0].password == pwd.hexdigest():
            request.session['admin'] = m[0]
            gettime = datetime.date.today()    
            list = Match.objects.filter(gettime=gettime).order_by('state')      
            c = Context({'list':list}) 
            t = loader.get_template('admin.htm')
            return HttpResponse(t.render(c))
        else:
            return result("Your username and password didn't match.")
    else:
        return result("Your username and password didn't match.")

def adminLogout(request):
    try:
        del request.session['admin']
    except KeyError:
        pass
    return result("You're logged out.")

def logout(request):
    try:
        del request.session['gambler']
    except KeyError:
        pass
    return result("You're logged out.")
    
def betMatch(request,id,r):   
    id=int(id)
    r = str(r)
    match = Match.objects.get(id=id)
    now = datetime.datetime.now()
    if now>match.matchtime:
        return result("Kidding! Match is over!")
    gambler =  request.session.get('gambler')
    bets = Transaction.objects.filter(match=match,gambler=gambler)
    if len(bets)==0:
        transaction = Transaction(match=match,gambler=gambler,bet=1,bettime=now,result=r)
        transaction.save()
        return result("Thanks for your bet.")
    
    else:
        transaction=bets[0]
        transaction.bettime=now
        transaction.result=r
        transaction.save()
        return result("Thanks for update your bet.")

def viewMatchBet(request):  
    if request.session.get('admin', False):
        return result("You've not admin!")
    matchdate = datetime.date.today()    
    list = Match.objects.filter(matchdate=matchdate)      
    c = Context({'list':list}) 
    t = loader.get_template('index.htm')
    return HttpResponse(t.render(c))

def viewGambler(request):   
    admin=request.session.get('admin')
    if admin is None:
        t = loader.get_template('admin_login.htm')
        c = Context({}) 
        return HttpResponse(t.render(c))
    list = Gambler.objects.all().order_by("-state") 
    c = Context({'list':list}) 
    t = loader.get_template('gambler.htm')
    return HttpResponse(t.render(c))
 
def admin(request):   
    admin=request.session.get('admin')
    if admin is None:
        t = loader.get_template('admin_login.htm')
        c = Context({}) 
        return HttpResponse(t.render(c))
    gettime = datetime.date.today()    
    list = Match.objects.filter(gettime=gettime).order_by('-state')      
    c = Context({'list':list}) 
    t = loader.get_template('admin.htm')
    return HttpResponse(t.render(c))
 
def viewGamblerBet(request):   
    if request.session.get('admin', None):
        return result("You've not admin!")
    matchdate = datetime.date.today()    
    list = Match.objects.filter(matchdate=matchdate)      
    c = Context({'list':list}) 
    t = loader.get_template('index.htm')
    return HttpResponse(t.render(c))

def refreshMatches(request):   
    admin=request.session.get('admin')
    if admin is None:
        return result("You've not admin!") 
    getMatches()
    return result("Get Matches again!") 

def myaccount(request):
    gambler =  request.session.get('gambler')
    if gambler is None:
        c = Context({}) 
        t = loader.get_template('login.htm')
        return HttpResponse(t.render(c))
    else:
        c = Context({'gambler':gambler}) 
        t = loader.get_template('my.htm')
        return HttpResponse(t.render(c))
    
def updateAccount(request):
    gambler =  request.session.get('gambler')
    name = request.POST['name']
    pwd = request.POST['password']
    pwd1 = request.POST['password1']
    pwd2 = request.POST['password2']
    if name!="":
        gambler.name=name
    if pwd!="":
        pwd = md5.new(pwd)
        pwd.digest()
        if gambler.password == pwd.hexdigest():
            if pwd1!="" and pwd2!="" and pwd1==pwd2:
                pwd1= md5.new(pwd1)
                gambler.password = pwd1.hexdigest()
            else:
                result("Please input the same password twice!")
        else:
            return result("Wrong old password!")
    gambler.save()
    request.session['gambler']=gambler
    return result("Account update!")
    
def mybet(request):
    gambler =  request.session.get('gambler')
    if gambler is None:
        c = Context({}) 
        t = loader.get_template('login.htm')
        return HttpResponse(t.render(c))
    else:
        bets = Transaction.objects.filter(gambler=gambler).order_by('-bettime')
        c = Context({'gambler':gambler,'bets':bets}) 
        t = loader.get_template('mybet.htm')
        return HttpResponse(t.render(c))

def result(r):
    c = Context({'result':r}) 
    t = loader.get_template('result.htm')
    return HttpResponse(t.render(c))

def adminresult(r):
    c = Context({'result':r}) 
    t = loader.get_template('admin_result.htm')
    return HttpResponse(t.render(c))

def search(request):
    key=request.GET['q']
    list = Match.objects.filter(hometeam__contains=key, awayteam__contains=key)  
    c = Context({'list':list,'key':key}) 
    t = loader.get_template('search.htm')
    return HttpResponse(t.render(c))  