#coding=utf-8
import datetime,time    
import getpass
import os
import sys
import md5
import json
from weibo import APIClient
from django.template import Context, loader,RequestContext
from django.db.models import Q
from django.http import *
from BetBall.bet.timer import *
from BetBall.bet.models import *  

#APP_KEY = '3118024522' # app key of betball
#APP_SECRET = '95895b5b4556994a798224902af57d30' # app secret of betball
#CALLBACK_URL = 'http://www.noya35.com/weiboLoginBack' # callback url

APP_KEY = '2945318614' # app key of betball
APP_SECRET = '26540ac5e2728be53005df042bc9bc00' # app secret of betball
CALLBACK_URL = 'http://127.0.0.1:8888/weiboLoginBack' # callback url
client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
SITE_URL = 'http://www.noya35.com'

def listTodayMatches(request):    
    gambler =  request.session.get('gambler')
    if gambler is None:
        c = Context({}) 
        t = loader.get_template('login.htm')
        return HttpResponse(t.render(c))
    else:
        now = datetime.datetime.now()  
        list = Match.objects.filter(state='1', matchtime__gte=now)     
        c = Context({'list':list,'session':request.session}) 
        t = loader.get_template('index.htm')
        return HttpResponse(t.render(c))
    
def viewMatches(request,year,month,date):
    year=int(year)    
    month=int(month)    
    date=int(date)    
    matchdate = datetime.date(year,month,date)  
    list = Match.objects.filter(state='1', matchdate=matchdate)      
    c = Context({'list':list,'matchdate':matchdate,'session':request.session}) 
    t = loader.get_template('matches.htm')
    return HttpResponse(t.render(c))

def listTodayAllMatches(request):    
    now = datetime.datetime.now()    
    list = Match.objects.filter(matchtime__gte=now)      
    c = Context({'list':list,'session':request.session}) 
    t = loader.get_template('index.htm')
    return HttpResponse(t.render(c))

def openMatch(request,id): 
    id=int(id)
    match = Match.objects.get(id=id)
    match.state='1'
    match.save()
    g = Gambler.objects.filter(~Q(weibo_nick=''),~Q(weibo_nick=None)) 
    at_user=''
    for gambler in g:
        at_user+='@'+gambler.weibo_nick+' '
    #发微博吸引投注！
    status = u'亲们，又有比赛可以砸可乐拉！'+match.hometeam+'vs'+match.awayteam+u'，您别b4啊！'+SITE_URL+' '+at_user
    if client!=None:
        expires_in = request.session.get('expires_in')
        access_token = request.session.get('access_token')
        client.set_access_token(access_token, expires_in)
        client.post.statuses__update(status=status)
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
    c = Context({'list':list,'session':request.session}) 
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

def weiboLogin(request):
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    url = client.get_authorize_url()
    return HttpResponseRedirect(url) 

def weiboLoginBack(request):
    #得到微博认证的信息
    code = request.GET['code']
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    r = client.request_access_token(code)
    access_token = r.access_token
    expires_in = r.expires_in
    # TODO: 在此可保存access token
    request.session['access_token'] = access_token
    request.session['expires_in'] = expires_in
    client.set_access_token(access_token, expires_in)
    #测试发微博
#    status = u'亲们，俺刚才手快，测试了一把，您别b4啊！'
#    client.post.statuses__update(status=status)
    #得到微博用户的id，如果有绑定，则直接登录，没有则跳到绑定页面
    json_obj = client.get.statuses__user_timeline()
    weibo_user = json_obj['statuses'] [0]['user']
    #得到用户的weibo UID
    weibo = weibo_user['id']
#    request.session['weibo_client'] = client
    request.session['weibo'] = weibo
    #得到用户的微博nick
    weibo_nick = weibo_user['screen_name']
    request.session['weibo_nick'] = weibo_nick
    a = Admin.objects.filter(weibo=weibo)
    #先尝试admin登陆
    if len(a)!=0:
        request.session['admin'] = a[0]
        now = datetime.datetime.now()    
        list = Match.objects.filter(matchtime__gte=now).order_by('-state','matchtime')     
        c = Context({'list':list,'session':request.session}) 
        t = loader.get_template('admin.htm')
        return HttpResponse(t.render(c))
    #尝试用户登陆
    u = Gambler.objects.filter(weibo=weibo)
    if len(u)!=0:
        gambler = u[0]
        request.session['gambler'] = gambler
        gambler.weibo_nick=weibo_nick
        gambler.save()
        return myaccount(request)
    else:
        c = Context({'info':'Please bind your account or register first!','session':request.session}) 
        t = loader.get_template('bind.htm')
        return HttpResponse(t.render(c))
    return HttpResponseRedirect("/") 

def bind(request): 
    m = Gambler.objects.filter(eid=request.POST['username'])      
    pwd = md5.new(request.POST['password'])
    pwd.digest()
    if len(m)!=0:
        if  m[0].password == pwd.hexdigest():
            if m[0].state=='0':
                return result("Account not active, please contact admin.")
            else:
                gambler = m[0]
                request.session['gambler'] = gambler
                weibo = request.session['weibo']
                gambler.weibo = weibo
                gambler.save() 
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
    weibo = request.session['weibo']
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
        gambler = Gambler(name=name,eid=username,weibo=weibo,password=pwd.hexdigest(),state='0',regtime=datetime.datetime.now(),balance=0)
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
            c = Context({'list':list,'session':request.session}) 
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
    #下注自动发微博
    status = u'亲们，俺刚才手快，砸了一罐可乐在上面'+match.hometeam+'vs'+match.awayteam+u'，您别b4啊！'+SITE_URL
    if client!=None:
        expires_in = request.session.get('expires_in')
        access_token = request.session.get('access_token')
        client.set_access_token(access_token, expires_in)
        client.post.statuses__update(status=status)
    if len(bets)==0:
        transaction = Transaction(match=match,gambler=gambler,bet=1,bettime=now,result=r,state='0')
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
    c = Context({'list':list,'session':request.session}) 
    t = loader.get_template('index.htm')
    return HttpResponse(t.render(c))

