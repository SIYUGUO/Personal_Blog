from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
# Django-taggit
from taggit.managers import TaggableManager

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name="Post_likes",blank=True)
    favorites = models.ManyToManyField(User, related_name="Post_favorites",blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk':self.pk})



