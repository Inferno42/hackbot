import asyncio
import websockets
import json
import re
import time
from bs4 import BeautifulSoup
import urllib.request

loop = None

class Hackbot:

    channel = "lobby"
    nick = "hackbot"
    socket = None

    userchecked = False

    userlist = []

    def __init__(self):
        print("Hackbot object created.")

    @asyncio.coroutine
    def Connect(self, dest):
        login_payload = {'cmd': 'join',
                         'channel': self.channel,
                         'nick': self.nick}
        self.socket = yield from websockets.connect(dest)

        command = json.dumps(login_payload)

        yield from self.socket.send(command)

    @asyncio.coroutine
    def SendMessage(self, message):
        chat = {'cmd': 'chat',
               'text': message}

        command = json.dumps(chat)
        yield from self.socket.send(command)

    def StartLoop(self):
        yield from self.Loop()

    @asyncio.coroutine
    def Loop(self):
        print("Loop Established")
        while True:
            response = yield from self.socket.recv()
            yield from self.ParseRecv(response)

    @asyncio.coroutine
    def ListCommands(self):
        with open("command_list", 'r') as target:
            content = target.read()
            yield from self.SendMessage(content)

    @asyncio.coroutine
    def ListChannels(self):
        with open("channel_list", 'r') as target:
            content = target.read()
            yield from self.SendMessage(content)

    @asyncio.coroutine
    def PrintURL(self, text):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        for url in urls:
            soup = BeautifulSoup(urllib.request.urlopen(url))
            yield from self.SendMessage(soup.title.string)
            print(url)

    @asyncio.coroutine
    def WriteChannel(self, channel):
        target = open("channel_list", 'r+')
        with target as search:
            for line in search:
                line = line.rstrip()
                if channel == line:
                    yield from self.SendMessage("That channel already exists though :(")
                    return 0
            target.write("https://hack.chat/?" + channel + "\n")
            yield from self.SendMessage("New channel " + channel + " made!")

    @asyncio.coroutine
    def ParseRecv(self, response):
        parsed = json.loads(response)
        print(parsed)

        if self.userchecked == False:
            self.userlist = parsed['nicks']
            self.userchecked = True
            print(self.userlist)

        nick = ""
        text = ""
        cmd = ""

        cmd = parsed["cmd"] #There will always be a cmd

        try:
            nick = parsed["nick"]
        except KeyError:
            nick = '*' #No nick means it was the server

        try:
            text = parsed["text"]
        except KeyError:
            text = ""

        text = str(text.encode('ascii', 'replace').decode('ascii'))

        if len(text) < 2000:
            print(nick + ": "+ text)
        else:
            print("Message too long.")

        if nick != '*' and nick != 'hackbot': #No matter the nick
            if re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
                yield from self.PrintURL(text)

            text = text.lower() #Do this AFTER url testing due to caps being possibly needed for the URL

            if cmd == "onlineRemove": #left
                self.userlist.remove(nick)

            if cmd == "onlineAdd": #joined
                self.userlist.append(nick)
                yield from self.SendMessage("Welcome " + nick + "!")

            if text.find("hackbot") == 0: #Hackbot commands
                if text.find("new channel") == 8:
                    try:
                        channel = text.split("new channel ")
                        if len(channel[1]) <= 15:
                            yield from self.WriteChannel(channel[1])
                        else:
                            yield from self.SendMessage("Channel too long.")
                    except IndexError:
                        yield from self.SendMessage("what channel?")

                if text.find("list users") == 8 or text.find("users") == 8:
                    yield from self.SendMessage(str(self.userlist))

                if text.find("list channels") == 8:
                    yield from self.ListChannels()

                if text.find("commands") == 8 or text.find("help") == 8:
                    yield from self.ListCommands()

                if text.find("echo") == 8:
                    echotext = text.split("echo ")
                    try:
                        t = echotext[1]
                        yield from self.SendMessage(echotext[1])
                    except IndexError:
                        yield from self.SendMessage("Echo what?")

                if len(text) == 7:
                    yield from self.SendMessage('Yes?')

def StartUp():
    hackbot = Hackbot()
    print("Starting Hackbot")
    print("Connecting to server")
    yield from hackbot.Connect('wss://hack.chat/chat-ws')
    print("Connected!")
    print("Starting Loop")
    yield from hackbot.StartLoop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(StartUp())
    loop.close()



