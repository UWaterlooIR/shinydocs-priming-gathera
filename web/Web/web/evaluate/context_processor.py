from web.evaluate.forms import QrelUploadForm
from web.evaluate.forms import QrelActivateForm


def qrel_forms_processor(request):
    if not request.user.is_authenticated:
        return {}
    # FORMS
    context = {'form_qrel_upload': QrelUploadForm(),
               'form_qrel_activate': QrelActivateForm(user=request.user)}
    return context
