from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import AutodeskConstructionCloudProject

@login_required
def index(request):
    return render(request, 'index.html', {'username': request.user.username})

def projects(request):
    if not request.user.has_perm('analytics.view_autodeskconstructioncloudproject'):
        raise PermissionDenied
    can_add_projects = True if request.user.has_perm('analytics.add_autodeskconstructioncloudproject') else False
    return render(request, 'projects.html', {'can_add_projects': can_add_projects, 'projects': AutodeskConstructionCloudProject.objects.all()})