from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from userbot.events import register
from userbot import bot
from time import sleep
import random
import os
from telethon.tl.types import MessageMediaPhoto
import asyncio
from PIL import Image, ImageDraw, ImageFont
import textwrap
from userbot.cmdhelp import CmdHelp


from userbot.language import get_value
LANG = get_value("scrapers_bot")


def is_message_image(message):
    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            return True
        if message.media.document:
            if message.media.document.mime_type.split("/")[0] == "image":
                return True
        return False
    return False


async def silently_send_message(conv, text):
    await conv.send_message(text)
    response = await conv.get_response()
    await conv.mark_read(message=response)
    return response


def MemeYap(Resim, Text, FontS=40, Bottom=False, BottomText=None):
    Foto = Image.open(Resim)
    Yazi = ImageDraw.Draw(Foto)
    FontSize = 20
    ImgFraction = float(f"0.{FontS}")

    Font = ImageFont.truetype("./userbot/fonts/impact.ttf", FontSize)
    while Font.getsize(Text)[0] < ImgFraction * Foto.size[0]:
        FontSize += 1
        Font = ImageFont.truetype("./userbot/fonts/impact.ttf", FontSize)
    FontSize -= 1
    Font = ImageFont.truetype("./userbot/fonts/impact.ttf", FontSize)

    def drawTextWithOutline(text, x, y):
        Yazi.text((x - 2, y - 2), text, (0, 0, 0), font=Font)
        Yazi.text((x + 2, y - 2), text, (0, 0, 0), font=Font)
        Yazi.text((x + 2, y + 2), text, (0, 0, 0), font=Font)
        Yazi.text((x - 2, y + 2), text, (0, 0, 0), font=Font)
        Yazi.text((x, y), text, (255, 255, 255), font=Font)

    w, h = Yazi.textsize(Text, Font)
    Satirlar = textwrap.wrap(Text, width=22)
    lastY = -h

    for i in range(0, len(Satirlar)):
        w, h = Yazi.textsize(Satirlar[i], Font)
        x = Foto.width / 2 - w / 2
        y = i * h
        drawTextWithOutline(Satirlar[i], x, y)

        if Bottom:
            Bottom_Satirlar = textwrap.wrap(BottomText, width=22)
            lastY = Foto.height - h * (len(Bottom_Satirlar) + 1) - 10

            for i in range(0, len(Bottom_Satirlar)):
                w, h = Yazi.textsize(Bottom_Satirlar[i], Font)
                x = Foto.width / 2 - w / 2
                y = lastY + h
                drawTextWithOutline(Bottom_Satirlar[i], x, y)
                lastY = y

    Foto.save("neon.png")


