from django.db import models

from user.models import User
from article.models import Article

# Create your models here.
class MessageRoom(models.Model):
    # article_id : 다른 글에서 시작된 쪽지를 구분하기 위함. ()
    article_id = models.PositiveIntegerField(default=0, null=False)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_room_user1', null = False)
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_room_user2', null = False)
    user1_active = models.BooleanField(default=True)
    user2_active = models.BooleanField(default=True)
    user1_unread = models.PositiveIntegerField(default=0, null=False)
    user2_unread = models.PositiveIntegerField(default=0, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=True)

    def __eq__(self, other):
        return (
            isinstance(other, MessageRoom) and 
            self.article_id == other.article_id and 
            (self.user1 == other.user1 and self.user2 == other.user2) or
            (self.user1 == other.user2 and self.user2 == other.user1)
        )

    # def save(self, *args, **kwargs):
    #     # 같은 유저끼리의 MessageRoom이 중복 생성되지않도록 id를 sort하여 model instance를 create.
    #     if self.user1.id > self.user2.id:
    #         self.user1, self.user2 = self.user2, self.user1
    #         self.user1_unread, self.user2_unread = self.user2_unread, self.user1_unread
    #     super(MessageRoom, self).save(*args, **kwargs)
    
    def other_user(self, user):
        if self.user1 == user:
            return self.user2
        elif self.user2 == user:
            return self.user1
        else:
            return

    def other_user_unread(self, user):
        if self.user1 == user:
            return self.user2_unread
        elif self.user2 == user:
            return self.user1_unread
        else:
            return
    
    def str_other_user_unread(self, user):
        if self.user1 == user:
            return "user2_unread"
        elif self.user2 == user:
            return "user1_unread"
        else:
            return

    def user_unread(self, user):
        if self.user1 == user:
            return self.user1_unread
        elif self.user2 == user:
            return self.user2_unread
        else:
            return

    def str_user_unread(self, user):
        if self.user1 == user:
            return "user1_unread"
        elif self.user2 == user:
            return "user2_unread"
        else:
            return

class Message(models.Model):
    # is_announce : "안내"이면 True
    # _active : 유저가 삭제 처리했을시 True, 아니면 False
    message_room = models.ForeignKey(MessageRoom, on_delete=models.CASCADE, related_name='message', null = False)
    is_announce = models.BooleanField(default=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender', null = False)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_receiver', null = False)
    sender_active = models.BooleanField(default=True)
    receiver_active = models.BooleanField(default=True)
    text = models.CharField(max_length=128, null = False)
    created_at = models.DateTimeField(auto_now_add=True)