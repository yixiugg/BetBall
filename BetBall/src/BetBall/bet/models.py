from django.db import models
class Gambler(models.Model):
    eid = models.CharField(max_length=7)
    name = models.CharField(max_length=20)
    balance = models.IntegerField(4)
    state = models.CharField(max_length=1)
    regtime = models.DateTimeField()
    password= models.CharField(max_length=32)

class Recharge(models.Model):
    gambler = models.ForeignKey(Gambler)
    amount = models.IntegerField(4)
    chargetime = models.DateTimeField()
    
class Match(models.Model):
    matchdate = models.DateField()
    matchtime = models.DateTimeField() 
    hometeam = models.CharField(max_length=50)
    awayteam = models.CharField(max_length=50)
    lega = models.CharField(max_length=50)
    final = models.CharField(max_length=50)
    state = models.CharField(max_length=1)
    result = models.CharField(max_length=5)
    gettime = models.DateField() 

class Transaction(models.Model):
    gambler = models.ForeignKey(Gambler)
    bettime = models.DateTimeField()
    bet = models.IntegerField(4)
    match = models.ForeignKey(Match)
    result = models.CharField(max_length=1)
    state = models.CharField(max_length=1)
    
class Position(models.Model):
    match = models.ForeignKey(Match)
    position = models.CharField(max_length=50)
    postime = models.DateTimeField()
    
class Admin(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    
    
