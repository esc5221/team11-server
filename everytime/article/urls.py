from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *

app_name = 'article'

router = SimpleRouter()

#router.register('board/<int:board_id>/article', ArticleViewSet, basename='article') 
router.register(r'board/(?P<board_id>\d+)/article', ArticleViewSet, basename='article')

urlpatterns = [
    path('', include(router.urls))
]