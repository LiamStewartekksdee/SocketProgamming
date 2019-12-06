#Sources Used: https://linuxacademy.com/blog/linux-academy/creating-an-irc-bot-with-python3/

import socket  	 #Imports the Socket library
import datetime  #Imports the datetime library

#Sets the socket,server,channel and bot name here
thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "127.0.0.1" 
channel = "#test" 
botname = "Prsdassdasdsaasobot" 		 
name = "Admin"

#Connects to the the sever and names the bot
thesocket.connect((server, 6667))

thesocket.send(bytes("USER "+ botname +" "+ botname +" "+ botname + " " + botname + "\n", "UTF-8")) 

thesocket.send(bytes("NICK "+ botname +"\n", "UTF-8"))


#Function to allow the bot to respond to pings
def ping(): 
	thesocket.send(bytes("PONG :pingisn", "UTF-8"))
	
#Function which allows the bot to join a channel	
def joinchan(chan): 
	thesocket.send(bytes("JOIN "+ chan +"\n", "UTF-8")) 
	themessage = ""
	
	if(themessage.find("End of /NAMES list.") == -1):  
	
		themessage = thesocket.recv(2048).decode("UTF-8")
		
		themessage = themessage.strip('\n\r')
		
		print(themessage)
		
		
#Function which sends a message to the bots given target 
def sendmsg(msg, target):
	thesocket.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))
	
#Main method for the bot program	
def main():
	joinchan(channel)
	while 1:
	
		themessage = thesocket.recv(2048).decode("UTF-8")
		
		themessage = themessage.strip('\n\r')
		
		print(themessage)
		
		#Function that will initialse user and message 
		if themessage.find("PRIVMSG") != -1:
			name = themessage.split('!',1)[0][1:]
			message = themessage.split('PRIVMSG',1)[1].split(':',1)[1]
			if len(name) < 17:
				#Function that allows the bot to display todays date
				if message.find('!Date') != -1:
					showDate = datetime.datetime.now()
					theDate = showDate.strftime('%Y-%m-%d')
					sendmsg('The date is: ' + theDate,channel)
					
				#Function that allows the bot to display the day of the week.
				elif message.find('!Day') != -1:
					showDay = datetime.datetime.now()
					theDay = showDay.strftime('%A')
					sendmsg('Today is: ' + theDay,channel)
					
				#Function that allows for the bot to display the time.
				elif message.find('!Time') != -1:
					showTime = datetime.datetime.now()
					theTime = showTime.strftime('%H:%M')
					sendmsg('The time is: ' + theTime,channel)
					
				#Function that allows the bot to reply to s user.
				elif message.find('Hello ' + botname) != -1:
				   sendmsg("Hello there " + name + "!", channel)
				   
				#Function that allows the bot to respond to private message and send a fact to the user
				elif themessage.find('PRIVMSG ' + botname) != -1:
					sendmsg('Hi there! Here is a random fact for ya: Did you know the input for the very famous Konami code is UP UP DOWN DOWN LEFT RIGHT LEFT RIGHT B A START!',name)
		else:
			#Function which pings to the channel
			if themessage.find("PING :") != -1:
				ping()
main()