from django.db import models

class CSVModel(models.Model):
    Campus_id = models.CharField(max_length=255)
    Name = models.TextField(blank=True, null=True)
    Age = models.IntegerField()
    Gender = models.TextField(blank=True, null=True)
    Address = models.TextField(blank=True, null=True)
    PUC_Background = models.TextField(blank=True, null=True)
    PUC_Marks = models.IntegerField(null=True, blank=True)
    Batch = models.IntegerField()
    Course = models.TextField(blank=True, null=True)
