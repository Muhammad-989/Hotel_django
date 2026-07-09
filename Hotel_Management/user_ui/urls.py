from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('user/update/', update_user, name='user_update'),
    path('user/delete/', deactivate_user, name='user_delete'),
    path('user/reservations/', check_reservation, name='user_reservations'),
    path('user/details/', get_user_details, name='user_details'),
    path('user/rooms_availability/', checkRoomsAvailability, name='rooms_availability'),
    path('user/make_reservation/', make_reservation, name='make_reservation'),
    path('user/services/', services, name='services'),
    path('user/food_order/', order_food, name='food_order'),
    path('user/service_history/', getservicehistory, name='service_history'),
    path('user/order_history/', getfoodhis, name='order_history'),
]

