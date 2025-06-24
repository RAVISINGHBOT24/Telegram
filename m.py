import json
import random
import re
from pyrogram.types import ChatPermissions
from datetime import datetime, timedelta
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from pyrogram.types import Message


API_ID = 20249833
API_HASH = "4d8a602fa4581d86666033e8a1b5cd28"
BOT_TOKEN = "7712914052:AAHowCymSw9WSz9SzDsOydhXhDcIMKsdrrs"
OWNER_ID = 6481324021
BOT_USERNAME = "VIPUSERRS77_BOT"  # Without @

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

warn_data = {}
admins = set([OWNER_ID])

try:
    with open("data.json", "r") as f:
        warn_data = json.load(f)
except:
    warn_data = {}

def is_admin(user_id):
    return user_id in admins or user_id == OWNER_ID

def save_data():
    with open("data.json", "w") as f:
        json.dump(warn_data, f)

@app.on_message(filters.command("help") & filters.group)
async def help_cmd(_, m: Message):
    if not m.from_user or not is_admin(m.from_user.id): return
    help_text = '''
🤖 *Bot Commands:*

⚠️ /warn - Reply to user to warn (3 warns = ban)
🔇 /mute [1m|2h|3d] - Mute user for time
🔊 /unmute - Unmute user
🚫 /ban - Ban user
✅ /unban [user_id] - Unban by ID
👑 /promo - Make user bot admin (OWNER only)
❌ /demote - Remove from bot admin (OWNER only)
🔗 *Auto-Warn on link*
👋 Welcome + Goodbye attitude replies
/help - Show this help message
'''
    await m.reply(help_text, quote=True)

@app.on_message(filters.command("warn") & filters.group)
async def warn_user(_, m: Message):
    if not m.from_user or not is_admin(m.from_user.id): return
    if not m.reply_to_message or not m.reply_to_message.from_user:
        await m.reply("⚠️ Reply mein command do jise warn karna hai.")
        return

    user = m.reply_to_message.from_user
    uid = str(user.id)
    warn_data[uid] = warn_data.get(uid, 0) + 1
    save_data()

    if warn_data[uid] >= 3:
        try:
            await m.chat.ban_member(user.id)
            warn_data[uid] = 0
            save_data()
            await m.reply(f"🚫 {user.mention} ko 3 warnings ke baad ban kiya gaya.")
        except:
            await m.reply("❌ Ban karne mein error aaya.")
    else:
        await m.reply(f"⚠️ {user.mention} ko warning di gayi. Total: {warn_data[uid]}/3")


