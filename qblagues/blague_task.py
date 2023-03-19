import random
from datetime import datetime, timedelta
from time import sleep
from typing import Any, Dict

import requests
from qgis.core import Qgis, QgsApplication, QgsMessageLog, QgsTask
from qgis.gui import QgisInterface
from qgis.PyQt.QtGui import QTransform
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
        dizzy_task = DizzyTask("Disiz la Peste", self.iface)
        QgsApplication.taskManager().addTask(dizzy_task)


class DizzyTask(QgsTask):
    def __init__(
        self,
        description: str,
        iface: QgisInterface,
        duration: float = 2.4,
        refresh: float = 0.08,
    ):
        super().__init__(description, QgsTask.CanCancel)
        self.iface = iface
        self.duration = duration
        self.refresh = refresh

    def run(self) -> bool:
        canvas = self.iface.mapCanvas()
        stop_time = datetime.now() + timedelta(seconds=self.duration)

        r = 0
        while datetime.now() < stop_time:

            d = 12  # max offset
            r = 8  # max angle

            rect = canvas.sceneRect()
            if rect.x() < -d or rect.x() > d or rect.y() < -d or rect.y() > d:
                # do not affect panning
                pass

            else:
                rect.moveTo(random.randint(-d, d), random.randint(-d, d))
                canvas.setSceneRect(rect)
                matrix = QTransform()
                matrix.rotate(random.randint(-r, r))
                canvas.setTransform(matrix)
                sleep(self.refresh)

        canvas.setSceneRect(canvas.sceneRect())
        canvas.setTransform(QTransform())
        return True
