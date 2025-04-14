import uuid
import os
from pathlib import Path

import catppuccin
import matplotlib.style
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from prodadvert_bot.application.interfaces.plotter import Plotter


class PlotterImpl(Plotter):
    def plot_views_and_clicks(
            self,
            days: list[int],
            views: list[int],
            clicks: list[int],
    ) -> str:
        matplotlib.style.use(catppuccin.PALETTE.mocha.identifier)
        ax = plt.figure().gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.plot(days, views, '-.', label="Views")
        plt.plot(days, clicks, label="Clicks")
        plt.xlabel("Dates")
        plt.ylabel("Count")
        plt.legend()
        plt.title("Daily statistics")
        uid = uuid.uuid4()
        path = f"plots/{uid}.png"
        Path("plots").mkdir(parents=True, exist_ok=True)
        plt.savefig(path)
        plt.cla()
        plt.clf()
        return path

    def dispose_of(self, plot_file: str) -> None:
        os.remove(plot_file)
