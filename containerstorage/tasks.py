from datetime import datetime, timedelta
from logging import getLogger

from celery.decorators import periodic_task

from containerstorage.models import Node

log = getLogger("containerstorage.tasks")


@periodic_task(run_every=timedelta(minutes=5), name="containerstorage.clean_old_node_task")
def clean_old_nodes():
    log.info("Scheduled task: removing old nodes")
    old_nodes_no, old_nodes = Node.objects.filter(last_updated__lte=datetime.now() - timedelta(minutes=3)).delete()
    if old_nodes_no:
        log.info("Removed old nodes: {nodes}".format(nodes=str(old_nodes)))
