"""
Armenian Prayers for HyeTutor App.

Prayer texts with line-by-line breakdowns for learning.
Each prayer has: full text, line-by-line with phonetic and English translation.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PrayerLine:
    """A single line of a prayer."""
    line_number: int
    armenian: str
    phonetic: str
    english: str
    audio_key: str  # e.g., "lords_prayer_line_01"
    armenian_audio: str = ""  # TTS pronunciation hack if needed
    
    def __post_init__(self):
        if not self.armenian_audio:
            self.armenian_audio = self.armenian


@dataclass
class Prayer:
    """A complete prayer with metadata and line-by-line breakdown."""
    id: str
    title: str
    armenian_title: str
    description: str
    lines: List[PrayerLine]
    full_audio_key: str = ""  # For complete recitation audio
    
    @property
    def full_armenian(self) -> str:
        """Return the complete prayer text."""
        return "\n".join(line.armenian for line in self.lines)


# ============================================================================
# THE LORD'S PRAYER (Hayr Mer)
# ============================================================================

LORDS_PRAYER = Prayer(
    id="lords_prayer",
    title="The Lord's Prayer",
    armenian_title="\u0540\u0561\u0575\u0580 \u0544\u0565\u0580",  # Հայր Մեր
    description="The most widely known Christian prayer, recited in Armenian churches worldwide. "
                "Known as 'Hayr Mer' (\u0540\u0561\u0575\u0580 \u0544\u0565\u0580), it holds a central place in Armenian spiritual life.",
    full_audio_key="lords_prayer_full",
    lines=[
        PrayerLine(
            line_number=1,
            armenian="\u0540\u0561\u0575\u0580 \u0574\u0565\u0580 \u0578\u0580 \u0575\u0565\u0580\u056f\u056b\u0576\u057d \u0565\u057d,",
            phonetic="Hayr mer vor hergins yes",
            english="Our Father who art in heaven,",
            audio_key="lords_prayer_line_01"
        ),
        PrayerLine(
            line_number=2,
            armenian="\u054d\u0578\u0582\u0580\u0562 \u0565\u0572\u056b\u0581\u056b \u0561\u0576\u0578\u0582\u0576 \u0554\u0578.",
            phonetic="Soorp yeghitsi anoon Ko",
            english="Hallowed be Thy name.",
            audio_key="lords_prayer_line_02"
        ),
        PrayerLine(
            line_number=3,
            armenian="\u0535\u056f\u0565\u057d\u0581\u0567 \u0561\u0580\u0584\u0561\u0575\u0578\u0582\u0569\u056b\u0582\u0576 \u0554\u0578.",
            phonetic="Yegestse arkayutiun Ko",
            english="Thy kingdom come.",
            audio_key="lords_prayer_line_03"
        ),
        PrayerLine(
            line_number=4,
            armenian="\u0535\u0572\u056b\u0581\u056b\u0576 \u056f\u0561\u0574\u0584 \u0554\u0578",
            phonetic="Yeghitsin gamk Ko",
            english="Thy will be done",
            audio_key="lords_prayer_line_04"
        ),
        PrayerLine(
            line_number=5,
            armenian="\u0555\u0580\u057a\u0567\u057d \u0575\u0565\u0580\u056f\u056b\u0576\u057d \u0565\u0582 \u0575\u0565\u0580\u056f\u0580\u056b.",
            phonetic="Vorbes hergins yev hergri",
            english="On earth as it is in heaven.",
            audio_key="lords_prayer_line_05"
        ),
        PrayerLine(
            line_number=6,
            armenian="\u0536\u0570\u0561\u0581 \u0574\u0565\u0580 \u0570\u0561\u0576\u0561\u057a\u0561\u0566\u0578\u0580\u0564 \u057f\u0578\u0582\u0580 \u0574\u0565\u0566 \u0561\u0575\u057d\u0585\u0580.",
            phonetic="Zhats mer hanapazort door mez aysor",
            english="Give us this day our daily bread.",
            audio_key="lords_prayer_line_06"
        ),
        PrayerLine(
            line_number=7,
            armenian="\u0535\u0582 \u0569\u0578\u0572 \u0574\u0565\u0566 \u0566\u057a\u0561\u0580\u057f\u056b\u057d \u0574\u0565\u0580,",
            phonetic="Yev togh mez zbardis mer",
            english="And forgive us our trespasses,",
            audio_key="lords_prayer_line_07"
        ),
        PrayerLine(
            line_number=8,
            armenian="\u0555\u0580\u057a\u0567\u057d \u0565\u0582 \u0574\u0565\u0584 \u0569\u0578\u0572\u0578\u0582\u0574\u0584 \u0574\u0565\u0580\u0578\u0581 \u057a\u0561\u0580\u057f\u0561\u057a\u0561\u0576\u0561\u0581.",
            phonetic="Vorbes yev mek toghoomk merots partapanats",
            english="As we forgive those who trespass against us.",
            audio_key="lords_prayer_line_08"
        ),
        PrayerLine(
            line_number=9,
            armenian="\u0535\u0582 \u0574\u056b \u057f\u0561\u0576\u056b\u0580 \u0566\u0574\u0565\u0566 \u056b \u0583\u0578\u0580\u0571\u0578\u0582\u0569\u056b\u0582\u0576,",
            phonetic="Yev mi danir zmez i portzutiun",
            english="And lead us not into temptation,",
            audio_key="lords_prayer_line_09"
        ),
        PrayerLine(
            line_number=10,
            armenian="\u0531\u0575\u056c \u0583\u0580\u056f\u0565\u0561 \u0566\u0574\u0565\u0566 \u056b \u0579\u0561\u0580\u0567\u0589",
            phonetic="Ayl prgya zmez i chare",
            english="But deliver us from evil.",
            audio_key="lords_prayer_line_10"
        ),
        PrayerLine(
            line_number=11,
            armenian="\u0536\u056b \u0554\u0578 \u0567 \u0561\u0580\u0584\u0561\u0575\u0578\u0582\u0569\u056b\u0582\u0576 \u0565\u0582 \u0566\u0585\u0580\u0578\u0582\u0569\u056b\u0582\u0576 \u0565\u0582 \u0583\u0561\u057c\u0584 \u0575\u0561\u0582\u056b\u057f\u0565\u0561\u0576\u057d.",
            phonetic="Zi Ko e arkayutiun yev zorutiun yev park havidyans",
            english="For Thine is the kingdom and the power and the glory forever.",
            audio_key="lords_prayer_line_11"
        ),
        PrayerLine(
            line_number=12,
            armenian="\u0531\u0574\u0567\u0576\u0589",
            phonetic="Amen",
            english="Amen.",
            audio_key="lords_prayer_line_12"
        ),
    ]
)


# ============================================================================
# PRAYER REGISTRY
# ============================================================================

PRAYERS = {
    "lords_prayer": LORDS_PRAYER,
    # Future prayers:
    # "hail_mary": HAIL_MARY,
    # "nicene_creed": NICENE_CREED,
    # "meal_blessing": MEAL_BLESSING,
}


def get_prayer(prayer_id: str) -> Prayer:
    """Retrieve a prayer by its ID."""
    return PRAYERS.get(prayer_id)


def list_prayers() -> list:
    """Return list of (prayer_id, prayer_title) tuples."""
    return [(pid, p.title) for pid, p in PRAYERS.items()]
