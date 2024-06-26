import os
import logging
import asyncio
from telethon import Button, TelegramClient, events
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - [%(levelname)s] - %(message)s'
)
LOGGER = logging.getLogger(__name__)

api_id = int(os.environ.get("APP_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("TOKEN")
client = TelegramClient('client', api_id, api_hash).start(bot_token=bot_token)
spam_chats = []

@client.on(events.NewMessage(pattern="^/start$"))
async def start(event):
    await event.reply(
        "**I am User Tagger Bot**,\n\nI will help you to mention near about all members in your group or channel..🫧",
        link_preview=False,
        buttons=(
            [
                Button.url("ᴏᴡɴᴇʀ", url="https://t.me/JARVIS_V2"),
                Button.url("sᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/JARVIS_V_SUPPORT")
            ]
        )
    )

@client.on(events.NewMessage(pattern="^/help$"))
async def help(event):
    helptext = "**Help Menu of User Tagger Bot**\n\nCommand: /utag\nYou can use this command with text or reply to text that you want to say to others.\n\n/atag\nYou can use this command with text or reply to text to tag all admins on group."
    await event.reply(
        helptext,
        link_preview=False,
        buttons=(
            [
                Button.url("ᴏᴡɴᴇʀ", url="https://t.me/JARVIS_V2"),
                Button.url("sᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/JARVIS_V_SUPPORT")
            ]
        )
    )

async def mention_users(event, mode, msg):
    chat_id = event.chat_id
    if event.is_private:
        return await event.respond("__This command can be used in groups and channels!__")

    if event.pattern_match.group(1) and event.is_reply:
        return await event.respond("__Give me one argument!__")
    elif event.pattern_match.group(1):
        mode = "text_on_cmd"
        msg = event.pattern_match.group(1)
    elif event.is_reply:
        mode = "text_on_reply"
        msg = await event.get_reply_message()
        if msg == None:
            return await event.respond("__I can't mention members for older messages! (messages which are sent before I'm added to this group)__")
    else:
        return await event.respond("__Reply to a message or give me some text to mention others!__")

    spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ''
    async for usr in client.iter_participants(chat_id):
        if not chat_id in spam_chats:
            break
        usrnum += 1
        usrtxt += f"[{usr.first_name}](tg://user?id={usr.id}) "
        if usrnum == 5:
            if mode == "text_on_cmd":
                txt = f"{usrtxt}\n\n{msg}"
                await client.send_message(chat_id, txt, link_preview=False, parse_mode='markdown')
            elif mode == "text_on_reply":
                await msg.reply(usrtxt, link_preview=False, parse_mode='markdown')
            await asyncio.sleep(2)
            usrnum = 0
            usrtxt = ''
    try:
        spam_chats.remove(chat_id)
    except:
        pass

@client.on(events.NewMessage(pattern="^/utag ?(.*)"))
async def utag(event):
    await mention_users(event, "text_on_cmd", event.pattern_match.group(1))

@client.on(events.NewMessage(pattern="^/atag ?(.*)"))
async def atag(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.respond("__This command can be used in groups and channels!__")

    try:
        participants = await client.get_participants(chat_id)
    except:
        return await event.respond("__Failed to fetch participants!__")

    admin_mentions = []
    for participant in participants:
        if (
            isinstance(participant.participant,
            (
                ChannelParticipantAdmin,
                ChannelParticipantCreator
            ))
        ):
            admin_mentions.append(f"[{participant.first_name}](tg://user?id={participant.id})")

    if admin_mentions:
        admin_mentions_text = ", ".join(admin_mentions)
        if event.pattern_match.group(1):
            msg = event.pattern_match.group(1)
            await client.send_message(chat_id, f"{admin_mentions_text}\n\n {msg}", link_preview=False, parse_mode='markdown')
        elif event.is_reply:
            msg = await event.get_reply_message()
            if msg == None:
                return await event.respond("__I can't mention members for older messages! (messages which are sent before I'm added to this group)__")
            await msg.reply(admin_mentions_text, link_preview=False, parse_mode='markdown')
        else:
            await client.send_message(chat_id, admin_mentions_text, link_preview=False, parse_mode='markdown')
    else:
        await event.respond("__No admins found in this group or channel!__")

@client.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
    if not event.chat_id in spam_chats:
        return await event.respond('__There is no process ongoing...__')
    else:
        try:
            spam_chats.remove(event.chat_id)
        except:
            pass
        return await event.respond('__Stopped.__')

print(">> Jarvis User TAgger Robot Started <<")
client.run_until_disconnected()
