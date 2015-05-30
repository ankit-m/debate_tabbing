import os
import jinja2
import webapp2
from google.appengine.ext import ndb
import hashlib
from ndbEntities import *
from util import *
from random import shuffle
from time import sleep

jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
    def render(self, file, values = {}):
        t = jinja_environment.get_template(file)
        self.response.out.write(t.render(values))

class RegisterHandler(Handler):
	pass
	# def render_front(self, **kwargs):
 #        values = {}
 #        self.render('register.html', values)
 #    def get(self):
 #        self.render_front()    
 #    def post(self):
 #        firstName = self.request.get('firstName')
 #        lastName = self.request.get('lastName')
 #        userName = self.request.get('userName')
 #        password = self.request.get('password')
 #        institute = self.request.get('institute')
 #        participant = self.request.get('type')
 #        confpass = self.request.get('confpass')

 #        if firstName and lastName and userName and password and institute and participant and confpass:
 #            a = Account(name = firstName + " " + lastName, username = userName, password = hashlib.sha256(password).hexdigest())
 #            a.put()

 #            if participant == 'deb':
 #                a = Debater(name = firstName + " " + lastName, institute = institute, score = 0)
 #                a.put()
 #            elif participant == 'adj':
 #                a = Adjudicator(name = firstName + " " + lastName, institute = institute)
 #                a.put()
 #            else:
 #                self.redirect('/register')
 #        else:
 #        	pass
 #            #error message
 #            # self.redirect('/register')

class RegDeskHandler(Handler):
    def render_front(self, **kwargs):
        debaters = ndb.gql("SELECT * FROM Debater")
        adjudicators = ndb.gql("SELECT * FROM Adjudicator")
        teams = ndb.gql("SELECT * FROM Teams")
        adjs = ndb.gql("SELECT * FROM Adjudicator")
        debInstitutes = []
        adjInstitutes = []
        for member in debaters:
            if member.institute not in debInstitutes:
                debInstitutes.append(member.institute)
        for member in adjudicators:
            if member.institute not in adjInstitutes:
                adjInstitutes.append(member.institute)

        values = {
            'debaters' : debaters,
            'adjudicators' : adjudicators,
            'teams' : teams,
            'adjs' : adjs,
            'debInstitutes' : debInstitutes,
            'adjInstitutes' : adjInstitutes
        }
        if kwargs:
            for key, value in kwargs.items():
                values[key] = value
        self.render("desk.html", values) 

    def get(self):
        self.render_front();

    def post(self):
        formType = self.request.get('reg')
        if formType == 'Register Team':
            teamName = self.request.get('teamName')
            member1 = self.request.get('member1')
            member2 = self.request.get('member2')
            member3 = self.request.get('member3')
            institute = self.request.get('institute')
            if teamName and member1 != 'Select' and member2 != 'Select' and member3 != 'Select' and institute != 'Select':
                mem1 = ndb.gql("SELECT * FROM Debater WHERE name=:1", member1).get()
                mem2 = ndb.gql("SELECT * FROM Debater WHERE name=:1", member2).get()
                mem3 = ndb.gql("SELECT * FROM Debater WHERE name=:1", member3).get()
                if mem1.institute == institute and mem2.institute == institute and mem3.institute == institute:
                    Teams(teamName = teamName, institute = institute, member1 = member1, member2 = member2, member3 = member3).put()
                    self.redirect('/regDesk')
                else:
                    self.render_front(teamName = teamName)
            else:
                self.render_front(teamName = teamName)
        
        elif formType == 'Register Adjudicator':
            name = self.request.get('name')
            institute = self.request.get('institute')
            if name != 'Select' and institute != 'Select':
                adj = ndb.gql("SELECT * FROM Adjudicator WHERE name=:1", name).get()   #check for same name
                if (adj.institute == institute):
                    adj.registered = True
                    adj.put()
                    self.redirect('/regDesk')
                else:
                    self.render_front()
            else:
                self.render_front()
        
        else:
            self.redirect('/regDesk')

