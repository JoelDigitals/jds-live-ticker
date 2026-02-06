from django.db import models
from django.contrib.auth.models import User

class LiveTicker(models.Model):
    TICKER_TYPES = [
        ('sport', 'Sport'),
        ('news', 'News'),
        ('custom', 'Custom'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    ticker_type = models.CharField(max_length=20, choices=TICKER_TYPES, default='custom')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class LiveTickerEvent(models.Model):
    ticker = models.ForeignKey(
        LiveTicker,
        on_delete=models.CASCADE,
        related_name='events'
    )

    time = models.TimeField()
    title = models.CharField(max_length=200)
    text = models.TextField()

    link = models.URLField(blank=True, null=True)
    link_label = models.CharField(
        max_length=100,
        blank=True,
        help_text="z. B. Mehr erfahren"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.time} – {self.title}"

