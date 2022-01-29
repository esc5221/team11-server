from django.shortcuts import render
from django.db.models import Q

from rest_framework import serializers, status, viewsets, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Message, MessageRoom
from .serializers import MessageCreateSerializer, MessageRoomSerializer, MessageRoomListSerializer, MessageSerializer

from common.fcm_notification import send_push

import logging
logger = logging.getLogger('django')

# Create your views here.
class MessageViewSet(viewsets.GenericViewSet):
    serializer_class = MessageCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    #POST /message/
    def create(self, request):
        data = request.data.copy()
        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        message = serializer.instance
        try:
            fcm_token = message.receiver.fcm_token
            send_push("new_message", message, fcm_token)
        except Exception as e:
            logger.debug(e)

        return Response(status=status.HTTP_200_OK, data={"success" : True})

class MessageRoomViewSet(viewsets.GenericViewSet):
    queryset = MessageRoom.objects.all()
    serializer_class = MessageRoomSerializer
    permission_classes = (permissions.IsAuthenticated,)

    #POST /message_room/{pk}/message/
    @action(methods=['post'], detail=True)
    def message(self, request, pk):
        try:
            message_room = MessageRoom.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"detail" : "쪽지가 존재하지 않습니다."})
        if message_room.other_user(request.user)==None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail" : "wrong user for this message_room"})

        data = request.data.copy()
        data["message_room_id"] = message_room.id
        serializer = MessageSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        message = serializer.instance
        try:
            fcm_token = message.receiver.fcm_token
            send_push("new_message", message, fcm_token)
        except Exception as e:
            logger.debug(e)
            
        return Response(status=status.HTTP_200_OK, data={"success" : True})

    #GET /message_room/{pk}/
    def retrieve(self, request, pk=None):
        try:
            message_room = MessageRoom.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"detail" : "쪽지가 존재하지 않습니다."})
        if message_room.other_user(request.user)==None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail" : "wrong user for this message_room"})

        serializer = MessageRoomSerializer(message_room, context={'request': request})

        # set unread to 0
        message_room = serializer.instance
        user_unread = message_room.str_user_unread(request.user)
        setattr(message_room, user_unread, 0)
        message_room.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    
    #GET /message_room/
    def list(self, request):
        q = Q(user1=request.user)|Q(user2=request.user)
        message_room = self.get_queryset().filter(q).order_by('-last_message_at')
        serializer = MessageRoomListSerializer(message_room, context={'request': request}, many=True)

        q = Q(user1=request.user, user1_unread=0)|Q(user2=request.user, user2_unread=0)
        unread_message_room = message_room.exclude(q)

        return Response(status=status.HTTP_200_OK, 
                        data={
                            'has_new_message': unread_message_room.exists(),
                            'message_rooms' : serializer.data
                            }
                        )

    #DELETE /message_room/{pk}
    def delete(self, request, pk=None):
        return Response(status=status.HTTP_200_OK, data={"API" : "DELETE /message/pk"})