class MainPage(Handler):
    def render_front(self, **kwargs):
        values = {}
        if kwargs:
            for key, value in kwargs.items():
                values[key] = value
        self.render('index.html', values)
    
    def get(self):
        # sampleRegistrations()
    	self.render_front()
        
    def post(self):
    	username = self.request.get('username')
        password = self.request.get('password')
        if username and password:
            if verify(username, password):
                account = ndb.gql("SELECT * FROM Account WHERE username=:1", username)
                name = account.get().name
                accountType = int(account.get().accountType)
                self.response.headers.add_header('Set-Cookie', 'username=%s|%s' %(str(username),str(hashlib.sha256(name+'upod1rwKHRmHzHuEYBzY').hexdigest())))
                if accountType == 1:
                    self.redirect('/adminConsole')
                elif accountType == 2:
                    self.redirect('/runner')
                elif accountType == 3:
                    self.redirect('/user')
                else:
                    self.redirect('/false')
            else:
                self.render_front(username = username, error = 'Invalid username or password')    #show error 
        else:
            self.render_front(username = username, error = 'Please enter both username and password')

class AdminConsoleHandler(Handler):
    def render_front(self, **kwargs):
        rounds = ndb.gql("SELECT * FROM Round")
        runners = ndb.gql("SELECT * FROM Runner")
        teams = ndb.gql("SELECT * FROM Teams")
        adjs = ndb.gql("SELECT * FROM Adjudicator")
        debaters = ndb.gql("SELECT * FROM Debater")
        values = {
            'rounds' : rounds,
            'runners' : runners,
            'teams' : teams,
            'adjs' : adjs,
            'debaters' : debaters
        }
        if kwargs:
            for key, value in kwargs.items():
                values[key] = value
        self.render('admin.html', values)

    def makeRound(self, teams, numberOfTeams, nextRound):
        teamList = teams.fetch(limit = None)
        
        adjs = ndb.gql("SELECT * FROM Adjudicator WHERE registered=:1 ORDER BY totalScore", True)
        numberOfAdjs = adjs.count()
        adjsPerRoom = numberOfAdjs/(numberOfTeams/2)
        adjList = adjs.fetch(limit = None)
	        
        runners = ndb.gql("SELECT * FROM Runner")
        if runners.count() < numberOfTeams/2:
        	self.redirect('/error')
        runnerList = runners.fetch(limit = None)
        shuffle(runnerList)

        # if adjsPerRoom%2 == 1:
        for i in range(0, numberOfTeams/2):
            adjsInRoom = ''
            for j in range(0, adjsPerRoom):
                temp = adjList.pop()
                adjsInRoom += '%s'% temp.name + '|' + '%s,'% temp.institute
            tempRunner = runnerList.pop()
            Matchups(roundName=nextRound, team1 = teamList.pop().teamName, team2 = teamList.pop().teamName, adjs = adjsInRoom, runner = tempRunner.name, room = tempRunner.room).put()
        sleep(1)
	    
	    # else:
	    # 	for i in range(0, numberOfTeams/2):
	    # 		adjsInRoom = ''


    def makeFirstRound(self, teams, numberOfTeams, nextRound):
        teamList = teams.fetch(limit = None)
        shuffle(teamList)
        
        adjs = ndb.gql("SELECT * FROM Adjudicator WHERE registered=:1", True)
        numberOfAdjs = adjs.count()
        adjsPerRoom = numberOfAdjs/(numberOfTeams/2)
        adjList = adjs.fetch(limit = None)
        shuffle(adjList)

        runners = ndb.gql("SELECT * FROM Runner")
        if runners.count() < numberOfTeams/2:
        	self.redirect('/error')
        runnerList = runners.fetch(limit = None)
        shuffle(runnerList)

        for i in range(0, numberOfTeams/2):
            adjsInRoom = ''
            for j in range(0, adjsPerRoom):
                temp = adjList.pop()
                adjsInRoom += '%s'% temp.name + '|' + '%s,'% temp.institute
            tempRunner = runnerList.pop()
            Matchups(roundName=nextRound, team1 = teamList.pop().teamName, team2 = teamList.pop().teamName, adjs = adjsInRoom, runner = tempRunner.name, room = tempRunner.room).put()
        sleep(1)

    def get(self):
        self.render_front()

    def post(self):
        submitType = self.request.get('submitType')
        if submitType == 'Set Round':
            roundName = self.request.get('roundName')
            date = self.request.get('date')
            time = self.request.get('time')
            if roundName and date and time:
                Round(roundName = roundName, date = date, time = time).put()
                sleep(1)
                self.redirect("/adminConsole")
            else:
                self.render_front(roundName = roundName, date = date, time = time)

        elif submitType == 'Release Motions':
            roundName = self.request.get('roundName')
            motion = self.request.get('motion')
            if roundName != 'Select Round' and motion: 
                a = ndb.gql("SELECT * FROM Round WHERE roundName=:1", roundName).get()
                a.motions = motion
                a.put()
                self.redirect('/adminConsole')
            else:
                pass    #error

        elif submitType == 'Register Runner':
            runnerName = self.request.get('runnerName')
            rID = self.request.get('rID')
            rpass = 'asd'   #generate password
            room = self.request.get('room')

            if runnerName and rID and room:
                Runner(name = runnerName, room = room).put()
                Account(name = runnerName, username = rID, password = hashlib.sha256(rpass).hexdigest(), accountType = 2).put()
                sleep(1)
                self.redirect('/adminConsole')
                
    			#Reference(id='father', kind='father').put()
				# Reference(parent=ndb.Key(Reference, 'father'), id=key_id, some_id_id=some_id, kind='user').put()
				# print Reference.query(Reference.some_id == some_id, Reference.kind == 'user', ancestor=ndb.Key(Reference, 'father')).get()

            else:
                pass

        elif submitType == 'Tabs':
            #teams ranking
            #adj clashes
            #trainee handling
            # roundName!!, teams , adjs, runner, room
            nextRound = str(self.request.get('nextRound'))  #check blank and same round already published
            checkFirstRound = ndb.gql("SELECT * FROM Matchups").get()
            adjs = ndb.gql("SELECT * FROM Adjudicator ORDER BY totalScore DESC")
            debaters = ndb.gql("SELECT * FROM Debater ORDER BY score DESC")
            if checkFirstRound:
                teams = ndb.gql("SELECT * FROM Teams ORDER BY score ASC")
                numberOfTeams = teams.count()
                if numberOfTeams%2 == 0:
                    self.makeRound(teams, numberOfTeams, nextRound)
                    matchups = ndb.gql("SELECT * FROM Matchups WHERE roundName=:1", nextRound)
                    self.render_front(matchups = matchups)
                else:
                    Teams(teamName = 'Swing', member1 = 'member1', member2 = 'member2', member3 = 'member3').put()
                    sleep(1)
                    self.makeRound(teams, numberOfTeams, nextRound)
                    matchups = ndb.gql("SELECT * FROM Matchups WHERE roundName=:1", nextRound)
                    self.render_front(matchups = matchups)
            else:
                teams = ndb.gql("SELECT * FROM Teams")
                numberOfTeams = teams.count()
                if numberOfTeams%2 == 0:
                    self.makeFirstRound(teams, numberOfTeams, nextRound)
                    matchups = ndb.gql("SELECT * FROM Matchups WHERE roundName=:1", nextRound)
                    self.render_front(matchups = matchups)
                else:
                    Teams(teamName = 'Swing', member1 = 'member1', member2 = 'member2', member3 = 'member3').put()
                    sleep(1)
                    self.makeFirstRound(teams, numberOfTeams, nextRound)
                    matchups = ndb.gql("SELECT * FROM Matchups WHERE roundName=:1", nextRound)
                    self.render_front(matchups = matchups)
        
        elif submitType == 'Delete Team':
        	teamName = self.request.get('deleteTeam')	#popup to confirm
        	deleteTeam = ndb.gql('SELECT * FROM Teams WHERE teamName = :1', teamName).get()
        	deleteTeam.key.delete()
        	sleep(1)
        	self.redirect('/adminConsole')

        elif submitType == 'Delete Adjudicator':
        	teamName = self.request.get('deleteTeam')	#popup to confirm
        	deleteTeam = ndb.gql('SELECT * FROM Teams WHERE teamName = :1', teamName).get()
        	deleteTeam.key.delete()
        	sleep(1)
        	self.redirect('/adminConsole')

