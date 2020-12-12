from django.contrib import messages

from web.evaluate.forms import QrelActivateForm
from web.evaluate.forms import QrelUploadForm


def upload_qrel_submit_form(request):
    success_message = "Qrel file uploaded successfully."

    form = QrelUploadForm(request.POST, request.FILES)
    if form.is_valid():
        f = form.save(commit=False)
        f.username = request.user

        # TODO: Validate qrel format

        f.save()
        request.user.current_qrel = form.instance
        request.user.save()
        messages.add_message(request,
                             messages.SUCCESS,
                             success_message)
    else:
        messages.add_message(request, messages.ERROR, f'Ops! {form.errors}')


def activate_qrel_submit_form(request):
    success_message = "Qrel file {} is now being used."

    form = QrelActivateForm(request.user, request.POST)

    if form.is_valid():
        selected_qrel_file = form.cleaned_data['qrels']
        request.user.current_qrel = selected_qrel_file
        request.user.save()
        messages.add_message(request,
                             messages.SUCCESS,
                             success_message.format(selected_qrel_file.qrel_file.name))
    else:
        messages.add_message(request, messages.ERROR, f'Ops! {form.errors}')
