#Standard libraries
import sys
import socket
import string

#In house libraries
from message import *

#Constants
SERVER_NAME = 'Server'

#Globals
g_in_battle = False

def EnterLobby(csocket, msg):
	if msg.opcode == LobbyMsg.connect:
		lobby_res = 'N'
		while(lobby_res != 'Y' and lobby_res != 'y'):
			lobby_res = input('Ready to begin? (Y/N) ')
		return Msg(LobbyMsg.ready).Send(SERVER_NAME, csocket)

	elif msg.opcode == LobbyMsg.waitOnOthers:
		print("Waiting on others...")

	elif msg.opcode == LobbyMsg.beginGame:
		print("Let the game begin!")
	
	return True

def PrintStats(csocket, msg):
	global g_in_battle
	
	if msg.opcode == StatsMsg.monster and g_in_battle == False:
		g_in_battle = True
		print('A monster draws near your party!')
	print(msg.str)
	
	return Msg(StatsMsg.ack).Send(SERVER_NAME, csocket)

def InBattle(csocket, msg):
	if msg.opcode == AttackMsg.result:
		#Print the results of an attack made by an entity
		print(msg.str)
		return Msg(AttackMsg.ack).Send(SERVER_NAME, csocket)
	elif msg.opcode == AttackMsg.request:
		#Server is requesting the client to make an attack
		print('Your turn!!')
		num_attacks = int(msg.str)
		chosen_attack = -1
		while chosen_attack < 1 or chosen_attack > num_attacks:
			try:
				chosen_attack = int(input('Choose an attack (enter number between 1 and ' + str(num_attacks) + '): '))
			except ValueError:
				print('Not an integer')
				chosen_attack = -1
		return Msg(AttackMsg.response, str(chosen_attack)).Send(SERVER_NAME, csocket)

def ConnectToServer(saddr):
	try:
		csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		csocket.connect((saddr, 80))
	except socket.error:
		print('Could not connect to server!')
		return None
	
	return csocket

def GameLoop(cname, csocket):
	#Send the server the chosen name
	good_connection = Msg(NameMsg.name, cname).Send(SERVER_NAME, csocket)
	while(good_connection):
		#Receive a message from the server
		msg = Msg().Recv(SERVER_NAME, csocket)
		if msg.opcode == BAD_OPCODE:
			good_connection = False
			break
		
		#Handle the server's message
		if msg.head == NameMsg.head:
			if msg.opcode == NameMsg.bad:
				print('Name already taken!')
				good_connection = False
		elif msg.head == LobbyMsg.head:
			good_connection = EnterLobby(csocket, msg)
		elif msg.head == StatsMsg.head:
			good_connection = PrintStats(csocket, msg)
		elif msg.head == AttackMsg.head:
			good_connection = InBattle(csocket, msg)
		elif msg.head == EndMsg.head:
			if msg.opcode == EndMsg.loss:
				print('Your party has lost!')
			else:
				print('Your party has won!')
			good_connection = Msg(EndMsg.ack).Send(SERVER_NAME, csocket)
			break
		else:
			print('Server sent a bad message: "' + msg + '"')

def Main():
	if len(sys.argv) < 3:
		print('Enter your name and the IP address for the server.')
		exit()

	cname = sys.argv[1]
	saddr = sys.argv[2]
	
	csocket = ConnectToServer(saddr)
	if csocket == None:
		return
	
	GameLoop(cname, csocket)
	
	csocket.close()

if __name__ == '__main__':
	Main()
