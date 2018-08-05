#Standard Libraries
import socket

#Messages must have the same format between the client and server
#This library ensures that this occurs

#Constants
#Headers must have the same length
#Headers must be unique
HEADER_LEN = 1
OPCODE_LEN = HEADER_LEN + 2
BAD_OPCODE = b''

#Client sends name upon connecting to server
class NameMsg:
	head = b'N'
	
	#Client sends name
	name = head + b'N:'
	
	#Server either accepts the name and adds the client or rejects the client
	good = head + b'G:'
	bad = head + b'B:'

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

class Msg:
	def __init__(self, opcode=BAD_OPCODE, str=''):
		self.opcode = opcode
		if len(opcode) >= OPCODE_LEN:
			self.head = opcode[0:HEADER_LEN]
		else:
			self.head = BAD_OPCODE
		self.str = str
	
	def Send(self, receiver_name, sock):
		data = self.opcode + self.str.encode()
		
		try:
			sock.sendall(data)
		except socket.error:
			print('Send Error: Failed to send data to "' + receiver_name + '"')
			return False
			
		return True
		
	def Recv(self, sender_name, sock, exp_opcode=BAD_OPCODE):
		(self.opcode, self.str) = (BAD_OPCODE, '')
		
		try:
			data = sock.recv(1024)
			if len(data) < OPCODE_LEN:
				raise socket.error	
				
			(self.opcode, self.str) = (data[0:OPCODE_LEN], data[OPCODE_LEN:].decode())
			if exp_opcode != BAD_OPCODE and self.opcode != exp_opcode:
				raise socket.error
				
		except socket.error:
			exp_opcode_str = b''
			if exp_opcode != BAD_OPCODE:
				exp_opcode_str = b', Expected Opcode was: ' + exp_opcode_str
			print('Receive Error: Got "' + data.decode() +  '" from "' + sender_name + '"' + exp_opcode_str.decode())
		
		return Msg(self.opcode, self.str)
		