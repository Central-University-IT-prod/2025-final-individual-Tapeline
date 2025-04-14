poetry run alembic upgrade head
poetry run uvicorn --factory prodadvert.main:get_app --host REDACTED --port 8080
#poetry run granian --interface asgi --factory prodadvert.main:get_app --host REDACTED --port 8080
wait
