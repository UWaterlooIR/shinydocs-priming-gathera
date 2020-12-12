from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms

from web.evaluate.models import Qrel


class QrelUploadForm(forms.ModelForm):
    """
    Form for uploading a QREL file

    """
    submit_name = 'upload-qrel-form'
    prefix = "qrel"

    class Meta:
        model = Qrel
        exclude = ["username"]

    qrel_file = forms.FileField(required=True, label='Qrel file (Standard TREC format)')

    def __init__(self, *args, **kwargs):
        super(QrelUploadForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            'qrel_file',
            StrictButton(u'Upload qrel file',
                         name=self.submit_name,
                         type="submit",
                         css_class='btn btn-outline-secondary')
        )


class QrelActivateForm(forms.Form):
    """
    Form for setting a QREL file as active for user

    """
    submit_name = 'activate-qrel-form'
    prefix = "qrel"

    class QrelsChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return f'{obj.qrel_file.name}'

    qrels = QrelsChoiceField(queryset=None, empty_label="Please select a qrel file")

    def __init__(self, user, *args, **kwargs):
        super(QrelActivateForm, self).__init__(*args, **kwargs)
        self.fields['qrels'].queryset = Qrel.objects.filter(username=user)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            'qrels',
            StrictButton(u'Use',
                         name=self.submit_name,
                         type="submit",
                         css_class='btn btn-outline-secondary')
        )
