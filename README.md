# SocketProgamming
Assignment 2 Networks: Socket Progamming Project

# SocketProgamming
Assignment 2 Networks: Socket Progamming Project

VERSION is python 3.7 / higher

Server is in SocketProgramming/src/ircserver.py
Bot is in SocketProgramming/chatbot.py

If the ip is not working then go to line 18 in ircserver.py and change self.HOST
and go to line 9 in chatbot.py and change server 

To run the server python3 ircserver.py or use ./ircserver.py
To run the bot python3 chatbot.py

Steps:
1. Run ircserver.py
2. Run chatbot.py
3. Join a channel in hexchat by doing /JOIN #test once logged in
4. On the side panel where users are shown click on Probot
5. In Probot you can use commands such as !Day !Time !Date and a random string to give a random fact this will be displayed on the channel
Probot is connected to
6. Connect another user to hexchat using a different nickname
7. you can PRIVMSG the user by doing /PRIVMSG target message
8. You can also click on thier profile to achieve this

Commands Available once user is connected:
/NICK
/USER
/JOIN
/PART
/USERS
/PRIVMSG