@app.on_message(filters.command("mute") & filters.group)
async def mute(_, m: Message):
    if not m.from_user or not is_admin(m.from_user.id):
        return

    if not m.reply_to_message or not m.reply_to_message.from_user:
        await m.reply("⚠️ Kisi user ke reply me `/mute` bhejein.")
        return

    target_id = m.reply_to_message.from_user.id
    member = await m.chat.get_member(target_id)

    if member.status in ("administrator", "creator"):
        await m.reply("⚠️ Admin ko mute nahi kar sakte.")
        return

    try:
        await m.chat.restrict_member(
            user_id=target_id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await m.reply(f"🔇 {m.reply_to_message.from_user.mention} ab mute ho chuka hai.")
    except Exception as e:
        await m.reply(f"❌ Mute karne mein error aaya.\n\nError: `{e}`")

from pyrogram.types import ChatPermissions

@app.on_message(filters.command("unmute") & filters.group)
async def unmute(_, m: Message):
    if not m.from_user or not is_admin(m.from_user.id):
        return

    # Case 1: Reply se target user
    target = None
    if m.reply_to_message and m.reply_to_message.from_user:
        target = m.reply_to_message.from_user
    # Case 2: Command me @username ya ID diya ho
    elif len(m.command) > 1:
        try:
            target = await app.get_users(m.command[1])
        except:
            await m.reply("❌ User nahi mila. Sahi @username ya ID do.")
            return
    else:
        await m.reply("⚠️ Usage: Reply karo ya `/unmute @username` use karo.")
        return

    try:
        await m.chat.restrict_member(
            user_id=target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await m.reply(f"✅ {target.mention} ab unmute ho chuka hai.")
    except Exception as e:
        await m.reply(f"❌ Unmute karne mein error aaya.\n\nError: `{e}`")

@app.on_message(filters.command("unban") & filters.group)
async def unban(_, m: Message):
    if not m.from_user or not is_admin(m.from_user.id):
        return

    # Case 1: Reply se target user
    target = None
    if m.reply_to_message and m.reply_to_message.from_user:
        target = m.reply_to_message.from_user
    # Case 2: Command me @username ya ID
    elif len(m.command) > 1:
        try:
            target = await app.get_users(m.command[1])
        except:
            await m.reply("❌ User nahi mila. Sahi @username ya ID do.")
            return
    else:
        await m.reply("⚠️ Usage: Reply karo ya `/unban @username` use karo.")
        return

    try:
        await m.chat.unban_member(target.id)
        await m.reply(f"✅ {target.mention} ab unban ho chuka hai.")
    except Exception as e:
        await m.reply(f"❌ Unban karne mein error aaya.\n\nError: `{e}`")

@app.on_message(filters.command("promo") & filters.group)
async def promo(_, m: Message):
    if not m.from_user or m.from_user.id != OWNER_ID:
        return

    target = None
    # Case 1: Reply se user
    if m.reply_to_message and m.reply_to_message.from_user:
        target = m.reply_to_message.from_user
    # Case 2: Command me @username ya ID
    elif len(m.command) > 1:
        try:
            target = await app.get_users(m.command[1])
        except:
            await m.reply("❌ User nahi mila. Sahi @username ya ID do.")
            return
    else:
        await m.reply("⚠️ Usage: Reply karo ya `/promo @username` likho.")
        return

    admins.add(target.id)
    await m.reply(f"✅ {target.mention} ab bot admin ban gaya hai.")

@app.on_message(filters.command("demote") & filters.group)
async def demote(_, m: Message):
    if not m.from_user or m.from_user.id != OWNER_ID:
        return

    target = None
    # Case 1: Reply se user
    if m.reply_to_message and m.reply_to_message.from_user:
        target = m.reply_to_message.from_user
    # Case 2: Command me @username ya ID
    elif len(m.command) > 1:
        try:
            target = await app.get_users(m.command[1])
        except:
            await m.reply("❌ User nahi mila. Sahi @username ya ID do.")
            return
    else:
        await m.reply("⚠️ Usage: Reply karo ya `/demote @username` likho.")
        return

    admins.discard(target.id)
    await m.reply(f"❌ {target.mention} ko bot admin se hata diya gaya.")

@app.on_message(filters.group & filters.text)
async def detect_links(_, m: Message):
    if not m.from_user or is_admin(m.from_user.id): return
    if re.search(r"https?://|t\\.me|@", m.text):
        await m.delete()
        uid = str(m.from_user.id)
        warn_data[uid] = warn_data.get(uid, 0) + 1
        save_data()
        if warn_data[uid] >= 3:
            try:
                await m.chat.ban_member(m.from_user.id)
                warn_data[uid] = 0
                save_data()
                await m.reply(f"🚫 {m.from_user.mention} ko 3 link ke baad ban kiya gaya.")
            except:
                pass
        else:
            await m.reply(f"⚠️ {m.from_user.mention} link mat bhejo! Warning {warn_data[uid]}/3")

@app.on_message(filters.new_chat_members)
async def welcome(_, m: Message):
    for user in m.new_chat_members:
        name = f"@{user.username}" if user.username else user.first_name
        try:
            user_info = await app.get_chat(user.id)
            if user_info.photo:
                await m.reply_photo(user_info.photo.big_file_id, caption=f"👋 Welcome {name}!")
            else:
                await m.reply(f"👋 Welcome {name}!")
        except:
            await m.reply(f"👋 Welcome {name}!")

leave_msgs = [
    "{name} gaya... Ab group main shanti hai 😎",
    "Finally {name} nikal gaya 😤",
    "{name} left... no one will miss you 😂",
    "Goodbye {name}, aur kabhi mat aana 😏",
    "{name} gaya, ab real members bache hain 💪",
    "{name} ka exit hua, group ka level up 🔥",
    "Shukr hai {name} chala gaya 🙏",
    "{name} = out. Group = peaceful 🧘‍♂️",
    "{name}, door ho ja 😒",
    "{name} gaya... party time! 🎉",
    "{name} ka farewell bina cake ke 😆",
    "{name} leave kr gaya... drama khatam 😌",
    "{name} gaya, ab tension free 😌",
    "{name} was a mistake, now corrected ✔️",
    "{name} out. Group IQ level increased 📈",
]

# Sample stats dictionary (you can link this to your data system)
stats_data = {
    "total_warns": 0,
    "total_bans": 0,
    "groups_count": 0,  # Update this dynamically if you track group joins
}

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(_, m):
    total_warned = len(warn_data)
    total_admins = len(bot_admins)
    await m.reply_text(f"📊 Bot Stats:\n\n👤 Warned Users: {total_warned}\n👑 Bot Admins: {total_admins}")

@app.on_message(filters.private & filters.command("start"))
async def start(_, m):
    buttons = [
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/VIPUSERRS77_BOT?startgroup=true")],
        [InlineKeyboardButton("👑 Owner", url="https://t.me/R_SDANGER77")]
    ]
    
    await m.reply_text(
        "**🤖 Welcome to Security Bot!**\n\n"
        "👑 *Owner:* [@R_SDANGER77](https://t.me/R_SDANGER77)\n\n"
        "🔐 Ye bot sirf group me kaam karta hai.\n"
        "✅ Bot ko kisi group me add karo tabhi commands kaam karenge.\n\n"
        "🛠️ Agar aap bot ke admin banna chahte ho, toh owner se contact karein.\n\n"
        "__Powered by attitude & security 🛡️__",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )

EMOJI_REPLIES = {
    "🔥": "Jala dala na bro! 🔥",
    "❤️": "Pyaar baatne ka shauk hai kya? ❤️",
    "😭": "Rote reh jaoge... Ravi Bhai toh OP hai 😎",
    "😂": "Hasi toh phasi 🤣",
    "😎": "Style level: Ravi Bhai 😎",
    "🤔": "Sochta hi reh gaya...",
    "💔": "Tuta dil, attitude kill 😏",
    "🤣": "Full comedy scene hai bhai!",
    "😡": "Gussa kam kar, warna warn ho jayega 😤",
    "🤡": "Tum comedian ho ya real joker? 🤡"
}

@app.on_message(filters.group & filters.text, group=4)
async def emoji_responder(_, m: Message):
    if not m.text: return
    for emoji, reply in EMOJI_REPLIES.items():
        if emoji in m.text:
            await m.reply(reply)
            break

BAD_WORDS = ["mc", "bc", "bkl", "bhosdike", "bhenchod", "madarchod", "maderchod", "chod", "lodu", "gaand", "chutiya", "chut", "randi", "gandu"]

@app.on_message(filters.group, group=2)
async def bad_word_detector(_, m: Message):
    if not m.from_user or is_admin(m.from_user.id):
        return

    msg_text = m.text.lower() if m.text else ""
    if any(word in msg_text for word in BAD_WORDS):
        await m.delete()
        user_id = str(m.from_user.id)
        chat_id = str(m.chat.id)
        warns.setdefault(chat_id, {})
        warns[chat_id].setdefault(user_id, 0)
        warns[chat_id][user_id] += 1

        warn_count = warns[chat_id][user_id]
        if warn_count >= 3:
            try:
                await m.chat.ban_member(m.from_user.id)
                await m.reply(f"🚫 {m.from_user.mention} ko 3 warnings ke baad ban kiya gaya.")
            except:
                await m.reply("❌ Ban karne mein error aaya.")
        else:
            await m.reply(f"⚠️ {m.from_user.mention} - Gaali dene par warning di gayi.\nWarning: {warn_count}/3")

@app.on_message(filters.left_chat_member)
async def bye(_, m: Message):
    user = m.left_chat_member
    name = f"@{user.username}" if user.username else user.first_name
    msg = random.choice(leave_msgs).replace("{name}", name)
    await m.reply(msg)

app.run()