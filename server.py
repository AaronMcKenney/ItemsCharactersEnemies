import sys
import time
import socket
import thread
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
connections = []
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
	global numConnections, connections, players

	while 1:
		(csocket, caddr) = ssocket.accept()
		#Upon connection, get the client's name
		try:
			msg = csocket.recv(1024)
			if msg == '' or msg[0:headerLen] != NameMsg.head:
				raise socket.error
		except socket.error as e:
			csocket.close()
			return
		cname = msg[headerLen:]

		numConnections += 1
		
		if mode == lobby:
			#We are in the lobby
			connections.append((csocket, caddr, cname))
			print("New connection: " + cname + " at " + caddr[0])
			csocket.sendall(LobbyMsg.connect)
			thread.start_new_thread(clientThread, (csocket, caddr, cname))

		elif mode == inCombat:
			for player in disconnected(players):
				if player.matches(caddr, cname):
					player.reconnect(csocket)
					break
			
def clientThread(csocket, caddr, cname):
	global numConnections, numReady, everyoneReady

	isReady = False

	#Receive client messages
	try:
		msg = csocket.recv(1024)
		if msg == '':
			raise socket.error
	except socket.error as e:
		csocket.close()
		numConnections -= 1
		connections.pop(connections.index((csocket, caddr, cname)))
		if isReady == True:
			numReady -= 1
		print caddr[0] + ' closed!'
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


def createPlayers():
	global connections

	charFile = open('characters.json', 'r')
	characters = json.load(charFile)
	characters = characters["Characters"]
	shuffle(characters)

	plist = []

	for i, (csocket, caddr, cname) in enumerate(connections):
		plist.append(Player(csocket, caddr, cname, characters[i]))

	return plist
	
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
		if player.isConnected:
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
		print 'no players in battle!'
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
		for thing in turnList:
			if type(thing) is Player and thing.isAlive():
				#Tell the player it's their turn
				thing.send(AttackMsg.one + '\nYour turn!\n' + thing.getAttacksStr())
				msg = thing.recv()
				if msg != AttackMsg.ack:
					#Assume a disconnect, remove them from this battle
					#Pray that they reconnect before the next battle
					turnList.remove(thing)
					thing.disconnect()
					print thing.getName() + ' did not recv attack attack msg. Booting from battle'
					if len(connected(players)) == 0:
						return 0
					continue
					
				#Ask the player to choose an attack
				thing.send(AttackMsg.num + str(thing.getNumAttacks()))
				chosenAttack = thing.recv()
				attackIndex = thing.getLegalAttackIndex(chosenAttack)
				if attackIndex == -1:
					#Illegal (or bad) attack
					#Remove them from battle and put them in the corner
					turnList.remove(thing)
					thing.disconnect()
					print thing.getName() + ' did not recv attack index msg. Booting from battle'
					if len(connected(players)) == 0:
						return 0
					continue
				chosenAttack = thing.getAttack(attackIndex-1)

				#Send results of attack to all players
				resultStr = curMonster.hit(thing, chosenAttack)
				for player in connected(players):
					player.send(AttackMsg.many + resultStr)
					msg = player.recv()
					if msg != AttackMsg.ack:
						#Assume a disconnect, remove them from this battle
						#Pray that they reconnect before the next battle
						turnList.remove(player)
						player.disconnect()
						print player.getName() + ' did not recv player attack attack msg. Booting from battle'
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
					player.send(AttackMsg.many + resultStr)
					msg = player.recv()
					if msg != AttackMsg.ack:
						turnList.remove(player)
						player.disconnect()
						print player.getName() + ' did not recv monster attack attack msg. Booting from battle'
				if len(connected(players)) == 0:
					return 0
				if not partyLives(players):
					return -1
def main():
	global everyoneReady, mode, players

	ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		ssocket.bind(('', 80))
	except socket.error as msg:
		print("Bind failed. Error code: " + str(msg[0]))
		quit()

	ssocket.listen(5)
	print("Server ready")

	thread.start_new_thread(serverThread, (ssocket,))

	#If everyone is ready, start the game
	everyoneReady.acquire()
	while(numReady != numConnections or numConnections == 0):
		#Don't start the game until all players in lobby are ready
		everyoneReady.wait()
	everyoneReady.release()

	for client in connections:
		client[0].sendall(LobbyMsg.beginGame)
	mode = inCombat

	print("Ready set go!")
	players = createPlayers()
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
		print 'the party has lost'
	elif res == 1:
		end = EndMsg.win
		print 'the party has won'
	else:
		print 'the party has left/disconnected ;~;'
	for player in connected(players):
		player.send(end)
		if player.recv() != EndMsg.ack:
				print player.getName() + ' did not get EndMsg'				
	
	print 'shutting down'
if __name__ == '__main__':
	main()
