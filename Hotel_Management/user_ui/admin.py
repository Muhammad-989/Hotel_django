from django.contrib import admin
from .models import User, Room, Service, Menu, RoomReservation, Order, OrderDetail, ServiceHistory

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Service)
admin.site.register(Menu)
admin.site.register(RoomReservation)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(ServiceHistory)
