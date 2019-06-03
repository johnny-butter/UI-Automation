import os
import sys
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'dbModels.settings'
django.setup()

from dbModels.models import Questions
from sshtunnel import SSHTunnelForwarder as tunnel
from django.db import connection


class dbTunnel:
    def __init__(self, userId):
        self.userId = str(userId)
        self.server = tunnel(SERVER,
                             ssh_username=SSH_USERNAME,
                             ssh_pkey=P_KEY,
                             remote_bind_address=BIND_ADDRESS,
                             local_bind_address=BIND_ADDRESS)


class userInfoCheck(dbTunnel):

    @property
    def ratedTitle(self):
        with self.server:
            title = Questions.objects \
                .filter(user=self.userId) \
                .order_by('-updated_at') \
                .first()
            if title:
                title = title.description
            connection.close()
        return title
