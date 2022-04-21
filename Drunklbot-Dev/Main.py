import os
import sys
import time
import json

from twitchio.ext import commands
from Economy import Economy

twitch_oauth = ""
twitch_secret = ""
twitch_id = ""

class Nykitna(commands.Bot):
	def __init__(self):
		super().__init__(token = twitch_oauth, prefix = "$", client_secret = twitch_secret, initial_channels = ["drunklockholmes"])

		with open(os.path.join(os.getcwd(), "Admins.json"), "r") as f:
			self.admins = json.load(f)
			f.close()
	
	async def event_ready(self):
		print("Ready!")

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

	@commands.command(name = "shutdown")
	async def shutdown(self, context : commands.Context):
		if context.author.name not in self.admins:
			await context.send("Unauthorized.")
		else:
			self.close()
			time.sleep(2)
			sys.exit(0)

if __name__ == "__main__":
	Client = Nykitna()
	Client.add_cog(Economy(Client))
	Client.run()
