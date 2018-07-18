#Messages must have the same format between the client and server

#Headers must have the same length
#Headers must be unique
headerLen = 1
optionLen = headerLen + 2

#Client sends name upon connecting to server
class NameMsg:
	head = b'N'

class LobbyMsg:
	head = b'L'

	#Server related lobby messages
	connect = head + b'C:'
	waitOnOthers = head + b'W:'
	beginGame = head + b'B:'
	#Client related lobby messages
	ready = head + b'Y:'
	notReady = head + b'N:'

#Server sends stats to clients
#Client requests stats from clients
class StatsMsg:
	head = b'S'

	#Server related stats messages
	self = head + b'Y:'
	party = head + b'P:'
	monster = head + b'M:'
	#Cliient related stats messages
	ack = head + b'A:'
	
#Make sure that a client is alive
class ConnMsg:
	head = b'P'
	
	#Server related message
	ping = head + b'I:'
	#Client related message
	pong = head + b'O:'

class AttackMsg:
	head = b'A'
	
	#Server requests an attack from client,
	#client responds with ack
	one = head + b'O:'
	#Server sends number of attacks to client
	#Client responds with an attack
	num = head + b'N:'
	#Server calculates an attack, and relays the 
	#results to all clients.
	#Client responds with an ack
	many = head + b'M:'
	
	ack = head + b'A:'
	
class EndMsg:
	head = b'E'
	
	#Server says party wins
	win = head + b'W:'
	#Server says party loses
	loss = head + b'L:'
	
	#Client says ack
	ack = head + b'A:'