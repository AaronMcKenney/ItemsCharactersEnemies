class Character(object):

	def __init__(self, cname, cdesc, chealth, cmana, cattacks):
		self.name = cname
		self.description = cdesc
		self.maxHealth = chealth
		self.health = chealth
		self.maxMana = cmana
		self.mana = cmana
		self.attacks = cattacks

	def getName(self):
		return self.name
		
	def getStats(self):
		statsOut = 'Character name: ' + self.name + '\n'
		statsOut += '\tDescription: ' + self.description + '\n'
		statsOut += '\tHP: ' + str(self.health) + '/' + str(self.maxHealth) + '\n'
		statsOut += '\tMP: ' + str(self.mana) + '/' + str(self.maxMana) + '\n'

		return statsOut.encode()
		
	def getAttacksStr(self):
		attacksOut = '\tAttacks: \n'
		count = 0
		for attack in self.attacks:
			count += 1
			attacksOut += '\t\t' + str(count) + ". " + attack['Name'] + ": " + str(attack['Damage']) + '\n'
		
		return attacksOut.encode()

	def getAttack(self, index):
		return self.attacks[index]
		
	def getNumAttacks(self):
		attacksOut = 0
		for attack in self.attacks:
			attacksOut += 1
		
		return attacksOut

	def isAlive(self):
		if self.health > 0:
			return True
		return False
		
	def hit(self, monster, attack):
		#Get attacked by monster with attack
		#Calculate new hp and string to send to party
		resultStr = monster.getName() + ' used ' + attack['Name'] + '!\n'
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
		
		return resultStr.encode()