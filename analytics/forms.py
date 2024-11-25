from django import forms
from .models import AutodeskConstructionCloudProject, AutodeskConstructionCloudReport

class AutodeskConstructionCloudProjectForm(forms.ModelForm):

    class Meta:
        model = AutodeskConstructionCloudProject
        fields = '__all__'

class AutodeskConstructionCloudReportForm(forms.ModelForm):

    class Meta:
        model = AutodeskConstructionCloudReport
        fields = '__all__'