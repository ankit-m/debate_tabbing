from google.appengine.ext import ndb

class Teams(ndb.Model):
	teamName = ndb.StringProperty(required = True)
	institute = ndb.StringProperty()
	member1 = ndb.StringProperty(required = True)
	member2 = ndb.StringProperty(required = True)
	member3 = ndb.StringProperty(required = True)
	mem1Score = ndb.IntegerProperty(required = True, default = 0)
	mem2Score = ndb.IntegerProperty(required = True, default = 0)
	mem3Score = ndb.IntegerProperty(required = True, default = 0)
	score = ndb.IntegerProperty(required = True, default = 0)
	record = ndb.StringProperty(required = True, default = "")

class Adjudicator(ndb.Model):
	name = ndb.StringProperty(required = True)
	institute = ndb.StringProperty(required = True)
	score = ndb.StringProperty(required = True, default = '')	#comma seperated
	totalScore = ndb.IntegerProperty(default = 0, required = True)
	trainee = ndb.BooleanProperty(default = False)
	registered = ndb.BooleanProperty(required = True, default = True) 	#change later

class Debater(ndb.Model):
	name = ndb.StringProperty(required = True)
	institute = ndb.StringProperty(required = True)
	score = ndb.StringProperty(required = True, default='')	#comma seperated
	totalScore = ndb.IntegerProperty(required = True, default = 0)

class Runner(ndb.Model):
	name = ndb.StringProperty(required = True)
	room = ndb.StringProperty(required = True)
	lastRound = ndb.StringProperty(required = True, default = "")

class Account(ndb.Model):
	name = ndb.StringProperty(required = True)
	username = ndb.StringProperty(required = True)
	password = ndb.StringProperty(required = True)
	accountType = ndb.IntegerProperty(required = True, default = 3) 	#1: Admin , 2: Runner, 3: User
	date = ndb.DateTimeProperty(auto_now_add = True)

class Round(ndb.Model):
	roundName = ndb.StringProperty(required = True)
	motions = ndb.TextProperty(required = True, default="Not Released Yet")
	date = ndb.StringProperty(required = True)
	time = ndb.StringProperty(required = True)

class Matchups(ndb.Model):
	roundName = ndb.StringProperty(required = True)
	team1 = ndb.StringProperty(required = True)		#refers to team names
	team2 = ndb.StringProperty(required = True)
	adjs = ndb.StringProperty(required = True)	#comma seperated
	runner = ndb.StringProperty(required = True)
	room = ndb.StringProperty(required = True)