def viewGambler(request):   
    admin=request.session.get('admin')
    if admin is None:
        t = loader.get_template('admin_login.htm')
        c = Context({}) 
        return HttpResponse(t.render(c))
    list = Gambler.objects.all().order_by("-state") 
    c = Context({'list':list,'session':request.session}) 
    t = loader.get_template('gambler.htm')
    return HttpResponse(t.render(c))
 
def admin(request): 
    admin=request.session.get('admin')  
    if admin is None:
        t = loader.get_template('admin_login.htm')
        c = Context({}) 
        return HttpResponse(t.render(c))
    now = datetime.datetime.now()    
    list = Match.objects.filter(matchtime__gte=now).order_by('-state','matchtime')        
    c = Context({'list':list,'session':request.session}) 
    t = loader.get_template('admin.htm')
    return HttpResponse(t.render(c))
 
def lega(request,lega): 
    admin=request.session.get('admin')  
    if admin is None:
        t = loader.get_template('admin_login.htm')
        c = Context({}) 
        return HttpResponse(t.render(c))
    now = datetime.datetime.now()    
    list = Match.objects.filter(matchtime__gte=now,lega=lega).order_by('-state','matchtime')        
    c = Context({'list':list,'session':request.session}) 
    t = loader.get_template('admin.htm')
    return HttpResponse(t.render(c))
    
def opened(request):   
    admin=request.session.get('admin')
    if admin is None:
        return adminresult("You've not admin!")
    list = Match.objects.filter(state='1').order_by('-gettime')      
    c = Context({'list':list,'session':request.session}) 
    t = loader.get_template('opened.htm')
    return HttpResponse(t.render(c))
 
def viewGamblerBet(request,id): 
    admin=request.session.get('admin')
    if admin is None:
        return adminresult("You've not admin!")
    id=int(id)
    gambler = Gambler.objects.get(id=id)    
    list = Transaction.objects.filter(gambler=gambler).order_by('-bettime')       
    c = Context({'list':list,'gambler':gambler,'session':request.session}) 
    t = loader.get_template('gambler_bet.htm')
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
        c = Context({'gambler':gambler,'session':request.session}) 
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
        c = Context({'gambler':gambler,'bets':bets,'session':request.session}) 
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
    list = Match.objects.filter(Q(lega__icontains=key)|Q(hometeam__icontains=key)|Q(awayteam__icontains=key))  
    now = datetime.datetime.now()
    c = Context({'list':list,'key':key,'now':now,'session':request.session}) 
    t = loader.get_template('search.htm')
    return HttpResponse(t.render(c))  

def clean(request,id):
    admin=request.session.get('admin')
    if admin is None:
        return adminresult("You've not admin!")
    id=int(id)
    transaction = Transaction.objects.get(id=id) 
    transaction.state='2'
    transaction.save()
    return adminresult("Transaction clean!") 

def settle(request,id):
    admin=request.session.get('admin')
    if admin is None:
        return adminresult("You've not admin!")
    id=int(id)
    bet = Transaction.objects.get(id=id)
    if bet.match.result is not None and bet.match.result!="":
        if bet.match.result==bet.result:
            bet.gambler.balance=( bet.gambler.balance+1)
            bet.bet=1
        else:
            bet.gambler.balance=( bet.gambler.balance-1)
            bet.bet=-1
    bet.state='1'
    bet.save()
    return adminresult("Transaction settled!")    


def cancelBet(request,id):
    id=int(id)
    transaction = Transaction.objects.get(id=id) 
    matchtime = transaction.match.matchtime
    now = datetime.datetime.now()
    if now>matchtime:
        return result("Match is over, you cannot cancel this bet!")   
    else:  
        transaction.delete() 
        return result("Transaction clean!")     
    
def viewMatchBets(request,id):
    id=int(id)
    match = Match.objects.get(id=id) 
    bets = Transaction.objects.filter(match=match).order_by('-bettime') 
    c = Context({'list':bets,'match':match,'session':request.session}) 
    t = loader.get_template('match_bet.htm')
    return HttpResponse(t.render(c))

def setResult(request,id,r):
    id=int(id)
    result=int(r)
    match = Match.objects.get(id=id) 
    match.result=result
    match.save()
    bets = Transaction.objects.filter(match=match).order_by('-bettime') 
    for bet in bets:
        if bet.state!='1':
            if bet.result==r:
                bet.gambler.balance=( bet.gambler.balance+1)
                bet.bet=1
            else:
                bet.gambler.balance=( bet.gambler.balance-1)
                bet.bet=-1
            bet.gambler.save()
        bet.state='1'
        bet.save()
    return adminresult("Set result succeed!")    

 
def addMatch(request):  
    t =time.strptime(request.POST['matchtime'], "%Y-%m-%d %H:%M:%S")
    y,m,d,h,M,s = t[0:6]
    matchtime=datetime.datetime(y,m,d,h,M,s)
    matchdate=datetime.date(y,m,d)
    lega=request.POST['lega'];
    water=request.POST['water'];
    hometeam=request.POST['hometeam'];
    awayteam=request.POST['awayteam'];
    match = Match(gettime=datetime.datetime.now(),lega=lega,matchtime=matchtime,matchdate=matchdate,hometeam=hometeam,awayteam=awayteam,state='1',final=water)
    match.save()
    return adminresult("Add match succeed!") 
    
def setSession(c,request):
    c['session']=request.session