from google.appengine.ext import ndb
import hashlib
from ndbEntities import *
import random

def sampleRegistrations():

	Debater(name = 'Ankit Muchhala', institute = 'DAIICT').put()
	Debater(name = 'Baruni', institute = 'DAIICT').put()
	Debater(name = 'Chaitanya', institute = 'DAIICT').put()
	Debater(name = 'Yognik', institute = 'NLUJ').put()
	Debater(name = 'NIyam', institute = 'NLUJ').put()
	Debater(name = 'Akshay', institute = 'NLUJ').put()
	Debater(name = 'Ram', institute = 'Nirma').put()
	Debater(name = 'Shyam', institute = 'Nirma').put()
	Debater(name = 'Lam', institute = 'Nirma').put()
	Debater(name = 'andy', institute = 'RAMJAS').put()
	Debater(name = 'sandy', institute = 'RAMJAS').put()
	Debater(name = 'pandy', institute = 'RAMJAS').put()
	Debater(name = 'rita', institute = 'LSR').put()
	Debater(name = 'sita', institute = 'LSR').put()
	Debater(name = 'gita', institute = 'LSR').put()
	Debater(name = 'ron', institute = 'NLS').put()
	Debater(name = 'shon', institute = 'NLS').put()
	Debater(name = 'don', institute = 'NLS').put()

	Adjudicator(name = 'Sid', institute='RAMJAS').put()
	Adjudicator(name ='Rahul', institute='NLUD').put()
	Adjudicator(name = 'Sahil', institute = 'RAMJAS').put()
	Adjudicator(name = 'Kushan', institute='DAIICT').put()
	Adjudicator(name = 'Komal', institute='DAIICT').put()
	Adjudicator(name = 'Chirag', institute='DAIICT').put()
	Adjudicator(name = 'Akshar', institute='DAIICT').put()
	Adjudicator(name = 'Suyash', institute='LSR').put()
	Adjudicator(name = 'Rambo', institute='LSR').put()
	Adjudicator(name = 'Juhi', institute='Nirma').put()

	Teams(teamName = 'DAIICT1', institute = 'DAIICT', member1 = 'Ankit Muchhala', member2 = 'Baruni', member3 = 'Chaitanya').put()
	Teams(teamName = 'WTF', institute = 'NLUJ', member1 = 'NIyam', member2 = 'Yognik', member3 = 'Akshay').put()
	Teams(teamName = 'Dudes', institute='NLS', member1 ='ron', member2 = 'shon', member3='don').put()
	Teams(teamName = 'whores', institute='LSR', member1 = 'rita', member2 = 'sita', member3 = 'gita').put()
	Teams(teamName = 'RAMJASS', institute='RAMJAS', member1='andy', member2 = 'sandy', member3='pandy').put()
	Teams(teamName = 'Washing Powder', institute = 'Nirma', member1 = 'Ram', member2 = 'Shyam', member3 = 'Lam').put()

def checkRunner(name, hashString):
	if (hashString == hashlib.sha256(name+'upod1rwKHRmHzHuEYBzY').hexdigest()):
		return True
	else:
		return False

def verify(username, password):
	a = ndb.gql("SELECT * FROM Account WHERE username=:1", username).get()
	if a:
		storedPass = a.password
		if(hashlib.sha256(password).hexdigest() == storedPass):
			return True
		else:
			return False
	else:
		return False

def generatePassword():
	password = ''
	for i in [0,6]:
		symbol = random.choice('abcdefghijklmnopqrstuvwxyz1234567890')
		password += symbol
	return password