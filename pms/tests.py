from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Room, Room_type


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