class UserHandler(Handler):
    def get(self):
        #name
        #win loss record
        #last matches details
        #scores when released by admin
        #change password
        #shout feature**
        self.render('user.html')

class RunnerHandler(Handler):
    def get(self):
        username = self.request.cookies.get('username')
        if username:
            a = username.split('|')
            name = ndb.gql("SELECT * FROM Account WHERE username=:1", a[0]).get().name
            if checkRunner(name, a[1]):
                matchup = ndb.gql("SELECT * FROM Matchups WHERE runner=:1", name)
                if matchup.get():
                    for p in matchup:
                        t1 = p.team1
                        t2 = p.team2
                    team1 = ndb.gql("SELECT * FROM Teams WHERE teamName=:1", t1)
                    team2 = ndb.gql("SELECT * FROM Teams WHERE teamName=:1", t2)
                    matchup = matchup.get()
                    team1 = team1.get()
                    team2 = team2.get()
                    adjs = matchup.adjs.split(',')
                    adjs.pop()
                    values = {
                        'matchup' : matchup,
                        'adjs' : adjs,
                        'team1' : team1,
                        'team2' : team2
                    }
                    self.render("runner.html", values)
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/')

    def post(self):
        username = self.request.cookies.get('username')
        a = username.split('|')
        name = ndb.gql("SELECT * FROM Account WHERE username=:1", a[0]).get().name
        matchup = ndb.gql("SELECT * FROM Matchups WHERE runner=:1", name)
        for p in matchup:
            t1 = p.team1
            t2 = p.team2
        team1 = ndb.gql("SELECT * FROM Teams WHERE teamName=:1", t1)
        team2 = ndb.gql("SELECT * FROM Teams WHERE teamName=:1", t2)
        matchup = matchup.get()
        team1 = team1.get()
        team2 = team2.get()
        adjs = matchup.adjs.split(',')
        adjs.pop()

        t1m1 = int(self.request.get('t1m1'))
        t1m2 = int(self.request.get('t1m2'))
        t1m3 = int(self.request.get('t1m3'))
        t2m1 = int(self.request.get('t2m1'))
        t2m2 = int(self.request.get('t2m2'))
        t2m3 = int(self.request.get('t2m3'))
        winner = self.request.get('winner')

        if winner == 't1' and t1m1+t1m2+t1m3 > t2m1+t2m2+t2m3:
        	pass
        elif winner == 't2' and t1m1+t1m2+t1m3 < t2m1+t2m2+t2m3:
        	pass
        else:
        	self.redirect('/error')

        if(t1m1 and t1m2 and t1m3 and t2m1 and t2m2 and t2m3):
            team1.mem1Score += t1m1
            team1.mem2Score += t1m2
            team1.mem3Score += t1m3
            team1.score += t1m1 + t1m2 + t1m3

            team2.mem1Score += t2m1
            team2.mem2Score += t2m2
            team2.mem3Score += t2m3
            team2.score += t2m1 + t2m2 + t2m3

            team1.put()
            team2.put()

            debater = ndb.gql("SELECT * FROM Debater WHERE name=:1", team1.member1).get()
            debater.score += '%d,' % t1m1
            debater.totalScore += t1m1
            debater.put()
            debater = ndb.gql("SELECT * FROM Debater WHERE name=:1", team1.member2).get()
            debater.score += '%d,' % t1m2
            debater.totalScore += t1m2
            debater.put()
            debater = ndb.gql("SELECT * FROM Debater WHERE name=:1", team1.member3).get()
            debater.score += '%d,' % t1m3
            debater.totalScore += t1m3
            debater.put()
            debater = ndb.gql("SELECT * FROM Debater WHERE name=:1", team2.member1).get()
            debater.score += '%d,' % t2m1
            debater.totalScore += t2m1
            debater.put()
            debater = ndb.gql("SELECT * FROM Debater WHERE name=:1", team2.member2).get()
            debater.score += '%d,' % t2m2
            debater.totalScore += t2m2
            debater.put()
            debater = ndb.gql("SELECT * FROM Debater WHERE name=:1", team2.member3).get()
            debater.score += '%d,' % t2m3
            debater.totalScore += t2m3
            debater.put()
            sleep(1)

            for i in adjs:
                adjScore = self.request.get(i)
                a = i.split('|')
                adj = ndb.gql("SELECT * FROM Adjudicator WHERE name=:1", a[0]).get()
                adj.score += '%d,' % int(adjScore)
                adj.totalScore += int(adjScore)
                adj.put()
        else:
            pass

application = webapp2.WSGIApplication([('/', MainPage), 
                                       ('/register', RegisterHandler),
                                       ('/regDesk', RegDeskHandler),
                                       ('/adminConsole', AdminConsoleHandler),
                                       ('/runner', RunnerHandler),
                                       ('/user', UserHandler)
                                       ], debug=True)
