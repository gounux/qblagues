#! python3  # noqa: E265

"""
    Main plugin module.
"""

# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# project
from qblagues.__about__ import __title__
from qblagues.blague_task import BlagueTask
from qblagues.gui.dlg_settings import PlgOptionsFactory
from qblagues.resources import *  # noqa
from qblagues.toolbelt import PlgLogger, PlgTranslator

# ############################################################################
# ########## Classes ###############
# ##################################


class QblaguesPlugin:
    action_blagues: QAction
    action_settings: QAction

    @property
    def menu_title(self) -> str:
        return "&QBlague"

    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.log = PlgLogger().log

        # translation
        plg_translation_mngr = PlgTranslator()
        translator = plg_translation_mngr.get_translator()
        if translator:
            QCoreApplication.installTranslator(translator)
        self.tr = plg_translation_mngr.tr

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)
        self.toolbar = self.iface.addToolBar(self.menu_title)

        # Blague action
        self.action_blagues = QAction(
            QIcon(":/plugins/qblagues/mdrrr"),
            self.tr("Blague"),
            self.iface.mainWindow(),
        )
        self.action_blagues.triggered.connect(self.blague)
        self.iface.addWebToolBarIcon(self.action_blagues)

        # Settings action
        self.action_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings"),
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(
            lambda: self.iface.showOptionsDialog(
                currentPage="mOptionsPage{}".format(__title__)
            )
        )

        # Add actions to toolbar
        self.toolbar.addAction(self.action_blagues)

        # Add actions to QGIS web menu
        self.iface.addPluginToWebMenu(self.menu_title, self.action_blagues)
        self.iface.addPluginToWebMenu(self.menu_title, self.action_settings)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginWebMenu(self.menu_title, self.action_blagues)
        self.iface.removePluginWebMenu(self.menu_title, self.action_settings)

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove actions
        del self.toolbar
        del self.action_blagues
        del self.action_settings

    def blague(self):
        blague_task = BlagueTask("Blague", self.iface)
        QgsApplication.taskManager().addTask(blague_task)
