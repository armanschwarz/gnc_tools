import os
import tempfile
import unittest
from pathlib import Path

from gnc_attachment_check import check_attachments

FIXTURE_DIR = Path(__file__).parent


class TestAttachmentCheck(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = self.temp_dir.name
        open(os.path.join(self.base_path, "test_invoice.txt"), "w").close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_attachment_check(self):
        errors, file_paths = check_attachments(
            str(FIXTURE_DIR / "test_accounts.gnucash"),
            self.base_path,
        )

        self.assertCountEqual(file_paths, [
            os.path.join(self.base_path, "test_invoice_missing.txt"),
            os.path.join(self.base_path, "test_invoice.txt"),
        ])
        self.assertEqual(errors, [
            os.path.join(self.base_path, "test_invoice_missing.txt"),
        ])
