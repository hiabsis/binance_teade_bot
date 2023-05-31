from trade.model.account import AccountFactory

account = AccountFactory.load_by_config()

print(account.format_str())
