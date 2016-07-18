#! /bin/sh


rm -rf /etc/celery_*.pid
rm -rf /var/log/celery_*.log

source /virtualenv/bin/activate

cd /app
./manage.py celery -A containerstorageservice --detach --logfile=/var/log/celery_worker.log --pidfile=/etc/celery_worker.pid worker --concurrency=1 --loglevel=info
./manage.py celery -A containerstorageservice --detach --logfile=/var/log/celery_beat.log --pidfile=/etc/celery_beat.pid beat --loglevel=info
sleep 5
tail -F /var/log/celery_worker.log /var/log/celery_beat.log
