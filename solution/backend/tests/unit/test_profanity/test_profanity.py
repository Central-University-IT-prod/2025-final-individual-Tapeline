import pytest

from prodadvert.domain.moderation import TextModerator, enrich_blacklist, _REPLACEMENTS


@pytest.mark.parametrize(
    ("text", "blacklist"),
    [
        ("плохое слово", ["плохое"]),
        ("плoхoе слово", ["плохое"]),  # eng o
        ("пл𝐨х𝐨е слово", ["плохое"]),
        ("пл0х0е слово", ["плохое"]),
        ("п-л-о-х-о-е слово", ["плохое"]),
        ("BAD WORD", ["BAD"]),
        ("B𝓐D WORD", ["BAD"]),
        ("BАD WORD", ["BAD"]),  # rus A
        ("B4D WORD", ["BAD"]),
    ]
)
def test_has_profanity(text, blacklist):
    blacklist = enrich_blacklist(blacklist)
    moderator = TextModerator(blacklist)
    result = moderator.moderate(text)
    assert not result.is_ok


@pytest.mark.parametrize(
    ("text", "blacklist"),
    [
        ("неплохо", ["плохо"]),
        ("badlands", ["bad"]),
    ]
)
def test_no_false_positives(text, blacklist):
    blacklist = enrich_blacklist(blacklist)
    moderator = TextModerator(blacklist)
    result = moderator.moderate(text)
    assert result.is_ok
