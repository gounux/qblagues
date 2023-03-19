#! python3  # noqa: E265

"""
    Plugin settings.
"""

# standard
from dataclasses import asdict, dataclass, fields
from typing import List

# PyQGIS
from qgis.core import QgsSettings

# package
import qblagues.toolbelt.log_handler as log_hdlr
from qblagues.__about__ import __api_base_url__, __title__, __version__

# ############################################################################
# ########## Classes ###############
# ##################################


@dataclass
class PlgSettingsStructure:
    """Plugin settings structure and defaults values."""

    # blagues api
    api_base_url: str = __api_base_url__
    api_access_token: str = ""

    # categories
    category_global: bool = True
    category_dev: bool = True
    category_dark: bool = False
    category_limit: bool = False
    category_beauf: bool = False
    category_blondes: bool = False

    # global
    debug_mode: bool = False
    version: str = __version__

    @property
    def excluded_categories(self) -> List[str]:
        """Returns blagues categories that are excluded (not selected)
        :return:
        """
        return [
            cat
            for cat, active in [
                ("global", self.category_global),
                ("dev", self.category_dev),
                ("dark", self.category_dark),
                ("limit", self.category_limit),
                ("beauf", self.category_beauf),
                ("blondes", self.category_blondes),
            ]
            if active
        ]


class PlgOptionsManager:
    @staticmethod
    def get_plg_settings() -> PlgSettingsStructure:
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings
        :rtype: PlgSettingsStructure
        """
        # get dataclass fields definition
        settings_fields = fields(PlgSettingsStructure)

        # retrieve settings from QGIS/Qt
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # map settings values to preferences object
        li_settings_values = []
        for i in settings_fields:
            li_settings_values.append(
                settings.value(key=i.name, defaultValue=i.default, type=i.type)
            )

        # instanciate new settings object
        options = PlgSettingsStructure(*li_settings_values)

        settings.endGroup()

        return options

    @staticmethod
    def get_value_from_key(key: str, default=None, exp_type=None):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        if not hasattr(PlgSettingsStructure, key):
            log_hdlr.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(
                    ",".join(PlgSettingsStructure._fields)
                ),
                log_level=1,
            )
            return None

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            out_value = settings.value(key=key, defaultValue=default, type=exp_type)
        except Exception as err:
            log_hdlr.PlgLogger.log(
                message="Error occurred trying to get settings: {}.Trace: {}".format(
                    key, err
                )
            )
            out_value = None

        settings.endGroup()

        return out_value

    @classmethod
    def set_value_from_key(cls, key: str, value) -> bool:
        """Set plugin QSettings value using the key.

        :param key: QSettings key
        :type key: str
        :param value: value to set
        :type value: depending on the settings
        :return: operation status
        :rtype: bool
        """
        if not hasattr(PlgSettingsStructure, key):
            log_hdlr.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(
                    ",".join(PlgSettingsStructure._fields)
                ),
                log_level=2,
            )
            return False

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            settings.setValue(key, value)
            out_value = True
        except Exception as err:
            log_hdlr.PlgLogger.log(
                message="Error occurred trying to set settings: {}.Trace: {}".format(
                    key, err
                )
            )
            out_value = False

        settings.endGroup()

        return out_value

    @classmethod
    def save_from_object(cls, plugin_settings_obj: PlgSettingsStructure):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        settings = QgsSettings()
        settings.beginGroup(__title__)

        for k, v in asdict(plugin_settings_obj).items():
            cls.set_value_from_key(k, v)

        settings.endGroup()
