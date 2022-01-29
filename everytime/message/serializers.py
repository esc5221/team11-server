from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone
from datetime import datetime

from rest_framework import serializers, status

from common.custom_exception import CustomException

from .models import Message, MessageRoom
from board.models import Board
from article.models import Article
from comment.models import Comment
from comment.serializers import CommentSerializer

import logging
logger = logging.getLogger('django')

def time_formatting(timezone_obj):
    cur_year = timezone.localtime().year
    obj_year = timezone_obj.year
    if cur_year==obj_year:
        return timezone_obj.strftime('%m/%d %H:%M')
    else:
        return timezone_obj.strftime('%y/%m/%d %H:%M')

class MessageCreateSerializer(serializers.ModelSerializer):
    article_id = serializers.IntegerField(min_value=1, required=False)
    comment_id = serializers.IntegerField(min_value=1, required=False)
    text = serializers.CharField(max_length=128, required=True)

    class Meta:
        model =  Message
        fields = ('article_id', 'comment_id', 'text',)

    def validate(self, data):
        if bool(data.get('article_id')) ^ bool(data.get('comment_id')) == False:
            raise CustomException("article_id와 comment_id 중 하나만을 입력해야합니다.", status.HTTP_400_BAD_REQUEST)
        return data

    def create(self, validated_data):
        user1 = self.context['request'].user
        if article_id:=validated_data.get('article_id'):
            try:
                obj = Article.objects.get(id=article_id)
                is_anonymous = obj.is_anonymous
                board = obj.board
                user2 = obj.writer
                text = obj.title if bool(obj.title) else obj.text
                text = f"{board.name}에서 작성된 글을 통해 시작된 쪽지입니다.\n" \
                       + f"글 내용: {text[0:50]}"
            except:
                raise CustomException("article_id가 잘못되었습니다.", status.HTTP_400_BAD_REQUEST)
        elif comment_id:=validated_data.get('comment_id'):
            try:
                obj = Comment.objects.get(id=comment_id)
                is_anonymous = obj.is_anonymous
                board = obj.article.board
                user2 = obj.commenter
                user_nickname = CommentSerializer.get_user_nickname(obj, obj)
                text = obj.text
                text = f"{board.name}에서 작성된 {user_nickname}의 댓글을 통해 시작된 쪽지입니다.\n \
                        글 내용: {text[0:50]}"
                article_id = obj.article.id
            except:
                raise CustomException("comment_id가 잘못되었습니다.", status.HTTP_400_BAD_REQUEST)
        if user1 == user2:
            raise CustomException("자신에게 쪽지를 보낼 수 없습니다.", status.HTTP_400_BAD_REQUEST)

        try:
            message_room = MessageRoom.objects.get(article_id=article_id, user1=user1, user2=user2, is_anonymous=is_anonymous)
        except Exception as e:
            logger.debug(e)
            message_room = MessageRoom.objects.create(article_id=article_id, user1=user1, user2=user2, is_anonymous=is_anonymous, user2_unread=1)
            Message.objects.create(
                message_room=message_room, 
                is_announce=True,
                sender=user1,
                receiver=user2,
                text=text
            )
        message = Message.objects.create(
                    message_room=message_room, 
                    is_announce=False,
                    sender=user1,
                    receiver=user2,
                    text=validated_data.get("text")
                )
        return message

class MessageRoomListSerializer(serializers.ModelSerializer):
    user_nickname = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model =  MessageRoom
        fields = ('id', 'user_nickname', 'unread_count', 'last_message',)

    def get_user_nickname(self, obj):
        return "익명" if obj.is_anonymous else obj.other_user(self.context['request'].user).nickname
    
    def get_unread_count(self, obj):
        return obj.user_unread(self.context['request'].user)
    
    def get_last_message(self, obj):
        queryset = Message.objects.filter(message_room=obj).last()
        return MessageSerializer(queryset).data

class MessageRoomSerializer(serializers.ModelSerializer):
    user_nickname = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    class Meta:
        model =  MessageRoom
        fields = ('id', 'user_nickname', 'messages',)

    def get_user_nickname(self, obj):
        return "익명" if obj.is_anonymous else obj.other_user(self.context['request'].user).nickname

    def get_messages(self, obj):
        queryset = Message.objects.filter(message_room=obj).order_by('-id')
        return MessageInroomSerializer(queryset, many=True, context=self.context).data
    
class MessageRoomListSerializer(MessageRoomSerializer):
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta(MessageRoomSerializer.Meta):
        fields = ('id', 'user_nickname', 'unread_count', 'last_message',)

    def get_unread_count(self, obj):
        return obj.user_unread(self.context['request'].user)
    
    def get_last_message(self, obj):
        queryset = Message.objects.filter(message_room=obj).last()
        return MessageSerializer(queryset).data

class MessageSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    message_room_id = serializers.IntegerField(write_only=True)

    class Meta:
        model =  Message
        fields = ('id', 'created_at', 'text', 'message_room_id',)

    def create(self, validated_data):
        message_room = MessageRoom.objects.get(id=validated_data['message_room_id'])
        sender = self.context['request'].user
        validated_data['sender'] = sender
        validated_data['receiver'] = message_room.other_user(sender)
        other_user_unread = message_room.str_other_user_unread(sender)
        unread_count = message_room.other_user_unread(sender) + 1
        setattr(message_room, other_user_unread, unread_count)

        message_room.last_message_at = datetime.now()
        message_room.save()

        return super().create(validated_data)
        
    def get_created_at(self, obj):
        local_created_at = timezone.localtime(obj.created_at)
        return time_formatting(local_created_at)

class MessageInroomSerializer(MessageSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model =  Message
        fields = ('id', 'type', 'created_at', 'text', )

    def get_type(self, obj):
        if obj.is_announce == True:
            return "안내"
        elif obj.sender == self.context['request'].user:
            return "보낸 쪽지"
        else:
            return "받은 쪽지"
