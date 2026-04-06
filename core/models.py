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


class Conversation(models.Model):
    user_one = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dm_conversations_started')
    user_two = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dm_conversations_received')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(user_one__lt=models.F('user_two')), name='conversation_user_order_check'),
            models.UniqueConstraint(fields=['user_one', 'user_two'], name='unique_conversation_pair'),
        ]

    def save(self, *args, **kwargs):
        if self.user_one_id and self.user_two_id and self.user_one_id > self.user_two_id:
            self.user_one_id, self.user_two_id = self.user_two_id, self.user_one_id
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_direct(cls, first_user, second_user):
        if first_user.id == second_user.id:
            raise ValueError('Direct messages require two different users.')

        user_one, user_two = (first_user, second_user) if first_user.id < second_user.id else (second_user, first_user)
        conversation, _ = cls.objects.get_or_create(user_one=user_one, user_two=user_two)
        return conversation

    def __str__(self):
        return f"DM: {self.user_one.username} & {self.user_two.username}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dm_messages_sent')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:40]}"
