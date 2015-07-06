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
    command = ['chat', '$\\blue{\\text{' + message + '}}$']
    command = json.dumps(command)
    yield from websocket.send(command)

@asyncio.coroutine
def Join():
    global websocket
    websocket = yield from websockets.connect('ws://hack.chat:6060')
    command = ['join', channel, nick]
    command = json.dumps(command)
    print(command)
    yield from websocket.send(command)

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

