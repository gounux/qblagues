#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash

        # for whole tests
        python -m unittest tests.qgis.test_plg_preferences
        # for specific test
        python -m unittest tests.qgis.test_plg_preferences.TestPlgPreferences.test_plg_preferences_structure
"""

from typing import List

# standard library
from qgis.testing import unittest

# project
from qblagues.__about__ import __api_base_url__, __version__
from qblagues.toolbelt.preferences import PlgSettingsStructure

# ############################################################################
# ########## Classes #############
# ################################


class TestPlgPreferences(unittest.TestCase):
    def test_plg_preferences_structure(self):
        """Test settings types and default values."""
        settings = PlgSettingsStructure()

        # blagues api
        self.assertTrue(hasattr(settings, "api_base_url"))
        self.assertIsInstance(settings.api_base_url, str)
        self.assertEqual(settings.api_base_url, __api_base_url__)
        self.assertTrue(hasattr(settings, "api_access_token"))
        self.assertIsInstance(settings.api_access_token, str)
        self.assertEqual(settings.api_access_token, "")

        # blagues categories
        self.assertTrue(hasattr(settings, "category_global"))
        self.assertIsInstance(settings.category_global, bool)
        self.assertEqual(settings.category_global, True)
        self.assertTrue(hasattr(settings, "category_blondes"))
        self.assertIsInstance(settings.category_blondes, bool)
        self.assertEqual(settings.category_blondes, False)

        excluded = settings.excluded_categories
        self.assertIsInstance(excluded, List)
        self.assertEqual(len(excluded), 4)
        self.assertIn("dark", excluded)
        self.assertIn("limit", excluded)
        self.assertIn("beauf", excluded)
        self.assertIn("blondes", excluded)
        self.assertNotIn("global", excluded)
        self.assertNotIn("dev", excluded)

        # global
        self.assertTrue(hasattr(settings, "debug_mode"))
        self.assertIsInstance(settings.debug_mode, bool)
        self.assertEqual(settings.debug_mode, False)
        self.assertTrue(hasattr(settings, "version"))
        self.assertIsInstance(settings.version, str)
        self.assertEqual(settings.version, __version__)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
