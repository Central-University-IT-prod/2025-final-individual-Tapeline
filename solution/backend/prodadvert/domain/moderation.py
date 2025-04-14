from types import MappingProxyType
from typing import final

from attrs import frozen
from homoglyphs import Homoglyphs


def enrich_blacklist(blacklist: list[str]) -> list[str]:
    """Add homoglyphic variations."""
    blacklist = list(map(replace_homoglyphs, blacklist))
    return blacklist + list(map(lambda s: s.lower(), blacklist))


def _get_homoglyphic_replacement_dict(alphabet: str) -> dict[str, str]:
    replacements = {}
    homoglyphs = Homoglyphs()
    for letter in alphabet:
        for homoglyph in homoglyphs.get_combinations(letter):
            replacements[homoglyph] = letter
    return replacements


_ALPHABET = "abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
_ALPHABET += _ALPHABET.upper()
_STRAIGHT_MAPPINGS = MappingProxyType({
    "а": "a",
    "с": "c",
    "е": "e",
    "к": "k",
    "о": "o",
    "р": "p",
    "у": "y",
    "А": "A",
    "В": "B",
    "С": "C",
    "Е": "E",
    "Н": "H",
    "К": "K",
    "О": "O",
    "Р": "P",
    "Т": "T",
    "Х": "X",
    "0": "O",
    "5": "S",
    "4": "A",
})
_REPLACEMENTS = MappingProxyType(
    _get_homoglyphic_replacement_dict(_ALPHABET)
)


def replace_homoglyphs(text: str) -> str:
    text = "".join(_STRAIGHT_MAPPINGS.get(sym, sym) for sym in text)
    return "".join(_REPLACEMENTS.get(sym, sym) for sym in text)


@final
@frozen
class ModerationResult:
    is_ok: bool
    banned_fragment: str = ""


class TextModerator:
    def __init__(
            self,
            blacklist: list[str],
    ) -> None:
        self.blacklist = blacklist

    def moderate(self, text: str) -> ModerationResult:
        words = map(
            _sanitize_word,
            replace_homoglyphs(text).lower().split()
        )
        orig_words = text.split()
        for i, word in enumerate(words):
            if word in self.blacklist:
                return ModerationResult(
                    is_ok=False, banned_fragment=orig_words[i]
                )
        return ModerationResult(is_ok=True)


def _sanitize_word(word: str) -> str:
    return "".join(char for char in word if char in _ALPHABET)
