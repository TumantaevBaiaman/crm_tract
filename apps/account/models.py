from django.db import models


class ModelsSatusAccount(models.Model):
    name = models.CharField(max_length=255, null=False)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: {self.name}"


class ModelsAccount(models.Model):
    name = models.CharField(max_length=255, null=False)
    status = models.ForeignKey(ModelsSatusAccount, on_delete=models.CASCADE, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: {self.name}"
