chmod +x db_setup.sh

ls -l db_setup.sh

alembic init alembic

alembic revision --autogenerate -m "initial"

alembic -n tryfastapi revision --autogenerate -m "initial"

alembic -n tryfastapi upgrade head

celery -A app.celery_tasks.c_app worker

celery -A app.celery_tasks.c_app flower