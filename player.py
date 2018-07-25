import socket

from character import *
from message import *

class Player(object):

	def __init__(self, psocket, paddr, pname, charinfo):
		self.sock = psocket
		self.connected = True
		self.waitForNextBattle = False
		self.addr = paddr
		self.name = pname
		self.character = Character(charinfo['Name'], charinfo['Description'], charinfo['Health'], charinfo['Attacks'])

	def __del__(self):
		self.sock.close()

	#Two players are equal if all of their attributes match
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		else:
			return False
	def __ne__(self, other):
		return not self.__eq__(other)

	def send(self, data):
		try:
			self.sock.sendall(data)
		except socket.error:
			self.sock.close()
			return -1
		return 1
			
	def recv(self):
		try:
			msg = self.sock.recv(1024)
			if msg == b'':
				raise socket.error
			return msg
		except socket.error:
			self.sock.close()
			return ''

	def disconnect(self):
		self.sock.close()
		self.connected = False
	
	def reconnect(self, newSock):
		self.sock = newSock
		self.connected = False
		self.waitForNextBattle = True

	def isConnected(self):
		return self.connected
		
	def enable(self):
		if self.connected == False and self.waitForNextBattle == True:
			self.connected = True
			self.waitForNextBattle = False
		
	def matches(self, addr, name):
		if self.addr == addr and self.name == name:
			return True
		return False
		
	def getName(self):
		return self.name
		
	def getCharName(self):
		return self.character.getName()
			
	def getStats(self):
		return b'Player name: ' + self.name.encode() + b'\n' + self.character.getStats()

	def getAttacksStr(self):
		return self.character.getAttacksStr()

	def getAttack(self, index):
		return self.character.getAttack(index)
		
	def getNumAttacks(self):
		return self.character.getNumAttacks()

	def sendPartyStats(self, plist):
		ownStats = b'You:\n'
		if len(plist) != 1:
			otherPlayerStats = b'\nYour Party:\n'
		else:
			otherPlayerStats = b''
			
		for player in plist:
			if self.__eq__(player):
				ownStats += player.getStats()
				ownStats += player.getAttacksStr()
			else:
				otherPlayerStats += player.getStats()
				otherPlayerStats += player.getAttacksStr()

		#List your own stats first, and then list everyone elses
		self.send(StatsMsg.party + ownStats + otherPlayerStats)
		if self.recv() != StatsMsg.ack:
			print(self.name + b' did not receive party stats')
		
	def isAlive(self):
		return self.character.isAlive()
	
	def getLegalAttackIndex(self, attackStr):
		#Takes in a client's chosen attack and ensures
		#that they picked a legal move
		#Returns -1 if bad/illegal, or index in attack list
		
		if len(attackStr) > optionLen + 1:
			return -1
		option = attackStr[0:optionLen]
		if option != AttackMsg.num:
			return -1
		try:
			attack = int(attackStr[optionLen:])
		except ValueError:
			return -1
		
		if attack < 1 or attack > self.character.getNumAttacks():
			return -1
		return attack
		
	def hit(self, monster, attack):
		return self.character.hit(monster, attack)