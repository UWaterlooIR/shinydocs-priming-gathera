import json
import logging

from braces import views
from django.http import HttpResponse
from django.http import JsonResponse
from django.views import generic
from interfaces.DocumentSnippetEngine import functions as DocEngine

from web.CAL.exceptions import CALError
from web.core.mixin import RetrievalMethodPermissionMixin
from web.interfaces.CAL import functions as CALFunctions

logger = logging.getLogger(__name__)


class CALHomePageView(views.LoginRequiredMixin,
                      RetrievalMethodPermissionMixin,
                      generic.TemplateView):
    template_name = 'CAL/CAL.html'

    def get(self, request, *args, **kwargs):
        return super(CALHomePageView, self).get(self, request, *args, **kwargs)


class CALMessageAJAXView(views.CsrfExemptMixin,
                         views.LoginRequiredMixin,
                         RetrievalMethodPermissionMixin,
                         views.JsonRequestResponseMixin,
                         generic.View):
    """
    Generic view to capture specific log messages from browser
    """
    require_json = False

    def post(self, request, *args, **kwargs):
        try:
            client_time = self.request_json.get(u"client_time")
            message = self.request_json.get(u"message")
            action = self.request_json.get(u"action")
            page_title = self.request_json.get(u"page_title")
            doc_CAL_snippet = self.request_json.get(u'doc_CAL_snippet')
            doc_id = self.request_json.get(u'doc_id')
            extra_context = self.request_json.get(u'extra_context')
        except KeyError:
            error_dict = {u"message": u"your input must include client_time, "
                                      u"message, ... etc"}
            return self.render_bad_request_response(error_dict)

        context = {u"message": u"Your log message with action '{}' and of "
                               u"document '{}' has been logged.".format(action, doc_id)}
        return self.render_json_response(context)


class DocAJAXView(views.CsrfExemptMixin,
                  RetrievalMethodPermissionMixin,
                  views.LoginRequiredMixin,
                  views.JsonRequestResponseMixin,
                  views.AjaxResponseMixin, generic.View):
    """
    View to get a list of documents (with their content) to judge from CAL
    """
    require_json = False

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

    def get_ajax(self, request, *args, **kwargs):
        session = self.request.user.current_session.uuid
        seed_query = self.request.user.current_session.topic.seed_query
        try:
            docids_to_judge, top_terms = CALFunctions.get_documents(str(session), 10)
            if not docids_to_judge:
                return self.render_json_response([])

            ret = {}
            next_patch_ids = []
            for docid_score_pair in docids_to_judge:
                doc_id, doc_score = docid_score_pair.split(':')
                ret[doc_id] = doc_score
                next_patch_ids.append(doc_id)

            doc_ids_hack = []
            for doc_id in next_patch_ids:
                doc = {'doc_id': doc_id}
                if '.' in doc_id:
                    doc['doc_id'], doc['para_id'] = doc_id.split('.')
                doc_ids_hack.append(doc)

            if 'doc' in self.request.user.current_session.strategy:
                documents = DocEngine.get_documents(next_patch_ids,
                                                    seed_query,
                                                    top_terms)
            else:
                documents = DocEngine.get_documents_with_snippet(doc_ids_hack,
                                                                 seed_query,
                                                                 top_terms)

            return self.render_json_response(documents)
        except TimeoutError:
            error_dict = {u"message": u"Timeout error. Please check status of servers."}
            return self.render_timeout_request_response(error_dict)
        except CALError as e:
            return JsonResponse({"message": "Ops! CALError."}, status=404)


class DocIDsAJAXView(views.CsrfExemptMixin,
                     RetrievalMethodPermissionMixin,
                     views.LoginRequiredMixin,
                     views.JsonRequestResponseMixin,
                     views.AjaxResponseMixin, generic.View):
    """
    View to get ids of documents to judge from CAL
    """
    require_json = False

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

    def get_ajax(self, request, *args, **kwargs):
        session = self.request.user.current_session.uuid
        seed_query = self.request.user.current_session.topic.seed_query
        try:
            docs_ids_to_judge = CALFunctions.get_documents(str(session), 10)
            return self.render_json_response(docs_ids_to_judge)
        except TimeoutError:
            error_dict = {u"message": u"Timeout error. Please check status of servers."}
            return self.render_timeout_request_response(error_dict)
        except CALError as e:
            # TODO: add proper http response for CAL errors
            return JsonResponse({"message": "Ops! CALError."}, status=404)
