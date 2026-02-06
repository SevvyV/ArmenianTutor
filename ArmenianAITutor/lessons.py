"""
Lesson registry for Armenian Tutor App - 28 Lessons (A1 → B1)

All lesson content organized sequentially for progressive learning.
To add new lessons: Insert in appropriate position and renumber all subsequent lessons.
"""

from models import Lesson, VocabItem, Sentence


# ============================================================================
# TIER 1: ABSOLUTE BEGINNERS (A1 - Weeks 1-4)
# ============================================================================

LESSONS = {
    # -------------------------------------------------------------------------
    # LESSON 1: Greetings & Introductions
    # -------------------------------------------------------------------------
    "lesson_01": Lesson(
        id="lesson_01",
        title="Lesson 1: Greetings & Introductions",
        lesson_type="vocabulary",
        prefix="",
        items=[
            VocabItem("Hello", "Բարեւ", "Parev"),
            VocabItem("How are you?", "Ինչպէ՞ս ես", "Inchbes es?"),
            VocabItem("I am well", "Լաւ եմ", "Lav em"),
            VocabItem("Thank you", "Շնորհակալ եմ", "Shnorhagal em"),
            VocabItem("Goodbye", "Ցտեսութիւն", "Tsedesutyun"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 2: Numbers 1-100 (NEW - Priority #1)
    # -------------------------------------------------------------------------
    "lesson_02": Lesson(
        id="lesson_02",
        title="Lesson 2: Numbers 1-100",
        lesson_type="vocabulary",
        prefix="numbers",
        items=[
            # 1-10
            VocabItem("1 One", "Մէկ", "Meg"),
            VocabItem("2 Two", "Երկու", "Yergoo"),
            VocabItem("3 Three", "Երեք", "Yerek"),
            VocabItem("4 Four", "Չորս", "Chors"),
            VocabItem("5 Five", "Հինգ", "Hink"),
            VocabItem("6 Six", "Վեց", "Vets"),
            VocabItem("7 Seven", "Եօթը", "Yot"),
            VocabItem("8 Eight", "Ութը", "Out"),
            VocabItem("9 Nine", "Ինը", "Ine"),
            VocabItem("Ten", "Տասը", "Dase"),
            # 11-20
            VocabItem("Eleven", "Տասնըմէկ", "Tasnemeg"),
            VocabItem("Twelve", "Տասնըերկու", "Tasneyergoo"),
            VocabItem("Thirteen", "Տասնըերեք", "Tasneyerek"),
            VocabItem("Fourteen", "Տասնըչորս", "Tasnechors"),
            VocabItem("Fifteen", "Տասնըհինգ", "Tasnehink"),
            VocabItem("Sixteen", "Տասնըվեց", "Tasnevets"),
            VocabItem("Seventeen", "Տասնըեօթը", "Tasneyot"),
            VocabItem("Eighteen", "Տասնըութը", "Tasneout"),
            VocabItem("Nineteen", "Տասնըինը", "Tasneine"),
            VocabItem("Twenty", "Քսան", "Ksan"),
            # Tens
            VocabItem("Thirty", "Երեսուն", "Yeresoun"),
            VocabItem("Forty", "Քառասուն", "Karasoun"),
            VocabItem("Fifty", "Հիսուն", "Hisoun"),
            VocabItem("Sixty", "Վաթսուն", "Vatsoun"),
            VocabItem("Seventy", "Եօթանասուն", "Yotanasoun"),
            VocabItem("Eighty", "Ութսուն", "Outsoun"),
            VocabItem("Ninety", "Իննսուն", "Innesoun"),
            VocabItem("Hundred", "Հարիւր", "Haryur"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 3: Family
    # -------------------------------------------------------------------------
    "lesson_03": Lesson(
        id="lesson_03",
        title="Lesson 3: Family",
        lesson_type="vocabulary",
        prefix="family",
        items=[
            VocabItem("Father", "Հայրիկ", "Hayrig"),
            VocabItem("Mother", "Մայրիկ", "Mayrig"),
            VocabItem("Brother", "Եղբայր", "Yeghpayr"),
            VocabItem("Sister", "Քոյր", "Kouyr"),
            VocabItem("Grandfather", "Մեծ հայր", "Medz hayr"),
            VocabItem("Grandmother", "Մեծ մայր", "Medz mayr"),
            VocabItem("Son", "Տղայ", "Degha"),
            VocabItem("Daughter", "Աղջիկ", "Aghchig"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 4: Common Objects
    # -------------------------------------------------------------------------
    "lesson_04": Lesson(
        id="lesson_04",
        title="Lesson 4: Common Objects",
        lesson_type="vocabulary",
        prefix="objects",
        items=[
            VocabItem("Book", "Գիրք", "Kirk"),
            VocabItem("Newspaper", "Թերթ", "Tert"),
            VocabItem("Pen", "Գրիչ", "Krich"),
            VocabItem("Paper", "Թուղթ", "Tought"),
            VocabItem("Phone", "Հեռաձայն", "Heratsayn"),
            VocabItem("Computer", "Համակարգիչ", "Hamakarkich"),
            VocabItem("Watch/Clock", "Ժամացոյց", "Jamatsouyt"),
            VocabItem("Glasses", "Ակնոց", "Aknots"),
            VocabItem("Bag", "Պայուսակ", "Bayousag"),
            VocabItem("Key", "Բանալի", "Panali"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 5: Essential Verbs - Present Tense (NEW - Links to Verb Tool)
    # -------------------------------------------------------------------------
    "lesson_05": Lesson(
        id="lesson_05",
        title="Lesson 5: Essential Verbs - Present Tense",
        lesson_type="sentences",
        prefix="sent",
        items=[
            # To Be
            Sentence("I am", "Ես եմ", "Yes em", "essential_be_i_present"),
            Sentence("You are", "Դուն ես", "Toun es", "essential_be_you_present"),
            # To Have
            Sentence("I have", "Ես ունիմ", "Yes ounim", "essential_have_i_present"),
            Sentence("You have", "Դուն ունիս", "Toun ounis", "essential_have_you_present"),
            # To Go
            Sentence("I go", "Ես կ'երթամ", "Yes g'ertham", "essential_go_i_present"),
            Sentence("You go", "Դուն կ'երթաս", "Toun g'erthas", "essential_go_you_present"),
            # To Want
            Sentence("I want", "Ես կ'ուզեմ", "Yes g'ouzem", "essential_want_i_present"),
            Sentence("You want", "Դուն կ'ուզես", "Toun g'ouzes", "essential_want_you_present"),
            # To Do
            Sentence("I do", "Ես կ'ընեմ", "Yes g'enem", "essential_do_i_present"),
            Sentence("You do", "Դուն կ'ընես", "Toun g'enes", "essential_do_you_present"),
        ]
    ),
    
    # =========================================================================
    # TIER 2: BUILDING FOUNDATIONS (A1 - Weeks 5-8)
    # =========================================================================
    
    # -------------------------------------------------------------------------
    # LESSON 6: Animals
    # -------------------------------------------------------------------------
    "lesson_06": Lesson(
        id="lesson_06",
        title="Lesson 6: Animals",
        lesson_type="vocabulary",
        prefix="animals",
        items=[
            VocabItem("Dog", "Շուն", "Shoon"),
            VocabItem("Cat", "Կատու", "Gadoo"),
            VocabItem("Bird", "Թռչուն", "Trchoon"),
            VocabItem("Horse", "Ձի", "Tzi"),
            VocabItem("Cow", "Կով", "Gov"),
            VocabItem("Sheep", "Ոչխար", "Vochkhar"),
            VocabItem("Chicken", "Հաւ", "Hav"),
            VocabItem("Mouse", "Մուկ", "Mook"),
            VocabItem("Bear", "Արջ", "Arch"),
            VocabItem("Lion", "Առիւծ", "Ariudz"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 7: Food & Kitchen
    # -------------------------------------------------------------------------
    "lesson_07": Lesson(
        id="lesson_07",
        title="Lesson 7: Food & Kitchen",
        lesson_type="vocabulary",
        prefix="food",
        items=[
            # Food items
            VocabItem("Bread", "Հաց", "Hats"),
            VocabItem("Water", "Ջուր", "Joor"),
            VocabItem("Cheese", "Պանիր", "Banir"),
            VocabItem("Milk", "Կաթ", "Gat"),
            VocabItem("Coffee", "Սուրճ", "Soorj"),
            VocabItem("Tea", "Թէյ", "Tey"),
            VocabItem("Egg", "Հաւկիթ", "Havgit"),
            VocabItem("Meat", "Միս", "Mis"),
            VocabItem("Chicken", "Հաւ", "Hav"),
            VocabItem("Fish", "Ձուկ", "Tzoog"),
            VocabItem("Fruit", "Պտուղ", "Bdoogh"),
            VocabItem("Vegetable", "Բանջարեղէն", "Panchareghen"),
            # Kitchen items
            VocabItem("Spoon", "Դգալ", "Tkal"),
            VocabItem("Fork", "Պատառաքաղ", "Badarakagh"),
            VocabItem("Knife", "Դանակ", "Danag"),
            VocabItem("Plate", "Պնակ", "Pnag"),
            VocabItem("Bowl", "Աման", "Aman"),
            VocabItem("Cup/Mug", "Գաւաթ", "Kavat"),
            VocabItem("Glass", "Բաժակ", "Pajag"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 8: Colors & Shapes (NEW)
    # -------------------------------------------------------------------------
    "lesson_08": Lesson(
        id="lesson_08",
        title="Lesson 8: Colors & Shapes",
        lesson_type="vocabulary",
        prefix="colors",
        items=[
            # Colors
            VocabItem("Red", "Կարմիր", "Garmir"),
            VocabItem("Blue", "Կապոյտ", "Gapoyt"),
            VocabItem("Green", "Կանաչ", "Ganach"),
            VocabItem("Yellow", "Դեղին", "Deghin"),
            VocabItem("Black", "Սեւ", "Sev"),
            VocabItem("White", "Ճերմակ", "Chermag"),
            VocabItem("Orange", "Նարնջագոյն", "Narnjaguyn"),
            VocabItem("Purple", "Մանուշակագոյն", "Manushakaguyn"),
            VocabItem("Brown", "Դարչնագոյն", "Darchnaguyn"),
            VocabItem("Gray", "Մոխրագոյն", "Mokhaguyn"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 9: Essential Verbs - Past Tense (NEW - Links to Verb Tool)
    # -------------------------------------------------------------------------
    "lesson_09": Lesson(
        id="lesson_09",
        title="Lesson 9: Essential Verbs - Past Tense",
        lesson_type="sentences",
        prefix="sent",
        items=[
            # To Be
            Sentence("I was", "Ես էի", "Yes ei", "essential_be_i_past"),
            Sentence("You were", "Դուն էիր", "Toun eir", "essential_be_you_past"),
            # To Have
            Sentence("I had", "Ես ունէի", "Yes ounei", "essential_have_i_past"),
            Sentence("You had", "Դուն ունէիր", "Toun ouneir", "essential_have_you_past"),
            # To Go
            Sentence("I went", "Ես գացի", "Yes gatsi", "essential_go_i_past"),
            Sentence("You went", "Դուն գացիր", "Toun gatsir", "essential_go_you_past"),
            # To Want
            Sentence("I wanted", "Ես ուզեցի", "Yes ouzetsi", "essential_want_i_past"),
            Sentence("You wanted", "Դուն ուզեցիր", "Toun ouzetsir", "essential_want_you_past"),
            # To Do
            Sentence("I did", "Ես ըրի", "Yes eri", "essential_do_i_past"),
            Sentence("You did", "Դուն ըրիր", "Toun erir", "essential_do_you_past"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 10: Days & Months (NEW)
    # -------------------------------------------------------------------------
    "lesson_10": Lesson(
        id="lesson_10",
        title="Lesson 10: Days & Months",
        lesson_type="vocabulary",
        prefix="time",
        items=[
            # Days of the week
            VocabItem("Monday", "Երկուշաբթի", "Yergoushabti"),
            VocabItem("Tuesday", "Երեքշաբթի", "Yerekshabti"),
            VocabItem("Wednesday", "Չորեքշաբթի", "Chorkshabti"),
            VocabItem("Thursday", "Հինգշաբթի", "Hinkshabti"),
            VocabItem("Friday", "Ուրբաթ", "Ourpat"),
            VocabItem("Saturday", "Շաբաթ", "Shapat"),
            VocabItem("Sunday", "Կիրակի", "Giragi"),
            # Months
            VocabItem("January", "Յունուար", "Hounvar"),
            VocabItem("February", "Փետրուար", "Pedrvar"),
            VocabItem("March", "Մարտ", "Mard"),
            VocabItem("April", "Ապրիլ", "Abril"),
            VocabItem("May", "Մայիս", "Mayis"),
            VocabItem("June", "Յունիս", "Hounis"),
            VocabItem("July", "Յուլիս", "Houlis"),
            VocabItem("August", "Օգոստոս", "Okostos"),
            VocabItem("September", "Սեպտեմբեր", "Sebdemper"),
            VocabItem("October", "Հոկտեմբեր", "Hoktemper"),
            VocabItem("November", "Նոյեմբեր", "Noyemper"),
            VocabItem("December", "Դեկտեմբեր", "Tegtemper"),
        ]
    ),
    
    # =========================================================================
    # TIER 3: DAILY LIFE (A1-A2 - Weeks 9-12)
    # =========================================================================
    
    # -------------------------------------------------------------------------
    # LESSON 11: Telling Time (NEW - Priority #4)
    # -------------------------------------------------------------------------
    "lesson_11": Lesson(
        id="lesson_11",
        title="Lesson 11: Telling Time",
        lesson_type="vocabulary",
        prefix="time",
        items=[
            VocabItem("Hour", "Ժամ", "Zham"),
            VocabItem("Minute", "Վայրկեան", "Vayrgyan"),
            VocabItem("Morning", "Առաւօտ", "Aravod"),
            VocabItem("Afternoon", "Կէսօրէ ետք", "Gesoree yedg"),
            VocabItem("Evening", "Երեկոյ", "Yerekhoy"),
            VocabItem("Night", "Գիշեր", "Gisher"),
            VocabItem("One o'clock", "Ժամը մէկ", "Zham mek"),
            VocabItem("Two o'clock", "Ժամը երկու", "Zham yergoo"),
            VocabItem("Half past", "Կէս", "Ges"),
            VocabItem("What time?", "Ժամը քանի՞ն", "Zham kanin?"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 12: Essential Verbs - Future Tense (NEW - Links to Verb Tool)
    # -------------------------------------------------------------------------
    "lesson_12": Lesson(
        id="lesson_12",
        title="Lesson 12: Essential Verbs - Future Tense",
        lesson_type="sentences",
        prefix="sent",
        items=[
            # To Be
            Sentence("I will be", "Ես պիտի ըլլամ", "Yes pidi ellam", "essential_be_i_future"),
            Sentence("You will be", "Դուն պիտի ըլլաս", "Toun pidi ellas", "essential_be_you_future"),
            # To Have
            Sentence("I will have", "Ես պիտի ունենամ", "Yes pidi ounenam", "essential_have_i_future"),
            Sentence("You will have", "Դուն պիտի ունենաս", "Toun pidi ounenas", "essential_have_you_future"),
            # To Go
            Sentence("I will go", "Ես պիտի երթամ", "Yes pidi yertham", "essential_go_i_future"),
            Sentence("You will go", "Դուն պիտի երթաս", "Toun pidi yerthas", "essential_go_you_future"),
            # To Want
            Sentence("I will want", "Ես պիտի ուզեմ", "Yes pidi ouzem", "essential_want_i_future"),
            Sentence("You will want", "Դուն պիտի ուզես", "Toun pidi ouzes", "essential_want_you_future"),
            # To Do
            Sentence("I will do", "Ես պիտի ընեմ", "Yes pidi enem", "essential_do_i_future"),
            Sentence("You will do", "Դուն պիտի ընես", "Toun pidi enes", "essential_do_you_future"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 13: Body Parts (NEW)
    # -------------------------------------------------------------------------
    "lesson_13": Lesson(
        id="lesson_13",
        title="Lesson 13: Body Parts",
        lesson_type="vocabulary",
        prefix="body",
        items=[
            VocabItem("Head", "Գլուխ", "Gloukh"),
            VocabItem("Hair", "Մազ", "Maz"),
            VocabItem("Face", "Երես", "Yeres"),
            VocabItem("Eye", "Ակն", "Agn"),
            VocabItem("Ear", "Ականջ", "Aganj"),
            VocabItem("Nose", "Քիթ", "Kit"),
            VocabItem("Mouth", "Բերան", "Peran"),
            VocabItem("Tooth", "Ակռայ", "Agra"),
            VocabItem("Hand", "Ձեռք", "Tzerk"),
            VocabItem("Leg", "Ոտք", "Vodg"),
            VocabItem("Foot", "Ոտք", "Vodg"),
            VocabItem("Arm", "Բազուկ", "Pazouk"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 14: Morning Routine
    # -------------------------------------------------------------------------
    "lesson_14": Lesson(
        id="lesson_14",
        title="Lesson 14: Morning Routine",
        lesson_type="sentences",
        prefix="sent",
        items=[
            # Wake Up
            Sentence("I wake up early", "Ես կանուխ կ'արթննամ", "Yes ganoukh g'artnnam", 
                    "wake_up_pres", armenian_audio="Ես կանուխ կ'արթննա", context="Present"),
            Sentence("I woke up early", "Ես կանուխ արթնցայ", "Yes ganoukh artntsa",
                    "wake_up_past", armenian_audio="Ես կանուխ արթնցա", context="Past"),
            Sentence("I will wake up early", "Ես կանուխ պիտի արթննամ", "Yes ganoukh pidi artnnam",
                    "wake_up_fut", context="Future"),
            
            # Wash Hands
            Sentence("I wash my hands", "Ես կը լուամ իմ ձեռքերս", "Yes ge lvam im tzerkers",
                    "wash_hands_pres", armenian_audio="Ես կը լվամ իմ ձեռքերս", context="Present"),
            Sentence("I washed my hands", "Ես լուացի իմ ձեռքերս", "Yes lvatsi im tzerkers",
                    "wash_hands_past", armenian_audio="Ես լվացի իմ ձեռքերս", context="Past"),
            Sentence("I will wash my hands", "Ես պիտի լուամ իմ ձեռքերս", "Yes pidi lvam im tzerkers",
                    "wash_hands_fut", armenian_audio="Ես պիտի լվամ իմ ձեռքերս", context="Future"),
            
            # More routine activities
            Sentence("I brush my teeth", "Ես կը խոզանակեմ ակռաներս", "Yes ge khozanagem agraneres",
                    "brush_teeth_pres", context="Present"),
            Sentence("I comb my hair", "Ես կը սանտրեմ մազերս", "Yes ge santrem mazers",
                    "comb_hair_pres", context="Present"),
            Sentence("I drink coffee", "Ես սուրճ կը խմեմ", "Yes sourj ge khmem",
                    "drink_coffee_pres", context="Present"),
            Sentence("I eat breakfast", "Ես նախաճաշ կ'ուտեմ", "Yes nakhajash g'oudem",
                    "eat_breakfast_pres", context="Present"),
        ]
    ),
    
    # -------------------------------------------------------------------------
    # LESSON 15: Clothing (NEW)
    # -------------------------------------------------------------------------
    "lesson_15": Lesson(
        id="lesson_15",
        title="Lesson 15: Clothing",
        lesson_type="vocabulary",
        prefix="clothing",
        items=[
            VocabItem("Shirt", "Վերնաշապիկ", "Vernashapig"),
            VocabItem("Pants", "Տաբատ", "Dapad"),
            VocabItem("Dress", "Զգեստ", "Zghesd"),
            VocabItem("Coat", "Վերարկու", "Verargoo"),
            VocabItem("Shoes", "Կօշիկ", "Goshig"),
            VocabItem("Socks", "Գուլպա", "Goulpa"),
            VocabItem("Hat", "Գլխարկ", "Glkharg"),
            VocabItem("Scarf", "Շալ", "Shal"),
            VocabItem("Gloves", "Ձեռնոց", "Tzernotz"),
            VocabItem("Tie", "Փողկապ", "Poghgap"),
        ]
    ),
    
    # =========================================================================
    # NOTE: Lessons 16-28 will be added progressively
    # These are placeholders showing the structure
    # =========================================================================
    
    # Future lessons (to be fully developed):
    # lesson_16: Prepositions
    # lesson_17: Directions & Locations
    # lesson_18: Places in Town
    # lesson_19: Transportation
    # lesson_20: At the Restaurant (sentences)
    # lesson_21: Shopping (sentences)
    # lesson_22: Weather & Seasons
    # lesson_23: Hobbies & Activities
    # lesson_24: Action Verbs (10 common)
    # lesson_25: Question Words
    # lesson_26: Furniture & Home
    # lesson_27: Negation
    # lesson_28: Work & School
}


# Helper function to get lesson by ID
def get_lesson(lesson_id: str) -> Lesson:
    """Retrieve a lesson by its ID."""
    return LESSONS.get(lesson_id)


# Helper function to list all available lessons in order
def list_lessons_ordered() -> list:
    """
    Return list of (lesson_id, lesson_title) tuples in sequential order.
    Ensures lessons are always displayed 1-28 in order.
    """
    # Sort by lesson_id (lesson_01, lesson_02, etc.)
    sorted_ids = sorted(LESSONS.keys())
    return [(lid, LESSONS[lid].title) for lid in sorted_ids]
