from django.db import models

# Max chars for ACC is 260

class AutodeskConstructionCloudProject(models.Model):
    name = models.CharField(max_length=260)
    org = models.CharField(max_length=260)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AutodeskConstructionCloudReport(models.Model):
    project = models.ForeignKey(AutodeskConstructionCloudProject, on_delete=models.CASCADE)
    name = models.CharField(max_length=260)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return self.name