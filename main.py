#!/usr/bin/env python
# coding: utf-8

import sys
import os
import signal
import webbrowser
import csv
import getpass
import tomli  # import tomllib in Python 3.11
import psutil
import readchar
from Bot import Bot


def lock(filename: str):
    # Prevents multiple instances
    pidfile = open(filename, mode="w+", encoding="UTF-8")
    if os.path.exists(filename):
        prev_pid = None
        pid = os.getpid()
        try:
            prev_pid = int(pidfile.readline())
            if prev_pid == pid and psutil.pid_exists(prev_pid):
                pidfile.close()
                sys.exit(0)
        except ValueError:
            pass
        pidfile.write(str(pid))
    else:
        pidfile.write(str(os.getpid()))
    pidfile.close()


lock("PUBTF_bot.lock")

twitch_config = {"prefix": "?", "channel": ""}
rcon_config = {"port": 25575}
factorio_config = {"twitch_messages": False}
debug = False  # I shouldn't do this

# Get config values
with open('configs/config.toml', encoding="UTF-8") as fileObj:
    tomlfile = tomli.loads(fileObj.read())
    if "debug" in tomlfile:
        if tomlfile["debug"]:
            debug = True
            print(f"pid: {os.getpid()}")
    if "twitch_messages" in tomlfile["Factorio"]:
        factorio_config["twitch_messages"] = tomlfile["Factorio"]["twitch_messages"]
    if "channel" in tomlfile["Twitch"]:
        twitch_config["channel"] = tomlfile["Twitch"]["channel"].strip().lower()
    if "bot_id" in tomlfile["Twitch"]:
        twitch_config["bot_id"] = tomlfile["Twitch"]["bot_id"].strip()
    if "prefix" in tomlfile["Twitch"]:
        twitch_config["prefix"] = tomlfile["Twitch"]["prefix"].strip()
    if "token" in tomlfile["Twitch"]:
        twitch_config["token"] = tomlfile["Twitch"]["token"].strip()
    if "port" in tomlfile["rcon"]:
        rcon_config["port"] = tomlfile["rcon"]["port"]
    if "host" in tomlfile["rcon"]:
        rcon_config["host"] = tomlfile["rcon"]["host"].strip()
    if "password" in tomlfile["rcon"]:
        rcon_password = tomlfile["rcon"]["password"]
        if isinstance(rcon_password, str):
            rcon_config["password"] = rcon_password.strip()
        else:
            rcon_config["password"] = rcon_password.tostring()


if not twitch_config.get("bot_id"):
    print("[ERROR] Twitch.bot_id doesn't exist in the configuration file", file=sys.stderr)
    sys.exit('''
        Go to https://dev.twitch.tv/ and login with this twitch account. Then click "Your Console"->"Register Your Application". Fill in the fields:

        name: FactorioBot
        OAuth Redirect URLs: https://twitchapps.com/tokengen/
        Category: Chat Bot

        Complete the reCAPTCHA and click save at the bottom. Copy the Client ID and paste it into config.cfg.
    ''')

if not twitch_config.get("token"):
    SCOPE = "chat:read chat:edit whispers:edit"
    url = f'https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={twitch_config.get("bot_id")}&redirect_uri=https://twitchapps.com/tokengen/&scope={SCOPE}'
    webbrowser.open(url)
    while not twitch_config.get("token"):
        twitch_config["token"] = getpass.getpass(prompt="Enter token: ").strip()


bot = Bot(twitch_config, rcon_config, debug)

bot.check_mod("useful_book")
bot.check_mod("AARR")
AARR_source = bot.get_AARR_source()
if factorio_config["twitch_messages"]:
    prefix = None
    if bot.mods.get("useful_book"):
        prefix = '__useful_book__ RunRCONScript("Print Twitch message",'
    elif AARR_source and AARR_source == "AARR":
        prefix = '__AARR__ printTwitchMessage('
    elif AARR_source and AARR_source == "level":
        prefix = 'printTwitchMessage('
    if prefix:
        @bot.event()
        async def event_message(ctx):
            # 'Runs every time a message is sent in chat.'
            if ctx.author is None:
                return
            bot.rcon.send_command(f'/sc {prefix}"{ctx.author.name}","{ctx.content}")')
    else:
        @bot.event()
        async def event_message(ctx):
            # 'Runs every time a message is sent in chat.'
            if ctx.author is None:
                return
            bot.rcon.send_command(f'/sc game.print({"", "[color=purple][Twitch][/color] ", {ctx.author.name}, {"colon"}, " ", {ctx.content}})')

if bot.mods.get("useful_book"):
    with open('configs/UB_data.csv', encoding="UTF-8", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            twitch_command = row["twitch_command"].strip()
            if twitch_command:
                twitch_command = row["twitch_command"].strip()
                script_name = row["script_name"].strip()
                command_type = row["type"].strip()
                if not twitch_command or not script_name or not command_type:
                    continue
                ub_command = {
                    "twitch_command": twitch_command,
                    "script_name": script_name,
                    "type": command_type
                }
                count_args = row["count_args"].strip()
                if count_args:
                    ub_command["count_args"] = int(count_args)
                twitch_description = row["twitch_description"].strip()
                if twitch_description:
                    ub_command["twitch_description"] = twitch_description
                bot.add_ub_command(ub_command)


class GracefulExit(SystemExit):
    def __init__(self, msg=None, code=None):
        super().__init__(msg)
        self.code = code


def sigint_handler(signum, frame):
    msg = "Ctrl-c was pressed. Do you really want to exit? y/n "
    print(msg, end="", flush=True)
    res = readchar.readchar().lower()
    if res == b'y':
        os.remove("PUBTF_bot.lock")
        raise GracefulExit(code=0)
    print("", end="\r", flush=True)
    print(" " * len(msg), end="", flush=True)  # clear the printed line
    print("    ", end="\r", flush=True)


signal.signal(signal.SIGINT, sigint_handler)
bot.run()
os.remove("PUBTF_bot.lock")

# (It's possible improve a lot of stuff, but I'll leave it as it is)
