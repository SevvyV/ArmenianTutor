"""
Armenian Alphabet data for HyeTutor App.

Supports both Western and Eastern Armenian pronunciations.
Images use numbered naming: lesson_01_alphabet_01w.png, lesson_01_alphabet_01e.png
"""

from dataclasses import dataclass
from typing import List


@dataclass
class AlphabetLetter:
    """A single Armenian letter with pronunciation data."""
    position: int        # 1-38, order in the Armenian alphabet
    capital: str         # Uppercase letter
    lowercase: str       # Lowercase letter
    armenian_name: str   # Name of the letter in Armenian script
    phonetic: str        # Phonetic pronunciation of the letter name
    sound: str           # The sound the letter makes
    sound_example: str   # English example of the sound

    @property
    def image_key_western(self) -> str:
        return f"lesson_01_alphabet_{self.position:02d}w"

    @property
    def image_key_eastern(self) -> str:
        return f"lesson_01_alphabet_{self.position:02d}e"


# ============================================================================
# WESTERN ARMENIAN ALPHABET
# ============================================================================

WESTERN_ALPHABET: List[AlphabetLetter] = [
    AlphabetLetter(1, "Ա", "ա", "Այպ", "Ayp", "a", "as in father"),
    AlphabetLetter(2, "Բ", "բ", "Պեն", "Pen", "p", "as in pet"),
    AlphabetLetter(3, "Գ", "գ", "Գիմ", "Keem", "k", "as in kite"),
    AlphabetLetter(4, "Դ", "դ", "Դա", "Ta", "t", "as in top"),
    AlphabetLetter(5, "Ե", "ե", "Եչ", "Yech", "ye", "as in yes"),
    AlphabetLetter(6, "Զ", "զ", "Զա", "Za", "z", "as in zebra"),
    AlphabetLetter(7, "Է", "է", "Է", "Eh", "e", "as in egg"),
    AlphabetLetter(8, "Ը", "ը", "Ըթ", "Ut", "u", "as in up (schwa)"),
    AlphabetLetter(9, "Թ", "թ", "Թո", "To", "t", "as in top (hard)"),
    AlphabetLetter(10, "Ժ", "ժ", "Ժե", "Zhe", "zh", "as in pleasure"),
    AlphabetLetter(11, "Ի", "ի", "Ինի", "Ini", "i", "as in machine"),
    AlphabetLetter(12, "Լ", "լ", "Լիւն", "Lyun", "l", "as in look"),
    AlphabetLetter(13, "Խ", "խ", "Խե", "Khe", "kh", "as in Bach"),
    AlphabetLetter(14, "Ծ", "ծ", "Ծա", "Dza", "dz", "as in birds"),
    AlphabetLetter(15, "Կ", "կ", "Կեն", "Gen", "g", "as in go"),
    AlphabetLetter(16, "Հ", "հ", "Հո", "Ho", "h", "as in hat"),
    AlphabetLetter(17, "Ձ", "ձ", "Ձա", "Tsa", "ts", "as in cats"),
    AlphabetLetter(18, "Ղ", "ղ", "Ղադ", "Ghad", "gh", "guttural r (French r)"),
    AlphabetLetter(19, "Ճ", "ճ", "Ճե", "Je", "j", "as in joy"),
    AlphabetLetter(20, "Մ", "մ", "Մեն", "Men", "m", "as in man"),
    AlphabetLetter(21, "Յ", "յ", "Յի", "Hee", "h/y", "as in hi or yes"),
    AlphabetLetter(22, "Ն", "ն", "Նու", "Nu", "n", "as in no"),
    AlphabetLetter(23, "Շ", "շ", "Շա", "Sha", "sh", "as in shoe"),
    AlphabetLetter(24, "Ո", "ո", "Ո", "Vo", "vo/o", "as in vote or more"),
    AlphabetLetter(25, "Չ", "չ", "Չա", "Cha", "ch", "as in church"),
    AlphabetLetter(26, "Պ", "պ", "Պե", "Be", "b", "as in boy"),
    AlphabetLetter(27, "Ջ", "ջ", "Ջե", "Che", "ch", "as in church (hard)"),
    AlphabetLetter(28, "Ռ", "ռ", "Ռա", "Ra", "r", "rolled r"),
    AlphabetLetter(29, "Ս", "ս", "Սե", "Se", "s", "as in sit"),
    AlphabetLetter(30, "Վ", "վ", "Վեւ", "Vev", "v", "as in voice"),
    AlphabetLetter(31, "Տ", "տ", "Տիւն", "Dyun", "d", "as in dog"),
    AlphabetLetter(32, "Ր", "ր", "Րե", "Re", "r", "soft r"),
    AlphabetLetter(33, "Ց", "ց", "Ցո", "Tso", "ts", "as in cats (hard)"),
    AlphabetLetter(34, "Ւ", "ւ", "Ւիւն", "Hivyun", "v", "as in voice"),
    AlphabetLetter(35, "Փ", "փ", "Փիւր", "Pyur", "p", "as in pet"),
    AlphabetLetter(36, "Ք", "ք", "Քե", "Ke", "k", "as in kite"),
    AlphabetLetter(37, "Օ", "օ", "Օ", "O", "o", "as in more"),
    AlphabetLetter(38, "Ֆ", "ֆ", "Ֆե", "Fe", "f", "as in fox"),
]


