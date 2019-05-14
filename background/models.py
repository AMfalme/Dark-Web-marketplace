from django.db import models


class CryptoCurrencies(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True, primary_key=True)
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name
