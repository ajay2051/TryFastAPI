chmod +x db_setup.sh

ls -l db_setup.sh

alembic init alembic

alembic revision --autogenerate -m "initial"

alembic -n tryfastapi revision --autogenerate -m "initial"

alembic -n tryfastapi upgrade head

celery -A app.celery_tasks.c_app worker  --loglevel=INFO

celery -A app.celery_tasks.c_app flower

st run http://127.0.0.1:8000/openapi.json --experimental=openapi-3.1