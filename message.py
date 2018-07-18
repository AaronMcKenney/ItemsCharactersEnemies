#Messages must have the same format between the client and server

#Headers must have the same length
#Headers must be unique
headerLen = 1
optionLen = headerLen + 2

#Client sends name upon connecting to server
class NameMsg:
	head = 'N'

class LobbyMsg:
	head = 'L'

	#Server related lobby messages
	connect = head + 'C:'
	waitOnOthers = head + 'W:'
	beginGame = head + 'B:'
	#Client related lobby messages
	ready = head + 'Y:'
	notReady = head + 'N:'

#Server sends stats to clients
#Client requests stats from clients
class StatsMsg:
	head = 'S'

	#Server related stats messages
	self = head + 'Y:'
	party = head + 'P:'
	monster = head + 'M:'
	#Cliient related stats messages
	ack = head + 'A:'
	
#Make sure that a client is alive
class ConnMsg:
	head = 'P'
	
	#Server related message
	ping = head + 'I:'
	#Client related message
	pong = head + 'O:'

class AttackMsg:
	head = 'A'
	
	#Server requests an attack from client,
	#client responds with ack
	one = head + 'O:'
	#Server sends number of attacks to client
	#Client responds with an attack
	num = head + 'N:'
	#Server calculates an attack, and relays the 
	#results to all clients.
	#Client responds with an ack
	many = head + 'M:'
	
	ack = head + 'A:'
	
class EndMsg:
	head = 'E'
	
	#Server says party wins
	win = head + 'W:'
	#Server says party loses
	loss = head + 'L:'
	
	#Client says ack
	ack = head + 'A:'