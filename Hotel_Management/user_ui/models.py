from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The Password field must be set')  # Ensure password is provided
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        if not password:
            raise ValueError('The Password field must be set for superusers')  # Ensure password is provided
        user = self.create_user(email, first_name, last_name, password)
        user.is_admin = True
        user.save(using=self._db)
        return user
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField(blank=True,null=True)
    gender = models.CharField(max_length=1,blank=True,null=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    def __str__(self):
        return self.email
    @property
    def is_staff(self):
        return self.is_admin

class Room(models.Model):
    room_no = models.AutoField(primary_key=True)
    room_type = models.CharField(max_length=100)


class Service(models.Model):
    service_name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=500)


class Menu(models.Model):
    item_name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=500)
    price = models.IntegerField()
    def __str__(self):
        return self.item_name


class RoomReservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()


class Order(models.Model):
    reservation = models.ForeignKey(RoomReservation, on_delete=models.CASCADE)
    order_date = models.DateField()


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class ServiceHistory(models.Model):
    reservation = models.ForeignKey(RoomReservation, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_date = models.DateField()
