import sys
import socket
import string

from message import *

inBattle = False

def enterLobby(csocket, msg):
	if msg == LobbyMsg.connect:
		lobbyRes = "N"
		while(lobbyRes != "Y" and lobbyRes != "y"):
			lobbyRes = raw_input("Ready to begin? (Y/N) ")
		csocket.sendall(LobbyMsg.ready)

	elif msg == LobbyMsg.waitOnOthers:
		print("Waiting on others...")

	elif msg == LobbyMsg.beginGame:
		print("Let the game begin!")

def printStats(csocket, option, msg):
	global inBattle
	
	if option == StatsMsg.monster and inBattle == False:
		inBattle = True
		print 'A monster draws near your party!'
	print msg
		
	csocket.sendall(StatsMsg.ack)

def inBattle(csocket, option, message):
	if option == AttackMsg.one or option == AttackMsg.many:
		#Print what attacks the client's character can make
		print message
		csocket.sendall(AttackMsg.ack)
	elif option == AttackMsg.num:
		#Server is requesting the client to make an attack
		numAttacks = int(message)
		chosenAttack = -1
		while chosenAttack < 1 or chosenAttack > numAttacks:
			try:
				chosenAttack = int(raw_input("Choose an attack (enter number between 1 and " + str(numAttacks) + "): "))
			except ValueError:
				print 'Not an integer'
				chosenAttack = -1
		csocket.sendall(AttackMsg.num + str(chosenAttack))
	elif option == AttackMsg.many:
		#Server is printing results of an attack made
		print message
	
def main():
	if len(sys.argv) < 3:
		print('Enter your name and the IP address for the server.')
		exit()

	cname = sys.argv[1]
	saddr = sys.argv[2]
	csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	csocket.connect((saddr, 80))

	try:
		csocket.sendall(NameMsg.head + cname)
		while(1):
			try:
				msg = csocket.recv(1024)
				if msg == '':
					raise socket.error
			except socket.error as e:
				print("Didn't receive data from the server!")
				exit()

			msgHead = msg[0:headerLen]
				
			if msgHead == LobbyMsg.head:
				enterLobby(csocket, msg)

			elif msgHead == StatsMsg.head:
				printStats(csocket, msg[0:optionLen], msg[optionLen:])
				
			elif msgHead == ConnMsg.head:
				if msg == ConnMsg.ping:
					csocket.sendall(ConnMsg.pong)
					
			elif msgHead == AttackMsg.head:
				inBattle(csocket, msg[0:optionLen], msg[optionLen:])
			
			elif msgHead == EndMsg.head:
				if msg == EndMsg.loss:
					print 'Your party has lost!'
					csocket.sendall(EndMsg.ack)
				else:
					print 'Your party has won!'
					csocket.sendall(EndMsg.ack)
				csocket.close()
				return
			
			else:
				print 'Server sent a bad message: ', msg
	finally:
			csocket.close()

if __name__ == '__main__':
	main()