@register(outgoing=True, pattern="^.sangmata(?: |$)(.*)")
async def sangmata(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.edit('🔸 __Bir mesaja cavab olaraq işlətməlisən.__')
        return
    reply_message = await event.get_reply_message()
    if not reply_message.text:
        await event.edit(LANG['REPLY_MSG'])
        return
    chat = "@SangMataInfo_bot"
    reply_message.sender
    if reply_message.sender.bot:
        await event.edit('**Bu insan deyil! Bu botdur.** ❌')
        return
    await event.edit(LANG['WORKING_ON'])
    async with bot.conversation(chat, exclusive=False) as conv:
        response = None
        try:
            msg = await reply_message.forward_to(chat)
            response = await conv.get_response(message=msg, timeout=5)
        except YouBlockedUserError:
            await event.edit("__Hmmm.. {chat} əngəllənib.__ __Get əngəli aç sonra gəl.__ 😒")
            return
        except Exception as e:
            print(e.__class__)

        if not response:
            await event.edit(LANG['NOT_RESPONSE'])
        elif response.text.startswith("Forward"):
            await event.edit('__Bu istifadəçi öz profilini gizli saxladığı üçün mən onun haqqında heç bir şey əldə edə bilmədim. Di get topunla oyna..__ 😒')
        else:
            await event.edit(response.text)
        sleep(1)
        await bot.send_read_acknowledge(chat, max_id=(response.id + 3))
        await conv.cancel_all()


@register(outgoing=True, pattern="^.meme ?((\\d*)(.*))")
async def memeyap(event):
    """ """
    font = event.pattern_match.group(2)
    if font == "":
        font = 35
    else:
        font = int(font)
    text = event.pattern_match.group(3)
    await event.edit(LANG['MEMING'])
    if event.is_reply:
        reply = await event.get_reply_message()
        if ";" in text:
            Split = text.split(";")
            Bottom = True
            Text = Split[0]
            BottomText = Split[1]
        else:
            Bottom = False
            Text = text
            BottomText = None

        if reply.photo:
            Resim = await reply.download_media()
        elif reply.sticker and reply.file.ext == ".webp":
            if os.path.exists("./Neon.png"):
                os.remove("./Neon.png")

            foto = await reply.download_media()
            im = Image.open(foto).convert("RGB")
            im.save("Neon.png", "png")
            Resim = "Neon.png"
        elif reply.sticker and reply.file.ext == ".tgs":
            sticker = await reply.download_media()
            os.system(
                f"lottie_convert.py --frame 0 -if lottie -of png '{sticker}' NeonSticker.png")
            os.remove(sticker)
            Resim = "Neon.png"
        elif reply.media:
            Resim = await reply.download_media()
            Sure = os.system(
                "ffmpeg -i '" +
                Resim +
                "' 2>&1 | grep Duration | awk '{print $2}' | tr -d , | awk -F ':' '{print ($3+$2*60+$1*3600)/2}'``")
            os.system(
                f"ffmpeg -i '{Resim}' -vcodec mjpeg -vframes 1 -an -f rawvideo -ss {Sure} NeonThumb.jpg")
            os.remove(Resim)
            Resim = 'NeonThumb.jpg'
        else:
            return await event.edit(LANG['REPLY_TO_MEME'])

        if os.path.exists("./neonrmeme.png"):
            os.remove("./neonmeme.png")

        MemeYap(Resim, Text, font, Bottom, BottomText)
        await event.client.send_file(event.chat_id, "./neonmeme.png", reply_to=reply)
        await event.delete()
        os.remove(Resim)
    else:
        await event.edit(LANG['REPLY_TO_MEME'])


@register(outgoing=True, pattern="^.scan")
async def scan(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.edit(LANG['REPLY_TO_MESSAGE'])
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await event.edit(LANG['REPLY_TO_FILE'])
        return
    chat = "@DrWebBot"
    reply_message.sender
    if reply_message.sender.bot:
        await event.edit(LANG['REPLY_USER_ERR'])
        return
    await event.edit(LANG['MIZAH_EXE'])
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(
                    incoming=True,
                    from_users=161163358))
            await event.client.forward_messages(chat, reply_message)
            response = await response
        except YouBlockedUserError:
            await event.reply(LANG['BLOCKED_CHAT'])
            return

        if response.text.startswith("Forward"):
            await event.edit(LANG['USER_PRIVACY'])
        elif response.text.startswith("Select"):
            await event.client.send_message(chat, "English")
            await event.edit(LANG['WAIT_EDIT'])

            response = conv.wait_event(
                events.NewMessage(
                    incoming=True,
                    from_users=161163358))
            await event.client.forward_messages(chat, reply_message)
            response = conv.wait_event(
                events.NewMessage(
                    incoming=True,
                    from_users=161163358))
            response = await response

            await event.edit(f"**{LANG['SCAN_RESULT']}:**\n {response.message.message}")

        elif response.text.startswith("Still"):
            await event.edit(LANG['SCANNING'])

            response = conv.wait_event(
                events.NewMessage(
                    incoming=True,
                    from_users=161163358))
            response = await response
            if response.text.startswith("No threats"):
                await event.edit(LANG['CLEAN'])
            else:
                await event.edit(f"**{LANG['VIRUS_DETECTED']}**\n\nƏtraflı məlumat: {response.message.message}")


@register(outgoing=True, pattern="^.creation")
async def creation(event):
    if not event.reply_to_msg_id:
        await event.edit(LANG['REPLY_TO_MSG'])
        return
    reply_message = await event.get_reply_message()
    if event.fwd_from:
        return
    chat = "@creationdatebot"
    reply_message.sender
    if reply_message.sender.bot:
        await event.edit(LANG['REPLY_TO_MSG'])
        return
    await event.edit(LANG['CALCULATING_TIME'])
    async with event.client.conversation(chat) as conv:
        try:
            await event.client.forward_messages(chat, reply_message)
        except YouBlockedUserError:
            await event.reply(f"**Hmmm, deyəsən {chat} əngəlləmisən. Xaiş əngəldən çıxar.**")
            return

        response = conv.wait_event(
            events.NewMessage(
                incoming=True,
                from_users=747653812))
        response = await response
        if response.text.startswith("Looks"):
            await event.edit(LANG['PRIVACY_ERR'])
        else:
            await event.edit(f"**Məlumat hazırdı:** `{response.text.replace('**','')}`")


@register(outgoing=True, pattern="^.ocr2")
async def ocriki(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.edit(LANG['REPLY_TO_MSG'])
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await event.edit(LANG['REPLY_TO_MSG'])
        return
    chat = "@bacakubot"
    reply_message.sender
    if reply_message.sender.bot:
        await event.edit(LANG['REPLY_TO_MSG'])
        return
    await event.edit(LANG['READING'])
    async with event.client.conversation(chat) as conv:
        try:
            await event.client.forward_messages(chat, reply_message)
        except YouBlockedUserError:
            await event.reply(f"`Mmmh deyəsən` {chat} `əngəlləmisən. Xaiş əngəldən çıxar.`")
            return

        response = conv.wait_event(
            events.NewMessage(
                incoming=True,
                from_users=834289439))
        response = await response
        if response.text.startswith("Please try my other cool bot:"):
            response = conv.wait_event(
                events.NewMessage(
                    incoming=True,
                    from_users=834289439))
            response = await response

        if response.text == "":
            await event.edit(LANG['OCR_ERROR'])
        else:
            await event.edit(f"**{LANG['SEE_SOMETHING']}: **`{response.text}`")

from userbot import bot
import telethon

@register(outgoing=True, pattern="^.voicy")
async def voicy(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.edit(LANG['REPLY_TO_MSG'])
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await event.edit(LANG['REPLY_TO_MSG'])
        return
    chat = "@Voicybot"
    reply_message.sender
    if reply_message.sender.bot:
        await event.edit(LANG['REPLY_TO_MSG'])
        return
    await event.edit("__Səsi dinləyirəm...__")
    async with event.client.conversation(chat) as conv:
        try:
            await event.client.forward_messages(chat, reply_message)
        except YouBlockedUserError:
            await event.reply(f"`Hmm. Deyəsən,` {chat} `əngəlləmisən. Onun əngəlini qaldırıram.`")
            await bot(telethon.tl.functions.contacts.UnblockRequest(chat))

        response = conv.wait_event(events.MessageEdited(incoming=True,from_users=259276793))
        response = await response
        if response.text.startswith("__👋"):
            await event.edit(LANG['VOICY_LANG_ERR'])
        elif response.text.startswith("__👮"):
            await event.edit(LANG['VOICY_ERR'])
        else:
            await event.edit(f"**{LANG['HEAR_SOMETHING']}: **`{response.text}`")


Help = CmdHelp('scraper')
Help.add_command('sangmata','<cavab>','Seçilən istifadəçinin ad keçmişinə baxmaq.')
Help.add_command('scan','<cavab>','Seçilən faylda virus olub olmadığına baxın.')
Help.add_command('meme','<font> <üst;alt>','Fotoya yazı əlavə edin. İstəyirsinizsə font böyüklüyünüdə  yaza bilərsiz.','meme 20 vuqar')
Help.add_command('voicy','<cavab>','Səsi yazıya çevirin.')
Help.add_command('ocr2','<cavab>','Fotodakı yazını oxuyun.')
Help.add_command('creation','<cavab>','Cavab verdiyiniz insanın hesabının yaradılış tarixini öyrənin.')
Help.add()
