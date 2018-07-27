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

class AttackMsg:
	head = b'A'
	
	#Server sends number of attacks to client and requests client to pick one
	request = head + b'Q:'
	#Client responds with an attack
	response = head + b'A:'
	#Server calculates an attack, and relays the 
	#results to all clients.
	#Client responds with an ack
	result = head + b'R:'
	
	ack = head + b'A:'
	
class EndMsg:
	head = b'E'
	
	#Server says party wins
	win = head + b'W:'
	#Server says party loses
	loss = head + b'L:'
	
	#Client says ack
	ack = head + b'A:'