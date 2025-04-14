import uuid
from pathlib import Path

from customtkinter import CTk, CTkTextbox, CTkButton, CTkLabel

from backend.algorithm_playground.entities_constructor import create_entities
from prodadvert.domain.recommendation import Recommender


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.title("Playground")
        self.geometry("800x600")
        self.code = CTkTextbox(self, font=("JetBrains Mono", 16, "normal"))
        self.ok_btn = CTkButton(self, text="Ok", command=self._on_ok)
        self.save_btn = CTkButton(self, text="Save", command=self._on_save)
        self.label = CTkLabel(self, text="")
        self.rowconfigure(index=0, weight=100)
        self.rowconfigure(index=1, weight=1)
        self.rowconfigure(index=2, weight=1)
        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=1)
        self.code.grid(row=0, column=0, sticky="nswe", columnspan=2)
        self.label.grid(row=1, column=0, sticky="nswe", columnspan=2)
        self.ok_btn.grid(row=2, column=1, sticky="nswe")
        self.save_btn.grid(row=2, column=0, sticky="nswe")

    def _on_ok(self) -> None:
        entities = self.code.get("0.0", "end").split("\n\n")
        client, campaigns, views = create_entities(entities)
        clicks = {k: 0 for k in views.keys()}
        recommender = Recommender(client, campaigns, 0, clicks, views)
        best = recommender.get_best_campaign()
        self.label.configure(text=best.ad_text, require_redraw=True)

    def _on_save(self) -> None:
        Path(f"{uuid.uuid4()}_test.txt").write_text(self.code.get("0.0", "end"))
