import sys
import time
import traceback
from twitchio.ext import commands
from mcrcon import MCRcon


class Bot(commands.Bot):

    def __init__(self, twitch_config: dict, rcon_config: dict, debug: bool):
        self.ub_commands = []
        self.rcon = MCRcon(rcon_config["host"], rcon_config["password"], rcon_config["port"])
        self.help_description = ""
        self.admin_help_description = ""
        self.debug = debug
        self.channel = twitch_config["channel"]
        has_errors = True
        # TODO: Refactor
        for _ in range(6):
            try:
                self.rcon.connect()
                has_errors = False
                break
            except ConnectionRefusedError as error:
                print(error.strerror, file=sys.stderr)
            finally:
                time.sleep(5)
        if has_errors:
            sys.exit("No connection with rcon")
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
        version = self.rcon.command(f"/sc rcon.print(script.active_mods['{mod_name}'])")
        if not version or version.find("nil") >= 0:
            print(f"There's no https://mods.factorio.com/mod/{mod_name} on the server")
        else:
            print(f"Version of {mod_name} on the server: {version}")
            return version

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
                    self.rcon.command(f'/sc __useful_book__ RunRCONScript("{script_name}","{message}")')
        elif ub_command["type"] == "arguments":
            count_args = ub_command.get("count_args")

            async def _f(ctx: commands.Context):
                arguments = ctx.message.content[context_index:].strip().split()[:count_args]
                if arguments:
                    for argument in arguments:
                        argument = f"{argument}"
                    arguments = ",".join(arguments)
                    self.rcon.command(f'/sc __useful_book__ RunRCONScript("{script_name}","{arguments}")')
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

    async def close(self):
        self.rcon.disconnect()
        await super().close()
