from django import forms
from .models import AutodeskConstructionCloudProject

class AutodeskConstructionCloudProjectForm(forms.ModelForm):

    class Meta:
        model = AutodeskConstructionCloudProject
        fields = '__all__'