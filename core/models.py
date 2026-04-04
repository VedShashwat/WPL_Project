from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    game_id = models.CharField(max_length=100)
    current_rank = models.CharField(max_length=50, default='Unranked')
    win_rate = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.game_id}"
