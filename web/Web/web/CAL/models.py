from config.settings.base import AUTH_USER_MODEL as User

from django.contrib.postgres.fields import JSONField
from django.db import models

from web.core.models import Session


class DS_logging(models.Model):
    class Meta:
        unique_together = ['user', 'stratum_num', 'session']
        index_together = ['user', 'stratum_num', 'session']

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    stratum_size = models.IntegerField(default=-1)
    stratum_num = models.IntegerField(default=-1)
    sample_size = models.IntegerField(default=-1)

    T = models.IntegerField(default=-1)
    N = models.IntegerField(default=-1)
    R = models.IntegerField(default=-1)

    sampled_docs = JSONField(null=True, blank=True, default=list)
    stratum_docs = JSONField(null=True, blank=True, default=list)

    # Todo: Add more fields
    # created_at = models.DateTimeField(auto_now_add=True, editable=False)
    # updated_at = models.DateTimeField(auto_now=True)

    # The format of irels is: five-column irel format:
    #   topic 0 doc stratum rel
    # def __unicode__(self):
    #     return "{} 0 {} {} {}".format(self.doc_topic, self.doc_id, self.stratum_num, self.relevance)
    #
    # def __str__(self):
    #     return self.__unicode__()
