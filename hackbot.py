import asyncio
import websockets
import json
import re
import sys
import time
from bs4 import BeautifulSoup
import urllib.request

channel = "lobby"
nick = "hackbot"
userlist = ["hackbot"]

@asyncio.coroutine
def SendMessage(message):
    print("Sending Message")
    global websocket
    #command = ['chat', '$\\blue{\\text{' + message + '}}$']
    command = ['chat', message]
    command = json.dumps(command)
    yield from websocket.send(command)

@asyncio.coroutine
def Join():
    global websocket
    websocket = yield from websockets.connect('wss://hack.chat/chat-ws')
    command = ['join', channel, nick]
    command = json.dumps(command)
    print(command)
    yield from websocket.send(command)

def WriteChannel(channel):
    target = open("channel_list", 'r+')
    with target as search:
        for line in search:
            line = line.rstrip()
            if channel == line:
                yield from SendMessage("That channel already exists though :(")
                return 0
        target.write("https://hack.chat/?" + channel + "\n")
        yield from SendMessage("New channel " + channel + " made!")

def ListChannels():
    with open("channel_list", 'r') as target:
        content = target.read()
        yield from SendMessage(content)

def ListCommands():
    with open("command_list", 'r') as target:
        content = target.read()
        yield from SendMessage(content)

def PrintURL(text):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    for url in urls:
        soup = BeautifulSoup(urllib.request.urlopen(url))
        yield from SendMessage(soup.title.string)
        print(url)

def Echo(text):
    yield from SendMessage(text)
    
def DisplayUsers():
    yield from SendMessage(str(userlist))

@asyncio.coroutine
def ParseRecv(response):
    global userlist
    parsed = json.loads(response)
    nick = parsed['nick']
    text = parsed['text']

    text = str(text.encode('ascii', 'replace').decode('ascii'))
    print(text)
    
    if len(text) < 2000:
        print(nick + ": "+ text)
    else:
        print("Message too long.")

    if nick == '*':
        print(text)
        if text.find("Users online") > 0:
            startusers = text.split("Users online: ")
            users = startusers[1].split(", ")
            for user in users:
                userlist.append(user)
                
        if text.find("joined") > 0:
            print("Someone joined.")
            name = text.split(" joined")
            yield from SendMessage("Welcome " + name[0] + "!")
            userlist.append(name[0])

        if text.find("left") > 0:
            print("Someone left.")
            name = text.split(" left")
            userlist.remove(name[0])
            

    elif nick != '*' and nick != 'hackbot': #No matter the nick
        if re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
            yield from PrintURL(text)

        text = text.lower() #Do this AFTER url testing due to caps being possibly needed for the URL
        
        if text.find("hackbot") == 0: #Hackbot commands
            if text.find("new channel") == 8:
                try:
                    channel = text.split("new channel ")
                    yield from WriteChannel(channel[1])
                except IndexError:
                    yield from SendMessage("what channel?")

            if text.find("list users") == 8 or text.find("users") == 8:
                yield from DisplayUsers()

            if text.find("list channels") == 8:
                yield from ListChannels()

            if text.find("commands") == 8 or text.find("help") == 8:
                yield from ListCommands()

            if text.find("echo") == 8:
                echotext = text.split("echo ")
                try:
                    t = echotext[1]
                    yield from Echo(echotext[1])
                except IndexError:
                    yield from SendMessage("Echo what?")
                
            if len(text) == 7:  
                yield from SendMessage('Yes?')


    
@asyncio.coroutine
def Loop():
    yield from Join()
    while True:
        response = yield from websocket.recv()
        yield from ParseRecv(response)
    


asyncio.get_event_loop().run_until_complete(Loop())

