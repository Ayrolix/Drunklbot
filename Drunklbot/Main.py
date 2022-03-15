import os
import sys
import time
import json
import twitchio

from twitchio.ext import commands
from twitchio.ext.commands.errors import CommandOnCooldown
from Economy import Economy

twitch_oauth = ""
twitch_secret = ""
twitch_id = ""

class Nykitna(commands.Bot):
	def __init__(self):
		super().__init__(token = twitch_oauth, prefix = "$", client_secret = twitch_secret, initial_channels = ["drunklockholmes"])
	
	async def event_ready(self):
		print("Ready!")

	async def event_message(self, message : twitchio.Message):
		message.content = message.content.lower()
		await self.handle_commands(message = message)
	
	async def event_command_error(self, context : commands.Context, error):
		if isinstance(error, commands.errors.CommandOnCooldown):
			await context.send(f"{context.command.name} is on cooldown for {int(error.retry_after) // 60} minutes.")

	async def event_error(self, error, data: str = None):
		if isinstance(error, AttributeError):
			pass

	@commands.command(name = "help")
	async def helps(self, context : commands.Context, *, command = None):
		if command is not None:
			if command == "balance":
				await context.send("Usage: $balance. Description: Shows you the balances in your wallet and bank.")
			elif command == "deposit":
				await context.send("Usage: $deposit <amount>. Description: Takes money out of your wallet and puts it into your bank.")
			elif command == "withdraw":
				await context.send("Usage: $withdraw <amount>. Description: Takes money out of your bank and puts it into your wallet.")
			elif command == "gamble":
				await context.send("Usage: $gamble <amount>. Description: Gambles the specific amount of money for a chance to win more.")
			elif command == "rob":
				await context.send("Usage: $rob <user_mention>. Description: Attempts to rob the specified user.")
			elif command == "give":
				await context.send("Usage: $give <user_mention> <amount>. Description: Gives the mentioned user a specific amount of money from your wallet.")
			else:
				await context.send(f"There's no command called {command}.")
		else:
			await context.send("Help usage: $help <command>. Example commands: balance, deposit, withdraw, gamble, rob, give.")

if __name__ == "__main__":
	Client = Nykitna()
	Econ = Economy(Client)
	Client.add_cog(Econ)
	Econ.commit_changes.start()
	Client.run()
