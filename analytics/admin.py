from django.contrib import admin
from .models import AutodeskConstructionCloudProject, AutodeskConstructionCloudReport

# https://django-guardian.readthedocs.io/en/stable/userguide/admin-integration.html
from guardian.admin import GuardedModelAdmin

class AutodeskConstructionCloudProjectAdmin(GuardedModelAdmin):
    pass

class AutodeskConstructionCloudReportAdmin(GuardedModelAdmin):
    pass


admin.site.register(AutodeskConstructionCloudProject, AutodeskConstructionCloudProjectAdmin)
admin.site.register(AutodeskConstructionCloudReport, AutodeskConstructionCloudReportAdmin)