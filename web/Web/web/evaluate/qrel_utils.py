import csv
import io

from django.contrib import messages

from web.evaluate.forms import QrelActivateForm
from web.evaluate.forms import QrelUploadForm

def read_qrel_file(csv_reader):
    pass


def upload_qrel_submit_form(request):
    success_message = "Qrel file {} uploaded successfully."

    form = QrelUploadForm(request.POST, request.FILES)
    if form.is_valid():
        f = form.save(commit=False)
        f.username = request.user
        form.instance.qrel_name = form.qrel_name
        form.instance.qrel = form.qrel
        f.save()
        request.user.current_qrel = form.instance
        request.user.save()
        messages.add_message(request,
                             messages.SUCCESS,
                             success_message.format(form.qrel_name))
    else:
        messages.add_message(request, messages.ERROR, f'Ops! {form.errors}')


def activate_qrel_submit_form(request):
    success_message = "Qrel file {} is now being used."

    form = QrelActivateForm(request.user, request.POST)

    if form.is_valid():
        selected_qrel = form.cleaned_data['qrel']
        request.user.current_qrel = selected_qrel
        request.user.save()
        messages.add_message(request,
                             messages.SUCCESS,
                             success_message.format(selected_qrel.qrel_name))
    else:
        messages.add_message(request, messages.ERROR, f'Ops! {form.errors}')
