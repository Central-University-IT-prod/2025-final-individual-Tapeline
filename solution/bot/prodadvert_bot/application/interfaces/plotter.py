from abc import ABC, abstractmethod


class Plotter(ABC):
    @abstractmethod
    def plot_views_and_clicks(
            self,
            days: list[int],
            views: list[int],
            clicks: list[int],
    ) -> str:
        """Plot views and clicks. Return filename."""

    @abstractmethod
    def dispose_of(self, plot_file: str) -> None:
        """Dispose of temporary plot file."""
