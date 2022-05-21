import os
import sys
import time
import json
from twitchio.ext import commands
import factorio_rcon
from factorio_rcon import RCONConnectError
from factorio_rcon import InvalidPassword


class RCON(factorio_rcon.RCONClient):
    def connect(self):
        has_errors = True
        for _ in range(6):
            try:
                super().connect()
                has_errors = False
                break
            except RCONConnectError as error:
                print(error.args[0], file=sys.stderr)
            except InvalidPassword as error:
                sys.exit(error.args[0])
            finally:
                time.sleep(5)
        if has_errors:
            os.remove("PUBTF_bot.lock")  # TODO: improve
            sys.exit("No connection with rcon")


class Bot(commands.Bot):
    mods = None

    def __init__(self, twitch_config: dict, rcon_config: dict, debug: bool):
        self.ub_commands = []
        self.rcon = RCON(rcon_config["host"], rcon_config["port"], rcon_config["password"])
        self.help_description = ""
        self.admin_help_description = ""
        self.debug = debug
        self.channel = twitch_config["channel"]
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=twitch_config["token"], prefix=twitch_config["prefix"], initial_channels=[twitch_config["channel"]])

    async def event_ready(self):
        if self.debug:
            print(f"Bot name: {self.nick}")
            print(f"User id: {self.user_id}")
            print(f"Events: {self.events}")
            print(f"Commands: {self.commands}")
        if len(self.connected_channels) == 0:
            print(f'Bot didn\'t connect to "{self.channel}" channel')
            await self.close()
        elif self.debug:
            print(f"Connected channels: {self.connected_channels}")

    @commands.command()
    async def help(self, ctx: commands.Context):
        nick = ctx.author.name
        if nick == self.nick:
            await ctx.send(f"{self.admin_help_description}")
        elif nick == self.channel:
            await ctx.channel.send(f"/w @{nick} {self.admin_help_description}")  # ctx.channel.whisper seems wrong
        elif self.help_description:
            await ctx.channel.send(f"/w @{nick} {self.help_description}")  # ctx.channel.whisper seems wrong

    def check_mod(self, mod_name: str):
        version = self.mods.get(mod_name)
        if not version:
            print(f"There's no https://mods.factorio.com/mod/{mod_name} on the server")
        else:
            print(f"Version of {mod_name} on the server: {version}")

    # TOOD: refactor
    def add_ub_command(self, ub_command: dict) -> bool:
        _f = None
        script_name = ub_command["script_name"]
        twitch_command = ub_command["twitch_command"]
        context_index = len(twitch_command) + 2
        if ub_command["type"] == "message":
            async def _f(ctx: commands.Context):
                message = ctx.message.content[context_index:].strip()
                if message:
                    self.rcon.send_command(f'/sc __useful_book__ RunRCONScript("{script_name}","{message}")')
        elif ub_command["type"] == "arguments":
            count_args = ub_command.get("count_args")

            async def _f(ctx: commands.Context):
                arguments = ctx.message.content[context_index:].strip().split()[:count_args]
                if arguments:
                    for argument in arguments:
                        argument = f"{argument}"
                    arguments = ",".join(arguments)
                    self.rcon.send_command(f'/sc __useful_book__ RunRCONScript("{script_name}","{arguments}")')
        if _f:
            twitch_description = ub_command.get("twitch_description")
            if twitch_description:
                self.help_description = f'{self.help_description}{twitch_command} - {twitch_description}\n'
                self.admin_help_description = f'{self.admin_help_description}{twitch_command} - {twitch_description}\n'
            else:
                self.help_description = f'{self.help_description}{twitch_command}\n'
                self.admin_help_description = f'{self.admin_help_description}{twitch_command}\n'
            self.ub_commands.append(ub_command)
            self.add_command(commands.Command(twitch_command, _f))
            return True
        return False

    def get_AARR_source(self):
        return self.rcon.send_command('/sc if remote.interfaces.AARR then remote.call("AARR", "getSource") end')

    def connect_to_rcon(self):
        self.rcon.connect()
        message = self.rcon.send_command("/sc rcon.print(game.table_to_json(script.active_mods))")
        self.mods = json.loads(message)

    async def close(self):
        self.rcon.close()
        await super().close()
