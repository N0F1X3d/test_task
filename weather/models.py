from django.db import models

class SearchHistory(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('session_key', 'city')

    def __str__(self):
        return f"{self.city} ({self.count})"
