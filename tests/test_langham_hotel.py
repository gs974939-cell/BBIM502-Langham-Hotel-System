import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import langham_hotel as hotel


class HotelApplicationTests(unittest.TestCase):
    def setUp(self):
        self.saved_rooms = hotel.rooms.copy()
        self.saved_allocations = hotel.allocations.copy()
        self.saved_file = hotel.DATA_FILE
        self.temp_directory = tempfile.TemporaryDirectory()
        hotel.rooms.clear()
        hotel.allocations.clear()
        hotel.DATA_FILE = Path(self.temp_directory.name) / "LHMS_Studentid.txt"

    def tearDown(self):
        hotel.rooms.clear()
        hotel.rooms.update(self.saved_rooms)
        hotel.allocations.clear()
        hotel.allocations.update(self.saved_allocations)
        hotel.DATA_FILE = self.saved_file
        self.temp_directory.cleanup()

    def test_room_batches_preserve_existing_rooms(self):
        first_batch = ["2", "211", "Premium corner suite", "195", "212", "City view room", "175"]
        second_batch = ["1", "213", "Garden room", "160"]
        with patch("builtins.input", side_effect=first_batch), contextlib.redirect_stdout(io.StringIO()):
            hotel.add_rooms()
        with patch("builtins.input", side_effect=second_batch), contextlib.redirect_stdout(io.StringIO()):
            hotel.add_rooms()
        self.assertEqual(set(hotel.rooms), {"211", "212", "213"})

    def test_duplicate_room_number_is_rejected(self):
        hotel.rooms["211"] = {"room_number": 211, "features": "Suite", "nightly_rate": 195.0, "allocated": False}
        inputs = ["1", "211", "214", "Balcony room", "185"]
        with patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(io.StringIO()):
            hotel.add_rooms()
        self.assertIn("214", hotel.rooms)
        self.assertEqual(len(hotel.rooms), 2)

    def test_room_deletion_refuses_active_allocation(self):
        hotel.rooms["211"] = {"room_number": 211, "features": "Suite", "nightly_rate": 195.0, "allocated": True}
        hotel.allocations["211"] = {"room_number": 211, "customer_number": 6012, "customer_name": "Oliver Reed", "nights": 2, "nightly_rate": 195.0, "allocated_at": "2026-10-30T09:00:00"}
        with patch("builtins.input", return_value="211"), contextlib.redirect_stdout(io.StringIO()):
            hotel.delete_room()
        self.assertIn("211", hotel.rooms)

    def test_allocation_records_guest_and_occupancy(self):
        hotel.rooms["211"] = {"room_number": 211, "features": "Premium corner suite", "nightly_rate": 195.0, "allocated": False}
        inputs = ["1", "211", "6012", "Oliver Reed", "3"]
        with patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(io.StringIO()):
            hotel.allocate_rooms()
        self.assertEqual(hotel.allocations["211"]["customer_name"], "Oliver Reed")
        self.assertTrue(hotel.rooms["211"]["allocated"])

    def test_duplicate_active_customer_number_is_rejected(self):
        hotel.rooms["211"] = {"room_number": 211, "features": "Suite", "nightly_rate": 195.0, "allocated": False}
        hotel.rooms["212"] = {"room_number": 212, "features": "City view", "nightly_rate": 175.0, "allocated": False}
        hotel.allocations["211"] = {"room_number": 211, "customer_number": 6012, "customer_name": "Oliver Reed", "nights": 2, "nightly_rate": 195.0, "allocated_at": "2026-10-30T09:00:00"}
        inputs = ["1", "212", "6012", "6013", "Amelia Clarke", "2"]
        with patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(io.StringIO()):
            hotel.allocate_rooms()
        self.assertEqual(hotel.allocations["212"]["customer_number"], 6013)

    def test_billing_releases_room(self):
        hotel.rooms["211"] = {"room_number": 211, "features": "Suite", "nightly_rate": 195.0, "allocated": True}
        hotel.allocations["211"] = {"room_number": 211, "customer_number": 6012, "customer_name": "Oliver Reed", "nights": 2, "nightly_rate": 195.0, "allocated_at": "2026-10-30T09:00:00"}
        with patch("builtins.input", return_value="211"), contextlib.redirect_stdout(io.StringIO()) as output:
            hotel.billing_and_deallocate()
        self.assertNotIn("211", hotel.allocations)
        self.assertFalse(hotel.rooms["211"]["allocated"])
        self.assertIn("Total due: NZD 448.50", output.getvalue())

    def test_save_and_read_file(self):
        hotel.rooms["211"] = {"room_number": 211, "features": "Premium suite", "nightly_rate": 195.0, "allocated": True}
        hotel.allocations["211"] = {"room_number": 211, "customer_number": 6012, "customer_name": "Oliver Reed", "nights": 2, "nightly_rate": 195.0, "allocated_at": "2026-10-30T09:00:00"}
        with contextlib.redirect_stdout(io.StringIO()):
            hotel.save_allocations()
        stored = json.loads(hotel.DATA_FILE.read_text(encoding="utf-8"))
        self.assertEqual(stored["allocations"]["211"]["customer_name"], "Oliver Reed")
        with contextlib.redirect_stdout(io.StringIO()) as output:
            hotel.show_allocations_from_file()
        self.assertIn("Oliver Reed", output.getvalue())

    def test_backup_copies_data_then_clears_source(self):
        hotel.DATA_FILE.write_text("sample allocation record", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            hotel.backup_and_clear_file()
        backups = list(Path(self.temp_directory.name).glob("LHMS_Studentid_Backup_*.txt"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "sample allocation record\n")
        self.assertEqual(hotel.DATA_FILE.read_text(encoding="utf-8"), "")

    def test_missing_file_is_reported(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            hotel.show_allocations_from_file()
        self.assertIn("was not found", output.getvalue())


if __name__ == "__main__":
    unittest.main()
