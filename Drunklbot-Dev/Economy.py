import twitchio
import random
import json

from twitchio.ext import commands

class Economy(commands.Cog):
	
	def __init__(self, client = None) -> None:
		self.client = client
		self.currency = "Credit"
		with open("Database.json", "r") as f:
			self.database = json.load(f)
			f.close()

	def save_database(self) -> None:
		with open("Database.json", "w") as f:
			json.dump(self.database, f, indent = 4)

	def get_user(self, user_id):
		return self.database[user_id]["wallet"], self.database[user_id]["bank"]
	
	def set_user(self, user_id):
		if user_id not in self.database:
			self.database[user_id] = {"wallet" : 0, "bank" : 5000, "inventory" : []} ; pass
		else: pass

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------------------------------------------------------------------------------------

	# -------------------------------------------------------------------------------------------------------
	# Balance Command
	# -------------------------------------------------------------------------------------------------------
	@commands.command(name = "balance", aliases = ["bal", "wealth"])
	async def balance(self, context : commands.Context):
		user = str(context.author.id) ; self.set_user(user)
		wallet, bank = self.get_user(user)
		await context.send(f"Wallet: {wallet}, Bank: {bank}.")

	# -------------------------------------------------------------------------------------------------------
	# Deposit Command
	# -------------------------------------------------------------------------------------------------------
	@commands.command(name = "deposit")
	async def deposit(self, context : commands.Context, *, amount):
		user = str(context.author.id) ; self.set_user(user)
		wallet, bank = self.get_user(user)
		try:
			amount = abs(int(amount))
			if amount <= wallet:
				wallet -= amount ; bank += amount
				self.database[user].update({"wallet": wallet, "bank": bank})
				await context.send(f"Successfully moved {amount} {self.currency}s to your bank!")
			else:
				await context.send("You don't have enough to deposit into your bank.")
		except Exception as err:
			if isinstance(err, ValueError):
				if amount == "all":
					bank += wallet ; wallet -= wallet
					self.database[user].update({"wallet": wallet, "bank": bank})
					await context.send(f"Successfully moved all {self.currency}s to your bank!")
				elif amount == "half":
					half = round(wallet / 2) ; bank += half ; wallet -= half
					self.database[user].update({"wallet": wallet, "bank": bank})
					await context.send(f"Successfully moved {half} {self.currency}s to your bank!")
		finally:
			self.save_database()		

	# -------------------------------------------------------------------------------------------------------
	# Withdraw Command
	# -------------------------------------------------------------------------------------------------------
	@commands.command(name = "withdraw")
	async def withdraw(self, context : commands.Context, *, amount):
		user = str(context.author.id) ; self.set_user(user)
		wallet, bank = self.get_user(user)
		try:
			amount = abs(int(amount))
			if amount <= bank:
				wallet += amount ; bank -= amount
				self.database[user].update({"wallet": wallet, "bank": bank})
				await context.send(f"Successfully moved {amount} {self.currency}s to your wallet!")
			else:
				await context.send("You don't have enough to withdraw from your bank.")
		except Exception as err:
			if isinstance(err, ValueError):
				if amount == "all":
					wallet += bank ; bank -= bank;
					self.database[user].update({"wallet": wallet, "bank": bank})
					await context.send(f"Successfully moved all {self.currency}s to your wallet!")
				elif amount == "half":
					half = round(bank / 2)
					wallet += half ; bank -= half
					self.database[user].update({"wallet": wallet, "bank": bank})
					await context.send(f"Successfully moved {half} {self.currency}s to your wallet!")
		finally:
			self.save_database()

	# -------------------------------------------------------------------------------------------------------
	# Gamble Command
	# -------------------------------------------------------------------------------------------------------
	@commands.command(name = "gamble", aliases = ["bet"])
	async def gamble(self, context : commands.Context, *, amount):
		user = str(context.author.id) ; self.set_user(user)
		wallet, _ = self.get_user(user)
		try:
			amount = abs(int(amount))
			if wallet >= amount:
				luck = random.choices([0, 1, 2], [75, 50, 1], k = 1)[0]
				if luck == 0:
					wallet -= amount
					self.database[user].update({"wallet": wallet})
					await context.send("You lost! Better luck next time.")
				elif luck == 1:
					wallet += amount * 2
					self.database[user].update({"wallet": wallet})
					await context.send(f"You won {amount * 2} {self.currency}s!")
				elif luck == 2:
					wallet += amount ** 2
					self.database[user].update({"wallet": wallet})
					await context.send(f"Lucky individual aren't you {context.author.name}! You won {amount ** 2} {self.currency}s!")
			else:
				await context.send("You don't have that much in your wallet to bet!")
		except Exception as err:
			if isinstance(err, ValueError):
				if amount == "all":
					luck = random.choices([0, 1, 2], [75, 50, 1], k = 1)[0]
					if luck == 0:
						wallet -= wallet
						self.database[user].update({"wallet": wallet})
						await context.send("You lost! Better luck next time.")
					elif luck == 1:
						amount = wallet * 2
						wallet += amount
						self.database[user].update({"wallet": wallet})
						await context.send(f"You won {wallet * 2} {self.currency}s!")
					elif luck == 2:
						amount = wallet ** 2
						wallet += amount
						self.database[user].update({"wallet": wallet})
						await context.send(f"Lucky individual aren't you {context.author.name}! You won {amount} {self.currency}s!")
				elif amount == "half":
					luck = random.choices([0, 1, 2], [75, 50, 1], k = 1)[0]
					half = round(wallet / 2)
					if luck == 0:
						wallet -= half
						self.database[user].update({"wallet": wallet})
						await context.send("You lost! Better luck next time.")
					elif luck == 1:
						wallet += half * 2
						self.database[user].update({"wallet": wallet})
						await context.send(f"You won {half * 2} {self.currency}s!")
					elif luck == 2:
						wallet += amount ** 2
						self.database[user].update({"wallet": wallet})
						await context.send(f"Lucky individual aren't you {context.author.name}! You won {half ** 2} {self.currency}s!")
		finally:
			self.save_database()

	# -------------------------------------------------------------------------------------------------------
	# Rob Command
	# -------------------------------------------------------------------------------------------------------
	@commands.command(name = "rob", aliases = ["steal"])
	async def rob(self, context : commands.Context, victim : twitchio.User):
		robber_id, victim_id = str(context.author.id), str(victim.id)
		self.set_user(robber_id) ; self.set_user(victim_id)
		r_wallet, _ = self.get_user(robber_id) ; v_wallet, _ = self.get_user(victim_id)
		try:
			luck = random.choices([0, 1, 2], [75, 50, 1], k = 1)[0]
			if luck == 0:
				if r_wallet != 0:
					if r_wallet > 100:
						dropped = random.randint(1, 100)
						r_wallet -= dropped
						self.database[robber_id].update({"wallet": r_wallet})
						await context.send(f"{context.author.name} underestimated {victim.name} and dropped {dropped} {self.currency}s trying to get away.")
					else:
						dropped = random.randint(1, r_wallet)
						r_wallet -= dropped
						self.database[robber_id].update({"wallet": r_wallet})
						await context.send(f"{context.author.name} underestimated {victim.name} and dropped {dropped} {self.currency}s trying to get away.")
				else:
					await context.send(f"{context.author.name} tried robbing {victim.name} but it didn't go according to plan.")
			elif luck == 1:
				if v_wallet != 0:
					if v_wallet > 100:
						stolen = random.randint(1, 100)
						v_wallet -= stolen ; r_wallet += stolen
						self.database[victim_id].update({"wallet": v_wallet})
						self.database[robber_id].update({"wallet": r_wallet})
						await context.send(f"{context.author.name} stole {stolen} from {victim.name}.")
					else: # In case v_wallet is less than 100
						stolen = random.randint(1, v_wallet)
						v_wallet -= stolen ; r_wallet += stolen
						self.database[victim_id].update({"wallet": v_wallet})
						self.database[robber_id].update({"wallet": r_wallet})
						await context.send(f"{context.author.name} stole {stolen} from {victim.name}.")
				else:
					await context.send(f"{context.author.name} tried robbing {victim.name} but their either broke or smart.")
			elif luck == 2:
				if v_wallet != 0:
					stolen = random.randint(1, v_wallet)
					v_wallet -= stolen ; r_wallet += stolen
					self.database[victim_id].update({"wallet": v_wallet})
					self.database[robber_id].update({"wallet": r_wallet})
					await context.send(f"It was not {victim.name}'s lucky day. {context.author.name} stole {stolen} {self.currency}s.")
				else:
					await context.send(f"{context.author.name} tried robbing {victim.name} but their either broke or smart.")
		except Exception as err:
			print(err)
		finally:
			self.save_database()

	# -------------------------------------------------------------------------------------------------------
	# Work command
	# -------------------------------------------------------------------------------------------------------

	# Add work command

	# -------------------------------------------------------------------------------------------------------
	# Give Command
	# -------------------------------------------------------------------------------------------------------
	@commands.command(name = "give")
	async def give(self, context : commands.Context, reciever : twitchio.User, amount):
		giver_id = str(context.author.id) ; reciever_id = str(reciever.id)
		self.set_user(giver_id) ; self.set_user(reciever_id)
		g_wallet, _ = self.get_user(giver_id) ; r_wallet, _ = self.get_user(reciever_id)
		try:
			amount = abs(int(amount))
			if g_wallet >= amount:
				r_wallet += amount ; g_wallet -= amount
				self.database[giver_id].update({"wallet": g_wallet})
				self.database[reciever_id].update({"wallet": r_wallet})
				await context.send(f"{context.author.name} successfully gave {reciever.name} {amount} {self.currency}s!")
			else:
				await context.send("You cannot give more than you have!")
		except Exception as err:
			if isinstance(err, ValueError):
				if amount == "all":
					r_wallet += g_wallet ; g_wallet -= g_wallet
					self.database[giver_id].update({"wallet": g_wallet})
					self.database[reciever_id].update({"wallet": r_wallet})
					await context.send(f"{context.author.name} successfully gave {reciever.name} all their {self.currency}s!")
				elif amount == "half":
					half = round(g_wallet / 2)
					r_wallet += half ; g_wallet -= half
					self.database[giver_id].update({"wallet": g_wallet})
					self.database[reciever_id].update({"wallet": r_wallet})
					await context.send(f"{context.author.name} successfully gave {reciever.name} {half} {self.currency}s!")
		finally:
			self.save_database()

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Testing
# ------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
	Test = Economy()
	print(Test.details)
	print(Test.database)