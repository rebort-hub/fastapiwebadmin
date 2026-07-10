# -*- coding: utf-8 -*-
# @author: rebort

from app.plugin.fea_celery.worker import celery


@celery.task
def add(i):
    return 1 + i
