add_wallet_revision:
	@rm wallet.db
	@DB_URL="sqlite:///wallet.db" PYTHONPATH=../ alembic -n wallet upgrade head
	@DB_URL="sqlite:///wallet.db" PYTHONPATH=../ alembic -n wallet revision --autogenerate -m "${MESSAGE}"

