from django.db import models


class Country(models.Model):
    # ID automat din django
    name = models.CharField(max_length=100, unique=True)
    flag_image = models.ImageField(upload_to="flags/", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"
