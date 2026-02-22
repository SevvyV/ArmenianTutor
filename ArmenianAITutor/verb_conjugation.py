"""
Verb Conjugation Data for Armenian Tutor App - ALL 50 VERBS

Complete conjugation data for 50 most common Western Armenian verbs.
Links to audio files in: audio_library/verbs/{voice}/{verb_key}_{tense}.mp3
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class VerbConjugation:
    """
    Represents complete conjugation data for one verb.
    
    Audio files: audio_library/verbs/{voice}/verb_to_{verb_key}_{tense}.mp3
    - voice: "male" or "female"
    - verb_key: "be", "have", "go", etc.
    - tense: "present", "past", "future"
    """
    verb_key: str                # "be", "have", "go" (for audio filename)
    infinitive_english: str      # "To Be"
    infinitive_armenian: str     # "Ըլլալ"
    infinitive_phonetic: str     # "Eellal"
    
    # Conjugations for display
    # Format: { "present": ["եմ", "ես", "է", "ենք", "էք", "են"], ... }
    conjugations: Dict[str, List[str]] = field(default_factory=dict)


# Pronoun labels (same for all verbs)
PRONOUNS = ["I", "You", "He/She", "We", "You (plural)", "They"]


# ============================================================================
# ALL 50 WESTERN ARMENIAN VERBS (Alphabetical)
# ============================================================================

VERBS = {
    "to_answer": VerbConjugation(
        verb_key="answer",
        infinitive_english="To Answer",
        infinitive_armenian="Պատասխանել",
        infinitive_phonetic="Badaskanel",
        conjugations={
            "present": ["կը պատասխանեմ", "կը պատասխանես", "կը պատասխանէ", "կը պատասխանենք", "կը պատասխանէք", "կը պատասխանեն"],
            "past": ["պատասխանեցի", "պատասխանեցիր", "պատասխանեց", "պատասխանեցինք", "պատասխանեցիք", "պատասխանեցին"],
            "future": ["պիտի պատասխանեմ", "պիտի պատասխանես", "պիտի պատասխանէ", "պիտի պատասխանենք", "պիտի պատասխանէք", "պիտի պատասխանեն"]
        }
    ),
    
    "to_ask": VerbConjugation(
        verb_key="ask",
        infinitive_english="To Ask",
        infinitive_armenian="Հարցնել",
        infinitive_phonetic="Hartsnel",
        conjugations={
            "present": ["կը հարցնեմ", "կը հարցնես", "կը հարցնէ", "կը հարցնենք", "կը հարցնէք", "կը հարցնեն"],
            "past": ["հարցուցի", "հարցուցիր", "հարցուց", "հարցուցինք", "հարցուցիք", "հարցուցին"],
            "future": ["պիտի հարցնեմ", "պիտի հարցնես", "պիտի հարցնէ", "պիտի հարցնենք", "պիտի հարցնէք", "պիտի հարցնեն"]
        }
    ),
    
    "to_be": VerbConjugation(
        verb_key="be",
        infinitive_english="To Be",
        infinitive_armenian="Ըլլալ",
        infinitive_phonetic="Eellal",
        conjugations={
            "present": ["եմ", "ես", "է", "ենք", "էք", "են"],
            "past": ["էի", "էիր", "էր", "էինք", "էիք", "էին"],
            "future": ["պիտի ըլլամ", "պիտի ըլլաս", "պիտի ըլլայ", "պիտի ըլլանք", "պիտի ըլլաք", "պիտի ըլլան"]
        }
    ),
    
    "to_bring": VerbConjugation(
        verb_key="bring",
        infinitive_english="To Bring",
        infinitive_armenian="Բերել",
        infinitive_phonetic="Perel",
        conjugations={
            "present": ["կը բերեմ", "կը բերես", "կը բերէ", "կը բերենք", "կը բերէք", "կը բերեն"],
            "past": ["բերի", "բերիր", "բերաւ", "բերինք", "բերիք", "բերին"],
            "future": ["պիտի բերեմ", "պիտի բերես", "պիտի բերէ", "պիտի բերենք", "պիտի բերէք", "պիտի բերեն"]
        }
    ),
    
    "to_buy": VerbConjugation(
        verb_key="buy",
        infinitive_english="To Buy",
        infinitive_armenian="Գնել",
        infinitive_phonetic="Knel",
        conjugations={
            "present": ["կը գնեմ", "կը գնես", "կը գնէ", "կը գնենք", "կը գնէք", "կը գնեն"],
            "past": ["գնեցի", "գնեցիր", "գնեց", "գնեցինք", "գնեցիք", "գնեցին"],
            "future": ["պիտի գնեմ", "պիտի գնես", "պիտի գնէ", "պիտի գնենք", "պիտի գնէք", "պիտի գնեն"]
        }
    ),
    
    "to_call": VerbConjugation(
        verb_key="call",
        infinitive_english="To Call",
        infinitive_armenian="Կանչել",
        infinitive_phonetic="Ganchel",
        conjugations={
            "present": ["կը կանչեմ", "կը կանչես", "կը կանչէ", "կը կանչենք", "կը կանչէք", "կը կանչեն"],
            "past": ["կանչեցի", "կանչեցիր", "կանչեց", "կանչեցինք", "կանչեցիք", "կանչեցին"],
            "future": ["պիտի կանչեմ", "պիտի կանչես", "պիտի կանչէ", "պիտի կանչենք", "պիտի կանչէք", "պիտի կանչեն"]
        }
    ),
    
    "to_clean": VerbConjugation(
        verb_key="clean",
        infinitive_english="To Clean",
        infinitive_armenian="Մաքրել",
        infinitive_phonetic="Makrel",
        conjugations={
            "present": ["կը մաքրեմ", "կը մաքրես", "կը մաքրէ", "կը մաքրենք", "կը մաքրէք", "կը մաքրեն"],
            "past": ["մաքրեցի", "մաքրեցիր", "մաքրեց", "մաքրեցինք", "մաքրեցիք", "մաքրեցին"],
            "future": ["պիտի մաքրեմ", "պիտի մաքրես", "պիտի մաքրէ", "պիտի մաքրենք", "պիտի մաքրէք", "պիտի մաքրեն"]
        }
    ),
    
    "to_close": VerbConjugation(
        verb_key="close",
        infinitive_english="To Close",
        infinitive_armenian="Գոցել",
        infinitive_phonetic="Kotsel",
        conjugations={
            "present": ["կը գոցեմ", "կը գոցես", "կը գոցէ", "կը գոցենք", "կը գոցէք", "կը գոցեն"],
            "past": ["գոցեցի", "գոցեցիր", "գոցեց", "գոցեցինք", "գոցեցիք", "գոցեցին"],
            "future": ["պիտի գոցեմ", "պիտի գոցես", "պիտի գոցէ", "պիտի գոցենք", "պիտի գոցէք", "պիտի գոցեն"]
        }
    ),
    
    "to_come": VerbConjugation(
        verb_key="come",
        infinitive_english="To Come",
        infinitive_armenian="Գալ",
        infinitive_phonetic="Kal",
        conjugations={
            "present": ["կու գամ", "կու գաս", "կու գայ", "կու գանք", "կու գաք", "կու գան"],
            "past": ["եկայ", "եկար", "եկաւ", "եկանք", "եկաք", "եկան"],
            "future": ["պիտի գամ", "պիտի գաս", "պիտի գայ", "պիտի գանք", "պիտի գաք", "պիտի գան"]
        }
    ),
    
    "to_cook": VerbConjugation(
        verb_key="cook",
        infinitive_english="To Cook",
        infinitive_armenian="Եփել",
        infinitive_phonetic="Yepel",
        conjugations={
            "present": ["կը եփեմ", "կը եփես", "կը եփէ", "կը եփենք", "կը եփէք", "կը եփեն"],
            "past": ["եփեցի", "եփեցիր", "եփեց", "եփեցինք", "եփեցիք", "եփեցին"],
            "future": ["պիտի եփեմ", "պիտի եփես", "պիտի եփէ", "պիտի եփենք", "պիտի եփէք", "պիտի եփեն"]
        }
    ),
    
    "to_do": VerbConjugation(
        verb_key="do",
        infinitive_english="To Do",
        infinitive_armenian="Ընել",
        infinitive_phonetic="Enel",
        conjugations={
            "present": ["կ՚ընեմ", "կ՚ընես", "կ՚ընէ", "կ՚ընենք", "կ՚ընէք", "կ՚ընեն"],
            "past": ["ըրի", "ըրիր", "ըրաւ", "ըրինք", "ըրիք", "ըրին"],
            "future": ["պիտի ընեմ", "պիտի ընես", "պիտի ընէ", "պիտի ընենք", "պիտի ընէք", "պիտի ընեն"]
        }
    ),
    
    "to_drink": VerbConjugation(
        verb_key="drink",
        infinitive_english="To Drink",
        infinitive_armenian="Խմել",
        infinitive_phonetic="Khmel",
        conjugations={
            "present": ["կը խմեմ", "կը խմես", "կը խմէ", "կը խմենք", "կը խմէք", "կը խմեն"],
            "past": ["խմեցի", "խմեցիր", "խմեց", "խմեցինք", "խմեցիք", "խմեցին"],
            "future": ["պիտի խմեմ", "պիտի խմես", "պիտի խմէ", "պիտի խմենք", "պիտի խմէք", "պիտի խմեն"]
        }
    ),
    
    "to_eat": VerbConjugation(
        verb_key="eat",
        infinitive_english="To Eat",
        infinitive_armenian="Ուտել",
        infinitive_phonetic="Oudel",
        conjugations={
            "present": ["կ՚ուտեմ", "կ՚ուտես", "կ՚ուտէ", "կ՚ուտենք", "կ՚ուտէք", "կ՚ուտեն"],
            "past": ["կերայ", "կերար", "կերաւ", "կերանք", "կերաք", "կերան"],
            "future": ["պիտի ուտեմ", "պիտի ուտես", "պիտի ուտէ", "պիտի ուտենք", "պիտի ուտէք", "պիտի ուտեն"]
        }
    ),
    
    "to_finish": VerbConjugation(
        verb_key="finish",
        infinitive_english="To Finish",
        infinitive_armenian="Վերջացնել",
        infinitive_phonetic="Verjatsnel",
        conjugations={
            "present": ["կը վերջացնեմ", "կը վերջացնես", "կը վերջացնէ", "կը վերջացնենք", "կը վերջացնէք", "կը վերջացնեն"],
            "past": ["վերջացուցի", "վերջացուցիր", "վերջացուց", "վերջացուցինք", "վերջացուցիք", "վերջացուցին"],
            "future": ["պիտի վերջացնեմ", "պիտի վերջացնես", "պիտի վերջացնէ", "պիտի վերջացնենք", "պիտի վերջացնէք", "պիտի վերջացնեն"]
        }
    ),
    
    "to_forget": VerbConjugation(
        verb_key="forget",
        infinitive_english="To Forget",
        infinitive_armenian="Մոռնալ",
        infinitive_phonetic="Mornal",
        conjugations={
            "present": ["կը մոռնամ", "կը մոռնաս", "կը մոռնայ", "կը մոռնանք", "կը մոռնաք", "կը մոռնան"],
            "past": ["մոռցայ", "մոռցար", "մոռցաւ", "մոռցանք", "մոռցաք", "մոռցան"],
            "future": ["պիտի մոռնամ", "պիտի մոռնաս", "պիտի մոռնայ", "պիտի մոռնանք", "պիտի մոռնաք", "պիտի մոռնան"]
        }
    ),
    
    "to_give": VerbConjugation(
        verb_key="give",
        infinitive_english="To Give",
        infinitive_armenian="Տալ",
        infinitive_phonetic="Dal",
        conjugations={
            "present": ["կը տամ", "կը տաս", "կը տայ", "կը տանք", "կը տաք", "կը տան"],
            "past": ["տուի", "տուիր", "տուաւ", "տուինք", "տուիք", "տուին"],
            "future": ["պիտի տամ", "պիտի տաս", "պիտի տայ", "պիտի տանք", "պիտի տաք", "պիտի տան"]
        }
    ),
    
    "to_go": VerbConjugation(
        verb_key="go",
        infinitive_english="To Go",
        infinitive_armenian="Երթալ",
        infinitive_phonetic="Yertal",
        conjugations={
            "present": ["կ՚երթամ", "կ՚երթաս", "կ՚երթայ", "կ՚երթանք", "կ՚երթաք", "կ՚երթան"],
            "past": ["գացի", "գացիր", "գաց", "գացինք", "գացիք", "գացին"],
            "future": ["պիտի երթամ", "պիտի երթաս", "պիտի երթայ", "պիտի երթանք", "պիտի երթաք", "պիտի երթան"]
        }
    ),
    
    "to_have": VerbConjugation(
        verb_key="have",
        infinitive_english="To Have",
        infinitive_armenian="Ունենալ",
        infinitive_phonetic="Ounenal",
        conjugations={
            "present": ["ունիմ", "ունիս", "ունի", "ունինք", "ունիք", "ունին"],
            "past": ["ունէի", "ունէիր", "ունէր", "ունէինք", "ունէիք", "ունէին"],
            "future": ["պիտի ունենամ", "պիտի ունենաս", "պիտի ունենայ", "պիտի ունենանք", "պիտի ունենաք", "պիտի ունենան"]
        }
    ),
    
    "to_hear": VerbConjugation(
        verb_key="hear",
        infinitive_english="To Hear",
        infinitive_armenian="Լսել",
        infinitive_phonetic="Lsel",
        conjugations={
            "present": ["կը լսեմ", "կը լսես", "կը լսէ", "կը լսենք", "կը լսէք", "կը լսեն"],
            "past": ["լսեցի", "լսեցիր", "լսեց", "լսեցինք", "լսեցիք", "լսեցին"],
            "future": ["պիտի լսեմ", "պիտի լսես", "պիտի լսէ", "պիտի լսենք", "պիտի լսէք", "պիտի լսեն"]
        }
    ),
    
    "to_help": VerbConjugation(
        verb_key="help",
        infinitive_english="To Help",
        infinitive_armenian="Օգնել",
        infinitive_phonetic="Oknel",
        conjugations={
            "present": ["կ՚օգնեմ", "կ՚օգնես", "կ՚օգնէ", "կ՚օգնենք", "կ՚օգնէք", "կ՚օգնեն"],
            "past": ["օգնեցի", "օգնեցիր", "օգնեց", "օգնեցինք", "օգնեցիք", "օգնեցին"],
            "future": ["պիտի օգնեմ", "պիտի օգնես", "պիտի օգնէ", "պիտի օգնենք", "պիտի օգնէք", "պիտի օգնեն"]
        }
    ),
    
    "to_know": VerbConjugation(
        verb_key="know",
        infinitive_english="To Know",
        infinitive_armenian="Գիտնալ",
        infinitive_phonetic="Kidenal",
        conjugations={
            "present": ["գիտեմ", "գիտես", "գիտէ", "գիտենք", "գիտէք", "գիտեն"],
            "past": ["գիտէի", "գիտէիր", "գիտէր", "գիտէինք", "գիտէիք", "գիտէին"],
            "future": ["պիտի գիտնամ", "պիտի գիտնաս", "պիտի գիտնայ", "պիտի գիտնանք", "պիտի գիտնաք", "պիտի գիտնան"]
        }
    ),
    
    "to_learn": VerbConjugation(
        verb_key="learn",
        infinitive_english="To Learn",
        infinitive_armenian="Սորվիլ",
        infinitive_phonetic="Sorvil",
        conjugations={
            "present": ["կը սորվիմ", "կը սորվիս", "կը սորվի", "կը սորվինք", "կը սորվիք", "կը սորվին"],
            "past": ["սորվեցայ", "սորվեցար", "սորվեցաւ", "սորվեցանք", "սորվեցաք", "սորվեցան"],
            "future": ["պիտի սորվիմ", "պիտի սորվիս", "պիտի սորվի", "պիտի սորվինք", "պիտի սորվիք", "պիտի սորվին"]
        }
    ),
    
    "to_live": VerbConjugation(
        verb_key="live",
        infinitive_english="To Live",
        infinitive_armenian="Ապրիլ",
        infinitive_phonetic="Abril",
        conjugations={
            "present": ["կ՚ապրիմ", "կ՚ապրիս", "կ՚ապրի", "կ՚ապրինք", "կ՚ապրիք", "կ՚ապրին"],
            "past": ["ապրեցայ", "ապրեցար", "ապրեցաւ", "ապրեցանք", "ապրեցաք", "ապրեցան"],
            "future": ["պիտի ապրիմ", "պիտի ապրիս", "պիտի ապրի", "պիտի ապրինք", "պիտի ապրիք", "պիտի ապրին"]
        }
    ),
    
    "to_look": VerbConjugation(
        verb_key="look",
        infinitive_english="To Look",
        infinitive_armenian="Նայիլ",
        infinitive_phonetic="Nayil",
        conjugations={
            "present": ["կը նայիմ", "կը նայիս", "կը նայի", "կը նայինք", "կը նայիք", "կը նային"],
            "past": ["նայեցայ", "նայեցար", "նայեցաւ", "նայեցանք", "նայեցաք", "նայեցան"],
            "future": ["պիտի նայիմ", "պիտի նայիս", "պիտի նայի", "պիտի նայինք", "պիտի նայիք", "պիտի նային"]
        }
    ),
    
    "to_love": VerbConjugation(
        verb_key="love",
        infinitive_english="To Love",
        infinitive_armenian="Սիրել",
        infinitive_phonetic="Sirel",
        conjugations={
            "present": ["կը սիրեմ", "կը սիրես", "կը սիրէ", "կը սիրենք", "կը սիրէք", "կը սիրեն"],
            "past": ["սիրեցի", "սիրեցիր", "սիրեց", "սիրեցինք", "սիրեցիք", "սիրեցին"],
            "future": ["պիտի սիրեմ", "պիտի սիրես", "պիտի սիրէ", "պիտի սիրենք", "պիտի սիրէք", "պիտի սիրեն"]
        }
    ),
    
    "to_open": VerbConjugation(
        verb_key="open",
        infinitive_english="To Open",
        infinitive_armenian="Բանալ",
        infinitive_phonetic="Panal",
        conjugations={
            "present": ["կը բանամ", "կը բանաս", "կը բանայ", "կը բանանք", "կը բանաք", "կը բանան"],
            "past": ["բացի", "բացիր", "բացաւ", "բացինք", "բացիք", "բացին"],
            "future": ["պիտի բանամ", "պիտի բանաս", "պիտի բանայ", "պիտի բանանք", "պիտի բանաք", "պիտի բանան"]
        }
    ),
    
    "to_play": VerbConjugation(
        verb_key="play",
        infinitive_english="To Play",
        infinitive_armenian="Խաղալ",
        infinitive_phonetic="Khaghal",
        conjugations={
            "present": ["կը խաղամ", "կը խաղաս", "կը խաղայ", "կը խաղանք", "կը խաղաք", "կը խաղան"],
            "past": ["խաղացի", "խաղացիր", "խաղաց", "խաղացինք", "խաղացիք", "խաղացին"],
            "future": ["պիտի խաղամ", "պիտի խաղաս", "պիտի խաղայ", "պիտի խաղանք", "պիտի խաղաք", "պիտի խաղան"]
        }
    ),
    
    "to_put": VerbConjugation(
        verb_key="put",
        infinitive_english="To Put",
        infinitive_armenian="Դնել",
        infinitive_phonetic="Tnel",
        conjugations={
            "present": ["կը դնեմ", "կը դնես", "կը դնէ", "կը դնենք", "կը դնէք", "կը դնեն"],
            "past": ["դրի", "դրիր", "դրաւ", "դրինք", "դրիք", "դրին"],
            "future": ["պիտի դնեմ", "պիտի դնես", "պիտի դնէ", "պիտի դնենք", "պիտի դնէք", "պիտի դնեն"]
        }
    ),
    
    "to_read": VerbConjugation(
        verb_key="read",
        infinitive_english="To Read",
        infinitive_armenian="Կարդալ",
        infinitive_phonetic="Gartal",
        conjugations={
            "present": ["կը կարդամ", "կը կարդաս", "կը կարդայ", "կը կարդանք", "կը կարդաք", "կը կարդան"],
            "past": ["կարդացի", "կարդացիր", "կարդաց", "կարդացինք", "կարդացիք", "կարդացին"],
            "future": ["պիտի կարդամ", "պիտի կարդաս", "պիտի կարդայ", "պիտի կարդանք", "պիտի կարդաք", "պիտի կարդան"]
        }
    ),
    
    "to_remember": VerbConjugation(
        verb_key="remember",
        infinitive_english="To Remember",
        infinitive_armenian="Յիշել",
        infinitive_phonetic="Yishel",
        conjugations={
            "present": ["կը յիշեմ", "կը յիշես", "կը յիշէ", "կը յիշենք", "կը յիշէք", "կը յիշեն"],
            "past": ["յիշեցի", "յիշեցիր", "յիշեց", "յիշեցինք", "յիշեցիք", "յիշեցին"],
            "future": ["պիտի յիշեմ", "պիտի յիշես", "պիտի յիշէ", "պիտի յիշենք", "պիտի յիշէք", "պիտի յիշեն"]
        }
    ),
    
    "to_run": VerbConjugation(
        verb_key="run",
        infinitive_english="To Run",
        infinitive_armenian="Վազել",
        infinitive_phonetic="Vazel",
        conjugations={
            "present": ["կը վազեմ", "կը վազես", "կը վազէ", "կը վազենք", "կը վազէք", "կը վազեն"],
            "past": ["վազեցի", "վազեցիր", "վազեց", "վազեցինք", "վազեցիք", "վազեցին"],
            "future": ["պիտի վազեմ", "պիտի վազես", "պիտի վազէ", "պիտի վազենք", "պիտի վազէք", "պիտի վազեն"]
        }
    ),
    
    "to_say": VerbConjugation(
        verb_key="say",
        infinitive_english="To Say",
        infinitive_armenian="Ըսել",
        infinitive_phonetic="Esel",
        conjugations={
            "present": ["կ՚ըսեմ", "կ՚ըսես", "կ՚ըսէ", "կ՚ըսենք", "կ՚ըսէք", "կ՚ըսեն"],
            "past": ["ըսի", "ըսիր", "ըսաւ", "ըսինք", "ըսիք", "ըսին"],
            "future": ["պիտի ըսեմ", "պիտի ըսես", "պիտի ըսէ", "պիտի ըսենք", "պիտի ըսէք", "պիտի ըսեն"]
        }
    ),
    
    "to_see": VerbConjugation(
        verb_key="see",
        infinitive_english="To See",
        infinitive_armenian="Տեսնել",
        infinitive_phonetic="Desnel",
        conjugations={
            "present": ["կը տեսնեմ", "կը տեսնես", "կը տեսնէ", "կը տեսնենք", "կը տեսնէք", "կը տեսնեն"],
            "past": ["տեսայ", "տեսար", "տեսաւ", "տեսանք", "տեսաք", "տեսան"],
            "future": ["պիտի տեսնեմ", "պիտի տեսնես", "պիտի տեսնէ", "պիտի տեսնենք", "պիտի տեսնէք", "պիտի տեսնեն"]
        }
    ),
    
    "to_sell": VerbConjugation(
        verb_key="sell",
        infinitive_english="To Sell",
        infinitive_armenian="Ծախել",
        infinitive_phonetic="Dzakhel",
        conjugations={
            "present": ["կը ծախեմ", "կը ծախես", "կը ծախէ", "կը ծախենք", "կը ծախէք", "կը ծախեն"],
            "past": ["ծախեցի", "ծախեցիր", "ծախեց", "ծախեցինք", "ծախեցիք", "ծախեցին"],
            "future": ["պիտի ծախեմ", "պիտի ծախես", "պիտի ծախէ", "պիտի ծախենք", "պիտի ծախէք", "պիտի ծախեն"]
        }
    ),
    
    "to_sit": VerbConjugation(
        verb_key="sit",
        infinitive_english="To Sit",
        infinitive_armenian="Նստիլ",
        infinitive_phonetic="Nesdil",
        conjugations={
            "present": ["կը նստիմ", "կը նստիս", "կը նստի", "կը նստինք", "կը նստիք", "կը նստին"],
            "past": ["նստայ", "նստար", "նստաւ", "նստանք", "նստաք", "նստան"],
            "future": ["պիտի նստիմ", "պիտի նստիս", "պիտի նստի", "պիտի նստինք", "պիտի նստիք", "պիտի նստին"]
        }
    ),
    
    "to_sleep": VerbConjugation(
        verb_key="sleep",
        infinitive_english="To Sleep",
        infinitive_armenian="Քնանալ",
        infinitive_phonetic="Knanol",
        conjugations={
            "present": ["կը քնանամ", "կը քնանաս", "կը քնանայ", "կը քնանանք", "կը քնանաք", "կը քնանան"],
            "past": ["քնացայ", "քնացար", "քնացաւ", "քնացանք", "քնացաք", "քնացան"],
            "future": ["պիտի քնանամ", "պիտի քնանաս", "պիտի քնանայ", "պիտի քնանանք", "պիտի քնանաք", "պիտի քնանան"]
        }
    ),
    
    "to_speak": VerbConjugation(
        verb_key="speak",
        infinitive_english="To Speak",
        infinitive_armenian="Խօսիլ",
        infinitive_phonetic="Khosil",
        conjugations={
            "present": ["կը խօսիմ", "կը խօսիս", "կը խօսի", "կը խօսինք", "կը խօսիք", "կը խօսին"],
            "past": ["խօսեցայ", "խօսեցար", "խօսեցաւ", "խօսեցանք", "խօսեցաք", "խօսեցան"],
            "future": ["պիտի խօսիմ", "պիտի խօսիս", "պիտի խօսի", "պիտի խօսինք", "պիտի խօսիք", "պիտի խօսին"]
        }
    ),
    
    "to_stand": VerbConjugation(
        verb_key="stand",
        infinitive_english="To Stand",
        infinitive_armenian="Կայնիլ",
        infinitive_phonetic="Gaynil",
        conjugations={
            "present": ["կը կայնիմ", "կը կայնիս", "կը կայնի", "կը կայինք", "կը կայինք", "կը կային"],
            "past": ["կայնեցայ", "կայնեցար", "կայնեցաւ", "կայնեցանք", "կայնեցաք", "կայնեցան"],
            "future": ["պիտի կայնիմ", "պիտի կայնիս", "պիտի կայնի", "պիտի կայնինք", "պիտի կայնիք", "պիտի կայնին"]
        }
    ),
    
    "to_start": VerbConjugation(
        verb_key="start",
        infinitive_english="To Start",
        infinitive_armenian="Սկսիլ",
        infinitive_phonetic="Sgsil",
        conjugations={
            "present": ["կը սկսիմ", "կը սկսիս", "կը սկսի", "կը սկսինք", "կը սկսիք", "կը սկսին"],
            "past": ["սկսայ", "սկսար", "սկսաւ", "սկսանք", "սկսաք", "սկսան"],
            "future": ["պիտի սկսիմ", "պիտի սկսիս", "պիտի սկսի", "պիտի սկսինք", "պիտի սկսիք", "պիտի սկսին"]
        }
    ),
    
    "to_take": VerbConjugation(
        verb_key="take",
        infinitive_english="To Take",
        infinitive_armenian="Առնել",
        infinitive_phonetic="Arnel",
        conjugations={
            "present": ["կ՚առնեմ", "կ՚առնես", "կ՚առնէ", "կ՚առնենք", "կ՚առնէք", "կ՚առնեն"],
            "past": ["առի", "առիր", "առաւ", "առինք", "առիք", "առին"],
            "future": ["պիտի առնեմ", "պիտի առնես", "պիտի առնէ", "պիտի առնենք", "պիտի առնէք", "պիտի առնեն"]
        }
    ),
    
    "to_think": VerbConjugation(
        verb_key="think",
        infinitive_english="To Think",
        infinitive_armenian="Մտածել",
        infinitive_phonetic="Mdadzel",
        conjugations={
            "present": ["կը մտածեմ", "կը մտածես", "կը մտածէ", "կը մտածենք", "կը մտածէք", "կը մտածեն"],
            "past": ["մտածեցի", "մտածեցիր", "մտածեց", "մտածեցինք", "մտածեցիք", "մտածեցին"],
            "future": ["պիտի մտածեմ", "պիտի մտածես", "պիտի մտածէ", "պիտի մտածենք", "պիտի մտածէք", "պիտի մտածեն"]
        }
    ),
    
    "to_try": VerbConjugation(
        verb_key="try",
        infinitive_english="To Try",
        infinitive_armenian="Փորձել",
        infinitive_phonetic="Pordzel",
        conjugations={
            "present": ["կը փորձեմ", "կը փորձես", "կը փորձէ", "կը փորձենք", "կը փորձէք", "կը փորձեն"],
            "past": ["փորձեցի", "փորձեցիր", "փորձեց", "փորձեցինք", "փորձեցիք", "փորձեցին"],
            "future": ["պիտի փորձեմ", "պիտի փորձես", "պիտի փորձէ", "պիտի փորձենք", "պիտի փորձէք", "պիտի փորձեն"]
        }
    ),
    
    "to_understand": VerbConjugation(
        verb_key="understand",
        infinitive_english="To Understand",
        infinitive_armenian="Հասկնալ",
        infinitive_phonetic="Hasgnal",
        conjugations={
            "present": ["կը հասկնամ", "կը հասկնաս", "կը հասկնայ", "կը հասկնանք", "կը հասկնաք", "կը հասկնան"],
            "past": ["հասկցայ", "հասկցար", "հասկցաւ", "հասկցանք", "հասկցաք", "հասկցան"],
            "future": ["պիտի հասկնամ", "պիտի հասկնաս", "պիտի հասկնայ", "պիտի հասկնանք", "պիտի հասկնաք", "պիտի հասկնան"]
        }
    ),
    
    "to_wait": VerbConjugation(
        verb_key="wait",
        infinitive_english="To Wait",
        infinitive_armenian="Սպասել",
        infinitive_phonetic="Sbasel",
        conjugations={
            "present": ["կը սպասեմ", "կը սպասես", "կը սպասէ", "կը սպասենք", "կը սպասէք", "կը սպասեն"],
            "past": ["սպասեցի", "սպասեցիր", "սպասեց", "սպասեցինք", "սպասեցիք", "սպասեցին"],
            "future": ["պիտի սպասեմ", "պիտի սպասես", "պիտի սպասէ", "պիտի սպասենք", "պիտի սպասէք", "պիտի սպասեն"]
        }
    ),
    
    "to_wake_up": VerbConjugation(
        verb_key="wake_up",
        infinitive_english="To Wake Up",
        infinitive_armenian="Արթննալ",
        infinitive_phonetic="Artnnal",
        conjugations={
            "present": ["կ՚արթննամ", "կ՚արթննաս", "կ՚արթննայ", "կ՚արթննանք", "կ՚արթննաք", "կ՚արթննան"],
            "past": ["արթնցայ", "արթնցար", "արթնցաւ", "արթնցանք", "արթնցաք", "արթնցան"],
            "future": ["պիտի արթննամ", "պիտի արթննաս", "պիտի արթննայ", "պիտի արթննանք", "պիտի արթննաք", "պիտի արթննան"]
        }
    ),
    
    "to_walk": VerbConjugation(
        verb_key="walk",
        infinitive_english="To Walk",
        infinitive_armenian="Քալել",
        infinitive_phonetic="Kalel",
        conjugations={
            "present": ["կը քալեմ", "կը քալես", "կը քալէ", "կը քալենք", "կը քալէք", "կը քալեն"],
            "past": ["քալեցի", "քալեցիր", "քալեց", "քալեցինք", "քալեցիք", "քալեցին"],
            "future": ["պիտի քալեմ", "պիտի քալես", "պիտի քալէ", "պիտի քալենք", "պիտի քալէք", "պիտի քալեն"]
        }
    ),
    
    "to_want": VerbConjugation(
        verb_key="want",
        infinitive_english="To Want",
        infinitive_armenian="Ուզել",
        infinitive_phonetic="Ouzel",
        conjugations={
            "present": ["կ՚ուզեմ", "կ՚ուզես", "կ՚ուզէ", "կ՚ուզենք", "կ՚ուզէք", "կ՚ուզեն"],
            "past": ["ուզեցի", "ուզեցիր", "ուզեց", "ուզեցինք", "ուզեցիք", "ուզեցին"],
            "future": ["պիտի ուզեմ", "պիտի ուզես", "պիտի ուզէ", "պիտի ուզենք", "պիտի ուզէք", "պիտի ուզեն"]
        }
    ),
    
    "to_wash": VerbConjugation(
        verb_key="wash",
        infinitive_english="To Wash",
        infinitive_armenian="Լուալ",
        infinitive_phonetic="Lval",
        conjugations={
            "present": ["կը լուամ", "կը լուաս", "կը լուայ", "կը լուանք", "կը լուաք", "կը լուան"],
            "past": ["լուացի", "լուացիր", "լուաց", "լուացինք", "լուացիք", "լուացին"],
            "future": ["պիտի լուամ", "պիտի լուաս", "պիտի լուայ", "պիտի լուանք", "պիտի լուաք", "պիտի լուան"]
        }
    ),
    
    "to_work": VerbConjugation(
        verb_key="work",
        infinitive_english="To Work",
        infinitive_armenian="Աշխատիլ",
        infinitive_phonetic="Ashkhadil",
        conjugations={
            "present": ["կ՚աշխատիմ", "կ՚աշխատիս", "կ՚աշխատի", "կ՚աշխատինք", "կ՚աշխատիք", "կ՚աշխատին"],
            "past": ["աշխատեցայ", "աշխատեցար", "աշխատեցաւ", "աշխատեցանք", "աշխատեցաք", "աշխատեցան"],
            "future": ["պիտի աշխատիմ", "պիտի աշխատիս", "պիտի աշխատի", "պիտի աշխատինք", "պիտի աշխատիք", "պիտի աշխատին"]
        }
    ),
    
    "to_write": VerbConjugation(
        verb_key="write",
        infinitive_english="To Write",
        infinitive_armenian="Գրել",
        infinitive_phonetic="Krel",
        conjugations={
            "present": ["կը գրեմ", "կը գրես", "կը գրէ", "կը գրենք", "կը գրէք", "կը գրեն"],
            "past": ["գրեցի", "գրեցիր", "գրեց", "գրեցինք", "գրեցիք", "գրեցին"],
            "future": ["պիտի գրեմ", "պիտի գրես", "պիտի գրէ", "պիտի գրենք", "պիտի գրէք", "պիտի գրեն"]
        }
    ),
}


# Helper function to get verb by key
def get_verb(verb_key: str) -> VerbConjugation:
    """Retrieve a verb by its key (e.g., 'to_be')."""
    return VERBS.get(verb_key)


# Helper function to list all verbs alphabetically
def list_verbs_alphabetically() -> list:
    """
    Return list of (verb_key, infinitive_english) tuples alphabetically.
    For dropdown menu display.
    """
    return sorted(
        [(key, verb.infinitive_english) for key, verb in VERBS.items()],
        key=lambda x: x[1]  # Sort by English infinitive
    )


# Helper function to count total conjugations
def get_statistics() -> dict:
    """Return statistics about verb conjugations."""
    return {
        "total_verbs": len(VERBS),
        "total_conjugations": len(VERBS) * 3 * 6,  # 50 verbs × 3 tenses × 6 persons
        "total_audio_files": len(VERBS) * 3 * 2,   # 50 × 3 tenses × 2 voices = 300
    }
