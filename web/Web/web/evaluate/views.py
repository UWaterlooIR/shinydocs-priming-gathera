import logging

from braces import views
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from web.evaluate.qrel_utils import activate_qrel_submit_form
from web.evaluate.qrel_utils import upload_qrel_submit_form

logger = logging.getLogger(__name__)


class EvaluateHomePageView(views.LoginRequiredMixin,
                           generic.TemplateView):
    template_name = 'evaluate/evaluate.html'

    def get(self, request, *args, **kwargs):
        if not self.request.user.current_session:
            return HttpResponseRedirect(reverse_lazy('core:home'))
        return super(EvaluateHomePageView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "upload-qrel-form" in request.POST:
            upload_qrel_submit_form(request)
        elif "activate-qrel-form" in request.POST:
            activate_qrel_submit_form(request)

        return HttpResponseRedirect(self.request.path_info)
