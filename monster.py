import random
import player

class Monster(object):

	def __init__(self, mname, mdesc, mhealth, mattacks):
		self.name = mname
		self.description = mdesc
		self.maxHealth = mhealth
		self.health = mhealth
		self.attacks = mattacks

	def getName(self):
		return self.name
		
	def getStats(self):
		statsOut = 'Monster name: ' + self.name + '\n'
		statsOut += '\tDescription: ' + self.description + '\n'
		statsOut += '\tHP: ' + str(self.health) + '/' + str(self.maxHealth) + '\n'

		return statsOut

	def getAttacksStr(self):
		attacksOut = '\tAttacks: \n'
		for attack in self.attacks:
			attacksOut += '\t\t' + attack['Name'] + ": " + str(attack['Damage']) + '\n'
		
		return attacksOut
		
	def getAttack(self, index):
		return self.attacks[index]
		
	def getRandAttack(self, players):
		chosenPlayer = random.choice(players)
		chosenAttack = random.choice(self.attacks)
		return (chosenPlayer, chosenAttack)

	def getHealth(self):
		return self.health
		
	def isAlive(self):
		if self.health > 0:
			return True
		return False
		
	def hit(self, player, attack):
		#Get attacked by player with attack
		#Calculate new hp and string to send to party
		resultStr = player.getCharName() + ' used ' + attack['Name'] + '!\n'
		prevHealth = self.health
		self.health -= attack['Damage']
		if self.health < 0:
			self.health = 0
		
		damageDealt = prevHealth - self.health
		resultStr += self.name + ' took ' + str(damageDealt) + ' damage\n'
		resultStr += self.name + ' has ' + str(self.health) + ' HP left\n'
	
		if not self.isAlive():
			resultStr += self.name + ' has been slain!\n'
		
		resultStr += '\n'
		
		return resultStr