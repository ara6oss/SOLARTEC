from django.urls import path
from .views import *
app_name = 'api'



urlpatterns = [

   path('sendMessage', sendMessageView.as_view(), name='send_message'),
   path('sendFile', sendMultimediaView.as_view(), name='send_file'),
   path('sendLocation', sendLocationView.as_view(), name='send_location'),
   path('getNotification', getNotificationView.as_view(), name='get_notification'),
   path('selenium', selenium.as_view(), name='selenium'),

]