import asyncio
import websockets
import json
import sys

channel = "meta"
nick = "hackbot"

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

def ListChannels():
    target = open("channel_list", 'r')
    with target as search:
        for line in search:
            line = line.rstrip()
            yield from SendMessage(line)

def ListCommands():
    target = open("command_list", 'r')
    with target as search:
        for line in search:
            line = line.rstrip()
            yield from SendMessage(line)

@asyncio.coroutine
def ParseRecv(response):
    parsed = json.loads(response)
    nick = parsed['nick']
    text = parsed['text']
    if len(text) < 2000:
        print(nick + ": "+ text)
    else:
        print("Message too long.")

    if nick == '*':
        
        if text.find("joined") > 0:
            print("Someone joined.")
            name = text.split(" joined")
            yield from SendMessage("Welcome " + name[0] + "!")

    elif nick != '*': #No matter the nick
        if text.find("hackbot") == 0:
            if text.find("new channel") == 8:
                channel = text.split("new channel ")
                yield from WriteChannel(channel[1])

            if text.find("list channels") == 8:
                yield from ListChannels()

            if text.find("commands") == 8:
                yield from ListCommands()
                
            if len(text) == 7:  
                yield from SendMessage('Yes?')
            if nick == "Inferno":
                if text.find("leave") == 8:
                    sys.exit(0)


    
            
        

@asyncio.coroutine
def Loop():
    yield from Join()
    while True:
        response = yield from websocket.recv()
        yield from ParseRecv(response)
    


asyncio.get_event_loop().run_until_complete(Loop())

