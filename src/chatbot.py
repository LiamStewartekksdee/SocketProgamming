import socket
import datetime



# clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server = "localhost" # Server
# channel = "##bottestchannel" # Channel
# botnick = "ChatBot" # Your bots nick

# irc_server = ircserver((server, 6667))
# irc_server_addr, irc_server_hostname = irc_server.get_server_info()


class irc_bot:
	def __init__(self, clientsock, serversock, botnick):
		self.clientsock = clientsock
		self.botnick = botnick
		clientsock.send(bytes("USER "+ self.botnick +" "+ self.botnick +" "+ self.botnick + " " + self.botnick + "\n", "UTF-8")) #We are basically filling out a form with this line and saying to set all the fields to the bot nickname.
		clientsock.send(bytes("NICK "+ self.botnick +"\n", "UTF-8")) # assign the nick to the bot

	
	def joinchan(self, chan): # join channel(s).
		self.clientsock.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
		ircmsg = ""
		while ircmsg.find("End of /NAMES list.") == -1:  
			ircmsg = serversock.recv(2048).decode("UTF-8")
			ircmsg = ircmsg.strip('\n\r')
			print(ircmsg)
	
	def ping(self): # respond to server Pings.
		self.clientsock.send(bytes("PONG :pingisn", "UTF-8"))
	
	def sendmsg(self, msg, target='#bottest'): # sends messages to the target.
		self.clientsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))

def main():
	joinchan(channel)
	while 1:
		ircmsg = clientsock.recv(2048).decode("UTF-8")
		ircmsg = ircmsg.strip('\n\r')
		print(ircmsg)
		if ircmsg.find("PRIVMSG") != -1:
			name = ircmsg.split('!',1)[0][1:]
			message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
			if len(name) < 17:
				if message.find('!Date') != -1:
					showDate = datetime.datetime.now()
					theDate = showDate.strftime('%Y-%m-%d')
					sendmsg('The date is: ' + theDate)
					
				if message.find('!Day') != -1:
					showDay = datetime.datetime.now()
					theDay = showDay.strftime('%A')
					sendmsg('Today is: ' + theDay)
					
				if message.find('!Time') != -1:
					showTime = datetime.datetime.now()
					theTime = showTime.strftime('%H:%M')
					sendmsg('The time is: ' + theTime)
					
				if message.find('Hello ' + botnick) != -1:
				   sendmsg("Hello " + name + "!")    
		else:
			if ircmsg.find("PING :") != -1:
				ping()

# if __name__ == '__main__':
# 	main()