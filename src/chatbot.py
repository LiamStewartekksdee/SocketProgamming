import socket
import datetime
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "chat.freenode.net" # Server
channel = "##bottestchannel" # Channel
botnick = "ChatBot" # Your bots nick
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n", "UTF-8")) #We are basically filling out a form with this line and saying to set all the fields to the bot nickname.
ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # assign the nick to the bot
def joinchan(chan): # join channel(s).
	ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
	ircmsg = ""
	while ircmsg.find("End of /NAMES list.") == -1:  
		ircmsg = ircsock.recv(2048).decode("UTF-8")
		ircmsg = ircmsg.strip('\n\r')
		print(ircmsg)
def ping(): # respond to server Pings.
	ircsock.send(bytes("PONG :pingisn", "UTF-8"))
def sendmsg(msg, target=channel): # sends messages to the target.
	ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))
def main():
	joinchan(channel)
	while 1:
		ircmsg = ircsock.recv(2048).decode("UTF-8")
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
main()