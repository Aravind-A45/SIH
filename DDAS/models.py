from django.db import models

# Create your models here.

class FileMeta(models.Model):
    file_id = models.CharField(max_length=255)  
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
