""" Google Text to Speech
Available Commands:
.tts LanguageCode as reply to a message
.tts LangaugeCode | text to speak"""
from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.') / 'config.env'
load_dotenv(dotenv_path=env_path)

import asyncio
import os, sys
import subprocess
from datetime import datetime

from gtts import gTTS
import logging
from telethon import TelegramClient, events, functions, types
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")


if BOT_TOKEN is None:
    logging.info("Please give a Bot Token to run")
    print("Please give a Bot Token to run")
    sys.exit()

telebot = TelegramClient("TG_BOT", api_id=API_ID, api_hash=API_HASH)
telebot.start(bot_token=BOT_TOKEN)

@telebot.on(events.NewMessage(pattern="^/tts "))
async def _(event):

    if event.fwd_from:

        return

    input_str = event.pattern_match.group(1)

    start = datetime.now()

    if event.reply_to_msg_id:

        previous_message = await event.get_reply_message()

        text = previous_message.message

        lan = input_str

    elif "|" in input_str:

        lan, text = input_str.split("|")

    else:

        await event.reply("Invalid Syntax. Stopping.")

        return

    text = text.strip()

    lan = lan.strip()

    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):

        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)

    required_file_name = Config.TMP_DOWNLOAD_DIRECTORY + "voice.ogg"

    try:

        tts = gTTS(text, lang=lan)

        tts.save(required_file_name)

        command_to_execute = [
            "ffmpeg",
            "-i",
            required_file_name,
            "-map",
            "0:a",
            "-codec:a",
            "libopus",
            "-b:a",
            "100k",
            "-vbr",
            "on",
            required_file_name + ".opus",
        ]

        try:

            t_response = subprocess.check_output(
                command_to_execute, stderr=subprocess.STDOUT
            )

        except (subprocess.CalledProcessError, NameError, FileNotFoundError) as exc:

            await event.reply(str(exc))

            # continue sending required_file_name

        else:

            os.remove(required_file_name)

            required_file_name = required_file_name + ".opus"

        end = datetime.now()

        ms = (end - start).seconds

        await telebot.send_file(
            event.chat_id,
            required_file_name,
            # caption="Processed {} ({}) in {} seconds!".format(text[0:97], lan, ms),
            reply_to=event.message.reply_to_msg_id,
            allow_cache=False,
            voice_note=True,
        )

        os.remove(required_file_name)

        await event.reply("Processed {} ({}) in {} seconds!".format(text[0:97], lan, ms))

        await asyncio.sleep(5)

        await event.delete()

    except Exception as e:

        await event.reply(str(e))
