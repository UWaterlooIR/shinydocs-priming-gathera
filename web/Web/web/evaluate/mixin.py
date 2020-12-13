import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


class QrelSetRequiredMixin(object):
    """
    Mixin that checks if user has a qrel set
    """

    def dispatch(self, request, *args, **kwargs):

        if request.method == 'GET' and not request.user.current_qrel:
            messages.add_message(request,
                                 messages.ERROR,
                                 "Sorry, you need to set a qrel first. You can set a "
                                 "qrel from the settings bar.")
            return HttpResponseRedirect(reverse_lazy('core:home'))

        return super().dispatch(request, *args, **kwargs)


class TopicNumberSetRequiredMixin(object):
    """
    Mixin that checks if current session has a topic number set.
    """

    def dispatch(self, request, *args, **kwargs):
        # TODO: Allow custom sessions. It only works for predefined topics now
        if request.method == 'GET' and not request.user.current_session.topic.number:
            messages.add_message(request,
                                 messages.ERROR,
                                 "Sorry, you need to set the topic number first.")
            return HttpResponseRedirect(reverse_lazy('core:home'))

        return super().dispatch(request, *args, **kwargs)
