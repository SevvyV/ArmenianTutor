"""
Lesson registry for Armenian Tutor App - 43 Lessons (A1 → B1)

All lesson content organized sequentially for progressive learning.
To add new lessons: Insert in appropriate position and renumber all subsequent lessons.

CURRICULUM STRUCTURE:
  Tier 1 (1-5):   Absolute Beginners
  Tier 2 (6-10):  Building Foundations
  Tier 3 (11-15): Daily Life
  Tier 4 (16-21): Navigating the World
  Tier 5 (22-28): Expanding Horizons
  Tier 6 (29-35): Expressing Yourself
  Tier 7 (36-43): Conversational Skills

WESTERN ARMENIAN PHONETICS:
  Բ=P, Գ=K, Դ=T, Կ=G, Պ=B, Տ=D, Ծ=DZ, Ձ=TS, Ճ=J, Չ=CH
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
            VocabItem("👋 Hello", "Բարեւ", "Parev"),
            VocabItem("❓ How are you?", "Ինչպէ՞ս ես", "Inchbes es?"),
            VocabItem("😊 I am well", "Լաւ եմ", "Lav em"),
            VocabItem("🙏 Thank you", "Շնորհակալ եմ", "Shnorhagal em"),
            VocabItem("👋 Goodbye", "Ցտեսութիւն", "Tsedesutyun"),
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
            VocabItem("1️⃣ One", "Մէկ", "Meg"),
            VocabItem("2️⃣ Two", "Երկու", "Yergoo"),
            VocabItem("3️⃣ Three", "Երեք", "Yerek"),
            VocabItem("4️⃣ Four", "Չորս", "Chors"),
            VocabItem("5️⃣ Five", "Հինգ", "Hing"),
            VocabItem("6️⃣ Six", "Վեց", "Vetz"),
            VocabItem("7️⃣ Seven", "Եօթը", "Yotuh"),
            VocabItem("8️⃣ Eight", "Ութը", "Oot"),
            VocabItem("9️⃣ Nine", "Ինը", "Eenna"),
            VocabItem("🔟 Ten", "Տասը", "Dase"),
            # 11-20
            VocabItem("Eleven", "Տասնըմէկ", "Tasnemeg"),
            VocabItem("Twelve", "Տասնըերկու", "Tasneyergoo"),
            VocabItem("Thirteen", "Տասնըերեք", "Tasneyerek"),
            VocabItem("Fourteen", "Տասնըչորս", "Tasnechors"),
            VocabItem("Fifteen", "Տասնըհինգ", "Tasnehing"),
            VocabItem("Sixteen", "Տասնըվեց", "Tasnevetz"),
            VocabItem("Seventeen", "Տասնըեօթը", "Tasneyotuh"),
            VocabItem("Eighteen", "Տասնըութը", "Tasneoot"),
            VocabItem("Nineteen", "Տասնըինը", "Tasninn"),
            VocabItem("Twenty", "Քսան", "Ksan"),
            # Tens
            VocabItem("Thirty", "Երեսուն", "Yeresoun"),
            VocabItem("Forty", "Քառասուն", "Karasoun"),
            VocabItem("Fifty", "Հիսուն", "Hisoun"),
            VocabItem("Sixty", "Վաթսուն", "Vatsoun"),
            VocabItem("Seventy", "Եօթանասուն", "Yotanasoun"),
            VocabItem("Eighty", "Ութսուն", "Ootsoun"),
            VocabItem("Ninety", "Իննսուն", "Innsoun"),
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
            VocabItem("👨 Father", "Հայրիկ", "Hayrig"),
            VocabItem("👩 Mother", "Մայրիկ", "Mayrig"),
            VocabItem("👦 Brother", "Եղբայր", "Yeghpayr"),
            VocabItem("👧 Sister", "Քոյր", "Kouyr"),
            VocabItem("👴 Grandfather", "Մեծ հայր", "Medz hayr"),
            VocabItem("👵 Grandmother", "Մեծ մայր", "Medz mayr"),
            VocabItem("👶 Son", "Տղայ", "Degha"),
            VocabItem("👱‍♀️ Daughter", "Աղջիկ", "Aghchig"),
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
            VocabItem("📖 Book", "Գիրք", "Kirk"),
            VocabItem("📰 Newspaper", "Թերթ", "Tert"),
            VocabItem("🖊️ Pen", "Գրիչ", "Krich"),
            VocabItem("📄 Paper", "Թուղթ", "Tought"),
            VocabItem("📱 Phone", "Հեռաձայն", "Heratsayn"),
            VocabItem("💻 Computer", "Համակարգիչ", "Hamakarkich"),
            VocabItem("⌚ Watch/Clock", "Ժամացոյց", "Jamatsouyt"),
            VocabItem("👓 Glasses", "Ակնոց", "Aknots"),
            VocabItem("🎒 Bag", "Պայուսակ", "Bayousag"),
            VocabItem("🔑 Key", "Բանալի", "Panali"),
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
            VocabItem("🐶 Dog", "Շուն", "Shoon"),
            VocabItem("🐱 Cat", "Կատու", "Gadoo"),
            VocabItem("🐦 Bird", "Թռչուն", "Trchoon"),
            VocabItem("🐴 Horse", "Ձի", "Tzi"),
            VocabItem("🐄 Cow", "Կով", "Gov"),
            VocabItem("🐑 Sheep", "Ոչխար", "Vochkhar"),
            VocabItem("🐔 Chicken", "Հաւ", "Hav"),
            VocabItem("🐭 Mouse", "Մուկ", "Mook"),
            VocabItem("🐻 Bear", "Արջ", "Arch"),
            VocabItem("🦁 Lion", "Առիւծ", "Ariudz"),
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
            VocabItem("🍞 Bread", "Հաց", "Hats"),
            VocabItem("💧 Water", "Ջուր", "Joor"),
            VocabItem("🧀 Cheese", "Պանիր", "Banir"),
            VocabItem("🥛 Milk", "Կաթ", "Gat"),
            VocabItem("☕ Coffee", "Սուրճ", "Soorj"),
            VocabItem("🍵 Tea", "Թէյ", "Tey"),
            VocabItem("🥚 Egg", "Հաւկիթ", "Havgit"),
            VocabItem("🥩 Meat", "Միս", "Mis"),
            VocabItem("🍗 Chicken", "Հաւ", "Hav"),
            VocabItem("🐟 Fish", "Ձուկ", "Tzoog"),
            VocabItem("🍎 Fruit", "Պտուղ", "Bdoogh"),
            VocabItem("🥕 Vegetable", "Բանջարեղէն", "Panchareghen"),
            # Kitchen items
            VocabItem("🥄 Spoon", "Դգալ", "Tkal"),
            VocabItem("🍴 Fork", "Պատառաքաղ", "Badarakagh"),
            VocabItem("🔪 Knife", "Դանակ", "Danag"),
            VocabItem("🍽️ Plate", "Պնակ", "Pnag"),
            VocabItem("🥣 Bowl", "Աման", "Aman"),
            VocabItem("☕ Cup/Mug", "Գաւաթ", "Kavat"),
            VocabItem("🥃 Glass", "Բաժակ", "Pajag"),
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
            VocabItem("🔴 Red", "Կարմիր", "Garmir"),
            VocabItem("🔵 Blue", "Կապոյտ", "Gapoyt"),
            VocabItem("🟢 Green", "Կանաչ", "Ganach"),
            VocabItem("🟡 Yellow", "Դեղին", "Deghin"),
            VocabItem("⚫ Black", "Սեւ", "Sev"),
            VocabItem("⚪ White", "Ճերմակ", "Chermag"),
            VocabItem("🟠 Orange", "Նարնջագոյն", "Narnjaguyn"),
            VocabItem("🟣 Purple", "Մանուշակագոյն", "Manushakaguyn"),
            VocabItem("🟤 Brown", "Դարչնագոյն", "Darchnaguyn"),
            VocabItem("🩶 Gray", "Մոխրագոյն", "Mokhaguyn"),
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
            VocabItem("📅 Monday", "Երկուշաբթի", "Yergoushabti"),
            VocabItem("📅 Tuesday", "Երեքշաբթի", "Yerekshabti"),
            VocabItem("📅 Wednesday", "Չորեքշաբթի", "Chorkshabti"),
            VocabItem("📅 Thursday", "Հինգշաբթի", "Hingshabti"),
            VocabItem("📅 Friday", "Ուրբաթ", "Ourpat"),
            VocabItem("📅 Saturday", "Շաբաթ", "Shapat"),
            VocabItem("📅 Sunday", "Կիրակի", "Giragi"),
            # Months
            VocabItem("❄️ January", "Յունուար", "Hounvar"),
            VocabItem("❄️ February", "Փետրուար", "Pedrvar"),
            VocabItem("🌱 March", "Մարտ", "Mard"),
            VocabItem("🌱 April", "Ապրիլ", "Abril"),
            VocabItem("🌱 May", "Մայիս", "Mayis"),
            VocabItem("☀️ June", "Յունիս", "Hounis"),
            VocabItem("☀️ July", "Յուլիս", "Houlis"),
            VocabItem("☀️ August", "Օգոստոս", "Okostos"),
            VocabItem("🍂 September", "Սեպտեմբեր", "Sebdemper"),
            VocabItem("🍂 October", "Հոկտեմբեր", "Hoktemper"),
            VocabItem("🍂 November", "Նոյեմբեր", "Noyemper"),
            VocabItem("❄️ December", "Դեկտեմբեր", "Tegtemper"),
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
            VocabItem("🕐 Hour", "Ժամ", "Zham"),
            VocabItem("⏰ Minute", "Վայրկեան", "Vayrgyan"),
            VocabItem("🌅 Morning", "Առաւօտ", "Aravod"),
            VocabItem("☀️ Afternoon", "Կէսօրէ ետք", "Gesoree yedg"),
            VocabItem("🌆 Evening", "Երեկոյ", "Yerekhoy"),
            VocabItem("🌙 Night", "Գիշեր", "Gisher"),
            VocabItem("🕐 One o'clock", "Ժամը մէկ", "Zham mek"),
            VocabItem("🕑 Two o'clock", "Ժամը երկու", "Zham yergoo"),
            VocabItem("🕧 Half past", "Կէս", "Ges"),
            VocabItem("❓ What time?", "Ժամը քանի՞ն", "Zham kanin?"),
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
            VocabItem("👁️ Eye", "Ակն", "Agn"),
            VocabItem("👂 Ear", "Ականջ", "Aganj"),
            VocabItem("👃 Nose", "Քիթ", "Kit"),
            VocabItem("👄 Mouth", "Բերան", "Peran"),
            VocabItem("🦷 Tooth", "Ակռայ", "Agra"),
            VocabItem("✋ Hand", "Ձեռք", "Tzerk"),
            VocabItem("🦵 Leg", "Ոտք", "Vodg"),
            VocabItem("🦶 Foot", "Ոտք", "Vodg"),
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
            VocabItem("👕 Shirt", "Վերնաշապիկ", "Vernashapig"),
            VocabItem("👖 Pants", "Տաբատ", "Dapad"),
            VocabItem("👗 Dress", "Զգեստ", "Zghesd"),
            VocabItem("🧥 Coat", "Վերարկու", "Verargoo"),
            VocabItem("👞 Shoes", "Կօշիկ", "Goshig"),
            VocabItem("🧦 Socks", "Գուլպա", "Goulpa"),
            VocabItem("🎩 Hat", "Գլխարկ", "Glkharg"),
            VocabItem("🧣 Scarf", "Շալ", "Shal"),
            VocabItem("🧤 Gloves", "Ձեռնոց", "Tzernotz"),
            VocabItem("👔 Tie", "Փողկապ", "Poghgap"),
        ]
    ),
    
    # =========================================================================
    # TIER 4: NAVIGATING THE WORLD (A2 - Weeks 13-16)
    # =========================================================================
    
    # -------------------------------------------------------------------------
    # LESSON 16: Prepositions
    # -------------------------------------------------------------------------
    "lesson_16": Lesson(
        id="lesson_16",
        title="Lesson 16: Prepositions",
        lesson_type="vocabulary",
        prefix="prepositions",
        items=[
            VocabItem("In / Inside", "Մէջ", "Mej"),
            VocabItem("On / On top of", "Վրայ", "Vra"),
            VocabItem("Under", "Տակ", "Dag"),
            VocabItem("Next to / Beside", "Քով", "Kov"),
            VocabItem("In front of", "Առջեւ", "Arjev"),
            VocabItem("Behind", "Ետեւ", "Yedev"),
            VocabItem("Between", "Միջեւ", "Mijev"),
            VocabItem("Near / Close to", "Մօտ", "Mod"),
            VocabItem("Far from", "Հեռու", "Heroo"),
            VocabItem("With", "Հետ", "Hed"),
            VocabItem("Without", "Առանց", "Arants"),
            VocabItem("For", "Համար", "Hamar"),
        ]
    ),
    
    "lesson_17": Lesson(
        id="lesson_17",
        title="Lesson 17: Directions & Locations",
        lesson_type="vocabulary",
        prefix="directions",
        items=[
            VocabItem("Left", "Ձախ", "Tsakh"),
            VocabItem("Right", "Աջ", "Ach"),
            VocabItem("Straight", "Շիտակ", "Shidag"),
            VocabItem("Up", "Վեր", "Ver"),
            VocabItem("Down", "Վար", "Var"),
            VocabItem("Here", "Հոս", "Hos"),
            VocabItem("There", "Հոն", "Hon"),
            VocabItem("North", "Հիւսիս", "Hiusis"),
            VocabItem("South", "Հարավ", "Harav"),
            VocabItem("East", "Արեւելք", "Arevelk"),
            VocabItem("West", "Արեւմուտք", "Arevmoudk"),
            VocabItem("Corner", "Անկիւն", "Angiun"),
        ]
    ),
    
    "lesson_18": Lesson(
        id="lesson_18",
        title="Lesson 18: Places in Town",
        lesson_type="vocabulary",
        prefix="places",
        items=[
            VocabItem("House / Home", "Տուն", "Doon"),
            VocabItem("School", "Վարժարան", "Varjaran / Tbrotz"),
            VocabItem("Church", "Եկեղեցի", "Yegeghetsee"),
            VocabItem("Hospital", "Հիւանդանոց", "Hivantanots"),
            VocabItem("Store / Shop", "Խանութ", "Khanout"),
            VocabItem("Market", "Շուկա", "Shouga"),
            VocabItem("Restaurant", "Ճաշարան", "Jasharan"),
            VocabItem("Bank", "Տրամատուն", "Dramadoun"),
            VocabItem("Post Office", "Փոստատուն", "Bosdadoun"),
            VocabItem("Park / Garden", "Պարտէզ", "Bardez"),
            VocabItem("Library", "Գրադարան", "Gradaran"),
            VocabItem("Pharmacy", "Տեղատուն", "Deghadoun"),
        ]
    ),
    
    "lesson_19": Lesson(
        id="lesson_19",
        title="Lesson 19: Transportation",
        lesson_type="vocabulary",
        prefix="transport",
        items=[
            VocabItem("🚗 Car", "Ինքնաշարժ", "Inknacharzh"),
            VocabItem("🚌 Bus", "Հանրակառք", "Hanragark"),
            VocabItem("🚂 Train", "Շոգեկառք", "Shokegark"),
            VocabItem("✈️ Airplane", "Օդանավ", "Odanav"),
            VocabItem("🚢 Ship / Boat", "Նավ", "Nav"),
            VocabItem("🚲 Bicycle", "Հեծանիվ", "Hetsaniv"),
            VocabItem("Taxi", "Տաքսի", "Daksi"),
            VocabItem("Street / Road", "Փողոց", "Boghots"),
            VocabItem("Bridge", "Կամուրջ", "Gamoorj"),
            VocabItem("Ticket", "Տոմս", "Doms"),
        ]
    ),
    
    "lesson_20": Lesson(
        id="lesson_20",
        title="Lesson 20: At the Restaurant",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("A table for two, please", "Սեղան մը երկուի համար, խնդրեմ", "Seghan me yergoui hamar, khntrem", "restaurant_table"),
            Sentence("The menu, please", "Ճաշացանկը, խնդրեմ", "Jashatsanke, khntrem", "restaurant_menu"),
            Sentence("I would like...", "Կ’ուզէի...", "G'ouzei...", "restaurant_would_like"),
            Sentence("Water, please", "Ջուր, խնդրեմ", "Joor, khntrem", "restaurant_water"),
            Sentence("The bill, please", "Հաշիւը, խնդրեմ", "Hashive, khntrem", "restaurant_bill"),
            Sentence("It was delicious", "Շատ համով էր", "Shad hamov er", "restaurant_delicious"),
            Sentence("I am hungry", "Անօթի եմ", "Anoti em", "restaurant_hungry"),
            Sentence("I am thirsty", "Ծարավ եմ", "Tsarav em", "restaurant_thirsty"),
            Sentence("Do you have...?", "Դուք ունի՞ք...", "Touk ounik...?", "restaurant_do_you_have"),
            Sentence("No meat, please", "Առանց միս, խնդրեմ", "Arants mis, khntrem", "restaurant_no_meat"),
        ]
    ),
    
    "lesson_21": Lesson(
        id="lesson_21",
        title="Lesson 21: Shopping",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("How much is this?", "Ասիկա քանի՞ է", "Asiga kani e?", "shopping_how_much"),
            Sentence("Too expensive", "Շատ սուղ", "Shad sough", "shopping_expensive"),
            Sentence("Can you lower the price?", "Կրնաս իջեցնե՞լ", "Grnas ijetsnel?", "shopping_lower_price"),
            Sentence("I want to buy", "Կ’ուզեմ գնել", "G'ouzem knel", "shopping_want_buy"),
            Sentence("Do you have a bigger size?", "Աւելի մեծ չափ ունի՞ք", "Aveli medz chap ounik?", "shopping_bigger_size"),
            Sentence("Where is the fitting room?", "Ուռ է փորձասենյակը", "Oor e portzasenyage?", "shopping_fitting_room"),
            Sentence("I am just looking", "Կը նայիմ միայն", "Ge nayim miayn", "shopping_just_looking"),
            Sentence("I will take this one", "Ասիկա պիտի առնեմ", "Asiga bidi arnem", "shopping_take_this"),
            Sentence("Do you accept credit cards?", "Քարտ կ’առնէ՞ք", "Kard g'arnek?", "shopping_credit_card"),
            Sentence("Can I have a bag?", "Պայուսակ մը կրնա՞մ ունենալ", "Bayousag me grnam ounenal?", "shopping_bag"),
        ]
    ),
    
    # =========================================================================
    # TIER 5: EXPANDING HORIZONS (A2 - Weeks 17-20)
    # =========================================================================
    
    "lesson_22": Lesson(
        id="lesson_22",
        title="Lesson 22: Weather & Seasons",
        lesson_type="vocabulary",
        prefix="weather",
        items=[
            VocabItem("🌱 Spring", "Գարուն", "Karoun"),
            VocabItem("☀️ Summer", "Ամառ", "Amar"),
            VocabItem("🍂 Autumn", "Աշուն", "Ashoun"),
            VocabItem("❄️ Winter", "Ձմեռ", "Tsmer"),
            VocabItem("☀️ Sun", "Արեւ", "Arev"),
            VocabItem("☁️ Cloud", "Ամպ", "Amp"),
            VocabItem("🌧️ Rain", "Անձրեւ", "Antsrev"),
            VocabItem("❄️ Snow", "Ձիւն", "Tsiun"),
            VocabItem("🌬️ Wind", "Հով", "Hov"),
            VocabItem("🌡️ Hot", "Տաք", "Dag"),
            VocabItem("🥶 Cold", "Պաղ", "Bagh"),
            VocabItem("Sky", "Երկինք", "Yerging"),
        ]
    ),
    
    "lesson_23": Lesson(
        id="lesson_23",
        title="Lesson 23: Hobbies & Activities",
        lesson_type="vocabulary",
        prefix="hobbies",
        items=[
            VocabItem("🎵 Music", "Երաժշտութիւն", "Yerajshdutiun"),
            VocabItem("🎨 Painting / Drawing", "Նկարչութիւն", "Ngarchoutiun"),
            VocabItem("⚽ Sports", "Մարզանք", "Marzank"),
            VocabItem("📚 Reading", "Կարդալ", "Gardal"),
            VocabItem("🍳 Cooking", "Խոհարարութիւն", "Khoharoutiun"),
            VocabItem("🎶 Singing", "Երգ", "Yerk"),
            VocabItem("💃 Dancing", "Պար", "Bar"),
            VocabItem("📷 Photography", "Լուսանկարչութիւն", "Lousangarchoutiun"),
            VocabItem("✈️ Travel", "Ճամբորդութիւն", "Jamporchoutiun"),
            VocabItem("🎬 Movies / Cinema", "Շարժապատկեր", "Sharjabadger"),
            VocabItem("🎮 Games", "Խաղ", "Khagh"),
            VocabItem("🏊 Swimming", "Լողալ", "Loghal"),
        ]
    ),
    
    "lesson_24": Lesson(
        id="lesson_24",
        title="Lesson 24: Action Verbs in Context",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("I see the mountain", "Լեռը կը տեսնեմ", "Lere ge desnem", "action_see_mountain"),
            Sentence("I hear music", "Երաժշտութիւն կը լսեմ", "Yerajshdutiun ge lsem", "action_hear_music"),
            Sentence("I write a letter", "Նամակ մը կը գրեմ", "Namag me ge krem", "action_write_letter"),
            Sentence("I read a book", "Կիրք մը կը կարդամ", "Kirk me ge gardam", "action_read_book"),
            Sentence("I open the door", "Տուռը կը բանամ", "Doore ge panam", "action_open_door"),
            Sentence("I close the window", "Պատուհանը կը գոցեմ", "Badoohane ge gotsem", "action_close_window"),
            Sentence("I run every morning", "Ամէն առաւօտ կը վազեմ", "Amen aravod ge vazem", "action_run_morning"),
            Sentence("I walk to school", "Վարժարան կը քալեմ", "Varjaran ge kalem", "action_walk_school"),
            Sentence("I sit on the chair", "Աթոռին վրայ կը նստիմ", "Atorin vra ge nsdim", "action_sit_chair"),
            Sentence("I think about you", "Քեզի մասին կը մտածեմ", "Kezi masin ge mdadzem", "action_think_you"),
        ]
    ),
    
    "lesson_25": Lesson(
        id="lesson_25",
        title="Lesson 25: Question Words",
        lesson_type="vocabulary",
        prefix="questions",
        items=[
            VocabItem("❓ What?", "Ինչ՞", "Inch?"),
            VocabItem("❓ Who?", "Ով՞", "Ov?"),
            VocabItem("❓ Where?", "Ուռ՞", "Oor?"),
            VocabItem("❓ When?", "Երբ՞", "Yerp?"),
            VocabItem("❓ Why?", "Ինչու՞", "Inchoo?"),
            VocabItem("❓ How?", "Ինչպէ՞ս", "Inchbes?"),
            VocabItem("❓ How much? / How many?", "Քանի՞", "Kani?"),
            VocabItem("❓ Which?", "Որ՞", "Vor?"),
            VocabItem("❓ Whose?", "Որուն՞", "Voroun?"),
            VocabItem("❓ Is it? / Really?", "Իսկապէ՞ս", "Iskapes?"),
        ]
    ),
    
    "lesson_26": Lesson(
        id="lesson_26",
        title="Lesson 26: Furniture & Home",
        lesson_type="vocabulary",
        prefix="furniture",
        items=[
            VocabItem("Table", "Սեղան", "Seghan"),
            VocabItem("Chair", "Աթոռ", "Ator"),
            VocabItem("Bed", "Անկողին", "Angoghin"),
            VocabItem("Sofa / Couch", "Պազմոց", "Pazmots"),
            VocabItem("Mirror", "Հայելի", "Hayeli"),
            VocabItem("Window", "Պատուհան", "Badoohan"),
            VocabItem("Door", "Տուռ", "Door"),
            VocabItem("Closet / Wardrobe", "Պահարան", "Baharan"),
            VocabItem("Carpet / Rug", "Գորգ", "Gorg"),
            VocabItem("Lamp", "Լամբար", "Lambar"),
            VocabItem("Stairs", "Սանդուխք", "Sandookht"),
            VocabItem("Wall", "Պատ", "Bad"),
        ]
    ),
    
    "lesson_27": Lesson(
        id="lesson_27",
        title="Lesson 27: Negation",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("I don't know", "Չեմ գիտեր", "Chem kider", "negation_dont_know"),
            Sentence("I don't want", "Չեմ ուզեր", "Chem ouzer", "negation_dont_want"),
            Sentence("I don't understand", "Չեմ հասկնար", "Chem hasknar", "negation_dont_understand"),
            Sentence("I can't", "Չեմ կրնար", "Chem grnar", "negation_cant"),
            Sentence("There is no...", "Չկայ...", "Chga...", "negation_there_is_no"),
            Sentence("I have never been", "Երբեք գացած չեմ", "Yerpek gatsadz chem", "negation_never_been"),
            Sentence("Not yet", "Տակաւին ոչ", "Dagavin voch", "negation_not_yet"),
            Sentence("Nobody came", "Մէկը չեկաւ", "Mege chegav", "negation_nobody"),
            Sentence("Nothing happened", "Ոչինչ չեղաւ", "Vochinch cheghav", "negation_nothing"),
            Sentence("Don't worry", "Մի’ մտահոգիր", "Mi mdahokvir", "negation_dont_worry"),
        ]
    ),
    
    "lesson_28": Lesson(
        id="lesson_28",
        title="Lesson 28: Work & School",
        lesson_type="vocabulary",
        prefix="work",
        items=[
            VocabItem("Teacher", "Վարժապետ", "Varjabed"),
            VocabItem("Student", "Աշակերտ", "Ashagerd"),
            VocabItem("Doctor", "Պժիշկ", "Pjishg"),
            VocabItem("Lawyer", "Փաստաբան", "Bastoban"),
            VocabItem("Engineer", "Ճարտարապետ", "Jardarabed"),
            VocabItem("Office", "Գրասենյակ", "Krasenyag"),
            VocabItem("Boss / Manager", "Տնօրէն", "Dnoren"),
            VocabItem("Meeting", "Զողով", "Zhoghov"),
            VocabItem("Lesson / Class", "Տաս", "Das"),
            VocabItem("Homework", "Տնային աշխատանք", "Dnayin ashkhadank"),
            VocabItem("Exam / Test", "Քննութիւն", "Knoutiun"),
            VocabItem("Salary / Pay", "Աշխատավարձ", "Ashkhadavardz"),
        ]
    ),
    
    # =========================================================================
    # TIER 6: EXPRESSING YOURSELF (A2-B1 - Weeks 21-24)
    # =========================================================================
    
    "lesson_29": Lesson(
        id="lesson_29",
        title="Lesson 29: Emotions & Feelings",
        lesson_type="vocabulary",
        prefix="emotions",
        items=[
            VocabItem("😊 Happy", "Ուրախ", "Ourakh"),
            VocabItem("😢 Sad", "Տխուր", "Dkhoor"),
            VocabItem("😠 Angry", "Պարկացած", "Pargatsadz"),
            VocabItem("😨 Afraid / Scared", "Վախցած", "Vakhtsadz"),
            VocabItem("😮‍💨 Surprised", "Զարմացած", "Zarmatsadz"),
            VocabItem("😴 Tired", "Յոգնած", "Yoknadzadz"),
            VocabItem("😍 Thrilled / Excited", "Հիացած եմ", "Hiatsadz em"),
            VocabItem("😔 Worried", "Մտահոգ", "Mdahok"),
            VocabItem("😐 Bored", "Ձանձրացած", "Tsantratsadz"),
            VocabItem("😌 Calm / Peaceful", "Հանգիստ", "Hankisd"),
            VocabItem("🤩 Proud", "Հպարտ", "Hbard"),
            VocabItem("🥲 Lonely", "Մինակ", "Minag"),
        ]
    ),
    
    "lesson_30": Lesson(
        id="lesson_30",
        title="Lesson 30: Adjectives & Descriptions",
        lesson_type="vocabulary",
        prefix="adjectives",
        items=[
            VocabItem("Big / Large", "Մեծ", "Medz"),
            VocabItem("Small / Little", "Փոքր", "Pokr"),
            VocabItem("Long", "Երկայն", "Yergayn"),
            VocabItem("Short", "Կարճ", "Garch"),
            VocabItem("New", "Նոր", "Nor"),
            VocabItem("Old", "Հին", "Hin"),
            VocabItem("Good", "Լաւ", "Lav"),
            VocabItem("Bad", "Վատ", "Vad"),
            VocabItem("Beautiful", "Գեղեցիկ", "Keghetsig"),
            VocabItem("Ugly", "Տգեղ", "Dkegh"),
            VocabItem("Fast / Quick", "Արագ", "Arak"),
            VocabItem("Slow", "Տանտ", "Dand"),
            VocabItem("Heavy", "Ծանր", "Tsanr"),
            VocabItem("Light (weight)", "Թեթեւ", "Tetev"),
            VocabItem("Clean", "Մաքուր", "Makoor"),
            VocabItem("Dirty", "Կեղտոտ", "Geghdod"),
        ]
    ),
    
    "lesson_31": Lesson(
        id="lesson_31",
        title="Lesson 31: Nature & Outdoors",
        lesson_type="vocabulary",
        prefix="nature",
        items=[
            VocabItem("⛰️ Mountain", "Լեռ", "Ler"),
            VocabItem("🌊 Sea", "Ծով", "Dzov"),
            VocabItem("🏞️ Lake", "Լիճ", "Lich"),
            VocabItem("🌊 River", "Գետ", "Ked"),
            VocabItem("🌳 Tree", "Ծառ", "Tsar"),
            VocabItem("🌺 Flower", "Ծաղիկ", "Dzaghig"),
            VocabItem("🌿 Grass", "Խոտ", "Khod"),
            VocabItem("🌍 Earth / Ground", "Հող", "Hogh"),
            VocabItem("🪨 Stone / Rock", "Քար", "Kar"),
            VocabItem("🔥 Fire", "Կրակ", "Grab"),
            VocabItem("🌌 Star", "Աստղ", "Asdgh"),
            VocabItem("🌙 Moon", "Լուսին", "Loousin"),
        ]
    ),
    
    "lesson_32": Lesson(
        id="lesson_32",
        title="Lesson 32: Health & At the Doctor",
        lesson_type="vocabulary",
        prefix="health",
        items=[
            VocabItem("Doctor", "Պժիշկ", "Pjishg"),
            VocabItem("Medicine", "Տեղ", "Degh"),
            VocabItem("Pain", "Ցաւ", "Tsav"),
            VocabItem("Headache", "Գլխացաւ", "Glkhadzav"),
            VocabItem("Fever", "Ջերմութիւն", "Jermoutiun"),
            VocabItem("Cough", "Հազ", "Haz"),
            VocabItem("Cold (illness)", "Պաղ", "Bagh"),
            VocabItem("Blood", "Արիւն", "Ariun"),
            VocabItem("Heart", "Սիրտ", "Sird"),
            VocabItem("Stomach", "Ստամոքս", "Sdamoks"),
            VocabItem("Healthy", "Առողջ", "Aroghj"),
            VocabItem("Sick / Ill", "Հիւանդ", "Hivant"),
        ]
    ),
    
    "lesson_33": Lesson(
        id="lesson_33",
        title="Lesson 33: Polite Expressions & Social Phrases",
        lesson_type="vocabulary",
        prefix="polite",
        items=[
            VocabItem("Please", "Խնդրեմ", "Khntrem"),
            VocabItem("Excuse me", "Ներողութիւն", "Neroghoutiun"),
            VocabItem("Sorry", "Ներեցէք", "Neretseek"),
            VocabItem("Congratulations", "Շնորհաւոր", "Shnorhavyor"),
            VocabItem("🎂 Happy Birthday", "Շնորհաւոր տարեդարձդ", "Shnorhavyor daretartzd"),
            VocabItem("Welcome", "Պարի եկաք", "Pari yegak"),
            VocabItem("Of course", "Անշուշտ", "Anshousht"),
            VocabItem("No problem", "Խնդիր չկայ", "Khndir chga"),
            VocabItem("You're welcome", "Խնդրեմ", "Khntrem"),
            VocabItem("Cheers!", "Կենացը", "Genatse"),
            VocabItem("Bless you", "Առողջութիւն", "Aroghchoutiun"),
            VocabItem("Good luck", "Պարի յաջողութիւն", "Pari yajoghoutun"),
        ]
    ),
    
    "lesson_34": Lesson(
        id="lesson_34",
        title="Lesson 34: Armenian Cultural Terms",
        lesson_type="vocabulary",
        prefix="culture",
        items=[
            VocabItem("Cross-stone", "Խաչքար", "Khachkar"),
            VocabItem("Flatbread", "Լաւաշ", "Lavash"),
            VocabItem("Pomegranate", "Նուռ", "Noor"),
            VocabItem("Apricot", "Ծիրան", "Dziran"),
            VocabItem("Armenian flute", "Տուտուկ", "Doudoug"),
            VocabItem("Homeland", "Հայրենիք", "Hayrenik"),
            VocabItem("Diaspora", "Սփիւռք", "Sbiurk"),
            VocabItem("Genocide", "Ցեղասպանութիւն", "Tseghasbanoutiun"),
            VocabItem("Mount Ararat", "Արարատ", "Ararad"),
            VocabItem("Lake Sevan", "Սեւան Լիճ", "Sevan Lich"),
            VocabItem("Armenian Apostolic Church", "Հայ Առաքելական Եկեղեցի", "Hay Arakelagan Yegeghetsee"),
            VocabItem("Toast (celebratory)", "Կենաց", "Genats"),
        ]
    ),
    
    "lesson_35": Lesson(
        id="lesson_35",
        title="Lesson 35: Pronouns & Possessives",
        lesson_type="vocabulary",
        prefix="pronouns",
        items=[
            VocabItem("I", "Ես", "Yes"),
            VocabItem("You (singular)", "Տուն", "Toun"),
            VocabItem("He", "Ան", "An"),
            VocabItem("She", "Ան", "An"),
            VocabItem("We", "Մենք", "Menk"),
            VocabItem("You (plural)", "Տուք", "Touk"),
            VocabItem("They", "Անոնք", "Anonk"),
            VocabItem("My", "Իմ", "Im"),
            VocabItem("Your (singular)", "Ռու", "Ku"),
            VocabItem("His / Her", "Իր", "Ir"),
            VocabItem("Our", "Մեր", "Mer"),
            VocabItem("Your (plural)", "Ձեր", "Tser"),
            VocabItem("This", "Աս", "As"),
            VocabItem("That", "Ան", "An"),
        ]
    ),
    
    # =========================================================================
    # TIER 7: CONVERSATIONAL SKILLS (B1 - Weeks 25-28)
    # =========================================================================
    
    "lesson_36": Lesson(
        id="lesson_36",
        title="Lesson 36: Connectors & Small Words",
        lesson_type="vocabulary",
        prefix="connectors",
        items=[
            VocabItem("And", "Եւ", "Yev"),
            VocabItem("But", "Պայց", "Payts"),
            VocabItem("Because", "Որովհետեւ", "Vorovhedev"),
            VocabItem("Also / Too", "Ալ եւս", "Al evs"),
            VocabItem("Very", "Շատ", "Shad"),
            VocabItem("Maybe", "Կարելի է", "Gareli e"),
            VocabItem("Always", "Միշտ", "Mishd"),
            VocabItem("Never", "Երբեք", "Yerpek"),
            VocabItem("Sometimes", "Երբեմն", "Yerpemn"),
            VocabItem("Already", "Արդէն", "Arten"),
            VocabItem("Still / Yet", "Տակաւին", "Dagavin"),
            VocabItem("Then / After that", "Ետք", "Yedk"),
            VocabItem("Before", "Առաջ", "Araj"),
            VocabItem("If", "Եթէ", "Yete"),
        ]
    ),
    
    "lesson_37": Lesson(
        id="lesson_37",
        title="Lesson 37: Talking About Yourself",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("My name is...", "Անունս ... է", "Anouns ... e", "about_my_name"),
            Sentence("I am Armenian", "Ես Հայ եմ", "Yes Hay em", "about_i_am_armenian"),
            Sentence("I am from...", "Ես ...էն եմ", "Yes ...en em", "about_i_am_from"),
            Sentence("I live in...", "Ես ...մէջ կ’ապրիմ", "Yes ...mej g'abrim", "about_i_live_in"),
            Sentence("I work at...", "Ես ...մէջ կ’աշխատիմ", "Yes ...mej g'ashkhadim", "about_i_work_at"),
            Sentence("I am ... years old", "Ես ... տարեկան եմ", "Yes ... daregan em", "about_my_age"),
            Sentence("I speak Armenian", "Ես Հայերէն կը խօսիմ", "Yes Hayeren ge khosim", "about_speak_armenian"),
            Sentence("I am learning Armenian", "Ես Հայերէն կը սորվիմ", "Yes Hayeren ge sorvim", "about_learning_armenian"),
            Sentence("I am married", "Ես ամուսնացած եմ", "Yes amousnatsadz em", "about_married"),
            Sentence("I have two children", "Ես երկու զաւակ ունիմ", "Yes yergou zavag ounim", "about_children"),
        ]
    ),
    
    "lesson_38": Lesson(
        id="lesson_38",
        title="Lesson 38: Survival & Emergency Phrases",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("Help!", "Օգնութիւն՝", "Oknoutiun!", "survival_help"),
            Sentence("I am lost", "Կորսուած եմ", "Gorsvadz em", "survival_lost"),
            Sentence("I don't understand", "Չեմ հասկնար", "Chem hasknar", "survival_dont_understand"),
            Sentence("Do you speak English?", "Անկլերէն կը խօսիս՞", "Angleren ge khosis?", "survival_speak_english"),
            Sentence("Where is the hospital?", "Ուռ է հիւանդանոցը՞", "Oor e hivantanotse?", "survival_hospital"),
            Sentence("Call the police", "Ոստիկանութեան կանչեցէք", "Vosdikanoutyan ganchetsek", "survival_police"),
            Sentence("I need a doctor", "Պժիշկի պէտք ունիմ", "Pjishgi bedk ounim", "survival_need_doctor"),
            Sentence("I am allergic to...", "Ես ...ի ալերժի ունիմ", "Yes ...i alerji ounim", "survival_allergic"),
            Sentence("Please speak slowly", "Կամաց կամաց խօսեցէք", "Gamats gamats khosetsek", "survival_speak_slowly"),
            Sentence("Can you help me?", "Կրնաս ինծի օգնե՞լ", "Grnas indzi oknel?", "survival_can_you_help"),
        ]
    ),
    
    "lesson_39": Lesson(
        id="lesson_39",
        title="Lesson 39: Making Plans & Invitations",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("Let's go!", "Երթանք՝", "Yertank!", "plans_lets_go"),
            Sentence("Do you want to come?", "Կ’ուզես գալ՞", "G'ouzes kal?", "plans_want_to_come"),
            Sentence("What are you doing tomorrow?", "Վաղը ինչ պիտի ընես՞", "Vaghe inch bidi enes?", "plans_tomorrow"),
            Sentence("Are you free this weekend?", "Աս շաբաթաւերջ ազատ ես՞", "As shapataverjy azad es?", "plans_weekend"),
            Sentence("I invite you", "Ռեզ կը հրաւիրեմ", "Kez ge hravirem", "plans_invite"),
            Sentence("At what time?", "Ինչ ժամին՞", "Inch jamin?", "plans_what_time"),
            Sentence("Where shall we meet?", "Ուռ հանդիպինք՞", "Oor hantibink?", "plans_where_meet"),
            Sentence("I will be there", "Հոն պիտի ըլլամ", "Hon bidi ellam", "plans_will_be_there"),
            Sentence("Sorry, I can't", "Ներեցէք, չեմ կրնար", "Neretseek, chem grnar", "plans_sorry_cant"),
            Sentence("See you tomorrow", "Վաղը կը տեսնուինք", "Vaghe ge desnouvink", "plans_see_you_tomorrow"),
        ]
    ),
    
    "lesson_40": Lesson(
        id="lesson_40",
        title="Lesson 40: Evening Routine",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("I come home from work", "Աշխատանքէն տուն կու գամ", "Ashkhadanken doon gou kam", "evening_come_home"),
            Sentence("I cook dinner", "Ընտրիք կը պատրաստեմ", "Endrik ge badrasdem", "evening_cook_dinner"),
            Sentence("We eat together", "Միասին կ’ուտենք", "Miasin g'oudenk", "evening_eat_together"),
            Sentence("I watch television", "Հեռատեսիլ կը նայիմ", "Herradesil ge nayim", "evening_watch_tv"),
            Sentence("I read a book", "Գիրք մը կը կարդամ", "Kirk me ge gardam", "evening_read_book"),
            Sentence("I talk on the phone", "Հեռախօսով կը խօսիմ", "Herrakhosov ge khosim", "evening_phone"),
            Sentence("I take a shower", "Ծնցուղ կ’առնեմ", "Tsentsough g'arnem", "evening_shower"),
            Sentence("I brush my teeth", "Ակռաներս կը խոզանակեմ", "Agrainers ge khozanagem", "evening_brush_teeth"),
            Sentence("I go to bed", "Անկողին կ’երթամ", "Angoghin g'ertham", "evening_go_to_bed"),
            Sentence("Good night", "Կիշեր բարի", "Kisher pari", "evening_good_night"),
        ]
    ),
    
    "lesson_41": Lesson(
        id="lesson_41",
        title="Lesson 41: Phone & Texting Phrases",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("Hello? (on phone)", "Ալօ՞", "Alo?", "phone_hello"),
            Sentence("Who is speaking?", "Ով՞ կը խօսի", "Ov ge khosi?", "phone_who_speaking"),
            Sentence("Can you hear me?", "Կը լսես՞", "Ge lses?", "phone_can_you_hear"),
            Sentence("I will call you later", "Ետքը պիտի զանգեմ", "Yedke bidi zankem", "phone_call_later"),
            Sentence("Send me a message", "Լուր մը ղրկէ", "Loor me ghrgeh", "phone_send_message"),
            Sentence("I will text you", "Պիտի գրեմ քեզի", "Bidi krem kezi", "phone_text_you"),
            Sentence("My phone is dead", "Հեռախօսս մարեցաւ", "Herrakhoss maretsav", "phone_dead"),
            Sentence("What is your number?", "Ինչ է հեռախօսիդ թիւը՞", "Inch e herrakhosit tive?", "phone_your_number"),
            Sentence("I don't have signal", "Կապ չունիմ", "Kab chounim", "phone_no_signal"),
            Sentence("Talk to you soon", "Շուտով կը խօսինք", "Shoudov ge khosinkt", "phone_talk_soon"),
        ]
    ),
    
    "lesson_42": Lesson(
        id="lesson_42",
        title="Lesson 42: Opinions & Preferences",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("I like this", "Ասիկա կը սիրեմ", "Asiga ge sirem", "opinion_i_like"),
            Sentence("I don't like this", "Ասիկա չեմ սիրեր", "Asiga chem sirer", "opinion_dont_like"),
            Sentence("I prefer...", "Կը նախընտրեմ...", "Ge nakhendrem...", "opinion_prefer"),
            Sentence("I think that...", "Կը կարծեմ թէ...", "Ge gardzem te...", "opinion_i_think"),
            Sentence("I agree", "Համաձայն եմ", "Hamatsayn em", "opinion_agree"),
            Sentence("I disagree", "Համաձայն չեմ", "Hamatsayn chem", "opinion_disagree"),
            Sentence("It doesn't matter", "Կարեւոր չէ", "Garvor che", "opinion_doesnt_matter"),
            Sentence("That's a good idea", "Լաւ գաղափար է", "Lav kaghapar e", "opinion_good_idea"),
            Sentence("Which one do you like?", "Որը կը սիրես՞", "Vore ge sires?", "opinion_which_like"),
            Sentence("It's up to you", "Քեզի համար է", "Kezi hamar e", "opinion_up_to_you"),
        ]
    ),
    
    "lesson_43": Lesson(
        id="lesson_43",
        title="Lesson 43: Asking for Help & Clarification",
        lesson_type="sentences",
        prefix="sent",
        items=[
            Sentence("Can you help me?", "Կրնաս ինծի օգնե՞լ", "Grnas indzi oknel?", "help_can_you_help"),
            Sentence("I don't understand", "Չեմ հասկնար", "Chem hasknar", "help_dont_understand"),
            Sentence("Can you repeat that?", "Կրնաս կրկնե՞լ", "Grnas grgnel?", "help_repeat"),
            Sentence("What does this mean?", "Ասիկա ինչ կը նշանակէ՞", "Asiga inch ge nshanage?", "help_what_means"),
            Sentence("How do you say ... in Armenian?", "Հայերէնով ինչպէ՞ս կ’ըսեն", "Hayerenov inchbes g'esen...?", "help_how_say"),
            Sentence("Please write it down", "Խնդրեմ գրեցէք", "Khntrem gretsek", "help_write_down"),
            Sentence("I need help", "Օգնութեան պէտք ունիմ", "Oknoutyan bedk ounim", "help_need_help"),
            Sentence("Where can I find...?", "Ուռ կրնամ գտնել՞...", "Oor grnam kdnel...?", "help_where_find"),
            Sentence("Is there someone who speaks English?", "Մէկը կայ որ Անկլերէն կը խօսի՞", "Mege ga vor Angleren ge khosi?", "help_someone_english"),
            Sentence("Thank you for your help", "Շնորհակալ եմ օգնութեանդ", "Shnorhagal em oknoutyant", "help_thank_you"),
        ]
    ),
}


# Helper function to get lesson by ID
def get_lesson(lesson_id: str) -> Lesson:
    """Retrieve a lesson by its ID."""
    return LESSONS.get(lesson_id)


# Helper function to list all available lessons in order
def list_lessons_ordered() -> list:
    """
    Return list of (lesson_id, lesson_title) tuples in sequential order.
    Ensures lessons are always displayed 1-43 in order.
    """
    # Sort by lesson_id (lesson_01, lesson_02, etc.)
    sorted_ids = sorted(LESSONS.keys())
    return [(lid, LESSONS[lid].title) for lid in sorted_ids]
