run: 
	uvicorn app.main:app --reload

prod:
	alembic upgrade head
	uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
