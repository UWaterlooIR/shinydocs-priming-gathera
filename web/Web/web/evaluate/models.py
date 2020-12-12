from config.settings.base import AUTH_USER_MODEL as User

from django.db import models


class Qrel(models.Model):

    username = models.ForeignKey(User, on_delete=models.CASCADE)
    qrel_file = models.FileField(upload_to="qrels")

    created_at = models.DateTimeField(auto_now_add=True,
                                      editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "<User:{}, title:{}>".format(self.username, self.qrel_file.name)

    def __str__(self):
        return self.__unicode__()
