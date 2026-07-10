#!/bin/sh

port=$2
if [ "$port" = "" ]; then
  port=8101
fi

if [ $1 = "app" ]; then
    echo "start app"
    /usr/local/bin/python -m gunicorn "main:create_app()" --factory --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$port
fi

if [ $1 = "celery-worker" ]; then
    echo "start celery worker"
     /usr/local/bin/python -m celery -A app.plugin.fea_celery.worker.celery worker --pool=gevent -c 10 -l INFO
fi

if [ $1 = "celery-beat" ]; then
    echo "start celery beat"
    /usr/local/bin/python  -m celery -A app.plugin.fea_celery.worker.celery beat -S app.plugin.fea_celery.scheduler.schedulers:DatabaseScheduler -l INFO
fi