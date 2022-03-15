import logging
import twitchio
import random
import json
import schedule

from twitchio.ext import commands, routines

class Economy(commands.Cog):
	def __init__(self, client) -> None:
		self.client : commands. = client
		self.currency = "Spuds"
		self.hip = False
		self.participants : dict = {}
		self.victims : list = []
		with open("Data/Wallets.json", "r") as f:
			self.wallets : dict = json.load(f)
			f.close()
		with open("Data/Banks.json", "r") as f:
			self.banks : dict = json.load(f)
			f.close()

	async def get_user_wallet(self, user):
		return self.wallets[user]

	async def set_user_wallet(self, user, amount):
		self.wallets[user] = amount

	async def get_user_bank(self, user):
		return self.banks[user]
	
	async def set_user_bank(self, user, amount):
		self.banks[user] = amount

	async def create_user_data(self, user):
		if user not in self.wallets:
			if user not in self.banks:
				self.banks[user] = 5000
			self.wallets[user] = 0
		elif user not in self.banks:
			if user not in self.wallets:
				self.wallets[user] = 0
			self.banks[user] = 5000

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Routines
# ------------------------------------------------------------------------------------------------------------------------------------------------------

	@routines.routine(seconds = 5)
	async def commit_changes(self):
		with open("Data/Wallets.json", "w") as f:
			json.dump(self.wallets, f, indent = 4)
			f.close()
		with open("Data/Banks.json", "w") as f:
			json.dump(self.banks, f, indent = 4)
			f.close()

	@routines.routine(seconds = 5)
	async def run_pending(self):
		schedule.run_pending()

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Private Commands
# ------------------------------------------------------------------------------------------------------------------------------------------------------

	@commands.command(name = "currency")
	async def set_currency(self, context : commands.Context, new_currency_name : str):
		if context.author.name == "drunklockholmes" or context.author.name == "keshimae":
			new_currency_name = new_currency_name.capitalize()
			self.currency = new_currency_name
		else:
			await context.send("Not allowed to change the currency name.")

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Public Commands
# ------------------------------------------------------------------------------------------------------------------------------------------------------

	# -------------------------------------------------------------------------------------------------------
	# Balance Command
	# -------------------------------------------------------------------------------------------------------

	@commands.command(name = "balance", aliases = ["wealth"])
	async def balance(self, context : commands.Context):
		user = str(context.author.id)
		await self.create_user_data(user)
		wallet, bank = await self.get_user_wallet(user), await self.get_user_bank(user)
		await context.send(f"Wallet = {wallet} {self.currency} ; Bank = {bank} {self.currency}.")

	# -------------------------------------------------------------------------------------------------------
	# Deposit Command
	# -------------------------------------------------------------------------------------------------------

	@commands.command(name = "deposit")
	async def deposit(self, context : commands.Context, *, amount):
		user = str(context.author.id) ; await self.create_user_data(user)
		wallet, bank = await self.get_user_wallet(user), await self.get_user_bank(user)
		try:
			amount = abs(float(amount))
			if amount <= wallet:
				bank += amount ; wallet -= amount
				await self.set_user_wallet(user, wallet) ; await self.set_user_bank(user, bank)
				await context.send(f"Moved {amount} {self.currency} to the bank.")
			else:
				await context.send("Not enough in your wallet to deposit.")
		except Exception as e:
			if isinstance(e, ValueError):
				if amount == "all":
					bank += wallet ; wallet -= wallet
					await self.set_user_wallet(user, wallet) ; await self.set_user_bank(user, bank)
					await context.send(f"Moved all {self.currency} into the bank.")
				elif amount == "half":
					half = wallet / 2
					bank += half ; wallet -= half
					await self.set_user_wallet(user, wallet) ; await self.set_user_bank(user, bank)
					await context.send(f"Moved {half} {self.currency} into your bank.")	

	# -------------------------------------------------------------------------------------------------------
	# Withdraw Command
	# -------------------------------------------------------------------------------------------------------

	@commands.command(name = "withdraw")
	async def withdraw(self, context : commands.Context, *, amount):
		user = str(context.author.id) ; await self.create_user_data(user)
		wallet, bank = await self.get_user_wallet(user), await self.get_user_bank(user)
		try:
			amount = abs(float(amount))
			if amount <= bank:
				wallet += amount ; bank -= amount
				await self.set_user_wallet(user, wallet) ; await self.set_user_bank(user, bank)
				await context.send(f"Moved {amount} {self.currency} to your wallet ")
			else:
				await context.send("You don't have enough to move to your wallet.")
		except Exception as E:
			if isinstance(E, ValueError):
				if amount == "all":
					wallet += bank ; bank -= bank
					await self.set_user_wallet(user, wallet) ; await self.set_user_bank(user, bank)
					await context.send(f"Moved all {self.currency} to your wallet.")
				elif amount == "half":
					half = bank / 2
					wallet += half ; bank -= half
					await self.set_user_wallet(user, wallet) ; await self.set_user_bank(user, bank)
					await context.send(f"Moved {half} {self.currency} to your wallet.")

	# -------------------------------------------------------------------------------------------------------
	# Gamble Command
	# -------------------------------------------------------------------------------------------------------

	@commands.command(name = "gamble", aliases = ["bet"])
	async def gamble(self, context : commands.Context, *, amount):
		user = str(context.author.id) ; await self.create_user_data(user)
		wallet = await self.get_user_wallet(user)
		try:
			amount = abs(float(amount))
			if wallet >= amount:
				luck = random.choice([0, 1])
				if luck == 0:
					wallet -= amount
					await self.set_user_wallet(user, wallet)
					await context.send("You lost! Better luck next time.")
				elif luck == 1:
					wallet += amount * 2
					await self.set_user_wallet(user, wallet)
					await context.send(f"You won {amount * 2} {self.currency}!")
			else:
				await context.send("You don't have that much in your wallet to bet!")
		except Exception as err:
			if isinstance(err, ValueError):
				if amount == "all":
					luck = random.choice([0, 1])
					print(luck)
					if luck == 0:
						wallet -= wallet
						await self.set_user_wallet(user, wallet)
						await context.send("You lost! Better luck next time.")
					elif luck == 1:
						amount = wallet * 2
						wallet += amount
						await self.set_user_wallet(user, wallet)
						await context.send(f"You won {wallet * 2} {self.currency}!")
				elif amount == "half":
					half = round(wallet / 2)
					if luck == 0:
						wallet -= half
						await self.set_user_wallet(user, wallet)
						await context.send("You lost! Better luck next time.")
					elif luck == 1:
						wallet += half * 2
						await self.set_user_wallet(user, wallet)
						await context.send(f"You won {half * 2} {self.currency}!")

	# -------------------------------------------------------------------------------------------------------
	# Rob Command
	# -------------------------------------------------------------------------------------------------------

	@commands.command(name = "rob", aliases = ["steal"])
	async def rob(self, context : commands.Context, victim : twitchio.User):
		executor, reciever = str(context.author.id), str(victim.id)
		await self.create_user_data(executor) ; await self.create_user_data(reciever)
		exec_wallet = await self.get_user_wallet(executor) ; reciv_wallet = await self.get_user_wallet(reciever)
		try:
			luck = random.choice([0, 1, 2])
			if executor != reciever:
				if luck == 0:
					if exec_wallet != 0:
						dropped = random.randint(1, exec_wallet)
						exec_wallet -= dropped
						await self.set_user_wallet(executor, exec_wallet)
						await context.send(f"{context.author.name} underestimated {victim.name} and dropped {dropped} {self.currency} trying to get away.")
					else:
						await context(f"{context.author.name} tried robbing {victim.name} but it didn't going according to plan.")
				elif luck == 1:
					if reciv_wallet != 0:
						if reciv_wallet >= 100:
							stolen = random.randint(1, 100)
							reciv_wallet -= stolen ; exec_wallet += stolen
							await self.set_user_wallet(reciever, reciv_wallet) ; await self.set_user_wallet(executor, exec_wallet)
							await context.send(f"{context.author.name} stole {stolen} {self.currency} from {victim.name}.")
						else:
							stolen = random.randint(1, reciv_wallet)
							reciv_wallet -= stolen ; exec_wallet += stolen
							await self.set_user_wallet(reciever, reciv_wallet) ; await self.set_user_wallet(executor, exec_wallet)
							await context.send(f"{context.author.name} stole {stolen} {self.currency} from {victim.name}.")
					else:
						await context.send(f"{context.author.name} tried robbing {victim.name} but their either broke or smart.")
				elif luck == 2:
					if reciv_wallet != 0:
						stolen = random.randint(1, reciv_wallet)
						reciv_wallet -= stolen ; exec_wallet += stolen
						await self.set_user_wallet(reciever, reciv_wallet) ; await self.set_user_wallet(executor, exec_wallet)
						await context.send(f"{context.author.name} stole {stolen} {self.currency} from {victim.name}.")
					else:
						await context.send(f"{context.author.name} tried robbing {victim.name} but their either broke or smart.")
			else:
				await context.send("Did you mean to do that pal? Lets try that again.")
		except Exception as err:
			print(err)

	# -------------------------------------------------------------------------------------------------------
	# Work command
	# -------------------------------------------------------------------------------------------------------

	@commands.cooldown(rate = 1, per = 3600)
	@commands.command(name = "work")
	async def work(self, context : commands.Context):
		user = str(context.author.id) ; await self.create_user_data(user)
		self.wallets[user] += 500
		await context.send(f"You've earned 500 {self.currency}.")

	# -------------------------------------------------------------------------------------------------------
	# Give Command
	# -------------------------------------------------------------------------------------------------------

	@commands.command(name = "give")
	async def give(self, context : commands.Context, reciever : twitchio.User, amount):
		giver_id = str(context.author.id) ; reciever_id = str(reciever.id)
		await self.create_user_data(giver_id) ; await self.create_user_data(reciever_id)
		giver_wallet = await self.get_user_wallet(giver_id) ; reciever_wallet = await self.get_user_wallet(reciever_id)
		try:
			amount = abs(float(amount))
			if giver_wallet >= amount:
				reciever_wallet += amount ; giver_wallet -= amount
				await self.set_user_wallet(reciever, reciever_wallet) ; await self.set_user_wallet(giver_id, giver_wallet)
				await context.send(f"{context.author.name} gave {reciever.name} {amount} {self.currency}!")
			else:
				await context.send("You cannot give more than you have.")
		except Exception as E:
			if isinstance(E, ValueError):
				if amount == "all":
					reciever_wallet += giver_wallet ; giver_wallet -= giver_wallet
					await self.set_user_wallet(reciever_id, reciever_wallet) ; await self.set_user_wallet(giver_id, giver_wallet)
					await context.send(f"{context.author.name} gave {reciever.name} all the {self.currency} in their wallet.")
				elif amount == "half":
					half = giver_wallet / 2
					reciever_wallet += half ; giver_wallet -= half
					await self.set_user_wallet(reciever_id, reciever_wallet) ; await self.set_user_wallet(giver_id, giver_wallet)
					await context.send(f"{context.author.name} gave {reciever.name} {half} {self.currency}.")

	# -------------------------------------------------------------------------------------------------------
	# Heist Command
	# -------------------------------------------------------------------------------------------------------

	async def heist(self):
		luck = random.choice([0, 1])
		if luck == 0:
			await self.client
		elif luck == 1:
			pass

	# -------------------------------------------------------------------------------------------------------
	# Create Heist Command
	# -------------------------------------------------------------------------------------------------------

	@commands.command(name = "createheist")
	async def createheist(self, context : commands.Context, initial_amount):
		user = str(context.author.id)
		self.participants[user] = initial_amount
		self.hip = True
		schedule.every(30).minutes.do(heist)
		

	# -------------------------------------------------------------------------------------------------------
	# Join Heist Command
	# -------------------------------------------------------------------------------------------------------

	@commands.command(name = "joinheist")
	async def joinheist(self, context, offered_amount):
		user = str(context.author.id)
		if self.hip is True:
			self.participants[user] = offered_amount
		else:
			await context.send("There's no heist in progress. You need to create one with $createheist")

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Testing
# ------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
	Test = Economy()
	print(Test.details)
	print(Test.database)