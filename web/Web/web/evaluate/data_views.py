import json
import logging

from braces import views
from django.http import HttpResponse
from django.views import generic

from web.evaluate import data

logger = logging.getLogger(__name__)


class DataAJAXView(views.CsrfExemptMixin,
                   views.LoginRequiredMixin,
                   views.JsonRequestResponseMixin,
                   views.JSONResponseMixin, generic.View):
    """
    View to get data to visualize (User reported and found relevant documents).
    """

    def render_timeout_request_response(self, error_dict=None):
        if error_dict is None:
            error_dict = self.error_response_dict
        json_context = json.dumps(
            error_dict,
            cls=self.json_encoder_class,
            **self.get_json_dumps_kwargs()
        ).encode('utf-8')
        return HttpResponse(
            json_context, content_type=self.get_content_type(), status=502)

    def get(self, request, *args, **kwargs):

        try:
            session = self.request.user.current_session
            qrel = self.request.user.current_qrel
            if not qrel:
                self.render_json_response({u"error": u"No qrel is set."}, status=500)
            return self.render_json_response(data.user_reported_rel__user_found_rel(session, qrel))

        except TimeoutError:
            error_dict = {u"error": u"Timeout error. Please check status of servers."}
            return self.render_timeout_request_response(error_dict)
