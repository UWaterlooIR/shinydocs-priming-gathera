import csv
import io
from collections import defaultdict

from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.core.exceptions import ValidationError

from web.evaluate.models import Qrel


class QrelUploadForm(forms.ModelForm):
    """
    Form for uploading a QREL file

    """
    class Meta:
        model = Qrel
        exclude = ["username", "qrel", "qrel_name"]

    class QrelFileField(forms.FileField):
        def validate(self, file):
            super().validate(file)
            if not file.name.endswith(".csv"):
                raise ValidationError("Please upload a file ending with .csv extension.")

    submit_name = 'upload-qrel-form'
    prefix = "qrel"

    qrel_file = QrelFileField(required=True, label='Qrel file (Standard TREC format)')

    def __init__(self, *args, **kwargs):
        super(QrelUploadForm, self).__init__(*args, **kwargs)
        self.qrel = defaultdict(lambda: defaultdict(int))
        self.qrel_name = None

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            'qrel_file',
            StrictButton(u'Upload qrel file',
                         name=self.submit_name,
                         type="submit",
                         css_class='btn btn-outline-secondary')
        )

    def clean_qrel_file(self):
        file = self.cleaned_data['qrel_file']
        self.qrel_name = file.name
        with file:
            qrel_file = io.TextIOWrapper(file.file, encoding='utf-8')
            io_string = io.StringIO(qrel_file.read())
            reader = csv.reader(io_string, delimiter=" ")
            try:
                for r in reader:
                    topic, docid, rel = r[0], r[2], r[3]
                    self.qrel[topic][docid] = rel

            except IndexError:
                raise ValidationError("Couldn't read file properly. Please make sure the "
                                      "file is in the standard TREC "
                                      "format (space delimited)")
        return file


class QrelActivateForm(forms.Form):
    """
    Form for setting a QREL file as active for user

    """
    submit_name = 'activate-qrel-form'
    prefix = "qrel"

    class QrelsChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return f'{obj.qrel_name}'

    qrel = QrelsChoiceField(queryset=None, empty_label="Please select a qrel file")

    def __init__(self, user, *args, **kwargs):
        super(QrelActivateForm, self).__init__(*args, **kwargs)
        self.fields['qrel'].queryset = Qrel.objects.filter(username=user)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            'qrel',
            StrictButton(u'Use',
                         name=self.submit_name,
                         type="submit",
                         css_class='btn btn-outline-secondary')
        )
