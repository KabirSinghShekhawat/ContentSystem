init_db:
	alembic init migrations

migrate_db:
	@read -p "Enter revision message: " input; \
	python -m alembic revision --autogenerate -m "$$input"
	python -m alembic upgrade head
