from django.db import models


class ModelsSatusAccount(models.Model):
    name = models.CharField(max_length=255, null=False)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: {self.name}"


class ModelsAccount(models.Model):
    name = models.CharField(max_length=255, null=False)
    street1 = models.CharField(max_length=255, null=False)
    street2 = models.CharField(max_length=255, null=False)
    country = models.CharField(max_length=255, null=False)
    phone = models.CharField(max_length=255, null=False)
    email = models.CharField(max_length=255, null=False)
    hst = models.CharField(max_length=255, null=False)
    logo = models.ImageField(blank=True, null=True, upload_to='account')
    status = models.ForeignKey(ModelsSatusAccount, on_delete=models.CASCADE, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: {self.name}"
