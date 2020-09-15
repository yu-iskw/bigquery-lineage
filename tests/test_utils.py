import os
import unittest

from bigquery_lineage.utils import (
    get_project_root
)


class TestUtils(unittest.TestCase):

    def test_get_project_path(self):
        templates_path = get_project_root()
        self.assertTrue(os.path.isdir(templates_path))
