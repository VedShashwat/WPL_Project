from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    reputation = models.IntegerField(default=0)
    player_tag = models.CharField(max_length=30, blank=True)
    trophies = models.IntegerField(default=0)
    townhall_level = models.IntegerField(default=0)
    exp_level = models.IntegerField(default=0)
    cr_player_tag = models.CharField(max_length=30, blank=True)
    cr_trophies = models.IntegerField(default=0)
    cr_best_trophies = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - profile"


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.author.username} - {self.created_at:%Y-%m-%d %H:%M}"


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:40]}"
