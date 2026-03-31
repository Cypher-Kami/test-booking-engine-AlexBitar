from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Room, Room_type, Booking, Customer


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class RoomsFilterViewTest(TestCase):
    def setUp(self):
        room_type = Room_type.objects.create(name="Individual", price=20, max_guests=1)
        Room.objects.create(name="Room 1.1", room_type=room_type, description="")
        Room.objects.create(name="Room 1.2", room_type=room_type, description="")
        Room.objects.create(name="Room 2.1", room_type=room_type, description="")

    def test_no_filter_returns_all_rooms(self):
        response = self.client.get(reverse("rooms"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["rooms"]), 3)

    def test_filter_returns_matching_rooms(self):
        response = self.client.get(reverse("rooms"), {"name": "Room 1"})
        self.assertEqual(response.status_code, 200)
        names = [r["name"] for r in response.context["rooms"]]
        self.assertIn("Room 1.1", names)
        self.assertIn("Room 1.2", names)
        self.assertNotIn("Room 2.1", names)

    def test_filter_is_case_insensitive(self):
        response = self.client.get(reverse("rooms"), {"name": "room 1"})
        self.assertEqual(len(response.context["rooms"]), 2)

    def test_filter_no_match_returns_empty(self):
        response = self.client.get(reverse("rooms"), {"name": "XYZ"})
        self.assertEqual(len(response.context["rooms"]), 0)


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class DashboardOccupancyTest(TestCase):
    def setUp(self):
        self.room_type = Room_type.objects.create(name="Individual", price=20, max_guests=1)
        self.customer = Customer.objects.create(name="Test User", email="test@test.com", phone="123456789")
        for i in range(1, 5):
            Room.objects.create(name=f"Room {i}", room_type=self.room_type, description="")

    def _make_booking(self, room, state=Booking.NEW):
        Booking.objects.create(
            checkin="2022-01-01", checkout="2022-01-02",
            room=room, guests=1, customer=self.customer,
            total=20, code=f"CODE{room.id}", state=state
        )

    def test_occupancy_zero_with_no_bookings(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["dashboard"]["occupancy"], 0)

    def test_occupancy_correct_percentage(self):
        rooms = list(Room.objects.all())
        self._make_booking(rooms[0])  # 1 confirmed out of 4 rooms = 25%
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["dashboard"]["occupancy"], 25.0)

    def test_occupancy_100_percent(self):
        for room in Room.objects.all():
            self._make_booking(room)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["dashboard"]["occupancy"], 100.0)

    def test_cancelled_bookings_not_counted(self):
        rooms = list(Room.objects.all())
        self._make_booking(rooms[0], state=Booking.DELETED)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["dashboard"]["occupancy"], 0)
