# Hotel Management System (Backend API & Administration)

A robust, backend-focused **Django** and **MySQL** web application designed to streamline hotel hospitality workflows. The system features a fully customized user authentication model supporting role-based access control, allowing hotel staff to manage bookings while giving checked-in guests the power to request amenities directly from their rooms.

---

## Tech Stack & Architecture

* **Backend Framework:** Python / Django
* **Database:** MySQL (Relational database mapping complex reservation states)
* **Authentication:** Custom User Identity System (`user_ui_user`)

---

## Role-Based User Workflows

The application replaces the default Django authentication system with a custom-engineered user model split into two distinct operational roles:

### 1. Hotel Employees (Staff/Admin)

Responsible for core property management and desk operations:

* **Room Inventory Management:** Create, update, and monitor room statuses (Available, Occupied, Maintenance).
* **Reservation Engine:** Process check-ins, log check-outs, and manage long-term booking schedules.
* **Service Fulfillment:** Monitor incoming guest requests (food, laundry) and flag them as completed upon delivery.

### 2. Customers (Guests)

Using a secure, unique `user_id` tied to their active stay, guests can interact with the hotel's digital ecosystem:

* **Digital Room Service:** Browse the internal culinary menu and place real-time food orders directly to their room numbers.
* **Amenity Scheduling:** Request room maintenance or schedule services like laundry directly through the system tracking.

---

## Database Schema & Architecture

The backend manages relational data constraints across several key tables to ensure transaction isolation (e.g., stopping a room from being double-booked):

* `user_ui_user` - The foundational custom user model governing permissions.
* `user_ui_room` & `user_ui_roomreservation` - Tracks room attributes (pricing, capacity) and binds them to customer booking schedules.
* `user_ui_menu`, `user_ui_order`, & `user_ui_orderdetail` - Handles menu items, tracks active food orders, and calculates billing summaries.
* `user_ui_service` & `user_ui_servicehistory` - Manages auxiliary hotel facilities like scheduling laundry services and archiving completed requests.

---

## Local Installation & Setup

Follow these steps to deploy this backend environment locally for testing or code review.

### Prerequisites

* Python 3.10+
* MySQL Server

### 1. Clone & Environment Setup

```bash
# Clone the repository
git clone https://github.com/Muhammad-989/Hotel_django.git
cd Hotel_django

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment (Windows)
.venv\Scripts\activate

```

### 2. Dependency Installation

```bash
pip install -r requirements.txt

```

*(Note: If the standard MySQL driver encounters system environment compilation errors on Windows, `pymysql` is pre-configured as a safe fallback driver).*

### 3. Database Configuration

1. Initialize a new local schema inside your MySQL instance:
```sql
CREATE DATABASE hotel_db;

```


2. Navigate to the core configuration directory: `Hotel_Management/settings.py`.
3. Locate the `DATABASES` dictionary and update the `USER` and `PASSWORD` fields with your local MySQL credentials.

### 4. Apply Migrations & Launch

Because the project uses a nested directory environment, always pass through the application root before invoking management utilities:

```bash
# Move into the Django management root
cd Hotel_Management

# Generate the custom table schemas inside MySQL
python manage.py migrate

# Boot up the local development server
python manage.py runserver

```

Once running, the admin control center and backend routing can be accessed at `[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)`.

---

> ### Backend Developer Portfolio Note
> 
> 
> This repository showcases complex database relationship management, migration tracking, and custom user inheritance logic over standard out-of-the-box framework components. It highlights optimization choices regarding pure relational modeling for service workflows.
