wallets = {"0": 0, "468972149": 12000.0, "51011777": 5000, "107108076": 5048, "109133488": 10969.0, "756338362": 5000, "472443837": 5000}

for user in self.banks:
	if user not in self.participants:
		self.victims.append(user)

print(list(wallets.keys()))
print(list(wallets.values()))