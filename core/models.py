from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    game_id = models.CharField(max_length=100)
    current_rank = models.CharField(max_length=50, default='Unranked')
    win_rate = models.FloatField(default=0.0)
    reputation = models.IntegerField(default=0)
    player_tag = models.CharField(max_length=30, blank=True)
    trophies = models.IntegerField(default=0)
    townhall_level = models.IntegerField(default=0)
    exp_level = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.game_id}"


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.author.username} - {self.created_at:%Y-%m-%d %H:%M}"
