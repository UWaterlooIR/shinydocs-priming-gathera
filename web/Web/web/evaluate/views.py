import logging

from braces import views
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

logger = logging.getLogger(__name__)


class EvaluateHomePageView(views.LoginRequiredMixin,
                           generic.TemplateView):
    template_name = 'evaluate/evaluate.html'

    def get(self, request, *args, **kwargs):
        if not self.request.user.current_session:
            return HttpResponseRedirect(reverse_lazy('core:home'))
        return super(EvaluateHomePageView, self).get(self, request, *args, **kwargs)
