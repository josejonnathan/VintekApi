
from django.urls import path
from .views import MessageListView, MessageDetailView, ReplyCreateView,DeleteConversationView




urlpatterns =  [
    path('', MessageListView.as_view(), name='message_list'),
    path('<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('reply_create/', ReplyCreateView.as_view(), name='reply_create'),
    path('delete_conversation/<int:product_id>/', DeleteConversationView.as_view(), name='delete_conversation'),

]