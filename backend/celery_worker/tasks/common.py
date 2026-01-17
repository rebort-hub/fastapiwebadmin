# -*- coding: utf-8 -*-
# @author: rebort

from celery_worker.worker import celery


@celery.task
def add(i):
    return 1 + i
