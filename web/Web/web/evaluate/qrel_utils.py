from django.contrib import messages

from web.evaluate.forms import QrelActivateForm
from web.evaluate.forms import QrelUploadForm


def upload_qrel_submit_form(request):
    success_message = "Qrel file uploaded successfully."

    form = QrelUploadForm(request.POST, request.FILES)
    print(print(form))
    if form.is_valid():
        print(form)
        f = form.save(commit=False)
        f.username = request.user
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

    form = QrelActivateForm(request.POST)
    if form.is_valid():
        f = form.save(commit=False)
        f.username = request.user
        f.save()
        print(form)
        # request.user.current_qrel = form.instance
        # request.user.save()
        messages.add_message(request,
                             messages.SUCCESS,
                             success_message)
    else:
        messages.add_message(request, messages.ERROR, f'Ops! {form.errors}')
    form.instance.begin_session_in_cal()
