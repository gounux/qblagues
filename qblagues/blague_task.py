from typing import Any, Dict

import requests
from qgis.core import Qgis, QgsApplication, QgsMessageLog, QgsTask
from qgis.gui import QgisInterface
from requests import Response

from qblagues.toolbelt import PlgLogger, PlgOptionsManager, PlgTranslator


class BlagueTask(QgsTask):
    """Background task that fetches a blague on API and add it to QGIS"""

    blague: Dict[str, Any]
    exception: Exception

    def __init__(self, description: str, iface: QgisInterface):
        super().__init__(description)
        self.iface = iface
        self.tr = PlgTranslator().tr
        self.log = PlgLogger().log

    def run(self) -> bool:
        # get blaguesAPI config from settings
        settings = PlgOptionsManager.get_plg_settings()
        base_url = settings.api_base_url
        token = settings.api_access_token
        excl = settings.excluded_categories

        if not token:
            ex = Exception(
                "No BlaguesAPI access token provided ! Please get one and set it in the plugin's settings"
            )
            self.log(message=str(ex), log_level=Qgis.Critical)
            self.exception = ex
            return False

        # call blaguesAPI to fetch wan blague
        try:
            r: Response = requests.get(
                f"{base_url}/api/random",
                params={"disallow": excl},
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )
        except Exception as ex:
            self.log(message=str(ex), log_level=Qgis.Critical)
            self.exception = ex
            return False

        self.blague = r.json()
        return True

    def cancel(self):
        self.log(
            message=f"BlagueTask '{self.description()}' canceled",
            log_level=Qgis.Critical,
        )
        super().cancel()

    def finished(self, result: bool) -> None:
        # check if task was successful
        if not result:
            self.iface.messageBar().pushCritical(self.tr("Error"), str(self.exception))
            return
        # display blague in QGIS
        cat, joke, answer = (
            self.blague["type"],
            self.blague["joke"],
            self.blague["answer"],
        )
        self.log(
            message=f"[{cat.upper()} #{self.blague['id']}] {self.blague['joke']} {self.blague['answer']}",
            log_level=Qgis.Success,
        )
        if joke.endswith("?"):
            self.iface.messageBar().pushSuccess(cat.upper(), answer)
            self.iface.messageBar().pushWarning(cat.upper(), joke)
        else:
            self.iface.messageBar().pushSuccess(cat.upper(), f"{joke} {answer}")
