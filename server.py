import sys
import time
import socket
import threading
import json
from random import shuffle

from message import *
from player import *
from monster import *

#Global vars
numConnections = 0
numReady = 0
everyoneReady = threading.Condition()
players = []

#mode that the game is in and potential values (enum) for mode
lobby = 0
inCombat = 1

mode = lobby

def connected(players):
	connectedPlayers = []

	for player in players:
		if player.isConnected():
			connectedPlayers.append(player)
			
	return connectedPlayers

def disconnected(players):
	disconnectedPlayers = []
	
	for player in players:
		if not player.isConnected():
			disconnectedPlayers.append(player)
			
	return disconnectedPlayers

def enableAll(players):
	for player in players:
		player.enable()
	
def serverThread(ssocket):
	global numConnections, players

	while 1:
		(csocket, caddr) = ssocket.accept()
		#Upon connection, get the client's name
		try:
			msg = csocket.recv(1024)
			if msg == b'' or msg[0:optionLen] != NameMsg.name:
				raise socket.error
		except socket.error as e:
			csocket.close()
			return
		cname = msg[optionLen:].decode()
		
		badName = False
		for player in connected(players):
			if cname == player.name:
				print('REJECTED New connection: "' + cname + '" at ' + caddr[0] + ' due to duplicate name')
				csocket.sendall(NameMsg.bad)
				badName = True
				break
		if badName:
			continue

		numConnections += 1
		
		newPlayer = True
		for player in disconnected(players):
			if player.matches(caddr, cname):
				player.reconnect(csocket)
				newPlayer = False
				break
		
		if mode == lobby:
			if newPlayer:
				players.append(Player(csocket, caddr, cname))
			print('ACCEPTED New connection: "' + cname + '" at ' + str(caddr))
			csocket.sendall(LobbyMsg.connect)
			threading.Thread(target=clientThread, args=((csocket, caddr, cname))).start()
			
def clientThread(csocket, caddr, cname):
	global numConnections, numReady, everyoneReady, players

	isReady = False

	#Receive client messages
	try:
		msg = csocket.recv(1024)
		if msg == b'':
			raise socket.error
	except socket.error as e:
		for player in players:
			if player.matches(caddr, cname):
				player.disconnect()
				numConnections -= 1
				if isReady == True:
					numReady -= 1
				print(caddr[0] + ' closed!')
				return

	#Client ready to begin
	if msg == LobbyMsg.ready:
		if isReady != True:
			numReady += 1
			isReady = True
			print(cname + " is ready!")

		if numReady == numConnections:
			#Notify main thread to start game
			everyoneReady.acquire()
			everyoneReady.notifyAll()
			everyoneReady.release()
		else:
			csocket.sendall(LobbyMsg.waitOnOthers)

	elif msg == LobbyMsg.notReady:
		if isReady != False:
			numReady -= 1
			isReady = False
			print(caddr[0] + " is not ready!")

def createCharacters():
	global players

	charFile = open('characters.json', 'r')
	characters = json.load(charFile)
	characters = characters["Characters"]
	shuffle(characters)

	for i, player in enumerate(players):
		player.setCharacter(characters[i])
	
def createMonsters():

	monstFile = open('monsters.json', 'r')
	monsters = json.load(monstFile)
	monsters = monsters["Monsters"]
	shuffle(monsters)

	mlist = []

	for monst in monsters:
		mlist.append(Monster(monst['Name'], monst['Description'], monst['Health'], monst['Attacks']))

	return mlist
	
def getConnectedPlayers(players):
	connPlayers = []
	for player in players:
		if player.isConnected():
			connPlayers.append(player)
			
	return connPlayers
	
def partyLives(players):
	for player in players:
		if player.isAlive():
			return True
	return False
	
def battle(curMonster):
	#Battle between players and one monster
	#Returns 1 if players win, -1 if monster wins,
	#and 0 if all players disconnects
	global players
	
	#Ensures that a player can only be lost from this battle
	if len(players) == 0:
		print('no players in battle!')
		return 0
	for player in connected(players):
		player.send(StatsMsg.monster + curMonster.getStats())
		if player.recv() != StatsMsg.ack:
			player.disconnect()
		
	#Get turn order
	turnList = list(players) #list() creates deep copy
	turnList.append(curMonster)
	shuffle(turnList)
	
	while(curMonster.isAlive() and partyLives(connected(players))):
		for entity in turnList:
			if type(entity) is Player and entity.isAlive():
				#Ask the player to choose an attack
				entity.send(AttackMsg.request + str(entity.getNumAttacks()).encode())
				chosenAttack = entity.recv()
				attackIndex = entity.getLegalAttackIndex(chosenAttack)
				if attackIndex == -1:
					#Illegal (or bad) attack
					#Remove them from battle and put them in the corner
					turnList.remove(entity)
					entity.disconnect()
					print(entity.getName() + ' did not recv attack index msg. Booting from battle')
					if len(connected(players)) == 0:
						return 0
					continue
				chosenAttack = entity.getAttack(attackIndex-1)

				#Send results of attack to all players
				resultStr = curMonster.hit(entity, chosenAttack)
				for player in connected(players):
					player.send(AttackMsg.result + resultStr)
					msg = player.recv()
					if msg != AttackMsg.ack:
						#Assume a disconnect, remove them from this battle
						#Pray that they reconnect before the next battle
						turnList.remove(player)
						player.disconnect()
						print(player.getName() + ' did not recv player attack attack msg. Booting from battle')
				if len(connected(players)) == 0:
					return 0
				if not curMonster.isAlive():
					turnList.remove(curMonster)
					return 1
				
			else:
				#Monster's turn
				(chosenPlayer, chosenAttack) = curMonster.getRandAttack(players)
				resultStr = chosenPlayer.hit(curMonster, chosenAttack)
				for player in connected(players):
					player.send(AttackMsg.result + resultStr)
					msg = player.recv()
					if msg != AttackMsg.ack:
						turnList.remove(player)
						player.disconnect()
						print(player.getName() + ' did not recv monster attack attack msg. Booting from battle')
				if len(connected(players)) == 0:
					return 0
				if not partyLives(players):
					return -1
				
def main():
	global everyoneReady, mode, players

	ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		ssocket.bind(('', 80))
	except socket.error as err_msg:
		print("Bind failed. Error code: " + str(err_msg[0]))
		quit()

	ssocket.listen(5)
	print("Server ready")

	threading.Thread(target=serverThread, args=(ssocket,)).start()

	#If everyone is ready, start the game
	everyoneReady.acquire()
	while(numReady != numConnections or numConnections == 0):
		#Don't start the game until all players in lobby are ready
		everyoneReady.wait()
	everyoneReady.release()

	for player in players:
		player.send(LobbyMsg.beginGame)
	mode = inCombat

	print("Ready set go!")
	createCharacters()
	for player in players:
		player.sendPartyStats(players)

	monsters = createMonsters()
	
	#Start Game 
	res = 0
	for monster in monsters:
		enableAll(players)
		res = battle(monster)
		if res != 1:
			break
	
	if res == -1:
		end = EndMsg.loss
		print('The party has lost')
	elif res == 1:
		end = EndMsg.win
		print('The party has won')
	else:
		print('The party has left/disconnected ;~;')
	for player in connected(players):
		player.send(end)
		if player.recv() != EndMsg.ack:
				print(player.getName() + ' did not get EndMsg')		
	
	print('shutting down')

if __name__ == '__main__':
	main()
