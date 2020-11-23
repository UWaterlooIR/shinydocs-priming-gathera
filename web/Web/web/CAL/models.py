from config.settings.base import AUTH_USER_MODEL as User

from django.contrib.postgres.fields import JSONField
from django.db import models

from web.core.models import Session


class DS_logging(models.Model):
    # class Meta:
    #     unique_together = ['user', 'doc_id', 'session']
    #     index_together = ['user', 'doc_id', 'session']

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    doc_id = models.CharField(null=False, blank=False, max_length=512)
    # doc_topic = models.CharField(null=False, blank=False, max_length=64)

    # relevance assessment:  positive integers indicate grades of relevance
    # 0 indicates not relevant; -1 indicates in stratum but not in assessment sample
    # relevance = models.IntegerField(verbose_name='Relevance', null=True, blank=True)

    # sampling_rate = models.FloatField(default=-1)
    stratum_num = models.IntegerField(default=-1)
    # relevance_score = models.FloatField(default=-1)

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
