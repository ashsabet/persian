# -*- coding: utf-8 -*-
"""Curriculum content for the spoken/vocabulary units (Sections 1+).

Data-only module consumed by the `seed_curriculum` management command. Section 0
(the alphabet) stays data-driven from alphabet.csv with recorded audio; these
sections use TTS — every `words`/`phrases` item becomes a Word/Sentence row and
`generate_audio` renders `<key>.wav` with the local Piper (gyro) voice.

Conventions
- Register: standard Tehrani Persian, polite (shomā). Transliteration matches the
  alphabet set (ā/e/o/u/i, kh, gh, zh, sh, ch).
- `key`: ASCII slug, globally unique, namespaced per unit (u6-…, u6p-… for phrases)
  so it never collides with the alphabet keys.
- Each lesson lists `items` (keys drawn from its unit's words + phrases, in order);
  the seeder builds the exercises from them.
"""

SECTIONS = [
    {
        "slug": "survival",
        "order": 1,
        "title": "Survival & Self",
        "description": "Greet people, introduce yourself, count, and talk about family and everyday things (A1).",
        "units": [
            # ---------------------------------------------------------------- Unit 6
            {
                "slug": "u6-greetings",
                "order": 6,
                "title": "Unit 6 · Greetings & courtesy",
                "words": [
                    {"key": "u6-salam", "fa": "سلام", "tr": "salām", "en": "hello"},
                    {"key": "u6-khodahafez", "fa": "خداحافظ", "tr": "khodāhāfez", "en": "goodbye"},
                    {"key": "u6-sobh-bekheyr", "fa": "صبح بخیر", "tr": "sobh bekheyr", "en": "good morning"},
                    {"key": "u6-shab-bekheyr", "fa": "شب بخیر", "tr": "shab bekheyr", "en": "good night"},
                    {"key": "u6-mersi", "fa": "مرسی", "tr": "mersi", "en": "thanks"},
                    {"key": "u6-moteshakkeram", "fa": "متشکرم", "tr": "moteshakkeram", "en": "thank you"},
                    {"key": "u6-lotfan", "fa": "لطفاً", "tr": "lotfan", "en": "please"},
                    {"key": "u6-bebakhshid", "fa": "ببخشید", "tr": "bebakhshid", "en": "excuse me"},
                    {"key": "u6-bale", "fa": "بله", "tr": "bale", "en": "yes"},
                    {"key": "u6-na", "fa": "نه", "tr": "na", "en": "no"},
                    {"key": "u6-khahesh", "fa": "خواهش می‌کنم", "tr": "khāhesh mikonam", "en": "you're welcome"},
                ],
                "phrases": [
                    {"key": "u6p-khosh-amadid", "fa": "خوش آمدید", "tr": "khosh āmadid", "en": "welcome"},
                    {"key": "u6p-hale-shoma", "fa": "حال شما چطوره؟", "tr": "hāle shomā chetore?", "en": "how are you?"},
                    {"key": "u6p-khubam", "fa": "خوبم، مرسی", "tr": "khubam, mersi", "en": "I'm fine, thanks"},
                ],
                "lessons": [
                    {"slug": "u6-l1", "title": "Hello & goodbye",
                     "items": ["u6-salam", "u6-khodahafez", "u6-sobh-bekheyr", "u6-shab-bekheyr", "u6p-khosh-amadid"]},
                    {"slug": "u6-l2", "title": "Please & thank you",
                     "items": ["u6-mersi", "u6-moteshakkeram", "u6-lotfan", "u6-bebakhshid", "u6-khahesh"]},
                    {"slug": "u6-l3", "title": "Yes, no & how are you",
                     "items": ["u6-bale", "u6-na", "u6p-hale-shoma", "u6p-khubam"]},
                ],
            },
            # ---------------------------------------------------------------- Unit 7
            {
                "slug": "u7-introductions",
                "order": 7,
                "title": "Unit 7 · Introductions",
                "words": [
                    {"key": "u7-man", "fa": "من", "tr": "man", "en": "I"},
                    {"key": "u7-shoma", "fa": "شما", "tr": "shomā", "en": "you"},
                    {"key": "u7-esm", "fa": "اسم", "tr": "esm", "en": "name"},
                    {"key": "u7-irani", "fa": "ایرانی", "tr": "irāni", "en": "Iranian"},
                    {"key": "u7-amrikayi", "fa": "آمریکایی", "tr": "āmrikāyi", "en": "American"},
                    {"key": "u7-ostad", "fa": "استاد", "tr": "ostād", "en": "teacher"},
                    {"key": "u7-daneshjoo", "fa": "دانشجو", "tr": "dāneshjoo", "en": "student"},
                ],
                "phrases": [
                    {"key": "u7p-esm-q", "fa": "اسم شما چیه؟", "tr": "esme shomā chie?", "en": "what's your name?"},
                    {"key": "u7p-man-irani", "fa": "من ایرانی هستم", "tr": "man irāni hastam", "en": "I am Iranian"},
                    {"key": "u7p-ahle-koja", "fa": "شما اهل کجا هستید؟", "tr": "shomā ahle kojā hastid?", "en": "where are you from?"},
                    {"key": "u7p-khoshbakhtam", "fa": "خوشبختم", "tr": "khoshbakhtam", "en": "nice to meet you"},
                ],
                "lessons": [
                    {"slug": "u7-l1", "title": "I and you",
                     "items": ["u7-man", "u7-shoma", "u7-esm", "u7p-esm-q"]},
                    {"slug": "u7-l2", "title": "Where are you from?",
                     "items": ["u7-irani", "u7-amrikayi", "u7p-man-irani", "u7p-ahle-koja"]},
                    {"slug": "u7-l3", "title": "Nice to meet you",
                     "items": ["u7-ostad", "u7-daneshjoo", "u7p-khoshbakhtam"]},
                ],
            },
            # ---------------------------------------------------------------- Unit 8
            {
                "slug": "u8-numbers",
                "order": 8,
                "title": "Unit 8 · Numbers",
                "words": [
                    {"key": "u8-0", "fa": "صفر", "tr": "sefr", "en": "zero"},
                    {"key": "u8-1", "fa": "یک", "tr": "yek", "en": "one"},
                    {"key": "u8-2", "fa": "دو", "tr": "do", "en": "two"},
                    {"key": "u8-3", "fa": "سه", "tr": "se", "en": "three"},
                    {"key": "u8-4", "fa": "چهار", "tr": "chahār", "en": "four"},
                    {"key": "u8-5", "fa": "پنج", "tr": "panj", "en": "five"},
                    {"key": "u8-6", "fa": "شش", "tr": "shesh", "en": "six"},
                    {"key": "u8-7", "fa": "هفت", "tr": "haft", "en": "seven"},
                    {"key": "u8-8", "fa": "هشت", "tr": "hasht", "en": "eight"},
                    {"key": "u8-9", "fa": "نه", "tr": "noh", "en": "nine"},
                    {"key": "u8-10", "fa": "ده", "tr": "dah", "en": "ten"},
                    {"key": "u8-11", "fa": "یازده", "tr": "yāzdah", "en": "eleven"},
                    {"key": "u8-12", "fa": "دوازده", "tr": "davāzdah", "en": "twelve"},
                    {"key": "u8-20", "fa": "بیست", "tr": "bist", "en": "twenty"},
                ],
                "phrases": [
                    {"key": "u8p-age-q", "fa": "چند سال دارید؟", "tr": "chand sāl dārid?", "en": "how old are you?"},
                    {"key": "u8p-age-a", "fa": "من بیست سال دارم", "tr": "man bist sāl dāram", "en": "I am twenty years old"},
                    {"key": "u8p-phone", "fa": "شماره تلفن", "tr": "shomāre telefon", "en": "phone number"},
                ],
                "lessons": [
                    {"slug": "u8-l1", "title": "Zero to five",
                     "items": ["u8-0", "u8-1", "u8-2", "u8-3", "u8-4", "u8-5"]},
                    {"slug": "u8-l2", "title": "Six to ten",
                     "items": ["u8-6", "u8-7", "u8-8", "u8-9", "u8-10"]},
                    {"slug": "u8-l3", "title": "Eleven to twenty & age",
                     "items": ["u8-11", "u8-12", "u8-20", "u8p-age-q", "u8p-age-a"]},
                ],
            },
            # ---------------------------------------------------------------- Unit 9
            {
                "slug": "u9-family",
                "order": 9,
                "title": "Unit 9 · Family",
                "words": [
                    {"key": "u9-madar", "fa": "مادر", "tr": "mādar", "en": "mother"},
                    {"key": "u9-pedar", "fa": "پدر", "tr": "pedar", "en": "father"},
                    {"key": "u9-baradar", "fa": "برادر", "tr": "barādar", "en": "brother"},
                    {"key": "u9-khahar", "fa": "خواهر", "tr": "khāhar", "en": "sister"},
                    {"key": "u9-pesar", "fa": "پسر", "tr": "pesar", "en": "son"},
                    {"key": "u9-dokhtar", "fa": "دختر", "tr": "dokhtar", "en": "daughter"},
                    {"key": "u9-hamsar", "fa": "همسر", "tr": "hamsar", "en": "spouse"},
                    {"key": "u9-bachche", "fa": "بچه", "tr": "bachche", "en": "child"},
                    {"key": "u9-khanevade", "fa": "خانواده", "tr": "khānevāde", "en": "family"},
                ],
                "phrases": [
                    {"key": "u9p-pedare-man", "fa": "پدرِ من", "tr": "pedare man", "en": "my father"},
                    {"key": "u9p-khanevadeye-man", "fa": "خانواده‌ی من", "tr": "khānevādeye man", "en": "my family"},
                    {"key": "u9p-in-madar", "fa": "این مادرِ منه", "tr": "in mādare mane", "en": "this is my mother"},
                ],
                "lessons": [
                    {"slug": "u9-l1", "title": "Parents & siblings",
                     "items": ["u9-madar", "u9-pedar", "u9-baradar", "u9-khahar"]},
                    {"slug": "u9-l2", "title": "Children & family",
                     "items": ["u9-pesar", "u9-dokhtar", "u9-bachche", "u9-hamsar", "u9-khanevade"]},
                    {"slug": "u9-l3", "title": "My family (ezāfe)",
                     "items": ["u9p-pedare-man", "u9p-khanevadeye-man", "u9p-in-madar"]},
                ],
            },
            # ---------------------------------------------------------------- Unit 10
            {
                "slug": "u10-objects-colors",
                "order": 10,
                "title": "Unit 10 · Objects & colors",
                "words": [
                    {"key": "u10-miz", "fa": "میز", "tr": "miz", "en": "table"},
                    {"key": "u10-sandali", "fa": "صندلی", "tr": "sandali", "en": "chair"},
                    {"key": "u10-dar", "fa": "در", "tr": "dar", "en": "door"},
                    {"key": "u10-panjere", "fa": "پنجره", "tr": "panjere", "en": "window"},
                    {"key": "u10-ketab", "fa": "کتاب", "tr": "ketāb", "en": "book"},
                    {"key": "u10-khane", "fa": "خانه", "tr": "khāne", "en": "house"},
                    {"key": "u10-ghermez", "fa": "قرمز", "tr": "ghermez", "en": "red"},
                    {"key": "u10-abi", "fa": "آبی", "tr": "ābi", "en": "blue"},
                    {"key": "u10-sabz", "fa": "سبز", "tr": "sabz", "en": "green"},
                    {"key": "u10-zard", "fa": "زرد", "tr": "zard", "en": "yellow"},
                    {"key": "u10-siah", "fa": "سیاه", "tr": "siāh", "en": "black"},
                    {"key": "u10-sefid", "fa": "سفید", "tr": "sefid", "en": "white"},
                ],
                "phrases": [
                    {"key": "u10p-in-chie", "fa": "این چیه؟", "tr": "in chie?", "en": "what is this?"},
                    {"key": "u10p-ketab-abi", "fa": "این کتاب آبیه", "tr": "in ketāb ābie", "en": "this book is blue"},
                    {"key": "u10p-do-ta-ketab", "fa": "دو تا کتاب", "tr": "do tā ketāb", "en": "two books"},
                ],
                "lessons": [
                    {"slug": "u10-l1", "title": "Around the house",
                     "items": ["u10-miz", "u10-sandali", "u10-dar", "u10-panjere", "u10-ketab", "u10-khane"]},
                    {"slug": "u10-l2", "title": "Colors",
                     "items": ["u10-ghermez", "u10-abi", "u10-sabz", "u10-zard", "u10-siah", "u10-sefid"]},
                    {"slug": "u10-l3", "title": "This & that",
                     "items": ["u10p-in-chie", "u10p-ketab-abi", "u10p-do-ta-ketab"]},
                ],
            },
        ],
    },
]
