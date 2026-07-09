# views.py
import json
from datetime import timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.forms.models import model_to_dict

from .models import *
from django.utils import timezone

"""
   Example JSON:
   {
       "email": "user@example.com",
       "first_name": "John",
       "last_name": "Doe",
       "password": "securepassword123"
   }
"""
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')

        if not email or not first_name or not last_name or not password:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'User with this email already exists'}, status=400)

        User.objects.create_user(email=email, first_name=first_name, last_name=last_name, password=password)
        return JsonResponse({'success': 'User created successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


"""
    Example JSON:
    {
        "email": "user@example.com",
        "password": "securepassword123"
    }
"""
def login_view(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': 'User logged in successfully'})
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def get_user_details(request):
    if request.method == 'GET':
        user = request.user

        user_details = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'age': user.age,
            'gender': user.gender,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        }

        return JsonResponse(user_details)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

"""
    Example JSON:
    {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "1234567890",
        "age": 30,
        "gender": "M"
    }
"""
@login_required
def update_user(request):
    if request.method == 'POST':
        user = request.user
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.phone_number = data.get('phone_number', user.phone_number)
        user.age = data.get('age', user.age)
        user.gender = data.get('gender', user.gender)
        user.save()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def deactivate_user(request):
    if request.method == 'POST':
        user = request.user  # Get the currently authenticated user

        user.is_active = False  # Deactivate the user
        user.save()

        return JsonResponse({'success': 'User account has been deactivated'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def check_reservation(request):
    if request.method == 'GET':
        user = request.user
        today = timezone.now().date()
        reservations = RoomReservation.objects.filter(user=user, check_in_date__lte=today, check_out_date__gte=today)
        reservations_dict = list(reservations.values())
        return JsonResponse({'has_reservation': bool(reservations_dict)})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


"""
 {
        "check_in_date": "2024-08-20",
        "check_out_date": "2024-08-25"
  }
"""
@login_required
def checkRoomsAvailability(request):
    if request.method == 'GET':
        today = timezone.now().date()

        # Fetch all rooms
        rooms = Room.objects.all()
        room_availability = {}

        for room in rooms:
            # Fetch reservations for the room
            reservations = RoomReservation.objects.filter(room=room, check_out_date__gte=today).order_by(
                'check_in_date')
            reservations_dict = list(reservations.values())

            # Initialize availability periods
            availability_periods = []
            current_start = today

            for reservation in reservations_dict:
                if reservation['check_in_date'] > current_start:
                    availability_periods.append({
                        'start_date': current_start,
                        'end_date': reservation['check_in_date']
                    })
                current_start = max(current_start, reservation['check_out_date'])
            end_date = current_start + timedelta(days=40)
            # Add the period after the last reservation
            availability_periods.append({
                'start_date': current_start,
                'end_date': end_date
            })

            room_availability[room.room_no] = availability_periods

        return JsonResponse(room_availability)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        overlapping_reservations = RoomReservation.objects.filter(
            Q(Q(check_in_date__gte=check_in_date) & Q(check_in_date__lt=check_out_date)) |
            Q(Q(check_out_date__gt=check_in_date) & Q(check_out_date__lte=check_out_date))
        )
        overlapping_reservations_dict = list(overlapping_reservations.values())

        # Get the rooms associated with the overlapping reservations
        overlapping_rooms = [reservation['room_id'] for reservation in overlapping_reservations_dict]

        # Find all rooms that are not in the list of overlapping rooms
        available_rooms = Room.objects.exclude(room_no__in=overlapping_rooms)

        # Return the room numbers of the available rooms
        return JsonResponse({'available_rooms': list(available_rooms.values_list('room_no', flat=True))})


"""
    Example JSON:
    {
        "room_no": 10,
        "check_in_date": "2024-08-20",
        "check_out_date": "2024-08-25"
    }
"""
@login_required
def make_reservation(request):
    if request.method == 'POST':
        user = request.user

        # Load and validate JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        room_no = data.get('room_no')
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')

        # Validate required fields
        if not (room_no and check_in_date and check_out_date):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        # Get room and validate dates
        try:
            room = Room.objects.get(room_no=room_no)
        except Room.DoesNotExist:
            return JsonResponse({'error': 'Room No not found'}, status=404)

        try:
            check_in = parse_date(check_in_date)
            check_out = parse_date(check_out_date)
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        if check_in >= check_out:
            return JsonResponse({'error': 'check_in_date cannot be greater than check_out_date'}, status=400)

        # Check for existing reservations
        existing_reservations = RoomReservation.objects.filter(
            room=room,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        )

        if existing_reservations.exists():
            return JsonResponse({'error': 'Room not available in selected dates'}, status=409)

        # Create and save the reservation
        reservation = RoomReservation(
            user=user,
            room=room,
            check_in_date=check_in,
            check_out_date=check_out
        )
        reservation.save()

        return JsonResponse({'success': 'Reservation has been made'}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


"""
    Example JSON for POST request:
    {
        "service": "Laundry"
    }
"""
@login_required
def services(request):
    if request.method == 'GET':
        services = Service.objects.all().values()
        return JsonResponse({'services': list(services)}, safe=False)
    if request.method == 'POST':
        user = request.user
        today = timezone.now().date()
        reservation = RoomReservation.objects.filter(
            user=user,
            check_in_date__lte=today,
            check_out_date__gte=today
        ).first()
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        selected_service = data.get('service')
        serv = Service.objects.get(service_name=selected_service)
        service = ServiceHistory(
            reservation=reservation,
            service=serv,
            service_date=today
        )
        service.save()
        return JsonResponse({'success': 'Service scheduled successfully'}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


"""
    Example JSON for POST request:
    {
        "item1": 2,  # Item name as key, quantity as value
        "item2": 3
    }
"""
@login_required
def order_food(request):
    if request.method=='GET':
        menu_items = Menu.objects.all().values()
        menu_list = list(menu_items)
        return JsonResponse({'MENU':menu_list})
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        user = request.user
        today = timezone.now().date()

        reservation = RoomReservation.objects.filter(
            user=user,
            check_in_date__lte=today,
            check_out_date__gte=today
        ).first()
        today = timezone.now().date()
        order = Order(
            reservation=reservation,
            order_date=today
        )
        order.save()
        for item, quantity in data.items():
            itm=Menu.objects.get(item_name=item)
            orderDetail = OrderDetail(
                order=order,
                item=itm,
                quantity=quantity
            )
            orderDetail.save()

        return JsonResponse({'success': 'Order confirmed successfully'}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def getservicehistory(request):
    if request.method == 'GET':
        user = request.user
        reservations = RoomReservation.objects.filter(user=user)
        history_data = []

        for reservation in reservations:
            servicehistory = ServiceHistory.objects.filter(reservation=reservation)
            for service in servicehistory:
                history_data.append({
                    'reservation': model_to_dict(service.reservation),
                    'service': model_to_dict(service.service),
                    'service_date': service.service_date,
                })

        return JsonResponse(history_data, safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@login_required
def getfoodhis(request):
    if request.method == 'GET':
        user = request.user
        reservations = RoomReservation.objects.filter(user=user)
        history_data = []

        for reservation in reservations:
            orderhistory = Order.objects.filter(reservation=reservation)
            for order in orderhistory:
                order_details = OrderDetail.objects.filter(order=order)
                details = []
                for detail in order_details:
                    details.append({
                        'item': detail.item.name,
                        'quantity': detail.quantity,
                    })
                history_data.append({
                    'reservation': model_to_dict(reservation),
                    'service_date': order.order_date,
                    'order_details': details,
                })

        return JsonResponse(history_data, safe=False)