# ============================================================================
# EASTERN ARMENIAN ALPHABET
# ============================================================================

# Eastern uses the same letters but different pronunciations for some.
# The main differences are the consonant shifts:
#   Western Բ="p" -> Eastern Բ="b"
#   Western Գ="k" -> Eastern Գ="g"
#   Western Դ="t" -> Eastern Դ="d"
#   Western Ձ="ts" -> Eastern Ձ="dz"
#   Western Ճ="j"  -> Eastern Ճ="ch"
#   Western Պ="b" -> Eastern Պ="p"
#   Western Ջ="ch" -> Eastern Ջ="j"
#   Western Տ="d" -> Eastern Տ="t"
#   Western Ծ="dz" -> Eastern Ծ="ts"
#   Western Ց="ts(hard)" -> Eastern Ց="ts"

EASTERN_ALPHABET: List[AlphabetLetter] = [
    AlphabetLetter(1, "Ա", "ա", "Այբ", "Ayb", "a", "as in father"),
    AlphabetLetter(2, "Բ", "բ", "Բեն", "Ben", "b", "as in boy"),
    AlphabetLetter(3, "Գ", "գ", "Գիմ", "Gim", "g", "as in go"),
    AlphabetLetter(4, "Դ", "դ", "Դա", "Da", "d", "as in dog"),
    AlphabetLetter(5, "Ե", "ե", "Եչ", "Yech", "ye", "as in yes"),
    AlphabetLetter(6, "Զ", "զ", "Զա", "Za", "z", "as in zebra"),
    AlphabetLetter(7, "Է", "է", "Է", "Eh", "e", "as in egg"),
    AlphabetLetter(8, "Ը", "ը", "Ըթ", "Ut", "u", "as in up (schwa)"),
    AlphabetLetter(9, "Թ", "թ", "Թո", "To", "t", "as in top"),
    AlphabetLetter(10, "Ժ", "ժ", "Ժե", "Zhe", "zh", "as in pleasure"),
    AlphabetLetter(11, "Ի", "ի", "Ինի", "Ini", "i", "as in machine"),
    AlphabetLetter(12, "Լ", "լ", "Լիւն", "Lyun", "l", "as in look"),
    AlphabetLetter(13, "Խ", "խ", "Խեհ", "Kheh", "kh", "as in Bach"),
    AlphabetLetter(14, "Ծ", "ծ", "Ծա", "Tsa", "ts", "as in cats"),
    AlphabetLetter(15, "Կ", "կ", "Կեն", "Ken", "k", "as in kite"),
    AlphabetLetter(16, "Հ", "հ", "Հո", "Ho", "h", "as in hat"),
    AlphabetLetter(17, "Ձ", "ձ", "Ձա", "Tza", "dz", "as in birds"),
    AlphabetLetter(18, "Ղ", "ղ", "Ղաթ", "Ghat", "gh", "guttural g"),
    AlphabetLetter(19, "Ճ", "ճ", "Ճեհ", "Jeh", "ch", "as in church"),
    AlphabetLetter(20, "Մ", "մ", "Մեն", "Men", "m", "as in man"),
    AlphabetLetter(21, "Յ", "յ", "Յի", "Hi", "y", "as in yes"),
    AlphabetLetter(22, "Ն", "ն", "Նու", "Nu", "n", "as in no"),
    AlphabetLetter(23, "Շ", "շ", "Շահ", "Shah", "sh", "as in shoe"),
    AlphabetLetter(24, "Ո", "ո", "Ոո", "Vo", "v", "as in vote"),
    AlphabetLetter(25, "Չ", "չ", "Չա", "Cha", "ch", "as in church"),
    AlphabetLetter(26, "Պ", "պ", "Պեհ", "Peh", "p", "as in pet"),
    AlphabetLetter(27, "Ջ", "ջ", "Ջեհ", "Jheh", "j", "as in joy"),
    AlphabetLetter(28, "Ռ", "ռ", "Ռա", "Ra", "r", "rolled r"),
    AlphabetLetter(29, "Ս", "ս", "Սեհ", "Seh", "s", "as in sit"),
    AlphabetLetter(30, "Վ", "վ", "Վեւ", "Vev", "v", "as in voice"),
    AlphabetLetter(31, "Տ", "տ", "Տիւն", "Tyoon", "t", "as in top"),
    AlphabetLetter(32, "Ր", "ր", "Րե", "Re", "r", "soft r"),
    AlphabetLetter(33, "Ց", "ց", "Ցո", "Tso", "ts", "as in cats"),
    AlphabetLetter(34, "Ւ", "ւ", "Ւիւն", "Vyun", "v/u", "as in cool"),
    AlphabetLetter(35, "Փ", "փ", "Փիւր", "Pyur", "p", "as in pet"),
    AlphabetLetter(36, "Ք", "ք", "Քեհ", "Keh", "k", "as in kite"),
    AlphabetLetter(37, "Օ", "օ", "Օհ", "Oh", "o", "as in more"),
    AlphabetLetter(38, "Ֆ", "ֆ", "Ֆեհ", "Feh", "f", "as in fox"),
]
