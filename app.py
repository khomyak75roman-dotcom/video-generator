"""Генератор відео з запиту: озвучка edge-tts + відеокліпи Openverse + субтитри (ffmpeg).
UI у стилі iPhone (CustomTkinter, dark mode iOS). v3: скролінг, авто-ffmpeg, YouTube-фон.
v4: пошук YouTube без ключів — обрані знайдені відео йдуть кліпами у фон.
v5: фронтенд у стилі iPhone — вікно з пропорціями екрана ноутбука (16:10),
центрована колонка контенту, статус-бар з годинником, home-індикатор.
v6: кнопки 📋 «Вставити» в усіх полях для посилань (запит, YouTube, пошук).
v7: сценарій по частинах — кожна частина отримує свій фон з YouTube (авто-пошук).
v8: свій сценарій — 📂 відкрити з txt-файлу / 💾 зберегти у файл;
рядок «Кліп: посилання» ставить ТВОЄ конкретне відео у фон частини.
v9: після теми відео сам шукаю на YouTube відео по словах запиту і монтую їх у фон.
v10: кнопка 🌐 «Шукати на YouTube» — відкриває YouTube у браузері, назва вже у полі пошуку.
v11: ПКМ у будь-якому полі — меню «📋 Вставити» і «🧹 Очистити» (текст з буфера обміну).
v12: простіше поле YouTube — кілька посилань зразу, з них нарізаються фрагменти для компіляції.
v13: новий інтерфейс у стилі MoneyPrinterTurbo — таби «Генерація / Історія / Налаштування»,
сайдбар налаштувань, прев'ю готового відео з кадром, кроки пайплайну, журнал збоку.
v14: 💾 пресети налаштувань, 💬 4 стилі субтитрів, 🎨 стилістика картинки (Кіно/Тепло/Ч-Б…),
🎞 переходи між фрагментами (xfade), 📷 обкладинка YouTube (cover.jpg),
✂️ прибрання пауз з озвучки, 📚 батч-генерація (теми з нового рядка), 12 голосів edge-tts.
v15: 📜 транскрипція YouTube (субтитри без ключів) → стиснення до ~10 хв → сценарій,
🚫 фрагменти фону без обличчя людей (OpenCV, якщо встановлено),
📈 SEO-пак для YouTube: назва, опис, теги, ключові слова, хештеги, закріплений коментар.
v16: 🎧 мікс-режим для YouTube-каналу: пошук музики Pixabay (ключ зберігається
лише на твоєму комп'ютері — у код і GitHub не потрапляє), завантаження обраних
треків у папку MixTracks → годинний мікс з кросфейдами, гучністю за стандартом
YouTube (-14 LUFS), фон-петлею, обкладинкою і SEO-паком із треклистом.
v17: простий інтерфейс — один вибір режиму нагорі (🎬 Відео / 📜 Сценарій / 🎧 Мікс)
замість розкиданих перемикачів; поля показуються лише для обраного режиму;
рідкі налаштування згорнуті в «⚙️ Додатково», рідкі інструменти — в «🧰 Інструменти»
(інструменти поруч із місцем використання: пошук фону — у режимі Відео,
транскрипція — у Сценарії); 🖼 пошук зображень Pinterest для фону (без ключів).
v18: 🖼 пошук фото для фону у трьох джерелах — Openverse (відкриті ліцензії,
без ключа), Pixabay (офіційний API, той самий локальний ключ, що для музики)
і Pinterest; автори та джерела фото пишуться у credits.txt біля скачаних файлів.
v19: 🎼 генерація музики через Suno AI — опиши трек звичайною мовою
(«заспокійливий lo-fi про вечірній Київ»), і Suno зробить 2 варіанти,
а програма скачає готові mp3 у папку MixTracks (для міксу або фону).
Доступ — через cookie сесії з браузера; зберігається лише на цьому
комп'ютері (як ключ Pixabay). Офіційного публічного API у Suno нема,
тому це неформальний клієнт — для власного акаунта з малим обсягом.
v20: 🚫 усі зовнішні запуски (yt-dlp, ffmpeg, powershell) тепер без спливаючих
чорних консольних вікон — під час генерації нічого не з'являється поза вікном
програми (CREATE_NO_WINDOW автоматично для кожного subprocess-виклику).
v21: 🎨 BT.709 — правильні кольори після YouTube-ре-енкоду (без «вимитих» відтінків);
⚡ апаратний кодек, якщо є GPU (nvenc/amf/qsv, інакше libx264) — швидший фінальний рендер;
🎧 дакінг музики — фон сам притихає під голосом і повертається в паузах (sidechaincompress).
v22: 📦 кеш-банк сток-кліпів (патерн CDAF) — кліпи Openverse/Wikimedia качаються раз
і живуть у локальному кеші з індексом метаданих (запит/назва/ліцензія/теги):
повторні генерації тієї ж теми майже миттєві й не витрачають трафік;
🎚 гучність фінального міксу вирівнюється до -14 LUFS (EBU R128, стандарт YouTube) —
у всіх режимах, включно з фолбеком без субтитрів.
v23: 🥁 beat-sync фону — музика аналізується чистим Python (огибаюча енергії +
автокореляція онсетів → BPM + фаза) і зміни кадрів потрапляють у такт:
ефект «Director Mode» з AI-студій; ритм невиразний — монтується як раніше.
v24: 🔍 аудіо-лікар — готове відео перевіряється на тишу, кліпінг і довгі
паузи (silencedetect + volumedetect) і попереджає у журнал, не ламаючи генерацію;
🧪 передпольотні перевірки — перед стартом звіряється місце на диску, доступність
музики (запис без музики краще за падіння на 90-й хвилині) та наявність OpenCV.
v25: 🎤 караоке-субтитри — під час озвучки edge-tts віддає точні часові
мітки кожного слова (WordBoundary), і субтитри будуються за РЕАЛЬНИМ
голосом, а не рівномірною апроксимацією: короткі фрази з'являються точно
коли звучать (як auto-captions у CapCut/TikTok). Новий стиль субтитрів
«Караоке» (жовті з рамкою). Якщо хмара не дала міток або ввімкнено
прибирання пауз — тихо повертаємось до рівномірних субтитрів (fail-open).
v26: 🤖 агентне вікно — у режимі Відео з'явилось поле «🤖 Асистент»:
пиши фразу звичайною мовою («зроби вертикальне відео про каву голосом
Остапа з караоке-субтитрами, без музики») — парсер на правилах (нуль ключів,
Tier 1) сам налаштує тему, орієнтацію, голос, стиль субтитрів, музику,
обкладинку/SEO/щільну озвучку і підказує; «давай» — і генерація їде.
Невпізнане лишається темою; парсер ніколи не падає (fail-open).
v26.1–v26.3: 🤖 поле Асистента — багаторядкове зі скролінгом (CTkTextbox);
байнди хоткеїв — fail-open (збій байнда не валить старт); у полях теми
й Асистента — кнопки «📥 Вставити»: вставка з буфера працює завжди,
навіть якщо Ctrl+V у вашій збірці не перехоплюється.
v27: 🎯 «Тривалість: N» у сценарії — озвучка «під рядок»: atempo-фіт тривалості
частини без зміни висоти голосу (караоке-мітки стискаються разом зі звуком, fail-open);
🔊 перемикач «Майстеринг −14 LUFS» — two-pass EBU R128 (measured-лінійний —
прозоріш за однопрохідний динамічний); 📦 «під точний розмір» — two-pass копія
10/25/50/100 МБ (Discord/пошта/Shorts) поруч з оригіналом; ⏭️ фон з YouTube чистіший —
SponsorBlock вирізає спонсорські вставки (стара збірка yt-dlp — без вирізання, fail-open).
v28: 🎚 повзунок темпу озвучки (−20…+30%, edge-tts rate — голос лишається тим самим);
📄 credits.json — структуровані кредити всіх фонових джерел поруч з credits.txt
(фон з YouTube тепер теж пишеться у кредити); 🛡️ QC-звіт — повне декодування
-xerror, 3 кадр-проби і підсумок у qc.txt; 📋 manifest.json — план генерації
(режим, тема/частини, голос, стилі) як артефакт у робочій папці (fail-open).
v29: 🧠 Tier 2 — опційний локальний Ollama для Асистента: налаштування
живуть лише на комп'ютері (tools/ollama.json, як ключ Pixabay); слабка для
парсера фраза або «сценарій про …» без тексту — локальна модель розбирає
фразу у ті самі поля й уміє писати сценарій частинами; усе у фоновому потоці
(Tk не блокується), нема Ollama — Асистент працює як раніше (fail-open, нуль ключів).
v30: 🎚 довгі озвучки edge-tts більше не обриваються — текст ріжеться на
шматки по реченнях і зшивається воєдино, караоке-мітки зсуваються разом
з ними; 📑 chapters.txt — розділи YouTube за частинами (допис у SEO-пак);
📝 approval.txt — тривалість/розмір, артефакти ✓/— і поради перед публікацією;
📦 кнопка у сценарії — відновити частини з manifest.json минулого запуску.
v31: 🌐 Tier 2 тепер ходить і через 9Router — локальний OpenAI-сумісний роутер
(localhost:20128): перемикач Ollama/9Router у картці Асистента, моделі
підписуються так само (/v1/models, /v1/chat/completions); api-free, нуль
ключів, усе локально; нема роутера — Асистент працює як раніше (fail-open).
v32: 🛡️ no-regression guard у 📦-стисненні — битий або не менший за оригінал
результат прибирається, лишаю оригінал; маркер у manifest.json — той самий
розмір не стискається двічі; 📝 llm_trace.jsonl — журнал запитів Tier 2 (хто,
скільки тривало, чи відповіло; opik-патерн); 📺 платформа публікації — пресет
📦 і поради в approval.txt (HandBrake-пресети); 📏 правила проєкту для
Асистента — поле "rules" у tools/ollama.json (abide-урок).
v33: 🧬 картка «Метадані» в Інструментах — змінити метадані будь-якого відео
до невпізнаваності: Швидко (remux без перекодування — випалює всі теги/розділи,
пише випадкову creation_time) або Глибоко (ще й перекодування h264/aac —
стерає відбитки кодека). Вихідний файл не чіпається: результат *_meta.mp4 поруч.
v34: ⏱ ETA під час довгих перекодувань (ffmpeg -progress: «⏱ 34% • 1.2x •
лишилось ~2 хв»); 🧹 перемикач «Авто-чистка метаданих» — фінал після генерації
без анонімних тегів, з випадковою датою; 📈 перемикач «Апскейл до 4К» —
фінал масштабується до 3840×2160 (або 2160×3840 для вертикальних) lanczos+unsharp:
чесно — нових деталей не додає, але YouTube дає 4К-завантаженням вищий бітрейт,
тож після стиснення YouTube картинка виглядає краще. Обидва — fail-open.
v35: 🌐 Асистент уміє думати ОНЛАЙН — безкоштовний Pollinations
(text.pollinations.ai): третій перемикач «🌐 Онлайн» поруч з Ollama/9Router,
БЕЗ ключів і БЕЗ встановлення (анонімна модель gpt-oss-20b, ліміт ~1 запит/15 с);
POST /openai (OpenAI-формат) + GET-фолбек, пауза між запитами, усе fail-open —
мережі нема — Асистент працює як раніше (парсер правил).
v36: ⚡ Kilo Code — ще один БЕЗКЛЮЧОВИЙ онлайн-LLM (api.kilo.ai/api/gateway,
free-пул ~200 запитів/год — у рази щільніше за Pollinations, теж без встановлення);
🔑 «Ключ» — безкоштовні фрітір-ключі (Groq / GitHub Models / Gemini, OpenAI-сумісні,
Bearer) з tools/freekeys.json — файл лише на твоєму комп'ютері, як ключ Pixabay;
гроші — нуль, картка ніде не потрібна; 🎤 авто-субтитри — Whisper на Groq:
будь-яке відео → .srt + .txt (~8 год аудіо/день безкоштовно). Усе fail-open.
v37: 🤝 HF Spaces — публічний Gradio-API БЕЗ ключа (huggingface.co/spaces):
універсальний клієнт hf_space_call (queue-протокол gradio_api/call, fail-open) і
три нові інструменти в 🧰: 🗣 клонування голосу (Chatterbox: зразок аудіо 5–20 с
→ твій голос; текст ріжеться на шматки ≤300 символів і зшивається ffmpeg),
🖼 AI-картинка (FLUX.1-schnell: текст → зображення 1024×1024 за 4 кроки),
🎬 оживлення картинки (WAN 2.2: кадр → короткий mp4). Space-и публічні й
безкоштовні, черги ZeroGPU діляться на всіх — у годину пік може бути
«черга повна», тоді чесно пишемо в журнал і нічого не ламається (fail-open).
v38: 🧠 нейро-ядро — сімка нейромереж на HF Spaces, усі БЕЗ ключа:
🖌 редагування картинки промптом (FLUX.1 Kontext: «вечір, додай дощ» → нова
картинка), ✂️ видалення фону (прозорий png), 🔍 OCR (DeepSeek: текст зі
скріншота чи сторінки), 🎬 перехід двох кадрів (WAN 2.2: перший кадр →
останній — цемент між сценами); стан усього ядра — одна кнопка 🔄 Перевірити.
🗣 озвучка клоном у пайплайні: перемикач у 🧰 — і голосом відео вже не edge-tts,
а ТВІЙ голос (зразок зберігається в tools/clone.json лише локально, як ключ
Pixabay; клон не віддає міток слів — караоке-субтитри чесно відступають до
звичайних; не вийшло — озвучка як раніше, усе fail-open, нуль грошей).
v39: 🤖 Claude як мозок Асистента — чесний безкоштовний шлях: Puter
(User-Pays): безкоштовний акаунт puter.com → dashboard#account →
Create token → токен живе у tools/freekeys.json ЛИШЕ локально (як ключ
Pixabay; у коді і репо — нуль ключів). На «🔑 Ключ» Асистент думає
Claude Sonnet 5.5 (OpenAI-сумісний ендпоінт Puter; Haiku/Opus — у списку
моделей). Вичерпав місячний безкоштовний ліміт Puter (402) або токен
протух — чесно пишемо в журнал і падаємо на попередні плани (Groq /
Kilo / Pollinations — fail-open). Пріоритет ключів: Puter → Groq →
GitHub → Gemini; Whisper-субтитри Groq працюють окремо від вибору.
v40: 🔄 «Авто» — драбина джерел, щоб Асистент НІКОЛИ не впирався в ліміти:
🤖 Claude (Puter) → Claude (Anthropic-ключ) → Groq → GitHub → Gemini →
⚡ Kilo → 🌐 LLM7 → 🌐 Pollinations. Кожен запит іде по драбині: перший
живий відповідає, вичерпаний/лежачий — чесно пропускається (llm_trace),
наступного разу порядок той самий. 🌐 LLM7 — анонімний OpenAI-сумісний
шлюз (api.llm7.io, Bearer "unused", ~20–30 зап/хв, без реєстрації;
третя особа — без чутливих даних, моделі не офіційні). Гроші — нуль,
ключі — лише локально, усе fail-open.
v41: 💬 чат Асистента — дизайн і функціонал у стилі Claude: окреме вікно
з кремовою палітрою claude (ivory #FAF9F5, теракота #D97757), бульбашка
юзера праворуч, текст асистента зліва з кнопками 📋 Копіювати / 🔁 Ще
раз; багатохідна розмова з пам'яттю (history у всіх джерелах, включно
з драбиною «Авто»), ефект друку відповіді, ⏹ Стоп, чіпси-підказки на
старті, історія в tools/chat.json ЛИШЕ локально (як ключ Pixabay);
⚙️ «у поля генератора» — місток з розмови в налаштування відео.
Джерело думання чату — що обрано в картці Асистента (Claude/Kilo/
LLM7/драбина — без ключів). Кожен запит — у llm_trace.jsonl, усе
fail-open, гроші — нуль.
v42: 💬 «скопіювати функціонал Claude і як він реалізований» — у чат
прийшли фірмові механіки Claude: ⚡ справжній стрімінг (stream=True,
SSE-рядки "data: …" — токени малюються одразу, не «ефект друку»;
⏹ Стоп обриває стрім, зберігаючи часткову відповідь, як у Claude);
🎨 Markdown-рендер (жирний, курсив, `код`, заголовки, списки, цитати
— теги текстового поля); 📦 артефакти — великі код-блоки (від 5
рядків) ховаються у картки з кнопками 📋/💾/⤏у поля (сценарій летить
у генератор одним кліком); 🧠 пам'ять — «запам'ятай: …» пишеться в
tools/memory.json (лише локально) і підмішується у КОЖЕН системний
промпт, вікно керування з 🗑; 📎 вкладення файлів (txt/md/srt/json/py,
≤200 КБ у контекст); ✏️ редагування свого повідомлення з відкатом
розмови; Ctrl+K — нова розмова. Стрімінг працює по всій драбині «Авто»
(ступінь не засмітився — наступний), Pollinations при фолбеку
віддає відповідь одним шматком.
v43: 🖱 правий клік — всюди: «📋 Вставити» і «📄 Копіювати» (виділене,
а нема виділення — увесь текст) у полі Асистента, URL джерела і чаті;
відповіді чату і журнал тепер ВИДІЛЯЮТЬСЯ і копіюються (як у Claude:
мишею, Ctrl+C, Ctrl+A — відповідь не редагується, але завжди копіюється);
🔄 Джерело за замовчуванням — «Авто»-драбина; 🔑 нові безкоштовні шлюзи
у freekeys.json: ⚡ Cerebras (1М токенів/день), 🇪🇺 Mistral (experiment-план),
🧭 OpenRouter (:free-моделі), 🟩 NVIDIA NIM, 🟧 SambaNova, 🤗 HF Router
і 🤖 Google AI Studio (Gemini) — усі OpenAI-сумісні, ключі лише локально;
💬 чат Асистента — ТЕПЕР ВКЛАДКА «💬 Чат» у головному вікні: жодного
спливного вікна, повний функціонал Claude зі стрімінгом і артефактами.
v44: 🔑 вікно безкоштовних ключів (кнопка «🔑 Ключі» або перемикач
«Ключ»): обери шлюз → «🌐 Отримати ключ» — сторінка шлюзу відкриється
у Google Chrome → встав ключ → «💾 Запам'ятати назавжди» — запишеться
у tools/freekeys.json (папка програми, живе назавжди, у код не потрапляє);
«🔑 Авторизуватись через Google» — Google AI Studio у Chrome (акаунт
Google → Create API key → встав → запам'яталось); нема жодного ключа і
ти тиснеш «Ключ» — Chrome САМ відкриває сторінку отримання; 🧠 вибір
моделей у картці: Claude — Sonnet/Haiku/Opus, Mistral — лінійка,
Groq — gpt-oss (ChatGPT-подібні), 🟣 GLM — безкоштовний шлюз Zhipu
(glm-4.5-flash) + GLM:free у OpenRouter; Kilo/LLM7 — ChatGPT-шляхи
без ключа. Усе fail-open, гроші — нуль.
v45: 🟣 GLM всюди і ще LLM-платформи: GLM (Z.AI міжнародний) —
glm-4.7-flash (200K контекст), glm-4.5-flash, glm-4.6v-flash —
$0 за токен; GLM (Zhipu КНР) — оновлений список; 🌊 SiliconFlow —
фрітір ~1000 зап/хв (Qwen3-8B безкоштовна); 🟠 ModelScope (Alibaba)
— Qwen3.5/Qwen3 безкоштовно, ~2000 зап/день; OpenRouter — GLM:free
(z-ai/glm-5.2, glm-4.5-air, glm-4.5-flash). Драбина «Авто» — 18
ступенів: усі безкоштовні GLM і LLM, ключі — лише локально.
v46: 💬 чат більше НЕ ТУПИТЬ і вміє все: у шапці вкладки «Чат» —
своє 🎯 меню джерела (🤖 Claude онлайн / 💬 ChatGPT онлайн /
🇪🇺 Mistral онлайн + кожен шлюз окремо + Kilo/LLM7/Pollinations);
«🔑 Ключ» тепер іде до шлюзу, якому належить ОБРАНА модель
(freekey_engine_for), а лежачий/лімітний шлюз сам обмінюється
драбиною решти живих ключів — відповідь прилітає завжди; нема
ключа — чат чесно пише, де його взяти, а не мовчить.
v47: 🏠 СВІЙ БРАУЗЕР (кнопка «🌐 Браузер» у картці Асистента і в
чаті): адреса чи запит → reader-режим (читабельний текст, кеш
10 хв — не тупить), історія ⬅➡, пошук DuckDuckGo БЕЗ ключів,
«🌍 У Chrome» для сторінок з входом/JS. 🕵️ СВІЙ АГЕНТ у чаті:
«знайди/новини/погода…» або кнопка «🌐 Пошук» — агент спершу
йдить в DuckDuckGo, знайдене підмішується моделі — відповідь
свіжа, з джерелами-посиланнями. 🖱 ПКМ-меню виправлено і тепер
СТАНДАРТНЕ, як у будь-яких програмах: Вирізати/Копіювати/
Вставити/Виділити все/Очистити — у всіх полях (байнд жив не
там — меню могло не відкритись узагалі; виправлено).
v48: 📊 ВСІ напрацювання знань у чаті: ТАБЛИЦІ Markdown (| а | б |
+ |---|---|) — вирівняні колонки у моноширинному Consolas; ⚡
швидкість стріму — симв/с у мітці джерела під час відповіді;
🔗 кинь URL у повідомлення — агент сам прочитає сторінку;
🤖 СПРАВЖНІЙ tool-use: модель має право відповісти «🔍ПОШУК:
запит» — агент шукає в DuckDuckGo і модель відповідає ще раз
уже з даними; 💾 кеш відповідей (24 год) — те саме питання
миттєве і безкоштовне; 🌙 темна тема чату — кнопка у шапці;
📡 мітка відповіді показує, ЯКИЙ шлюз ФАКТИЧНО відповів
(навіть коли джерело — «Авто»/драбина). Усе fail-open.
v49: 🤖 ГПТ і ГУГЛ у чаті + видно, ЧОГО мовчить: «🤖 Gemini онлайн»
у меню джерел (ключ Google AI Studio + безключовий запас), ChatGPT
онлайн тепер з останнім безключовим ступенем — чат не мовчить ніколи;
🧠 ПЕРЕМИКАЧ МОДЕЛЕЙ у шапці чату (Claude-трійка, gpt-oss, Gemini,
GLM, Qwen, Mistral — список моделей обраного джерела); ⏳ драбина
чесно показує нотами «⏳ шлюз мовчить — пробую далі…» — видно, ЧОГО
нема відповіді; 🔐 Google — кнопка у шапці чату і вікні ключів:
ОДРАЗУ віко входу Google → Create API key; 🤖 tool-use чесний:
мережа мовчить — пояснення, а не сирий «🔍ПОШУК:»; 🌍 ПЕРЕКЛАД
КАРТИНКИ на 🇷🇺🇪🇸🇮🇹🇬🇧 (OCR → переклад драбиною → 4 txt) і 📷
ОБКЛАДИНКА ІНШОЮ МОВОЮ — та сама картинка, перекладений заголовок,
4 нові обкладинки. Усе fail-open, гроші — нуль.
v50: 🔎 ЛІКАР ПОШУКУ: DuckDuckGo блокував запити з «не-браузерним»
User-Agent (VideoGenerator/1.49) — тихо мовчав 403/anomaly, тому агент
і браузер не знаходили НІЧОГО. Тепер: WEB_UA — справжній браузерний
заголовок для пошуку і сторінок; драбина рушіїв — DuckDuckGo (html →
lite), а як лежить/лімітить — ЗАПАСНИЙ Mojeek (незалежний рушій, майже
не блокує, без ключів); пошук у своєму браузері більше НЕ фетчить
lite-сторінку — одразу драбина і список «№ — відкрию»; мітки кажуть,
ЯКИЙ рушій знайшов (DuckDuckGo чи Mojeek). Пошук без ключів, як і був.
v51: 📦 ПАКЕТ ІЗ ЗАМІТОК — чотири фічі з беклоґу: 💾 ДИСК-КЕШ LLM
(llm_cache.jsonl поруч із ключами) — відповіді переживають перезапуск
програми: постав те саме питання після запуску — відповідь миттєва;
📄 «Експорт» у шапці чату — розмова у читабельний txt (хто, джерело,
текст, дата); 🎤 «Голос» у шапці чату — ПРОДИКТУЙ питання: мікрофон
(dshow) → Whisper на Groq → текст у полі чату (без нових залежностей,
ключ Groq той самий, що для авто-субтитрів); 🌐 «Перекласти субтитри»
— будь-який .srt на будь-яку мову: LibreTranslate (без ключів), а як
інстанси мовчать — драбина LLM; таймінги не чіпаю. Усе fail-open.
v52: 🧹 БРАУЗЕР ПРИБРАНО (за запитом) — агент і «🔗 URL у чаті»
залишились; 🚰 LLMFaucet — «сірий» чесний безключовий агрегатор
(Bearer "free", селектори auto/auto:fast/auto:smart/auto:coding)
ступенем у драбині «Авто» і окремим джерелом чату; 🐎 AI HORDE —
краудсорс-сітка волонтерів (без реєстрації, до хвилини черги)
останнім ступенем драбини: драбина «Авто» — 21 джерело; 🧩 COHRE —
16-й безкоштовний шлюз з ключем (trial 1000 зап/міс, без картки);
🧭 OpenRouter — СВІЖІ :free-моделі (Nemotron 3.5-lightning:free
дефолт, gemma-4, dots-3, north-mini-code, inkling, flint); 🕵️
АГЕНТ×2: чистий запит (agent_query_clean), дата в контексті,
витяги ПЕРШИХ ДВОХ сторінок, tool-use до 2 раундів — після двох
чесне пояснення. НЕ прикріплено і чому: gpt4free/OmniRoute/ТГ-пули —
справді сірі, вірусні і вкрай нестабільні.
2.0: 🎬 ГЕНЕРАТОР 2.0 — кардинальна переробка за підсумками реверс-
інжинірингу 80+ репозиторіїв і 9 ТГ-каналів (архітектурна карта:
ЗАПИТ → edge-tts/HF-озвучка → фон (YouTube/Openverse/Wikimedia/Pixabay/
Pinterest/кеш-банк) → монтаж (xfade/beat-sync) → субтитри (libass
фолбек drawtext) → оверлеї → QC → рендер (BT.709, апаратний кодек);
АСИСТЕНТ → драбина 21 джерела + агент DDG→Mojeek ×2 раунди →
стрімінг → кеш RAM+диск → чат Claude-стилю). Нове у 2.0: 🏷️ ВЕРХНІ
ОВЕРЛЕЇ ffmpeg (плашка-заголовок, водяний знак, смуга прогресу —
патерн kajisho5/claude-motion: моушн-графіка без After Effects);
🛡️ QC+ — скан спалахів кадру і аудіо-попів (signalstats/volumedetect),
КОНТАКТ-ШИТ (5×4 мініатюри у qc.txt поруч) і статистика яскравості;
✂️ «Прибрати тишу з ГОТОВОГО відео» (auto-editor-молекула: silencedetect
→ нарізка живих сегментів → зшивка); 🎙️ ДУБЛЯЖ ЗА СУБТИТРАМИ (.srt →
edge-tts на рядок → atempo-фіт у таймінги → готова аудіодоріжка, а є
відео з тим самим ім'ям — і готовий дубляж-ролик); 🧪 A/B-ЗАГОЛОВКИ
(драбина LLM генерує 8 варіантів → оцінка хук-формулою → топ-3 у
журнал); 🔑 РОТАЦІЯ КЛЮЧІВ (кілька ключів одного шлюзу через кому у
freekeys.json — llm-apipool-патерн: 429/ліміт одного ключа ≠ стоп,
програма бере наступний); 🎯 auto:smart у «Авто» (важке питання —
Faucet сам підбирає розумнішу модель); 📋 EDL-ЕКСПОРТ (таймлайн
компіляції → CMX3600, відкривається у DaVinci Resolve). Усі фічі
fail-open, гроші — нуль, ключі — лише локально.
"""
import array
import asyncio
import base64
import hashlib
import html
import json
import os
import queue
import random
import re
import shutil
import subprocess
import sys
import threading
import tkinter
import time
import uuid
import webbrowser
import zipfile
from collections import Counter
from datetime import datetime
from tkinter import messagebox, filedialog, simpledialog
from urllib.parse import quote_plus, unquote_plus

import customtkinter as ctk
import edge_tts
import requests
# 🚫 v20: усі зовнішні запуски (yt-dlp, ffmpeg, ffprobe, powershell) — БЕЗ
# спливаючих чорних консольних вікон: підмінюємо subprocess.run/Popen так,
# щоб кожен виклик автоматично отримував CREATE_NO_WINDOW (на Windows).
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
_RUN_REAL = subprocess.run
_POPEN_REAL = subprocess.Popen


def _run_no_window(*args, **kwargs):
    kwargs.setdefault("creationflags", _NO_WINDOW)
    return _RUN_REAL(*args, **kwargs)


def _popen_no_window(*args, **kwargs):
    kwargs.setdefault("creationflags", _NO_WINDOW)
    return _POPEN_REAL(*args, **kwargs)


subprocess.run = _run_no_window
subprocess.Popen = _popen_no_window

try:
    from PIL import Image as PILImage  # кадр-прев'ю готового відео (Pillow іде в комплекті з CustomTkinter)
except Exception:
    PILImage = None

try:
    import cv2  # 🚫 v15: фільтр «без обличчя у кадрі» (якщо OpenCV нема — фільтр просто пропускається)
except Exception:
    cv2 = None

ctk.set_appearance_mode("dark")  # iOS: темна тема за замовчуванням
ctk.set_default_color_theme("blue")

# Шрифт Segoe UI — системний шрифт Windows (Roboto, що в CustomTkinter за замовчуванням, у Windows відсутній і виглядає дивно)

VOICES = {
    "Остап": "uk-UA-OstapNeural",
    "Поліна": "uk-UA-PolinaNeural",
    "Christopher (EN)": "en-US-ChristopherNeural",
    "Jenny (EN)": "en-US-JennyNeural",
    "Aria (EN)": "en-US-AriaNeural",
    "Guy (EN)": "en-US-GuyNeural",
    "Ryan (UK)": "en-GB-RyanNeural",
    "Sonia (UK)": "en-GB-SoniaNeural",
    "Marek (PL)": "pl-PL-MarekNeural",
    "Zofia (PL)": "pl-PL-ZofiaNeural",
    "Katja (DE)": "de-DE-KatjaNeural",
    "Conrad (DE)": "de-DE-ConradNeural",
}
SIZES = {
    "720p": "1280x720",
    "1080p": "1920x1080",
    "Shorts": "1080x1920 (Shorts)",
}
# v14 💬: стилі субтитрів — те саме force_style ffmpeg, що й «Subtitles styles» у CapCut
SUBTITLE_STYLES = {
    "Класичні": "FontSize=16",
    "Жовті з тінню (CapCut)": "FontSize=16,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,Outline=1,Shadow=1,Bold=1",
    "Білі з підкладкою": "FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101010,Outline=2,Shadow=0,Bold=0",
    "Неонові великі": "FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00ED3A7C,Outline=2,Shadow=1,Bold=1",
    "Караоке 🎤": "FontSize=15,PrimaryColour=&H0000E5FF,OutlineColour=&H00000000,Outline=2,Shadow=1,Bold=1,MarginV=36",
}
# v14 🎨: стилістика картинки — фільтри ffmpeg (як «Filters» у модних редакторах)
VIDEO_STYLES = {
    "Без стилю": "",
    "Кіно": "eq=contrast=1.12:saturation=1.05:brightness=-0.03,vignette=PI/5",
    "Тепло": "eq=saturation=1.1,colorbalance=rs=0.05:ms=0.03",
    "Чорно-біле": "hue=s=0,eq=contrast=1.1",
    "Яскраво": "eq=brightness=0.05:saturation=1.2",
    "Ретро": "noise=alls=6:allf=t,eq=saturation=0.85:contrast=1.05",
}
# v14 🎞: переходи між фрагментами компіляції (xfade ffmpeg; «Різко» = без переходу)
TRANSITIONS = {
    "Різко": "",
    "Наплив": "fade",
    "Затемнення": "fadeblack",
}
# v14 💾: папка пресетів налаштувань (JSON, поруч із результатами генерації)
PRESET_DIR = os.path.join(os.path.expanduser("~"), "Videos", "Generated", "presets")
YT_QUALITY = {"720p": 720, "1080p": 1080, "Максимальна": 2160}
YT_SEARCH_LIMIT = 12   # скільки результатів пошуку показувати
YT_CLIP_MAX_SEC = 120  # кожне обране відео — максимум стільки секунд у фоні
SCRIPT_MAX_SCENES = 12   # максимум частин сценарію у режимі «🎬 за сценарієм»
# v15 📈📜: українські стоп-слова — для SEO-паків і стиснення транскрипції
UA_STOPWORDS = frozenset((
    "і", "та", "у", "в", "з", "зі", "із", "на", "що", "як", "цей", "ця", "це", "ці",
    "той", "ті", "але", "або", "ж", "бо", "чому", "коли", "щоб", "чи", "не", "так",
    "також", "ще", "вже", "був", "була", "були", "було", "бути", "нема", "під",
    "над", "між", "без", "для", "до", "від", "про", "вони", "ми", "ви", "ти", "я",
    "він", "вона", "воно", "його", "її", "їх", "наш", "наших", "ваш", "ваша",
    "свій", "своє", "свої", "дуже", "можна", "треба", "потрібно", "які", "який",
    "яка", "яке", "всі", "все", "усе", "кожен", "ось", "отже", "проте", "однак",
    "після", "перед", "майже", "лише", "навіть", "якщо", "тому", "тут", "там",
    "де", "ні", "більше", "менше", "собі", "один", "два", "три", "як", "є",
))
TOOLS_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local", "VideoGenerator")
FFMPEG_EXE = os.path.join(TOOLS_DIR, "ffmpeg.exe")
YTDLP_EXE = os.path.join(TOOLS_DIR, "yt-dlp.exe")
YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_SOURCES = [
    "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip",
    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
]
YT_OUT_DIR = os.path.join(os.path.expanduser("~"), "Videos", "YouTube")
MERGE_OUT_DIR = os.path.join(os.path.expanduser("~"), "Videos", "Compiled")
APP_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
UA_STRING = "VideoGenerator/2.0 (https://github.com/khomyak75roman-dotcom/video-generator)"
WEB_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")  # 🔎 v50: пошуковики блокують «не-браузерні» UA
# v16 🎧: мікс-режим — папка треків і локальний ключ Pixabay (НЕ в коді/репозиторії)
MIX_TRACKS_DIR = os.path.join(os.path.expanduser("~"), "Videos", "MixTracks")
PIXABAY_KEY_FILE = os.path.join(TOOLS_DIR, "pixabay.key")
OLLAMA_CONF_FILE = os.path.join(TOOLS_DIR, "ollama.json")  # 🧠 v29/🌐 v31: URL+модель+провайдер, лише локально
POLLINATIONS_URL = "https://text.pollinations.ai"  # 🌐 v35: безкоштовний онлайн-LLM БЕЗ ключів (Pollinations)
KILO_URL = "https://api.kilo.ai/api/gateway"  # ⚡ v36: безкоштовний шлюз Kilo Code — 200 зап/год БЕЗ ключа
LLM7_URL = "https://api.llm7.io/v1"  # 🌐 v40: LLM7 — анонімний OpenAI-сумісний шлюз, Bearer "unused"
FREEKEYS_FILE = os.path.join(TOOLS_DIR, "freekeys.json")  # 🔑 v36: безкоштовні фрітір-ключі, лише локально
HF_SPACES = {  # 🤝 v37: публічні HF Spaces — Gradio-API БЕЗ ключа (fail-open)
    "tts": "https://resembleai-chatterbox.hf.space",   # 🗣 Chatterbox: клон голосу
    "img": "https://evalstate-flux1-schnell.hf.space",  # 🖼 FLUX.1-schnell: текст → картинка
    "vid": "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space",  # 🎬 WAN 2.2: кадр → відео
    "edit": "https://black-forest-labs-flux-1-kontext-dev.hf.space",  # 🖌 v38: FLUX.1 Kontext: редагування промптом
    "nobg": "https://not-lain-background-removal.hf.space",  # ✂️ v38: видалення фону
    "ocr": "https://merterbak-deepseek-ocr-demo.hf.space",  # 🔍 v38: DeepSeek-OCR: текст з картинки
    "fl": "https://multimodalart-wan-2-2-first-last-frame.hf.space",  # 🎬 v38: перший→останній кадр
}
CLONE_FILE = os.path.join(TOOLS_DIR, "clone.json")  # 🗣 v38: зразок голосу і перемикач клону, лише локально
# 🔑 v36: OpenAI-сумісні бази безкоштовних фрітір-ключів (усі — без картки; гроші — нуль)
FREEKEY_ENGINES = {
    "puter": {"url": "https://api.puter.com/puterai/openai/v1", "model": "anthropic/claude-sonnet-5-5"},  # 🤖 v39: Claude через безкоштовний Puter-токен
    "anthropic": {"url": "https://api.anthropic.com/v1", "model": "claude-sonnet-5-5"},  # 🤖 v40: Claude напряму — його безкоштовні $5-кредити (OpenAI-сумісний шар)
    "groq": {"url": "https://api.groq.com/openai/v1", "model": "openai/gpt-oss-120b"},
    "github": {"url": "https://models.github.ai/inference", "model": "openai/gpt-4o"},
    "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "gemini-2.5-flash"},  # 🤖 Google AI Studio
    "cerebras": {"url": "https://api.cerebras.ai/v1", "model": "llama-3.3-70b"},  # ⚡ v43: Cerebras — фрітір 1М токенів/день, найшвидший інференс
    "mistral": {"url": "https://api.mistral.ai/v1", "model": "mistral-small-latest"},  # 🇪🇺 v43: Mistral — experiment-план (безкоштовні запити)
    "openrouter": {"url": "https://openrouter.ai/api/v1", "model": "google/gemini-2.0-flash-exp:free"},  # 🧭 v43: OpenRouter — каталоґ :free-моделей
    "nvidia": {"url": "https://integrate.api.nvidia.com/v1", "model": "meta/llama-3.3-70b-instruct"},  # 🟩 v43: NVIDIA NIM — стартові кредити
    "sambanova": {"url": "https://api.sambanova.ai/v1", "model": "Meta-Llama-3.3-70B-Instruct"},  # 🟧 v43: SambaNova — безкоштовний фрітір
    "huggingface": {"url": "https://router.huggingface.co/v1", "model": "meta-llama/Llama-3.3-70B-Instruct"},  # 🤗 v43: HF Inference Router — пробний токен
    "zhipu": {"url": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4.7-flash"},  # 🟣 v44/v45: GLM (Zhipu КНР) — glm-*-flash безкоштовні, фрітір без картки
    "zai": {"url": "https://api.z.ai/api/paas/v4", "model": "glm-4.7-flash"},  # 🟣 v45: GLM (Z.AI міжнародний) — glm-4.7-flash (200K), 4.5-flash, 4.6v-flash — $0
    "siliconflow": {"url": "https://api.siliconflow.cn/v1", "model": "Qwen/Qwen3-8B"},  # 🌊 v45: SiliconFlow — фрітір 1000 зап/хв, Qwen3-8B безкоштовна
    "modelscope": {"url": "https://api-inference.modelscope.cn/v1", "model": "Qwen/Qwen3-8B"},  # 🟠 v45: ModelScope (Alibaba) — Qwen безкоштовно, ~2000 зап/день
    "cohere": {"url": "https://api.cohere.ai/compatibility/v1", "model": "command-a-plus-05-2026"},  # 🧩 v52: Cohere — OpenAI-сумісний шар, trial 1000 зап/міс без картки
}
FREEKEY_ORDER = ("puter", "anthropic", "cerebras", "groq", "mistral", "github",
                 "gemini", "openrouter", "nvidia", "sambanova", "huggingface",
                 "zhipu", "zai", "siliconflow", "modelscope", "cohere")  # 🪜 v43–v52: порядок драбини «Авто»
# 🌐 v44: де взяти безкоштовний ключ — сторінка відкривається у Chrome
KEY_SIGNUP = {
    "puter": "https://puter.com/dashboard#account",  # Create token
    "anthropic": "https://console.anthropic.com/settings/keys",
    "cerebras": "https://cloud.cerebras.ai/",
    "groq": "https://console.groq.com/keys",
    "mistral": "https://console.mistral.ai/api-keys",
    "github": "https://github.com/settings/tokens",
    "gemini": "https://aistudio.google.com/apikey",  # 🔑 Google AI Studio (акаунт Google)
    "openrouter": "https://openrouter.ai/settings/keys",
    "nvidia": "https://build.nvidia.com/",
    "sambanova": "https://cloud.sambanova.ai/apis",
    "huggingface": "https://huggingface.co/settings/tokens",
    "zhipu": "https://open.bigmodel.cn/userapi/apikey",  # 🟣 GLM (КНР)
    "zai": "https://z.ai/manage-apikey/apikey-list",  # 🟣 GLM (міжнародний)
    "siliconflow": "https://cloud.siliconflow.cn/account/ak",  # 🌊 SiliconFlow
    "modelscope": "https://modelscope.cn/my/myaccesstoken",  # 🟠 ModelScope
    "cohere": "https://dashboard.cohere.com/api-keys",  # 🧩 v52: Cohere
}
# 🔑 v44: коротка інструкція для кожного шлюзу (показується у вікні ключів)
KEY_HINTS = {
    "puter": "🤖 Claude без картки: реєстрація на puter.com → Dashboard → Account → «Create token» → скопіюй токен.",
    "anthropic": "🤖 Claude напряму: console.anthropic.com → API Keys — безкоштовні $5-кредити новим акаунтам.",
    "cerebras": "⚡ Cerebras: реєстрація на cloud.cerebras.ai (Google-акаунт) → API Keys — 1 млн токенів/день.",
    "groq": "🔑 Groq: console.groq.com (Google-акаунт) → API Keys → Create API Key — картка не потрібна.",
    "mistral": "🇪🇺 Mistral: console.mistral.ai → API Keys — experiment-план: безкоштовні запити.",
    "github": "🐙 GitHub Models: github.com → Settings → Developer settings → Personal access tokens (Fine-grained).",
    "gemini": "🤖 Google AI Studio: aistudio.google.com/apikey — увійди акаунтом Google → «Create API key».",
    "openrouter": "🧭 OpenRouter: openrouter.ai → Keys → Create Key — у каталозі шукай моделі з суфіксом :free.",
    "nvidia": "🟩 NVIDIA NIM: build.nvidia.com → Log in → Get API Key — стартові кредити, картка не потрібна.",
    "sambanova": "🟧 SambaNova: cloud.sambanova.ai → APIs → Create API Key — безкоштовний фрітір.",
    "huggingface": "🤗 HF: huggingface.co → Settings → Access Tokens → New token (Read).",
    "zhipu": "🟣 GLM (Zhipu КНР): open.bigmodel.cn → API Keys — glm-4.7-flash і glm-4.5-flash БЕЗКОШТОВНІ (телефон КНР для реєстрації).",
    "zai": "🟣 GLM (Z.AI міжнародний): z.ai → API Keys → Create key — glm-4.7-flash (200K контекст!), glm-4.5-flash і glm-4.6v-flash — $0 за токен, без картки.",
    "siliconflow": "🌊 SiliconFlow: cloud.siliconflow.cn → API-ключі — безкоштовні моделі позначені «Free» (Qwen3-8B), ~1000 зап/хв у фрітірі.",
    "modelscope": "🟠 ModelScope (Alibaba): modelscope.cn → Access Tokens — токен без картки; Qwen3.5/Qwen3 — безкоштовно, ~2000 зап/день.",
    "cohere": "🧩 Cohere: dashboard.cohere.com → API keys — trial-ключ: 1000 запитів/міс БЕЗ картки; модель command-a-plus-05-2026.",
}
# 🧠 v44: вибір моделей для кожного шлюзу (у т.ч. трійка Claude — як Sonnet/Haiku/Opus)
FREEKEY_MODELS = {
    "puter": ["anthropic/claude-sonnet-5-5", "anthropic/claude-haiku-5-5", "anthropic/claude-opus-5-5"],
    "anthropic": ["claude-sonnet-5-5", "claude-haiku-5-5", "claude-opus-5-5"],
    "cerebras": ["llama-3.3-70b", "llama3.1-8b"],
    "groq": ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"],
    "mistral": ["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest",
                "open-mistral-nemo", "magistral-small-latest"],
    "github": ["openai/gpt-4o", "openai/gpt-4o-mini", "microsoft/phi-4"],
    "gemini": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
    "openrouter": ["nvidia/nemotron-3.5-lightning:free",  # 🧭 v52: СВІЖИЙ каталог :free (25.10) — старі gpt-oss/GLM:free зникли
                   "nvidia/nemotron-3-ultra-550b-a55b:free",
                   "nvidia/nemotron-3-super-120b-a12b:free",
                   "google/gemma-4-31b-it:free",
                   "google/gemma-4-26b-a4b-it:free",
                   "dots-studio/dots-3-note-preview:free",
                   "cohere/north-mini-code:free",
                   "thinkingmachines/inkling:free",
                   "recursive/flint-v1.0:free",
                   "openrouter/free"],
    "nvidia": ["meta/llama-3.3-70b-instruct", "openai/gpt-oss-120b", "qwen/qwen3-235b-a22b-instruct"],
    "sambanova": ["Meta-Llama-3.3-70B-Instruct", "Meta-Llama-3.1-8B-Instruct"],
    "huggingface": ["meta-llama/Llama-3.3-70B-Instruct", "openai/gpt-oss-120b"],
    "zhipu": ["glm-4.7-flash", "glm-4.5-flash", "glm-4.6v-flash", "glm-4.6",
              "glm-4.5-air", "glm-4.5", "glm-4-flash-250414"],
    "zai": ["glm-4.7-flash", "glm-4.5-flash", "glm-4.6v-flash", "glm-4.6",
            "glm-4.5-air", "glm-4.5"],
    "siliconflow": ["Qwen/Qwen3-8B", "Qwen/Qwen2.5-7B-Instruct",
                    "Qwen/Qwen3-Coder-30B-A3B-Instruct"],
    "modelscope": ["Qwen/Qwen3-8B", "Qwen/Qwen3.5-35B-A3B", "Qwen/Qwen3.5-27B",
                   "Qwen/Qwen2.5-7B-Instruct"],
    "cohere": ["command-a-plus-05-2026"],
}
# 🧭 v52: дефолт OpenRouter — свіжа :free-модель (стара зникла з каталогу)
FREEKEY_ENGINES["openrouter"]["model"] = "nvidia/nemotron-3.5-lightning:free"
LLMFAUCET_URL = "https://api.llmfaucet.dev/v1"  # 🚰 v52: безключовий агрегатор (Pollinations+LLM7+OVH+AI Horde), Bearer "free"
FAUCET_MODELS = ("auto", "auto:fast", "auto:smart", "auto:coding")  # 🚰 селектори Faucet
HORDE_URL = "https://aihorde.net/api/v2"  # 🐎 v52: краудсорс-сітка волонтерів, анонімний apikey "0000000000"
LLM_TRACE_FILE = os.path.join(TOOLS_DIR, "llm_trace.jsonl")  # 📝 v32: журнал запитів Tier 2, лише локально
CHAT_FILE = os.path.join(TOOLS_DIR, "chat.json")  # 💬 v41: історія чату Асистента, лише локально
MEMORY_FILE = os.path.join(TOOLS_DIR, "memory.json")  # 🧠 v42: пам'ять чату (факти про користувача), лише локально
MIX_CROSSFADE = 7.0   # секунди перехресного затухання між треками міксу
# v17 🖼: Pinterest — куди скачуються обрані зображення пошуку
# v18 🖼: обрані фото пошуку (Openverse / Pixabay / Pinterest) скачуються сюди
PINS_DIR = os.path.join(TOOLS_DIR, "pins")
# v19 🎼: Suno AI — неофіційний клієнт (офіційного API у Suno нема);
# cookie сесії зберігається локально, як ключ Pixabay — у код і GitHub не потрапляє
SUNO_COOKIE_FILE = os.path.join(TOOLS_DIR, "suno.cookie")
SUNO_API = "https://studio-api.prod.suno.com"
SUNO_AUTH = "https://auth.suno.com"
SUNO_CLERK_V = "5.117.0"
# v22 📦: кеш-банк сток-кліпів (патерн CDAF: кліп качається раз — опис/ліцензія/теги
# зберігаються в індексі; повторні генерації тієї ж теми беруть кліпи з диска)
CLIP_CACHE_DIR = os.path.join(TOOLS_DIR, "clip_cache")
CLIP_CACHE_INDEX = os.path.join(CLIP_CACHE_DIR, "index.json")
CLIP_CACHE_MAX_BYTES = 1536 * 1024 * 1024   # ~1.5 ГБ; далі видаляються найстаріші



def ffmpeg_path():
    """Шукає ffmpeg: біля програми → в папці інструментів → у системі (PATH)."""
    for cand in (os.path.join(APP_DIR, "ffmpeg.exe"), FFMPEG_EXE):
        if os.path.exists(cand):
            return cand
    return "ffmpeg"


def ffmpeg_available():
    """Чи запускається ffmpeg (швидка перевірка -version)."""
    try:
        r = subprocess.run([ffmpeg_path(), "-version"], capture_output=True, timeout=15)
        return r.returncode == 0
    except Exception:
        return False


def ensure_ffmpeg(say):
    """ffmpeg — серце генератора, без нього нічого не працює.
    Якщо його немає на комп'ютері — один раз завантажує офіційну безкоштовну
    збірку (без жодних ключів) у папку інструментів."""
    if ffmpeg_available():
        return
    os.makedirs(TOOLS_DIR, exist_ok=True)
    if os.path.exists(FFMPEG_EXE):
        say("⚠️ ffmpeg.exe є, але не запускається — завантажую свіжу версію")
        try:
            os.remove(FFMPEG_EXE)
        except OSError:
            pass
    zip_path = os.path.join(TOOLS_DIR, "ffmpeg.zip")
    for url in FFMPEG_SOURCES:
        try:
            say("⬇️ Завантажую ffmpeg (офіційна збірка, ~100 МБ, тільки перший раз)…")
            with requests.get(url, stream=True, timeout=300,
                              headers={"User-Agent": UA_STRING}) as r, \
                 open(zip_path, "wb") as f:
                r.raise_for_status()
                total = int(r.headers.get("Content-Length") or 0)
                done, last_pct = 0, -1
                for chunk in r.iter_content(1 << 18):
                    f.write(chunk)
                    done += len(chunk)
                    if total:
                        pct = int(done * 100 / total)
                        if pct >= last_pct + 20:
                            last_pct = pct
                            say("⬇️ ffmpeg: {}%".format(pct))
            with zipfile.ZipFile(zip_path) as z:
                names = [n for n in z.namelist() if n.endswith("bin/ffmpeg.exe")]
                if not names:
                    raise RuntimeError("у архіві немає ffmpeg.exe")
                with z.open(names[0]) as src, open(FFMPEG_EXE, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        except Exception as e:
            say("ℹ️ Одне джерело не вийшло ({}), пробую інше…".format(str(e)[:120]))
            continue
        try:
            os.remove(zip_path)
        except OSError:
            pass
        if os.path.exists(FFMPEG_EXE) and os.path.getsize(FFMPEG_EXE) > 10_000_000:
            say("✅ ffmpeg встановлено — можна генерувати!")
            return
    raise RuntimeError("не вдалося встановити ffmpeg — перевір інтернет і спробуй ще раз")


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if r.returncode != 0:
        full = (r.stderr or "") + "\n--- stdout ---\n" + (r.stdout or "")
        if cwd:
            try:
                with open(os.path.join(cwd, "ffmpeg-error.txt"), "w", encoding="utf-8") as f:
                    f.write(full)
            except OSError:
                pass
        tail = "\n".join((r.stderr or r.stdout or "?").strip().splitlines()[-20:])
        raise RuntimeError(tail)
    return r


_HW_ENC_CACHE = None


def best_video_encoder_args():
    """v21: апаратний h264-кодек (nvenc/amf/qsv) якщо є; інакше libx264.
    v23: обирається лише кодек, що реально працює на цьому залізі
    (пробне кодування 1 кадру; у списку -encoders кодек є навіть без GPU)."""
    global _HW_ENC_CACHE
    if _HW_ENC_CACHE is None:
        _HW_ENC_CACHE = []
        try:
            r = subprocess.run([ffmpeg_path(), "-hide_banner", "-encoders"],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="ignore", timeout=20)
            encs = (r.stdout or "") + (r.stderr or "")
            for name, args in (
                ("h264_nvenc", ["-c:v", "h264_nvenc", "-preset", "p4",
                                "-rc", "vbr", "-cq", "20", "-b:v", "0"]),
                ("h264_amf", ["-c:v", "h264_amf", "-quality", "balanced",
                              "-b:v", "5M"]),
                ("h264_qsv", ["-c:v", "h264_qsv", "-global_quality", "20",
                              "-preset", "veryfast"]),
            ):
                if not re.search(r"\b" + name + r"\b", encs):
                    continue
                try:  # 🔧 v23: GPU нема — кодек не ініціалізується → libx264
                    pr = subprocess.run([ffmpeg_path(), "-hide_banner", "-nostdin",
                                         "-f", "lavfi", "-i", "color=c=black:s=160x120",
                                         "-frames:v", "1", "-c:v", name,
                                         "-f", "null", "-"],
                                        capture_output=True, timeout=30)
                except Exception:
                    pr = None
                if pr is not None and pr.returncode == 0:
                    _HW_ENC_CACHE = args
                    break
        except Exception:
            _HW_ENC_CACHE = []
    return list(_HW_ENC_CACHE) or ["-c:v", "libx264", "-crf", "20",
                                   "-preset", "veryfast"]


def audio_duration(path):
    r = subprocess.run([ffmpeg_path(), "-hide_banner", "-i", path], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", r.stderr)
    if not m:
        raise RuntimeError("Не вдалося визначити тривалість озвучки")
    h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mi * 60 + s
def speed_fit(mp3, target, workdir, say):
    """🎯 v27: підігнати озвучку під цільову тривалість частини сценарію
    (atempo — голос той самий, змінюється лише швидкість; без «голівки»).
    Fail-open: не вдалось або ціль надто далеко — повертаю початковий файл."""
    target = max(2.0, float(target))
    d = audio_duration(mp3)
    if d <= 0:
        return mp3
    ratio = d / target
    if abs(ratio - 1.0) < 0.04:
        return mp3
    if not (0.55 <= ratio <= 1.9):
        say("🎯 Ціль {:.1f} с надто далеко від озвучки ({:.1f} с) — лишаю як є".format(target, d))
        return mp3
    tempo = min(max(ratio, 0.75), 1.35)
    out = mp3[:-4] + ".fit.mp3" if mp3.lower().endswith(".mp3") else mp3 + ".fit.mp3"
    try:
        run([ffmpeg_path(), "-y", "-hide_banner", "-nostdin", "-i", mp3,
             "-filter:a", "atempo={:.4f}".format(tempo),
             "-c:a", "libmp3lame", "-q:a", "4", out], cwd=workdir)
    except Exception as e:
        say("🎯 Підгонка не вийшла ({}), лишаю як є".format(str(e)[:100]))
        return mp3
    d2 = audio_duration(out)
    if d2 > 0 and abs(d2 - target) < abs(d - target):
        say("🎯 Підігнав озвучку {:.1f} → {:.1f} с (швидкість ×{:.2f})".format(d, d2, tempo))
        return out
    say("🎯 Підгонка не покращила результат — лишаю як є")
    return mp3


def loudnorm_master(video, say, workdir):
    """🔊 v27: two-pass EBU R128 (−14 LUFS, TP −1.0 dB) поверх готового відео.
    Перший прохід міряє гучність, другий лінійно вирівнює — прозоро,
    без «дихання» однопрохідного динамічного режиму. Файл міняється на місці.
    Fail-open: не вийшло — файл лишається як був."""
    ff = ffmpeg_path()
    probe = subprocess.run([ff, "-hide_banner", "-nostdin", "-i", video,
                            "-af", "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=summary",
                            "-f", "null", "-"], capture_output=True, text=True,
                           encoding="utf-8", errors="ignore", timeout=600)
    log = (probe.stderr or "") + (probe.stdout or "")

    def grab(key):
        m = re.search(key + r":\s*(-?[0-9.]+)", log)
        return m.group(1) if m else None

    mi, mtp, mlra, mth = (grab("Input Integrated"), grab("Input True Peak"),
                          grab("Input LRA"), grab("Input Threshold"))
    if not mi or not mtp or not mlra or not mth:
        say("🔊 Гучність не вдалось виміряти — пропускаю майстеринг")
        return video
    tmp = video + ".master.mp4"
    run([ff, "-y", "-hide_banner", "-nostdin", "-i", video,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
         "-af", ("loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={}:measured_TP={}:"
                 "measured_LRA={}:measured_thresh={}:linear=true").format(mi, mtp, mlra, mth),
         tmp], cwd=workdir)
    os.replace(tmp, video)
    say("🔊 Майстеринг: {} LUFS → −14 LUFS (EBU R128, TP −1.0)".format(mi))
    return video


def compress_to_size(video, mb, say, workdir):
    """📦 v27: two-pass стиснення до цільового розміру (Discord/пошта/Shorts).
    Створює окремий файл final_XXmb.mp4 поруч з оригіналом (оригінал лишається).
    Fail-open: не влізе з пристойною якістю — пропускаю.
    🛡️ v32: no-regression guard — битий або не менший за оригінал результат
    прибирається (лишаю оригінал); маркер у manifest.json — не роблю двічі."""
    ff = ffmpeg_path()
    dur = audio_duration(video)
    if dur <= 0:
        return video
    audio_kbps = 128
    vb = int((mb * 8192 * 0.93 - audio_kbps) / dur)
    if vb < 120:
        say("📦 {:.0f} с не влізе у {} МБ з пристойною якістю — пропускаю стиснення".format(dur, mb))
        return video
    out = (video[:video.rfind(".")] + "_{}mb.mp4".format(mb))
    try:  # 🛡️ v32: ідемпотентність — цей розмір уже стиснутий → не роблю двічі
        with open(os.path.join(workdir, "manifest.json"), encoding="utf-8") as f:
            pk = (json.load(f) or {}).get("pack") or {}
        if int(pk.get("mb") or 0) == int(mb) and os.path.isfile(out):
            say("📦 Вже стиснуто до {} МБ ({}) — не роблю двічі".format(mb, os.path.basename(out)))
            return out
    except Exception:
        pass  # 🛡️ v32: нема маркера або кривий маніфест — стискаю як перший раз
    say("📦 Стискаю до {} МБ (two-pass, ~{} кбіт/с на відео)…".format(mb, vb))
    for extra in (["-pass", "1", "-an", "-f", "null", "-"],
                  ["-pass", "2", "-c:a", "aac", "-b:a", str(audio_kbps) + "k",
                   "-movflags", "+faststart", out]):
        run([ff, "-y", "-hide_banner", "-nostdin", "-i", video,
             "-c:v", "libx264", "-b:v", str(vb) + "k",
             "-maxrate", str(int(vb * 1.45)) + "k", "-bufsize", str(int(vb * 2)) + "k",
             "-preset", "medium", "-pix_fmt", "yuv420p", *extra], cwd=workdir)
    for junk in ("ffmpeg2pass-0.log", "ffmpeg2pass-0.log.mbtree"):
        try:
            os.remove(os.path.join(workdir, junk))
        except OSError:
            pass
    try:  # 🛡️ v32: decode-перевірка — стиснений файл мусить читатися цілком
        pr = run([ff, "-v", "error", "-i", out, "-f", "null", "-"], cwd=workdir)
        if getattr(pr, "returncode", 1) != 0:
            raise RuntimeError("decode-перевірка не пройшла")
    except Exception as e:
        try:
            os.remove(out)
        except OSError:
            pass
        say("⚠️ 📦 Стиснений файл вийшов битим ({}), лишаю оригінал".format(str(e)[:80]))
        return video
    if os.path.getsize(out) >= os.path.getsize(video):  # 🛡️ v32: не менший за оригінал — нема сенсу
        os.remove(out)
        say("📦 Стиснута копія вийшла не меншою за оригінал — лишаю оригінал")
        return video
    try:  # 🛡️ v32: маркер «цей розмір уже зроблено» у manifest.json
        mp = os.path.join(workdir, "manifest.json")
        try:
            with open(mp, encoding="utf-8") as f:
                d = json.load(f) or {}
        except Exception:
            d = {"app": "Генератор відео 2.0"}
        d["pack"] = {"mb": int(mb), "file": os.path.basename(out)}
        with open(mp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # 🛡️ v32: маркер — зручність, ніколи не ламає стиснення
    size = os.path.getsize(out) / (1024 * 1024)
    say("📦 Готово: {} — {:.1f} МБ (оригінал лишається поруч)".format(os.path.basename(out), size))
    return out


def audio_health_check(workdir, say):
    """🔍 v24: аудіо-лікар — швидка перевірка звуку готового final.mp4
    (silencedetect + volumedetect) і попередження у журнал: повна тиша,
    кліпінг, довгі паузи з таймкодами. Ніколи не ламає генерацію."""
    try:
        final = os.path.join(workdir, "final.mp4")
        if not os.path.isfile(final):
            return
        pr = subprocess.run([ffmpeg_path(), "-hide_banner", "-i", final,
                             "-af", "silencedetect=noise=-45dB:d=2,volumedetect",
                             "-f", "null", "-"], capture_output=True, text=True,
                            encoding="utf-8", errors="ignore", timeout=180)
        log = pr.stderr or ""
        mean = re.search(r"mean_volume:\s*(-?[\d.]+)\s*dB", log)
        peak = re.search(r"max_volume:\s*(-?[\d.]+)\s*dB", log)
        if mean is None:
            return  # звукової доріжки чи звіту нема — не лякаємо марно
        if float(mean.group(1)) < -55.0:
            say("🔇 АУДІО-ТРИВОГА: у фінальному відео повна тиша — озвучка, "
                "мабуть, не вбудувалася. Перевір final.mp4 і спробуй ще раз.")
        else:
            say("🔊 Гучність фіналу: середня {} dB, пік {} dB.".format(
                mean.group(1), peak.group(1) if peak else "?"))
            if peak and float(peak.group(1)) > -0.2:
                say("⚠️ Кліпінг: пік {} dB — звук підрізається в дах, "
                    "пониж музику чи голос.".format(peak.group(1)))
        pauses = [(float(t), float(d)) for t, d in re.findall(
            r"silence_start: (-?[\d.]+)[\s\S]*?silence_duration: ([\d.]+)", log)
            if float(d) >= 3.0]
        if pauses:
            stamps = ", ".join("{}:{:02d}".format(int(t // 60), int(t % 60))
                               for t, _ in pauses[:3])
            tail = " …" if len(pauses) > 3 else ""
            say("⏸ Довгі паузи (≥3с) у фіналі: {} ({} шт.){}".format(stamps, len(pauses), tail))
        elif float(mean.group(1)) >= -55.0:
            say("✅ Аудіо-лікар: порядок.")
    except Exception:
        pass  # 🔍 v24: діагностика — лише попередження, ніколи не ламає генерацію


def credits_to_json(workdir, say):
    """📄 v28: credits.json — структуровані кредити джерел фону поруч з credits.txt:
    тип, назва, ліцензія, автор, посилання — у machine-readable вигляді (для опису
    YouTube, перевірки прав, повторного використання). Fail-open: нема файлу або
    криві рядки — тихо йду далі, криві пишу як є у поле note."""
    src = os.path.join(workdir, "credits.txt")
    if not os.path.isfile(src):
        return
    try:
        recs, seen = [], set()
        with open(src, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                kind = "video" if line.startswith("🎬") else ("photo" if line.startswith("🖼️") else "note")
                parts = [p.strip() for p in line.split(" — ")]
                url = parts[3] if len(parts) >= 4 else ""
                if url and url in seen:
                    continue
                if url:
                    seen.add(url)
                if len(parts) >= 4:
                    recs.append({"type": kind,
                                 "title": parts[0].replace("🎬", "").replace("🖼️", "").replace("📦", "").strip(),
                                 "license": parts[1], "author": parts[2], "url": url})
                else:
                    recs.append({"type": kind, "note": line})
        data = {"generated": datetime.now().strftime("%Y-%m-%d %H:%M"), "sources": recs}
        with open(os.path.join(workdir, "credits.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        say("📄 Структуровані кредити джерел ({} поз.) — credits.json".format(len(recs)))
    except Exception:
        pass  # 📄 v28: кредити — доповнення, ніколи не ламають генерацію


def qc_report(workdir, say):
    """🛡️ v28: QC-звіт фіналу — повне декодування з -xerror (цілісність файлу),
    3 кадр-проби (10/50/90% тривалості) і підсумок у qc.txt біля відео.
    QC — лише діагностика: жодне попередження не ламає генерацію (fail-open)."""
    final = os.path.join(workdir, "final.mp4")
    if not os.path.isfile(final):
        return
    try:
        ff = ffmpeg_path()
        dur = audio_duration(final)
        pr = subprocess.run([ff, "-hide_banner", "-nostdin", "-xerror", "-i", final,
                             "-f", "null", "-"], capture_output=True, text=True,
                            encoding="utf-8", errors="ignore", timeout=600)
        clean = pr.returncode == 0
        frames = []
        for i, at in enumerate((max(dur * 0.1, 0), dur * 0.5, max(dur - 0.5, 0))):
            p = os.path.join(workdir, "qc_frame_{}.jpg".format(i + 1))
            try:
                run([ff, "-y", "-hide_banner", "-nostdin", "-ss", "{:.2f}".format(at),
                     "-i", final, "-frames:v", "1", "-q:v", "3", p], cwd=workdir)
                if os.path.isfile(p) and os.path.getsize(p) > 0:
                    frames.append("qc_frame_{}.jpg".format(i + 1))
            except Exception:
                pass
        size_mb = os.path.getsize(final) / (1024 * 1024)
        if clean:
            say("🛡️ QC: декодування чисте — {:.1f} с, {:.1f} МБ, {} кадр-проб(и) — qc.txt".format(
                dur, size_mb, len(frames)))
        else:
            say("🛡️ QC-ТРИВОГА: декодування з помилкою — відео може обриватись; "
                "переглянь кадр-проби і qc.txt")
        try:
            with open(os.path.join(workdir, "qc.txt"), "w", encoding="utf-8") as f:
                f.write("QC-звіт: {}\nдекодування (ffmpeg -xerror): {}\n"
                        "тривалість: {:.1f} с\nрозмір: {:.1f} МБ\nкадр-проби: {}\n".format(
                            datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "OK" if clean else "ПОМИЛКА ДЕКОДУВАННЯ", dur, size_mb,
                            ", ".join(frames) or "не вийшло"))
        except OSError:
            pass
    except Exception:
        pass  # 🛡️ v28: QC — лише діагностика, ніколи не ламає генерацію


def qc_visual(workdir, say):
    """🛡️ 2.0: QC+ — зріз ще глибше (патерни claude-motion QC-молекул):
    КОНТАКТ-ШИТ (мініатюри всього ролика сіткою 5×4 — qc_contact_sheet.jpg),
    СКАН СПЛАХІВ кадру (середня яскравість 2 рази/с; стрибок > 55 одиниць
    між сусідніми зрізами — «моргання», помітиш ворога одразу), АУДІО-ПОПИ
    (пікова гучність volumedetect) і статистика яскравості. Усе — у qc.txt.
    Fail-open: жодне попередження не ламає генерацію."""
    final = os.path.join(workdir, "final.mp4")
    if not os.path.isfile(final):
        return
    try:
        ff = ffmpeg_path()
        dur = audio_duration(final)
        # КОНТАКТ-ШИТ: до 20 кадрів рівномірно по ролику → сітка 5×4
        sheet = os.path.join(workdir, "qc_contact_sheet.jpg")
        try:
            step = max(dur / 20.0, 0.5)
            sel = "+".join("between(t,{:.2f},{:.2f})".format(
                i * step, i * step + 0.04) for i in range(20))
            run([ff, "-y", "-hide_banner", "-nostdin", "-i", final,
                 "-vf", "select='{}',scale=320:-1,tile=5x4".format(sel),
                 "-frames:v", "1", "-q:v", "4", sheet], cwd=workdir)
        except Exception:
            sheet = None
        # Яскравість кадру 2 рази/с → спалахи (стрибок між сусідніми зрізами)
        flashes, lows, highs, vals = 0, 0, 0, []
        try:
            pr = subprocess.run([ff, "-hide_banner", "-nostdin", "-i", final,
                                 "-vf", "fps=2,signalstats,metadata=print:key=lavfi.signalstats.YAVG",
                                 "-f", "null", "-"],
                                capture_output=True, text=True,
                                encoding="utf-8", errors="ignore", timeout=600)
            for mm in re.findall(r"lavfi\.signalstats\.YAVG=([\d.]+)",
                                 pr.stderr or ""):
                try:
                    vals.append(float(mm))
                except ValueError:
                    continue
            for a, b in zip(vals, vals[1:]):
                if abs(b - a) > 55:
                    flashes += 1
            if vals:
                lows, highs = int(min(vals)), int(max(vals))
        except Exception:
            vals = []
        # Аудіо-попи: пік гучності (максимум біля 0 dB — кліпінг/тріск)
        peak = None
        try:
            pr2 = subprocess.run([ff, "-hide_banner", "-nostdin", "-i", final,
                                  "-af", "volumedetect", "-f", "null", "-"],
                                 capture_output=True, text=True,
                                 encoding="utf-8", errors="ignore", timeout=600)
            mp = re.search(r"max_volume:\s*(-?[\d.]+)\s*dB", pr2.stderr or "")
            if mp:
                peak = float(mp.group(1))
        except Exception:
            pass
        try:
            with open(os.path.join(workdir, "qc.txt"), "a", encoding="utf-8") as f:
                f.write("\nQC+ (2.0):\nконтакт-шит: {}\nспалахів кадру: {}"
                        "\nяскравість: мін {} / макс {}\nпік гучності: {} dB\n".format(
                            "qc_contact_sheet.jpg" if sheet and os.path.isfile(sheet) else "не вийшло",
                            flashes, lows, highs,
                            ("{:.1f}".format(peak) if peak is not None else "?")))
            if sheet and os.path.isfile(sheet):
                say("🛡️ QC+: контакт-шит (20 кадрів сіткою) — qc_contact_sheet.jpg")
            if flashes:
                say("🛡️ QC+: {} різких спалахів яскравості — перевір, чи не "
                    "«моргає» відео (деталі у qc.txt)".format(flashes))
            if peak is not None and peak > -0.5:
                say("🛡️ QC+: пік гучності {:.1f} dB — звук на межі кліпінгу "
                    "(тріск на колонках); див. qc.txt".format(peak))
        except OSError:
            pass
    except Exception:
        pass  # 🛡️ QC — лише діагностика, ніколи не ламає генерацію


def silence_trim_video(video, say, min_sil=0.6):
    """✂️ 2.0: прибрати тишу з ГОТОВОГО відео (auto-editor-молекула:
    silencedetect → живі сегменти з підкладками 0.15 с → нарізка →
    зшивка → поруч <ім'я>_без_тиші.mp4). Мовчання коротше 0.6 с НЕ ріжу
    (природні паузи мови). Тиші нема/не вийшло — відео не чіпаю (fail-open)."""
    try:
        if not video or not os.path.isfile(video):
            say("✂️ Спершу обери відео 🙂")
            return None
        ensure_ffmpeg(say)
        ff = ffmpeg_path()
        say("✂️ Слухаю тишу (silencedetect)…")
        pr = subprocess.run([ff, "-hide_banner", "-nostdin", "-i", video,
                             "-af", "silencedetect=noise=-35dB:d={:.2f}".format(min_sil),
                             "-f", "null", "-"],
                            capture_output=True, text=True,
                            encoding="utf-8", errors="ignore", timeout=1800)
        log = pr.stderr or ""
        starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", log)]
        ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", log)]
        cuts = list(zip(starts, ends[:len(starts)]))
        if not cuts or all((b - a) < min_sil + 0.05 for a, b in cuts):
            say("✂️ Тиші нема — відео і так щільне, різати нема чого 🙂")
            return None
        total_dur = audio_duration(video) or (cuts[-1][1] + 1.0)
        segs, t = [], 0.0  # живі ділянки: [початок, кінець] з підкладкою 0.15 с
        pad = 0.15
        for a, b in cuts:
            if a - t > 0.3:
                segs.append((t, min(a + pad, total_dur)))
            t = max(t, b - pad)
        if total_dur - t > 0.3:
            segs.append((t, total_dur))
        segs = segs[:60]  # захист: не більше 60 шматків (інакше це не паузи, а дріб'язок)
        if len(segs) < 2:
            say("✂️ Знайшов лише одну живу ділянку — різати не буду")
            return None
        say("✂️ Тиша: {} пауз ({} с) — ріжу {} шматків…".format(
            len(cuts), "{:.1f}".format(sum(b - a for a, b in cuts)),
            len(segs)))
        workdir = os.path.dirname(os.path.abspath(video))
        parts, lst = [], os.path.join(workdir, "_trim_list.txt")
        for i, (a, b) in enumerate(segs):
            p = os.path.join(workdir, "_trim_{:02d}.mp4".format(i))
            run([ff, "-y", "-hide_banner", "-nostdin",
                 "-ss", "{:.2f}".format(a), "-i", video,
                 "-t", "{:.2f}".format(b - a),
                 "-c:v", "libx264", "-crf", "21", "-preset", "veryfast",
                 "-c:a", "aac", "-b:a", "160k", "-ar", "48000", p], cwd=workdir)
            parts.append(p)
        with open(lst, "w", encoding="utf-8") as f:
            for p in parts:
                f.write("file '{}'\n".format(p))
        out = os.path.splitext(video)[0] + "_без_тиші.mp4"
        run([ff, "-y", "-hide_banner", "-nostdin", "-f", "concat",
             "-safe", "0", "-i", lst, "-c", "copy", out], cwd=workdir)
        try:
            os.remove(lst)
            for p in parts:
                os.remove(p)
        except OSError:
            pass
        if os.path.isfile(out) and os.path.getsize(out) > 1024:
            say("✂️ Готово: {} (було {:.1f} с → стало {:.1f} с)".format(
                os.path.basename(out), total_dur, audio_duration(out)))
            try:
                os.startfile(workdir)
            except Exception:
                pass
            return out
        say("✂️ Зшивка не вийшла — оригінал не зачеплений (fail-open)")
        return None
    except Exception as e:
        say("✂️ Не вийшло: " + str(e)[:160])
        return None


def _hook_score(text):
    """🧪 2.0: числова оцінка заголовка за тією ж хук-формулою, що й «🧲
    Оцінити заголовок» (число/звертання/інтрига/вигода/довжина) — для
    рейтингу A/B-варіантів. 0–100."""
    t = " ".join((text or "").split())
    score = 50
    if re.search(r"\d", t):
        score += 15
    if re.search(r"(?iu)\b(ти|твій|твоє|твоя|ви|ваш|ваша|своє)\b", t):
        score += 12
    if re.search(r"(?iu)\b(як|чому|секрет|помилк|ніхто|найкращ|спосіб)\b", t):
        score += 13
    if re.search(r"(?iu)\b(без|стоп|покроков|порад|заощад|навчис|зароб|швидк)\b", t):
        score += 10
    if len(t) > 80:
        score -= 12
    elif len(t) >= 15:
        score += 10
    return max(0, min(100, score))


def ab_titles(query, say):
    """🧪 2.0: A/B-ЗАГОЛОВКИ (HypeIt-патерн): драбина LLM («Авто» — без
    грошей) генерує 8 варіантів хука під тему; кожен оцінюють хук-формулою
    (число/ти/інтрига/вигода/довжина) → топ-3 у журнал, усі — у
    ab_titles.txt (там же, де ключі, щоб не губились). Fail-open: LLM
    мовчить — підказка й вихід."""
    q = " ".join((query or "").split())
    if len(q) < 4:
        say("🧪 Спершу напиши тему у поле запиту 🙂")
        return
    say("🧪 Генерую 8 варіантів заголовка (драбина «Авто»)…")
    raw = llm_chat("auto", "", "",
                   "Тема відео: " + q + ". Придумай РІВНО 8 варіантів "
                   "короткого заголовка-хука для Shorts (українською, до 70 "
                   "символів кожен, без нумерації та лапок, кожен з нового "
                   "рядка). Різні формули: число, вигода, інтрига, помилка, "
                   "звертання «ти».",
                   system="Ти — редактор короткого відео. Лише 8 рядків "
                          "заголовків, без вступу і пояснень.",
                   timeout=90)
    lines = []
    for ln in (raw or "").splitlines():
        ln = ln.strip().lstrip("-•*0123456789.)").strip()
        if 8 <= len(ln) <= 100:
            lines.append(ln)
    lines = list(dict.fromkeys(lines))[:12]  # dedup, порядок зберігаю
    if len(lines) < 3:
        say("🧪 Драбина LLM мовчить — спробуй ще раз або питай в Асистента")
        return
    scored = sorted(((_hook_score(t), t) for t in lines), reverse=True)
    say("🧪 A/B-заголовки — топ-3 за хук-формулою:")
    for i, (sc, t) in enumerate(scored[:3], 1):
        say("🧪 {}. {}/100 — {}".format(i, sc, t))
    try:
        os.makedirs(TOOLS_DIR, exist_ok=True)
        with open(os.path.join(TOOLS_DIR, "ab_titles.txt"), "w", encoding="utf-8") as f:
            f.write("A/B-заголовки: " + q + " ("
                    + datetime.now().strftime("%d.%m.%Y %H:%M") + ")\n\n")
            for sc, t in scored:
                f.write("{:3d}/100  {}\n".format(sc, t))
        say("🧪 Усі {} варіантів з оцінками — ab_titles.txt (папка інструментів)".format(len(scored)))
    except Exception:
        pass  # файл не вийшов — журнал і так показав топ-3 (fail-open)


def overlays_pass(final, title, workdir, say):
    """🏷️ 2.0: ВЕРХНІ ОВЕРЛЕЇ на готове відео (патерн kajisho5/claude-motion:
    моушн-графіка чистим ffmpeg+PIL, без After Effects): 1) ПЛАШКА-ЗАГОЛОВОК
    знизу ліворуч (перші 5 с — theme за статикою kajisho5 «lower third»);
    2) ВОДЯНИЙ ЗНАК праворуч внизу (легкий, півпрозорий); 3) СМУГА ПРОГРЕСУ
    знизу через весь кадр (drawbox, росте з часом — патерн Shorts). Оригінал
    НЕ чіпаю: результат → final.mp4 лише якщо оверлей-рендер пройшов,
    інакше лишається як є (fail-open)."""
    try:
        if not final or not os.path.isfile(final):
            return
        ff = ffmpeg_path()
        dur = audio_duration(final) or 10.0
        pr = subprocess.run([ff, "-hide_banner", "-nostdin", "-i", final],
                            capture_output=True, text=True,
                            encoding="utf-8", errors="ignore", timeout=60)
        m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", pr.stderr or "")
        if not m:
            say("🏷️ Оверлеї пропускаю — не бачу розміру кадру")
            return
        w, h = int(m.group(1)), int(m.group(2))
        clean = "".join(ch for ch in (title or "") if ord(ch) <= 65535)[:90]
        inputs, filt = ["-i", final], []
        have_lower = have_wm = False
        if PILImage is not None and clean:
            try:
                from PIL import ImageDraw, ImageFont
                fs = max(16, int(w / 40))
                font = None
                for fp in ("C:\\Windows\\Fonts\\segoeuib.ttf",
                           "C:\\Windows\\Fonts\\arialbd.ttf",
                           "C:\\Windows\\Fonts\\segoeui.ttf"):
                    try:
                        font = ImageFont.truetype(fp, fs)
                        break
                    except Exception:
                        font = None
                if font is not None:
                    # плашка: напівпрозора капсула + текст (lower third)
                    lw = min(int(w * 0.62), int(fs * 0.62 * max(len(clean), 8)) + fs * 2)
                    lh = int(fs * 2.2)
                    img = PILImage.new("RGBA", (lw, lh), (0, 0, 0, 0))
                    d = ImageDraw.Draw(img)
                    d.rounded_rectangle([0, 0, lw - 1, lh - 1], radius=lh // 2,
                                        fill=(10, 12, 20, 168))
                    tw = d.textlength(clean, font=font)
                    d.text(((lw - tw) / 2, (lh - fs * 1.25) / 2), clean,
                           font=font, fill=(255, 255, 255, 238))
                    lower = os.path.join(workdir, "_ov_lower.png")
                    img.save(lower)
                    inputs += ["-i", lower]
                    have_lower = True
                    # водяний знак: маленький і скромний
                    wm_t = "VideoGenerator"
                    wfs = max(12, int(w / 72))
                    wm_img = PILImage.new("RGBA", (int(wfs * 7.5), int(wfs * 1.9)),
                                          (0, 0, 0, 0))
                    dw = ImageDraw.Draw(wm_img)
                    wmfont = ImageFont.truetype(fp, wfs)
                    dw.text((2, 1), wm_t, font=wmfont, fill=(255, 255, 255, 92))
                    wm = os.path.join(workdir, "_ov_wm.png")
                    wm_img.save(wm)
                    inputs += ["-i", wm]
                    have_wm = True
            except Exception:
                have_lower = have_wm = False
        last = "0:v"
        if have_lower:
            filt.append("[0:v][1:v]overlay=x={}:y={}:enable='between(t,0.2,5)'[v1]"
                        .format(int(w * 0.04), int(h * 0.82)))
            last = "v1"
        if have_wm:
            wm_i = 2 if have_lower else 1
            filt.append("[{}][{}:v]overlay=x=W-w-{}:y=H-h-{}[v2]"
                        .format(last, wm_i, int(w * 0.025), int(h * 0.03)))
            last = "v2"
        # смуга прогресу: drawbox, ширина росте з t (патерн Shorts-прогресу)
        filt.append("[{}]drawbox=x=0:y=ih-6:w='iw*t/{:.3f}':h=6:"
                    "color=0x0A84FF@0.85:t=fill[vf]".format(last, max(dur, 1.0)))
        out = os.path.join(workdir, "_ov_out.mp4")
        run([ff, "-y", "-hide_banner", "-nostdin"] + inputs +
            ["-filter_complex", ";".join(filt), "-map", "[vf]",
             "-map", "0:a?", "-c:v", "libx264", "-crf", "20",
             "-preset", "veryfast", "-pix_fmt", "yuv420p",
             "-c:a", "copy", out], cwd=workdir)
        if os.path.isfile(out) and os.path.getsize(out) > 1024:
            os.replace(out, final)
            say("🏷️ Оверлеї: плашка-заголовок + водяний знак + смуга прогресу — на місці")
        else:
            say("⚠️ Оверлей-рендер не вдався — відео лишилось чистим (fail-open)")
        for p in ("_ov_lower.png", "_ov_wm.png"):
            try:
                os.remove(os.path.join(workdir, p))
            except OSError:
                pass
    except Exception as e:
        say("⚠️ Оверлеї не вийшли ({}), відео лишається як є".format(str(e)[:120]))


def write_edl(slots, workdir, say=None, fps=25):
    """📋 2.0: EDL-ЕКСПОРТ (CMX3600) — таймлайн компіляції фону: кожен
    фрагмент з тривалістю і позначкою джерела. Відкривається у DaVinci
    Resolve / Premiere (імпорт EDL) — перемонтюй, якщо хочеш інакше.
    Артефакт-тека: до manifest.json поруч. Fail-open."""
    try:
        if not slots:
            return

        def _tc(sec):
            fr = max(int(round(float(sec) * fps)), 0)
            return "{:02d}:{:02d}:{:02d}:{:02d}".format(
                fr // (3600 * fps), (fr // (60 * fps)) % 60,
                (fr // fps) % 60, fr % fps)
        lines = ["TITLE: videogen_timeline", "FCM: NON-DROP FRAME", ""]
        t = 0.0
        for i, (c, take) in enumerate(slots, 1):
            d = float(take or 0)
            lines.append("{:03d}  AX  V  C        {} {} {} {}".format(
                i, _tc(0), _tc(d), _tc(t), _tc(t + d)))
            lines.append("* FROM CLIP NAME: " + os.path.basename(str(c)))
            lines.append("")
            t += d
        with open(os.path.join(workdir, "timeline.edl"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        if say:
            say("📋 Таймлайн — timeline.edl ({} фрагментів, відкривається у Resolve)".format(len(slots)))
    except Exception:
        pass  # артефакт, ніколи не ламає генерацію


def write_manifest(info, workdir, say):
    """📋 v28: manifest.json — план і результат генерації у робочій папці:
    режим, тема або частини сценарію (текст, запит, посилання, тривалість),
    голос, розмір, стилі. Артефакт-тека: видно, з чого зібрано відео, і легко
    повторити той самий запуск. Fail-open: не вийшло — не важливо."""
    try:
        data = {"generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "app": "Генератор відео 2.0"}
        data.update(info or {})
        with open(os.path.join(workdir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        say("📋 Маніфест генерації — manifest.json")
    except Exception:
        pass  # 📋 v28: маніфест — артефакт, ніколи не ламає генерацію


def make_chapters(scenes, durs, workdir, say):
    """📑 v30: chapters.txt — розділи YouTube за частинами сценарію: мітки
    «0:00 Перші слова озвучки частини». Менше двох частин — розділи не потрібні;
    список дописується в кінець youtube-seo.txt. Fail-open: артефакт."""
    try:
        if not scenes or len(scenes) < 2:
            return
        lines, t = [], 0.0
        for i, (sc, d) in enumerate(zip(scenes, durs or [])):
            name = " ".join(str(sc.get("text") or "").split()[:6]) or "Частина {}".format(i + 1)
            sec = int(round(t))
            lines.append("{}:{:02d} {}".format(sec // 60, sec % 60, name))
            t += max(float(d or 0), 1.0)
        with open(os.path.join(workdir, "chapters.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        say("📑 Розділи YouTube — chapters.txt ({} частин)".format(len(lines)))
        try:
            with open(os.path.join(workdir, "youtube-seo.txt"), "a", encoding="utf-8") as f:
                f.write("\n\nРОЗДІЛИ (скопіюй у YouTube):\n" + "\n".join(lines) + "\n")
        except Exception:
            pass
    except Exception as e:
        say("⚠️ Розділи не зібрав: " + str(e)[:120])


def write_approval(info, workdir, say):
    """📝 v30: approval.txt — «перевір перед публікацією»: тривалість і розмір
    final.mp4, режим/голос, артефакти робочої папки (✓ є / — нема) і короткий
    чек-лист. Fail-open: артефакт, ніколи не ламає генерацію."""
    try:
        final = os.path.join(workdir, "final.mp4")
        try:
            dur = "{:.0f} с".format(audio_duration(final))
        except Exception:
            dur = "?"
        try:
            size = "{:.1f} МБ".format(os.path.getsize(final) / 1048576.0)
        except Exception:
            size = "?"
        lines = ["APPROVAL — перевір перед публікацією", ""]
        for k, v in (info or {}).items():
            lines.append("{}: {}".format(k, v))
        lines.append("Відео: final.mp4 — {}, {}".format(dur, size))
        lines.append("")
        lines.append("Артефакти:")
        for fn, label in (("youtube-seo.txt", "📈 SEO-пак"), ("chapters.txt", "📑 Розділи"),
                          ("credits.txt", "📄 Кредити"), ("credits.json", "📄 Кредити JSON"),
                          ("qc.txt", "🛡️ QC-звіт"), ("manifest.json", "📋 Маніфест")):
            mark = "✓" if os.path.exists(os.path.join(workdir, fn)) else "—"
            lines.append("  {} {} ({})".format(mark, label, fn))
        lines.append("")
        lines.append("Перед публікацією: 1) проглянь відео цілком; 2) назва/опис/теги —")
        lines.append("з youtube-seo.txt; 3) розділи — з chapters.txt; 4) кредити джерел —")
        lines.append("з credits.txt у опис; 5) обмеження розміру — 📦-копія поруч із final.mp4.")
        plat = (info or {}).get("платформа")  # 📺 v32: поради платформи (HandBrake-пресети)
        tips = {"Shorts": ["до 60 секунд", "вертикальний кадр 9:16",
                           "додай #shorts у назву або опис"],
                "YouTube": ["100 МБ-копія для швидкого завантаження; якість перемиє YouTube сам"],
                "Telegram": ["звичайний чат — до 50 МБ"]}
        if plat and plat in tips:
            lines.append("")
            lines.append("Платформа {}:".format(plat))
            for tip in tips[plat]:
                lines.append("  • " + tip)
        with open(os.path.join(workdir, "approval.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        say("📝 approval.txt — чек-лист перед публікацією")
    except Exception:
        pass


def make_srt(sentences, total, workdir):
    """Субтитри: пропорційно довжині речень."""
    def fmt(t):
        h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")
    weights = [len(s) for s in sentences]
    scale = total / sum(weights)
    lines, start = [], 0.0
    for s, w in zip(sentences, weights):
        end = min(start + w * scale, total)
        lines.append(f"{len(lines)+1}\n{fmt(start)} --> {fmt(end)}\n{s}\n")
        start = end
    with open(os.path.join(workdir, "sub.srt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def narration_for(query):
    q = query.strip().rstrip(".")
    return (
        f"Привіт! У цьому відео ми розглянемо тему: {q}. "
        f"{q} — це цікава й актуальна тема, тому проведемо короткий огляд ключових моментів, "
        f"які допоможуть краще її зрозуміти. "
        f"Ми познайомимося з основними поняттями, розберемо, чому це важливо, "
        f"та окреслимо, з чого варто почати, якщо ви хочете зануритися глибше. "
        f"Сподіваємося, це відео буде для вас корисним. "
        f"Дякуємо за перегляд і до нових зустрічей!"
    )


def score_hook(text, say):
    """🧲 Оцінка заголовка за 5 ознаками сильного хука.
    Компактна українська адаптація 21 формули з відкритого youtube-скіла
    (чиста логіка, без ключів і без інтернету)."""
    t = " ".join((text or "").split())
    if len(t) < 3:
        say("🧲 Спершу встав заголовок у поле запиту 🙂")
        return
    score, tips = 50, []
    if re.search(r"\d", t):
        score += 15
    else:
        tips.append("додай конкретне число — «3 способи», «за 7 днів», «+40%» (формула «Статистика»)")
    if re.search(r"(?iu)\b(ти|твій|твоє|твоя|ви|ваш|ваша|своє)\b", t):
        score += 12
    else:
        tips.append("звертайся до глядача («ти», «твій») — так утримують перші секунди")
    if re.search(r"(?iu)\b(як|чому|секрет|помилк|ніхто|найкращ|спосіб)\b", t):
        score += 13
    else:
        tips.append("додай інтригу або обіцянку: «як…», «чому…», «головна помилка в…»")
    if re.search(r"(?iu)\b(без|стоп|покроков|порад|заощад|навчис|зароб|швидк)\b", t):
        score += 10
    else:
        tips.append("покажи вигоду глядача: «…без досвіду», «…і заощадиш годину»")
    if len(t) > 80:
        score -= 12
        tips.append("заголовок довгий — скороти до 40–70 символів, лиш одну обіцянку")
    elif len(t) >= 15:
        score += 10
    else:
        tips.append("занадто коротко — додай, що саме отримає глядач")
    score = max(0, min(100, score))
    if score >= 80:
        verdict = "сильно! Такий заголовок кличе"
    elif score >= 60:
        verdict = "непогано, але є куди рости"
    else:
        verdict = "слабко — перероби за порадами нижче"
    say("🧲 Оцінка заголовка: {}/100 — {}".format(score, verdict))
    if tips:
        for tip in tips[:3]:
            say("🧲 💡 " + tip)
    else:
        say("🧲 💡 Всі п'ять ознак на місці — можна генерувати!")


def fetch_openverse_images(query, workdir, count=3):
    """Зображення з Openverse (openverse.org) — БЕЗ API-ключа, відкриті ліцензії."""
    try:
        r = requests.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query, "page_size": count},
            headers={"User-Agent": "VideoGenerator/1.0 (Windows)"},
            timeout=25)
        if r.status_code != 200:
            return None, "Openverse: HTTP {}".format(r.status_code)
        items = [it for it in r.json().get("results", []) if it.get("url")][:count]
        if not items:
            return None, "Openverse: нічого не знайшов за запитом"
        paths = []
        for i, it in enumerate(items):
            u = it["url"]
            p = os.path.join(workdir, "img{}.jpg".format(i))
            with requests.get(u, timeout=30, headers={"User-Agent": "VideoGenerator/1.0"}) as d:
                d.raise_for_status()
                with open(p, "wb") as out:
                    for chunk in d.iter_content(65536):
                        out.write(chunk)
            paths.append(p)
            append_credit(workdir, "🖼️ {} — {} — {} — {}".format(
                (it.get("title") or "?")[:60], it.get("license") or "?",
                it.get("creator") or "?", it.get("foreign_landing_url") or ""))
        return (paths, None) if paths else (None, "Openverse: зображення не завантажились")
    except Exception as e:
        return None, "Openverse: {}".format(e)


def clip_cache_load():
    """📦 v22: індекс кеш-банку: url → метадані + шлях до файла в кеші."""
    try:
        with open(CLIP_CACHE_INDEX, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def clip_cache_save(idx):
    try:
        os.makedirs(CLIP_CACHE_DIR, exist_ok=True)
        with open(CLIP_CACHE_INDEX, "w", encoding="utf-8") as f:
            json.dump(idx, f, ensure_ascii=False)
    except OSError:
        pass


def clip_cache_get(idx, url):
    """Влучення в кеш: файл на місці і не порожній → шлях; битий запис вилучається."""
    ent = idx.get(url) or {}
    p = ent.get("path") or ""
    if p and os.path.exists(p) and os.path.getsize(p) > 0:
        return p
    idx.pop(url, None)
    return None


def clip_cache_put(idx, url, local_path, src, meta):
    """Реєструє щойно скачаний кліп у кеш-банку (копія + метадані за мотивами CDAF)."""
    try:
        os.makedirs(CLIP_CACHE_DIR, exist_ok=True)
        h = hashlib.md5(url.encode("utf-8")).hexdigest()
        dst = os.path.join(CLIP_CACHE_DIR, h + os.path.splitext(local_path)[1])
        if not os.path.exists(dst):
            shutil.copyfile(local_path, dst)
        tags = []
        for t in (meta.get("tags") or [])[:10]:
            if isinstance(t, dict):
                nm = str(t.get("name") or t.get("label") or "")[:30]
                if nm:
                    tags.append(nm)
            elif t:
                tags.append(str(t)[:30])
        idx[url] = {"path": dst, "bytes": os.path.getsize(dst), "src": src,
                    "query": (meta.get("query") or "")[:120],
                    "title": (meta.get("title") or "")[:120],
                    "license": (meta.get("license") or "")[:60],
                    "creator": (meta.get("creator") or "")[:80],
                    "duration": meta.get("duration") or 0.0,
                    "tags": tags, "saved": time.time()}
        clip_cache_evict(idx)
        clip_cache_save(idx)
    except OSError:
        pass


def clip_cache_evict(idx):
    """Кеш-банк не більший за ліміт: першими видаляються найдавніші кліпи."""
    total = 0
    for ent in idx.values():
        try:
            total += os.path.getsize((ent or {}).get("path") or "")
        except OSError:
            pass
    if total <= CLIP_CACHE_MAX_BYTES:
        return
    for url, ent in sorted(idx.items(), key=lambda kv: (kv[1] or {}).get("saved") or 0):
        if total <= CLIP_CACHE_MAX_BYTES:
            break
        try:
            total -= os.path.getsize(ent.get("path") or "")
            os.remove(ent["path"])
        except OSError:
            pass
        idx.pop(url, None)


def fetch_openverse_videos(query, workdir, need=30.0, max_clips=6):
    """Відео-кліпи з Openverse — відкриті ліцензії (Creative Commons), БЕЗ API-ключа.
    Завантажує кліпи, поки не набере ~need секунд матеріалу."""
    try:
        r = requests.get(
            "https://api.openverse.org/v1/videos/",
            params={"q": query, "page_size": 20},
            headers={"User-Agent": "VideoGenerator/1.1 (Windows; video-from-query)"},
            timeout=25)
        if r.status_code != 200:
            return None, "Openverse videos: HTTP {}".format(r.status_code)
        res = r.json().get("results", [])
        # duration у мілісекундах; беремо придатні кліпи
        good = [it for it in res
                if it.get("url")
                and 3000 <= (it.get("duration") or 0) <= 300000
                and (it.get("width") or 0) >= 480]
        if not good:
            return None, "Openverse videos: підходящих кліпів немає за запитом"
        paths, total, cached = [], 0.0, 0
        cache_idx = clip_cache_load()   # 📦 v22: кеш-банк кліпів
        for i, it in enumerate(good):
            if len(paths) >= max_clips or total >= need:
                break
            ext = os.path.splitext(it["url"].split("?")[0])[1].lstrip(".") or "mp4"
            p = os.path.join(workdir, "clip{}.{}".format(i, ext))
            credit = "🎬 {} — {} — {} — {}".format(
                (it.get("title") or "?")[:60], it.get("license") or "?",
                it.get("creator") or "?", it.get("foreign_landing_url") or "")
            cp = clip_cache_get(cache_idx, it["url"])
            if cp:
                try:
                    shutil.copyfile(cp, p)
                    paths.append(p)
                    total += (it.get("duration") or 0) / 1000.0
                    cached += 1
                    append_credit(workdir, credit)
                    continue
                except OSError:
                    pass
            try:
                with requests.get(it["url"], stream=True, timeout=90,
                                  headers={"User-Agent": "VideoGenerator/1.1"}) as d:
                    d.raise_for_status()
                    size = int(d.headers.get("Content-Length") or 0)
                    if size > 120 * 1024 * 1024:
                        continue  # пропускаємо надто великі файли
                    with open(p, "wb") as out:
                        for chunk in d.iter_content(1 << 16):
                            out.write(chunk)
                paths.append(p)
                total += (it.get("duration") or 0) / 1000.0
                clip_cache_put(cache_idx, it["url"], p, "openverse", {
                    "query": query, "title": it.get("title") or "",
                    "license": it.get("license") or "",
                    "creator": it.get("creator") or "",
                    "duration": (it.get("duration") or 0) / 1000.0,
                    "tags": it.get("tags") or []})
                append_credit(workdir, credit)
            except Exception:
                try:
                    os.remove(p)
                except OSError:
                    pass
        if cached:
            append_credit(workdir, "📦 {} кліп(ів) з локального кешу (без трафіку)".format(cached))
        return (paths, None) if paths else (None, "Openverse videos: кліпи не завантажились")
    except Exception as e:
        return None, "Openverse videos: {}".format(e)


def append_credit(workdir, line):
    """Збирає credits.txt — автори та ліцензії матеріалів у робочій папці."""
    try:
        with open(os.path.join(workdir, "credits.txt"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def fetch_wikimedia_images(query, workdir, count=3):
    """Зображення з Wikimedia Commons — БЕЗ ключа і БЕЗ жорстких лімітів.
    Дублює Openverse: якщо той обмежив запити, фото все одно знайдуться."""
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={"action": "query", "format": "json",
                    "generator": "search", "gsrsearch": "filetype:bitmap " + query,
                    "gsrnamespace": "6", "gsrlimit": str(count * 3),
                    "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1600"},
            headers={"User-Agent": UA_STRING, "Api-User-Agent": UA_STRING}, timeout=25)
        if r.status_code != 200:
            return None, "Wikimedia: HTTP {}".format(r.status_code)
        pages = ((r.json().get("query") or {}).get("pages") or {})
        items = sorted(pages.values(), key=lambda p: p.get("index", 999))
        paths = []
        for p in items:
            if len(paths) >= count:
                break
            ii = (p.get("imageinfo") or [{}])[0]
            if (ii.get("width") or 0) < 640 or ii.get("mime") not in ("image/jpeg", "image/png", "image/webp"):
                continue
            u = ii.get("thumburl") or ii.get("url")
            if not u:
                continue
            path = os.path.join(workdir, "wimg{}.jpg".format(len(paths)))
            try:
                with requests.get(u, timeout=60, headers={"User-Agent": UA_STRING}) as d:
                    d.raise_for_status()
                    with open(path, "wb") as out:
                        for chunk in d.iter_content(65536):
                            out.write(chunk)
            except Exception:
                continue
            paths.append(path)
            meta = ii.get("extmetadata") or {}
            author = re.sub(r"<[^>]+>", "", (meta.get("Artist") or {}).get("value", "?") or "?").strip()[:80]
            page_url = "https://commons.wikimedia.org/wiki/" + (p.get("title") or "").replace(" ", "_")
            append_credit(workdir, "🖼️ {} — {} — {} — {}".format(
                (p.get("title") or "?")[:60],
                (meta.get("LicenseShortName") or {}).get("value", "?"),
                author, page_url))
        return (paths, None) if paths else (None, "Wikimedia: нічого не знайшов за запитом")
    except Exception as e:
        return None, "Wikimedia: {}".format(e)


def fetch_wikimedia_videos(query, workdir, need=30.0, max_clips=6):
    """Відео-кліпи з Wikimedia Commons — БЕЗ ключа. Беремо готові легкі webm-транскоди
    ≤720p (прийом з відкритого проєкту clipforge): оригінали .ogv важкі та гірше
    читаються ffmpeg. Без webm-варіанта кліп пропускаємо."""
    def pick_webm(vi):
        cands = []
        for d in vi.get("derivatives") or []:
            src = d.get("src") or ""
            info = "{} {}".format(d.get("transcodekey") or "", d.get("type") or "").lower()
            if src and "webm" in info:
                h = d.get("height") or 0
                m = re.search(r"(\d+)p", d.get("transcodekey") or "")
                if not h and m:
                    h = int(m.group(1))
                cands.append((h, src))
        ok = [c for c in cands if 0 < c[0] <= 720]
        if ok:
            return max(ok, key=lambda c: c[0])[1]
        if cands:
            return min(cands, key=lambda c: c[0])[1]
        u = vi.get("url") or ""
        return u if u.lower().split("?")[0].endswith(".webm") else None

    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={"action": "query", "format": "json",
                    "generator": "search", "gsrsearch": "filetype:video " + query,
                    "gsrnamespace": "6", "gsrlimit": "20",
                    "prop": "videoinfo",
                    "viprop": "url|size|mime|extmetadata|duration|derivatives",
                    "viurlwidth": "640"},
            headers={"User-Agent": UA_STRING, "Api-User-Agent": UA_STRING}, timeout=25)
        if r.status_code != 200:
            return None, "Wikimedia videos: HTTP {}".format(r.status_code)
        pages = ((r.json().get("query") or {}).get("pages") or {})
        items = sorted(pages.values(), key=lambda p: p.get("index", 999))
        paths = []
        cache_idx = clip_cache_load()   # 📦 v22: кеш-банк кліпів
        for p in items:
            if len(paths) >= max_clips:
                break
            vi = (p.get("videoinfo") or [{}])[0]
            src = pick_webm(vi)
            if not src:
                continue
            d = vi.get("duration") or 0
            if d and not 3 <= d <= 300:
                continue
            path = os.path.join(workdir, "wclip{}.webm".format(len(paths)))
            cp = clip_cache_get(cache_idx, src)
            if cp:
                try:
                    shutil.copyfile(cp, path)
                    paths.append(path)
                    meta = vi.get("extmetadata") or {}
                    author = re.sub(r"<[^>]+>", "", (meta.get("Artist") or {}).get("value", "?") or "?").strip()[:80]
                    page_url = "https://commons.wikimedia.org/wiki/" + (p.get("title") or "").replace(" ", "_")
                    append_credit(workdir, "🎬 {} — {} — {} — {}".format(
                        (p.get("title") or "?")[:60],
                        (meta.get("LicenseShortName") or {}).get("value", "?"),
                        author, page_url))
                    continue
                except OSError:
                    pass
            try:
                with requests.get(src, stream=True, timeout=120, headers={"User-Agent": UA_STRING}) as resp:
                    resp.raise_for_status()
                    size = int(resp.headers.get("Content-Length") or 0)
                    if size > 120 * 1024 * 1024:
                        continue
                    with open(path, "wb") as out:
                        for chunk in resp.iter_content(1 << 16):
                            out.write(chunk)
                paths.append(path)
                clip_cache_put(cache_idx, src, path, "wikimedia", {
                    "query": query, "title": p.get("title") or "",
                    "license": ((vi.get("extmetadata") or {}).get("LicenseShortName") or {}).get("value", ""),
                    "duration": d})
                meta = vi.get("extmetadata") or {}
                author = re.sub(r"<[^>]+>", "", (meta.get("Artist") or {}).get("value", "?") or "?").strip()[:80]
                page_url = "https://commons.wikimedia.org/wiki/" + (p.get("title") or "").replace(" ", "_")
                append_credit(workdir, "🎬 {} — {} — {} — {}".format(
                    (p.get("title") or "?")[:60],
                    (meta.get("LicenseShortName") or {}).get("value", "?"),
                    author, page_url))
            except Exception:
                try:
                    os.remove(path)
                except OSError:
                    pass
        return (paths, None) if paths else (None, "Wikimedia videos: кліпів немає/не завантажились")
    except Exception as e:
        return None, "Wikimedia videos: {}".format(e)


def beat_grid(music_path, need_sec):
    """🥁 v23: битова сітка музики (патерн Director Mode з AI-студій):
    PCM 8 кГц моно → енергетична огибаюча (кадр 32 мс) → автокореляція
    онсетів → період (57–200 BPM, нормування у 70–170) + фаза кращого біта.
    Повертає (bpm, [t0, t1, …]) або None, якщо ритм невиразний чи помилка."""
    try:
        r = subprocess.run([ffmpeg_path(), "-hide_banner", "-nostdin",
                            "-i", music_path, "-f", "s16le", "-ac", "1",
                            "-ar", "8000", "-"], capture_output=True, timeout=180)
        if r.returncode != 0 or len(r.stdout) < 32000:
            return None
        arr = array.array("h")
        arr.frombytes(r.stdout[:len(r.stdout) // 2 * 2])
        hop, env = 256, []
        for pos in range(0, len(arr) - hop, hop):
            seg = arr[pos:pos + hop]
            env.append((sum(x * x for x in seg) / hop) ** 0.5)
        if len(env) < 100:
            return None
        flux = [0.0]
        for i in range(1, len(env)):
            flux.append(max(0.0, env[i] - env[i - 1]))
        peak = max(flux) or 1.0
        flux = [f / peak for f in flux]
        fps = 8000.0 / hop
        lo, hi = max(2, int(0.30 * fps)), int(1.05 * fps)  # періоди 0.30–1.05 с
        scores = {}
        for lag in range(lo, hi + 1):
            s = 0.0
            for i in range(len(flux) - lag):
                s += flux[i] * flux[i + lag]
            scores[lag] = s / max(1, len(flux) - lag)
        best_lag = max(scores, key=scores.get)
        mean_s = sum(scores.values()) / len(scores)
        if scores[best_lag] < 2.5 * max(mean_s, 1e-9):
            return None  # ритм невиразний (ембієнт/шум) — розрізати по битах нечесно
        period = best_lag / fps
        bpm = 60.0 / period
        if bpm < 70.0:
            period /= 2.0
            bpm *= 2.0
        elif bpm > 170.0:
            period *= 2.0
            bpm /= 2.0
        step = max(1, int(round(period * fps)))
        best_off, best_sc = 0, -1.0
        for off in range(min(step, len(flux))):
            sc = 0.0
            for i in range(off, len(flux), step):
                sc += flux[i]
            if sc > best_sc:
                best_off, best_sc = off, sc
        beats, t = [], best_off / fps
        while t < need_sec + 10.0:
            if t >= 0.0:
                beats.append(t)
            t += period
        if len(beats) < 4:
            return None
        return (bpm, beats)
    except Exception:
        return None


def xfade_join(segs, takes, workdir, trans, cross=0.5):
    """🎞 v14: склеює нормалізовані фрагменти з плавним переходом (xfade ffmpeg) —
    той самий «Наплив/Затемнення», що й у CapCut. Фрагменти вже однакові за
    розміром/fps, тож xfade проходить без підготовки."""
    ff = ffmpeg_path()
    bg = os.path.join(workdir, "bg.mp4")
    inputs = []
    for s in segs:
        inputs += ["-i", s]
    parts = []
    prev = "[0:v]"
    off = max(float(takes[0]) - cross, 0.0)
    for i in range(1, len(segs)):
        last = (i == len(segs) - 1)
        out = "[vout]" if last else "[vx{}]".format(i)
        parts.append("{}[{}:v]xfade=transition={}:duration={}:offset={:.2f}{}"
                     .format(prev, i, trans, cross, off, out))
        prev = out
        off += max(float(takes[i]) - cross, 0.0)
    cmd = [ff, "-y", "-hide_banner", "-nostdin", *inputs,
           "-filter_complex", ";".join(parts), "-map", "[vout]",
           "-c:v", "libx264", "-crf", "22", "-preset", "veryfast",
           "-pix_fmt", "yuv420p", "-an", bg]
    run(cmd, cwd=workdir)
    return bg


def build_bg_from_clips(clips, dur, w, h, workdir, transition="", no_faces=False, say=None, beats=None):
    """Справжній відеоряд: кожен кліп обрізається до свого слота, нормалізується
    і склеюється. Якщо матеріалу менше за озвучку — кліпи йдуть по колу.
    v14: transition ≠ «» — між фрагментами плавний перехід (xfade).
    v15: no_faces=True — спершу збираю з кліпів фрагменти без обличчя (OpenCV)."""
    ff = ffmpeg_path()
    w, h = int(w), int(h)
    if no_faces and clips:  # 🚫 v15: пул фрагментів без обличчя
        try:
            pool = noface_pool(clips, need=max(2, int(dur / 8) + 2),
                               workdir=workdir, say=say)
            if pool:
                clips = pool
        except Exception as e:
            if say:
                say("⚠️ Фільтр обличчя не вийшов ({}), монтую кліпи як є".format(str(e)[:120]))
    usable = []
    for c in clips:
        try:
            d = audio_duration(c)
            if d and d >= 1.0:
                usable.append((c, d))
        except Exception:
            pass
    if not usable:
        raise RuntimeError("жоден кліп не читається ffmpeg")
    per = max(dur / len(usable), 2.0)
    slots, i = [], 0
    while sum(s[1] for s in slots) < dur - 0.5:
        c, d = usable[i % len(usable)]
        slots.append((c, min(per, d)))
        i += 1
    if transition:  # v14: переходи «з'їдають» по 0.5 с на стик — додаємо матеріал
        guard = 0
        while sum(s[1] for s in slots) - 0.5 * max(len(slots) - 1, 0) < dur - 0.5 and guard < 200:
            c, d = usable[i % len(usable)]
            slots.append((c, min(per, d)))
            i += 1
            guard += 1
    if beats and len(slots) > 1:  # 🥁 v23: межі слотів — на найближчі бити музики
        try:
            dmap = {c: d for c, d in usable}
            bounds, t = [], 0.0
            for _, take in slots:
                t += take
                bounds.append(t)
            nb = []
            for b in bounds[:-1]:
                bb = min(beats, key=lambda x: abs(x - b))
                nb.append(bb if abs(bb - b) < 0.6 else b)
            nb.append(bounds[-1])
            slots2, prev = [], 0.0
            for j, b in enumerate(nb):
                take = max(b - prev, 0.8)
                take = min(take, dmap.get(slots[j][0], take))
                slots2.append((slots[j][0], take))
                prev = b
            slots = slots2
            if say:
                say("🥁 Зміни кадрів підігнано під бити музики")
        except Exception:
            pass  # beat-sync не вийшов — слоти лишаються рівними, це не помилка
    segs, takes = [], []
    for j, (c, take) in enumerate(slots):
        seg = os.path.join(workdir, "vseg{}.mp4".format(j))
        run([ff, "-y", "-hide_banner", "-nostdin", "-i", c, "-t", "{:.2f}".format(take),
             "-an", "-vf",
             ("scale={}:{}:force_original_aspect_ratio=increase,crop={}:{},"
              "fps=25,setsar=1,format=yuv420p").format(w, h, w, h),
             "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", seg])
        segs.append(seg)
        takes.append(take)
    write_edl(slots, workdir, say)  # 📋 2.0: таймлайн компіляції — у EDL (Resolve)
    if transition and len(segs) >= 2:  # v14: спершу пробуємо з переходами
        try:
            return xfade_join(segs, takes, workdir, TRANSITIONS.get(transition) or transition)
        except Exception:
            pass  # не вийшло — склеюємо різко, відео все одно збереться
    lst = os.path.join(workdir, "vlist.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for s in segs:
            f.write("file '{}'\n".format(s))
    bg = os.path.join(workdir, "bg.mp4")
    run([ff, "-y", "-hide_banner", "-nostdin", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", bg])
    return bg


def build_bg_from_images(images, dur, w, h, workdir):
    """Слайд-шоу з ефектом Ken Burns (zoompan) з кількох зображень."""
    ff = ffmpeg_path()
    segs = []
    per = max(dur / max(len(images), 1), 1.0)
    for i, img in enumerate(images):
        seg = os.path.join(workdir, "seg{}.mp4".format(i))
        frames = int(per * 25) + 1
        run([ff, "-y", "-hide_banner", "-nostdin", "-i", img,
             "-vf", ("scale={}:{}:force_original_aspect_ratio=increase,crop={}:{},"
                     "zoompan=z='min(zoom+0.0006,1.25)':"
                     "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={}:fps=25,"
                     "format=yuv420p").format(w, h, w, h, frames),
             "-t", "{:.2f}".format(per),
             "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", seg])
        segs.append(seg)
    lst = os.path.join(workdir, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for s in segs:
            f.write("file '{}'\n".format(s))
    bg = os.path.join(workdir, "bg.mp4")
    run([ff, "-y", "-hide_banner", "-nostdin", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", bg])
    return bg


def ensure_ytdlp(say):
    """Один раз завантажує офіційний yt-dlp.exe з GitHub (без жодних ключів)."""
    if os.path.exists(YTDLP_EXE):
        return YTDLP_EXE
    os.makedirs(TOOLS_DIR, exist_ok=True)
    say("⬇️ Перший раз: завантажую yt-dlp (офіційний завантажувач з GitHub, ~18 МБ)…")
    with requests.get(YTDLP_URL, stream=True, timeout=90,
                      headers={"User-Agent": UA_STRING}) as r, \
         open(YTDLP_EXE + ".part", "wb") as f:
        r.raise_for_status()
        for chunk in r.iter_content(1 << 16):
            f.write(chunk)
    os.replace(YTDLP_EXE + ".part", YTDLP_EXE)
    say("✅ yt-dlp встановлено")
    return YTDLP_EXE


def yt_search(query, limit, say):
    """Пошук на YouTube БЕЗ API-ключа (через ytsearch у yt-dlp). Повертає (список, помилка)."""
    exe = ensure_ytdlp(say)
    try:
        proc = subprocess.run([exe, "ytsearch{}:{}".format(limit, query),
                               "--flat-playlist", "--dump-json",
                               "--ignore-config", "--no-warnings"],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=90)
    except Exception as e:
        return [], "yt-dlp не запустився: " + str(e)[:150]
    results = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
        except Exception:
            continue
        if not j.get("id"):
            continue
        results.append({
            "url": "https://www.youtube.com/watch?v=" + str(j.get("id")),
            "title": str(j.get("title") or "")[:120],
            "dur": int(j.get("duration") or 0),
            "channel": str(j.get("channel") or j.get("uploader") or "")[:60],
            "views": int(j.get("view_count") or 0),
        })
    if not results:
        return [], "нічого не знайшов"
    return results, ""


def youtube_download(url, outdir, height, say, fixed_name=None, max_sec=0):
    """Завантажує відео з YouTube через yt-dlp. Повертає шлях до готового файлу."""
    os.makedirs(outdir, exist_ok=True)
    exe = ensure_ytdlp(say)
    if fixed_name:
        out_tmpl = os.path.join(outdir, fixed_name + ".%(ext)s")
    else:
        out_tmpl = os.path.join(outdir, "%(title).100B.%(ext)s")
    sb = []  # ⏭️ v27: SponsorBlock — вирізаю спонсорські вставки з фону, якщо yt-dlp уміє
    try:
        r = subprocess.run([exe, "--sponsorblock-remove", "sponsor", "--version"],
                           capture_output=True, text=True, timeout=20)
        if r.returncode == 0:
            sb = ["--sponsorblock-remove", "sponsor,selfpromo"]
        else:
            say("ℹ️ SponsorBlock не підтримується збіркою yt-dlp — фон без вирізання")
    except Exception:
        sb = []
    cmd = [exe, "--no-playlist", "--no-warnings", "--newline",
           "-f", "bv*[ext=mp4][height<={0}]+ba[ext=m4a]/b[ext=mp4][height<={0}]/b[height<={0}]".format(height),
           "--merge-output-format", "mp4",
           "--ffmpeg-location", os.path.dirname(os.path.abspath(ffmpeg_path())),
           "-o", out_tmpl, "--no-simulate", "--print", "after_move:filepath", *sb, url]
    if max_sec:
        cmd += ["--download-sections", "*0:00-{}:00".format(int(max_sec) // 60)]
    say("▶️ Завантажую відео з YouTube…")
    proc = subprocess.Popen(cmd, cwd=outdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, encoding="utf-8", errors="replace")
    final_path = None
    err = None
    last_pct = -100.0
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        if line.startswith("ERROR"):
            err = line[:250]
            break
        if "[download]" in line and "%" in line:
            try:
                pct = float(line.split("%")[0].split()[-1].replace(",", "."))
                if pct - last_pct >= 25 or pct >= 99.9:
                    last_pct = pct
                    say("⬇️ " + str(int(pct)) + "%")
            except ValueError:
                pass
        elif line.lower().endswith((".mp4", ".mkv", ".webm")) and os.path.isabs(line):
            final_path = line
    if err:
        proc.terminate()
        raise RuntimeError("yt-dlp: " + err)
    code = proc.wait()
    if code != 0 or not final_path:
        raise RuntimeError("yt-dlp не зміг завантажити відео (код {}). Перевір посилання.".format(code))
    append_credit(outdir, "🎬 {} — фонове відео (права належать автору каналу) — YouTube-канал — {}".format(os.path.basename(final_path), url))
    return final_path


def has_audio(path):
    """Чи є у файлі звукова доріжка (розбір виводу ffmpeg -i)."""
    r = subprocess.run([ffmpeg_path(), "-hide_banner", "-i", path], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return "Audio: " in (r.stderr or "")


def metadata_snapshot(path):
    """🧬 v33: знімок метаданих відео через ffmpeg -i (без ffprobe-залежностей):
    тривалість + теги контейнера/потоків (title, creation_time, encoder, location,
    камера тощо). Fail-open: будь-що не так — порожній словник."""
    try:
        pr = subprocess.run([ffmpeg_path(), "-hide_banner", "-i", path],
                            capture_output=True, text=True,
                            encoding="utf-8", errors="ignore", timeout=60)
        log = pr.stderr or ""
        out = {}
        m = re.search(r"Duration:\s*(\d+:\d+:\d+\.\d+)", log)
        if m:
            out["duration"] = m.group(1)
        for key, val in re.findall(
                r"^\s*(title|artist|album|comment|encoder|creation_time|"
                r"location|make|model|software|handler_name|composer)\s*:\s*(.*?)\s*$",
                log, re.M):
            out[key] = val
        return out
    except Exception:
        return {}


def ffmpeg_run_progress(cmd, total, say, tag, every=6):
    """⏱ v34: запуск ffmpeg з -progress pipe:1 і ETA у журнал:
    «⏱ Глибоко 34% • 1.2x • лишилось ~1 хв 40 с». total — тривалість входу
    у секундах (0 = прогресу не показувати). Fail-open: все зламалось —
    тихо переходжу на звичайний запуск. Повертає returncode."""
    real = list(cmd[:-1]) + ["-progress", "pipe:1", "-nostats", cmd[-1]]
    try:
        pr = subprocess.Popen(real, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              text=True, encoding="utf-8", errors="ignore")
        out_us, speed, last = 0.0, 1.0, 0.0
        for line in pr.stdout:
            line = line.strip()
            if line.startswith("out_time_us="):
                try:
                    out_us = float(line.split("=")[1]) / 1000000.0
                except Exception:
                    pass
            elif line.startswith("speed="):
                m = re.search(r"([\d.]+)x", line)
                if m:
                    speed = max(0.01, float(m.group(1)))
            now = time.time()
            if total and total > 0 and now - last >= every:
                last = now
                done = min(100.0, 100.0 * out_us / total)
                left = max(0.0, (total - out_us) / speed)
                say("⏱ {} {:.0f}% • швидкість {:.1f}x • лишилось ~{} хв {} с".format(
                    tag, done, speed, int(left // 60), int(left % 60)))
        pr.wait()
        return pr.returncode
    except Exception:
        try:
            prr = subprocess.run(list(cmd), capture_output=True, text=True,
                                 encoding="utf-8", errors="ignore", timeout=7200)
            return prr.returncode
        except Exception:
            return 1


def scrub_metadata(path, deep, say, out_path=None):
    """🧬 v33: змінити метадані відео до невпізнаваності.
    Швидко: remux (-c copy) — випалює ВСІ теги, розділи, XMP-згадки і пише
    нову випадкову creation_time; секунди, якість не чіпається.
    Глибоко: + перекодування h264/aac з -fflags +bitexact — стирає ще й
    відбитки кодека/статистику GOP; повільніше, якість ~crf 18; ⏱ v34: з ETA-прогресом.
    Вихідний файл НІКОЛИ не змінюється: результат = <ім'я>_meta.mp4 поруч.
    v34: out_path — перезаписати саме туда (наприклад, final.mp4 у конвеєрі):
    пишу у тимчасовий .part-файл і атомарно os.replace — фінал ніколи не
    буває «напівбитим»."""
    ff = ffmpeg_path()
    base = os.path.splitext(path)[0]
    inplace = out_path is not None  # 🧹 v34: перезапис цільового файлу (конвеєр)
    tmp = None
    if inplace:
        out = out_path
        tmp = out + ".part.mp4"
        real_out = tmp
    else:
        out = base + "_meta.mp4"
        n = 1
        while os.path.exists(out):
            out = "{}_meta_{}.mp4".format(base, n)
            n += 1
        real_out = out
    rnd = random.Random()
    fake_time = "{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.000000Z".format(
        rnd.randint(2016, 2025), rnd.randint(1, 12), rnd.randint(1, 28),
        rnd.randint(0, 23), rnd.randint(0, 59), rnd.randint(0, 59))
    cmd = [ff, "-y", "-hide_banner", "-nostdin", "-i", path,
           "-map_metadata", "-1", "-map_chapters", "-1",
           "-metadata", "creation_time=" + fake_time,
           "-metadata", "title=", "-metadata", "comment=",
           "-fflags", "+bitexact", "-movflags", "+faststart"]
    if deep:
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k"]
    else:
        cmd += ["-c", "copy"]
    say("🧬 Переписую метадані" +
        (" (глибоко, з перекодуванням)…" if deep else " (швидко, без перекодування)…"))
    prerr = ""
    if deep:
        try:
            total = audio_duration(path)
        except Exception:
            total = 0
        rc = ffmpeg_run_progress(cmd + [real_out], total, say, "🧬 Глибоко", every=6)
    else:
        pr = subprocess.run(cmd + [real_out], capture_output=True, text=True,
                            encoding="utf-8", errors="ignore", timeout=7200)
        rc = pr.returncode
        prerr = pr.stderr or ""
    if rc != 0 or not os.path.isfile(real_out) or os.path.getsize(real_out) < 1024:
        if os.path.isfile(real_out):
            os.remove(real_out)
        raise RuntimeError((prerr or "")[-400:] or "ffmpeg не дав файл")
    if inplace:
        os.replace(real_out, out)  # атомарно: ціль ніколи не лишається битою
    return out


def upscale_4k(path, say):
    """📈 v34: апскейл фіналу до 4К (3840×2160 / 2160×3840 для вертикальних).
    Чесно: нових деталей не додає (lanczos ×2 + легке шевко) — але YouTube
    кодує 4К-завантаження вищим бітрейтом → після стиснення YouTube картинка
    виглядає краще. Апаратний кодек, якщо є GPU. ⏱ ETA у журнал.
    Fail-open: не вийшло / вихід уже 4К — повертаю None, фінал лишається."""
    if not os.path.isfile(path):
        return None
    try:
        pr = subprocess.run([ffmpeg_path(), "-hide_banner", "-i", path],
                            capture_output=True, text=True,
                            encoding="utf-8", errors="ignore", timeout=60)
        m = re.search(r",\s(\d{2,5})x(\d{2,5})[\s,]", pr.stderr or "")
        if not m:
            return None
        w, h = int(m.group(1)), int(m.group(2))
    except Exception:
        return None
    if max(w, h) >= 3840 or min(w, h) < 480:
        say("📈 Апскейл не потрібен: роздільність {}x{}".format(w, h))
        return None
    out = os.path.splitext(path)[0] + "_4k.mp4"
    vf = "scale=3840:-2:flags=lanczos,unsharp=5:5:0.35" if w >= h else \
         "scale=-2:3840:flags=lanczos,unsharp=5:5:0.35"
    enc = best_video_encoder_args()
    q = ["-crf", "18"] if enc[1] == "libx264" else []
    cmd = [ffmpeg_path(), "-y", "-hide_banner", "-nostdin", "-i", path,
           "-vf", vf, *enc, *q, "-pix_fmt", "yuv420p", "-c:a", "copy",
           "-movflags", "+faststart", out]
    try:
        total = audio_duration(path)
    except Exception:
        total = 0
    rc = ffmpeg_run_progress(cmd, total, say, "📈 4К", every=6)
    if rc != 0 or not os.path.isfile(out) or os.path.getsize(out) < 1024:
        if os.path.isfile(out):
            os.remove(out)
        raise RuntimeError("4К-рендер не вдався")
    return out


def merge_videos(files, say):
    """Компіляція відеоряду: зшиває кілька відео в одне (720p, звук зберігається,
    файлам без звуку тиха доріжка додається автоматично)."""
    outdir = os.path.join(MERGE_OUT_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(outdir, exist_ok=True)
    ff = ffmpeg_path()
    vf = ("scale=1280:720:force_original_aspect_ratio=decrease,"
          "pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30")
    parts = []
    for i, src in enumerate(files):
        part = os.path.join(outdir, "part{:03d}.mp4".format(i))
        say("🎞 Обробляю {}/{}: {}".format(i + 1, len(files), os.path.basename(src)))
        if has_audio(src):
            cmd = [ff, "-y", "-hide_banner", "-nostdin", "-i", src,
                   "-vf", vf,
                   "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                   "-ar", "44100", "-ac", "2", part]
        else:
            cmd = [ff, "-y", "-hide_banner", "-nostdin", "-i", src,
                   "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                   "-vf", vf, "-map", "0:v", "-map", "1:a", "-shortest",
                   "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", part]
        run(cmd, cwd=outdir)
        parts.append(part)
    lst = os.path.join(outdir, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in parts:
            f.write("file '{}'\n".format(p.replace("\\", "/").replace("'", "'\\''")))
    out = os.path.join(outdir, "final.mp4")
    say("🎞 Зшиваю {} відео в одне…".format(len(parts)))
    run([ff, "-y", "-hide_banner", "-nostdin", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", out], cwd=outdir)
    return out


def _tts_chunks(text, limit=500):
    """🎚 v30: edge-tts обриває довгі тексти — ріжу на шматки по реченнях
    (до limit символів), наддовге речення — по словах. Список шматків."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= limit:
        return [text]
    parts, cur = [], ""
    for sent in re.split(r"(?<=[.!?…])\s+", text):
        if len(sent) > limit:  # наддовге речення — по словах
            wcur = ""
            for w in sent.split():
                if wcur and len(wcur) + 1 + len(w) > limit:
                    parts.append(wcur)
                    wcur = w
                else:
                    wcur = (wcur + " " + w).strip()
            if wcur:
                parts.append(wcur)
        elif cur and len(cur) + 1 + len(sent) > limit:
            parts.append(cur)
            cur = sent
        else:
            cur = (cur + " " + sent).strip()
    if cur:
        parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def _rm_parts(files):
    """🗑 v30: тихо прибрати тимчасові шматки озвучки (якщо лишились)."""
    for q in files:
        try:
            os.remove(q)
        except OSError:
            pass


def _tts_words(chunk, voice, out_mp3, rate_pct=0):
    """🎤 v30: один шматок edge-tts — аудіо у файл і мітки слів (WordBoundary,
    час у секундах). Не вийшло або без метрик — None."""
    words, audio = [], bytearray()
    try:
        async def _collect():
            cm = edge_tts.Communicate(chunk, voice, rate="{:+d}%".format(int(rate_pct or 0)))
            async for c in cm.stream():
                if c["type"] == "audio":
                    audio.extend(c["data"])
                elif c["type"] == "WordBoundary":
                    words.append((c.get("text", ""),
                                  c.get("offset", 0) / 1e7,
                                  (c.get("offset", 0) + c.get("duration", 0)) / 1e7))
        asyncio.run(_collect())
    except Exception:
        return None
    if not words or len(audio) < 500:
        return None
    try:
        with open(out_mp3, "wb") as f:
            f.write(bytes(audio))
        if os.path.getsize(out_mp3) < 500:
            return None
    except Exception:
        return None
    return words


def tts_save(text, voice, out_mp3, say, rate_pct=0):
    """Озвучка з запасними планами: edge-tts (довгий текст — шматками, 🎚 v30)
    → системний голос Windows → тиха пауза.

    Хмара edge-tts часом відповідає 403 (Microsoft обмежує доступ), а довгі
    тексти обривала на середині — тепер ріжуться на шматки і зшиваються;
    додаток усе одно генерує відео, а не падає.
    """
    # 🗣 v38: План 0 — клон голосу (Chatterbox, HF Space, БЕЗ ключа): перемикач у 🧰
    try:
        cfg = clone_cfg_load()
        if cfg.get("enabled") and (cfg.get("sample") or "").strip() and os.path.isfile(cfg["sample"]):
            say("🗣 Озвучка клоном твого голосу (Chatterbox, HF Space, без ключа)…")
            hf_tts_clone(text, cfg["sample"], out_mp3, say)
            say("🗣 Озвучено клоном твого голосу (Chatterbox, без ключа)")
            return
        if cfg.get("enabled"):
            say("ℹ️ Зразок голосу не знайдено (tools/clone.json) — озвучую edge-tts")
    except Exception as e:
        say("ℹ️ Клон голосу не вийшов ({}): озвучую як раніше".format(str(e)[:120]))

    ff = ffmpeg_path()
    chunks = _tts_chunks(text)

    # План 1: edge-tts — найкращі голоси; 🎚 v30: довгий текст шматками
    for attempt in (1, 2):
        parts, ok = [], bool(chunks)
        for i, ch in enumerate(chunks):
            p = "{}.part{:03d}".format(out_mp3, i)
            try:
                asyncio.run(edge_tts.Communicate(ch, voice, rate="{:+d}%".format(int(rate_pct or 0))).save(p))
                if os.path.exists(p) and os.path.getsize(p) > 500:
                    parts.append(p)
                else:
                    ok = False
                    break
            except Exception as e:
                say("ℹ️ edge-tts не відповів (спроба {}, шматок {} з {}): {}".format(attempt, i + 1, len(chunks), e))
                ok = False
                break
        if ok and parts:
            try:
                if len(parts) == 1:
                    os.replace(parts[0], out_mp3)
                else:
                    lst = out_mp3 + ".list"
                    with open(lst, "w", encoding="utf-8") as f:
                        for p in parts:
                            f.write("file '{}'\n".format(p.replace("\\", "/").replace("'", "'\\''")))
                    run([ff, "-y", "-hide_banner", "-nostdin", "-f", "concat", "-safe", "0",
                         "-i", lst, "-c:a", "libmp3lame", "-q:a", "4", out_mp3])
                    os.remove(lst)
                if len(parts) > 1:
                    say("🎚 Довгий текст озвучено {} шматками — без обривань".format(len(parts)))
                _rm_parts(parts)
                return
            except Exception as e:
                say("ℹ️ Шматки озвучки не зшиваються ({}): пробую ще раз".format(str(e)[:100]))
        _rm_parts(parts)
    say("⚠️ Хмарна озвучка недоступна — пробую системний голос Windows…")

    # План 2: системний голос Windows — працює без інтернету
    try:
        wav = os.path.join(os.environ.get("TEMP", "."), "vg_fallback.wav")
        if os.path.exists(wav):
            os.remove(wav)
        b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
        ps = (
            "Add-Type -AssemblyName System.Speech;"
            "$wav = Join-Path $env:TEMP 'vg_fallback.wav';"
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            "$s.SetOutputToWaveFile($wav);"
            "$s.Speak([System.Text.Encoding]::UTF8.GetString("
            "[Convert]::FromBase64String('" + b64 + "')));"
            "$s.Dispose()"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, timeout=300)
        if os.path.exists(wav) and os.path.getsize(wav) > 2000:
            run([ff, "-y", "-hide_banner", "-nostdin", "-i", wav,
                 "-c:a", "libmp3lame", "-b:a", "48k", "-ar", "24000", out_mp3])
            os.remove(wav)
            say("ℹ️ Озвучено системним голосом Windows (без хмари)")
            return
    except Exception as e:
        say(f"ℹ️ Системний голос не вдалося задіяти: {e}")

    # План 3: тиха пауза потрібної тривалості — відео все одно згенерується
    say("⚠️ Голосів немає — ставлю тиху паузу, щоб відео зібралось")
    seconds = max(3.0, len(text) / 14.0)
    run([ff, "-y", "-hide_banner", "-nostdin",
         "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", "%.2f" % seconds, "-c:a", "libmp3lame", "-b:a", "48k", out_mp3])


def tts_save_karaoke(text, voice, out_mp3, say, rate_pct=0):
    """🎤 v25: караоке-субтитри — edge-tts одночасно з озвучкою віддає
    часові мітки кожного слова (WordBoundary: offset/duration у 100-нс).
    🎚 v30: довгий текст озвучується шматками — мітки кожного шматка
    зсуваються на тривалість попередніх, тож караоке не спливає.
    Повертає список (слово, старт_с, кінець_с) або None, якщо хмара не дала
    метрик — тоді озвучку робить звичайний tts_save. Fail-open:
    караоке — надбудова, а не залежність; без нього все працює як раніше."""
    # 🗣 v38: клон не віддає міток слів — караоке неможливий, відступаємо до звичайних
    try:
        if clone_cfg_load().get("enabled"):
            say("ℹ️ Клон голосу без караоке-міток — субтитри будуть звичайні")
            return None
    except Exception:
        pass
    ff = ffmpeg_path()
    chunks = _tts_chunks(text)
    if not chunks:
        return None
    words, parts, base = [], [], 0.0
    for i, ch in enumerate(chunks):
        p = "{}.kpart{:03d}".format(out_mp3, i)
        got = _tts_words(ch, voice, p, rate_pct)
        if got is None:
            _rm_parts(parts)
            say("ℹ️ Караоке-мітки не зібрав (шматок {} з {}): озвучка зі звичайними планами".format(i + 1, len(chunks)))
            return None
        words.extend((w, s + base, e + base) for (w, s, e) in got)
        parts.append(p)
        try:
            base += audio_duration(p)
        except Exception:
            _rm_parts(parts)
            return None
    try:
        if len(parts) == 1:
            os.replace(parts[0], out_mp3)
        else:
            lst = out_mp3 + ".list"
            with open(lst, "w", encoding="utf-8") as f:
                for p in parts:
                    f.write("file '{}'\n".format(p.replace("\\", "/").replace("'", "'\\''")))
            run([ff, "-y", "-hide_banner", "-nostdin", "-f", "concat", "-safe", "0",
                 "-i", lst, "-c:a", "libmp3lame", "-q:a", "4", out_mp3])
            os.remove(lst)
            say("🎚 Караоке зшито з {} шматків — мітки на своїх місцях".format(len(parts)))
    except Exception:
        _rm_parts(parts)
        return None
    _rm_parts(parts)
    return words


def make_karaoke_srt(words, total, workdir, max_chars=26, max_gap=0.5, max_sec=3.0):
    """🎤 v25: SRT з РЕАЛЬНИХ міток слів (WordBoundary), а не з рівномірної
    апроксимації. Слова групуються у короткі фрази: довжина ≤ max_chars,
    пауза > max_gap або вікно > max_sec — нова фраза (стиль auto-captions:
    текст з'являється точно під голос). Повертає кількість фраз."""
    def fmt(t):
        h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
        return "{:02d}:{:02d}:{:06.3f}".format(int(h), int(m), s).replace(".", ",")
    lines, cur, start, end = [], [], 0.0, 0.0

    def flush():
        if cur:
            lines.append("{}\n{} --> {}\n{}\n".format(
                len(lines) + 1, fmt(start), fmt(min(end, total)), " ".join(cur)))

    for w, s0, e0 in words:
        if cur and (len(" ".join(cur)) + len(w) + 1 > max_chars
                    or s0 - end > max_gap
                    or s0 - start > max_sec):
            flush()
            cur = []
        if not cur:
            start = s0
        cur.append(w)
        end = max(e0, s0)
    flush()
    with open(os.path.join(workdir, "sub.srt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return len(lines)


AGENT_CMD_WORDS = (
    "зроби відео", "зробити відео", "створи відео", "створити відео", "згенеруй",
    "згенерувати", "зняти відео", "зроби ролик", "створи ролик", "потрібне відео",
    "потрібен ролик", "нехай буде відео",
)


def parse_agent_command(text):
    """🤖 v26: агентне вікно, Tier 1 — командний парсер без ключів:
    фраза → параметри генерації. Все невпізнане лишається темою,
    парсер НІКОЛИ не падає (fail-open: невідоме = тема)."""
    raw = text.strip()
    low = " " + raw.lower() + " "
    p = {"mode": "video", "query": raw, "size": None, "voice": None,
         "sub_style": None, "no_music": False, "cover": None, "seo": None,
         "trim": None, "script": None}
    # --- режим ---
    if "мікс" in low or "mix" in low:
        p["mode"] = "mix"
    elif "сценар" in low:
        p["mode"] = "script"
    # --- орієнтація/розмір ---
    if any(k in low for k in ("вертикал", "shorts", "reels", "tiktok", "9:16")):
        p["size"] = "Shorts"
    elif any(k in low for k in ("горизонтал", "16:9", "1080p", "ютуб", "youtube")):
        p["size"] = "1080p"
    # --- голос ---
    if "поліна" in low or "жіноч" in low or "жін" in low:
        p["voice"] = "Поліна"
    elif "остап" in low or "чоловіч" in low:
        p["voice"] = "Остап"
    # --- субтитри ---
    if "караоке" in low:
        p["sub_style"] = "Караоке 🎤"
    elif "жовт" in low:
        p["sub_style"] = "Жовті з тінню (CapCut)"
    # --- музика ---
    if "без музик" in low:
        p["no_music"] = True
    # --- прапорці ---
    if "обкладинк" in low or "прев'ю" in low or "превью" in low:
        p["cover"] = True
    if "seo" in low:
        p["seo"] = True
    if "щільн" in low or "без пауз" in low or "динамічн" in low:
        p["trim"] = True
    # --- тема: прибираємо командні слова, беремо після «про» ---
    theme = raw
    for w in AGENT_CMD_WORDS:
        if theme.lower().startswith(w):
            theme = theme[len(w):].lstrip(" :.,-\u2013\u2014")
            break
    if " про " in " " + theme.lower() + " ":
        idx = theme.lower().rfind(" про ")
        theme = theme[idx + len(" про "):].strip()
    theme = theme.strip().rstrip(".!?")
    p["query"] = theme if theme else raw
    # --- сценарій: текст після двокрапки (якщо дали) ---
    if p["mode"] == "script" and ":" in raw:
        body = raw.split(":", 1)[1].strip()
        if len(body) > 10:
            p["script"] = body
    return p


def ollama_list_models(url, timeout=8):
    """🧠 v29: список локально встановлених моделей Ollama (/api/tags).
    Нема сервера або помилка — порожній список (fail-open, нуль ключів)."""
    try:
        r = requests.get((url or "").rstrip("/") + "/api/tags", timeout=timeout)
        if r.status_code != 200:
            return []
        return [m.get("name") for m in (r.json().get("models") or [])
                if m.get("name")]
    except Exception:
        return []


def ollama_chat(url, model, prompt, system=None, timeout=90, history=None):  # 💬 v41: history — діалог
    """🧠 v29: один запит до локального Ollama (/api/chat, stream=false).
    Повертає текст відповіді або "" — нема сервера/таймаут/помилка (fail-open)."""
    try:
        body = {"model": model, "stream": False,
                "messages": ([{"role": "system", "content": system}] if system else [])
                + (history or []) + [{"role": "user", "content": prompt}]}  # 💬 v41: діалог
        r = requests.post((url or "").rstrip("/") + "/api/chat", json=body,
                          timeout=timeout)
        if r.status_code != 200:
            return ""
        return (((r.json().get("message") or {}).get("content") or "")).strip()
    except Exception:
        return ""


def ollama_parse_command(cmd, url, model, provider="ollama"):
    """🧠 v29: Tier 2 — LLM розбирає довільну фразу у ті самі поля, що й
    парсер Tier 1. Просить строгий JSON, невідомі значення ігнорує.
    Не вийшло — None, Асистент лишається на правилах (fail-open)."""
    system = ("Ти — парсер команд українського відеогенератора. Перетвори фразу "
              "користувача у JSON рівно з такими ключами: "
              '{"mode": "video|script|mix", "query": "тема", '
              '"size": "Shorts|1080p|null", "voice": "Поліна|Остап|null", '
              '"sub_style": "Караоке 🎤|Жовті з тінню (CapCut)|Класичні|null", '
              '"no_music": true|false, "cover": true|false|null, '
              '"seo": true|false|null, "trim": true|false|null, '
              '"script": "текст сценарію або null"}. '
              "Значення null — якщо в фразі нема. Відповідай ЛИШЕ JSON, без пояснень.")
    rules = project_rules()  # 📏 v32: правила проєкту (abide-урок) — обов'язкові для моделі
    if rules:
        system += "\nПравила проєкту (обов'язкові):\n- " + "\n- ".join(rules)
    out = llm_chat(provider, url, model, cmd, system=system, timeout=120)
    m = re.search(r"\{[\s\S]*\}", out or "")
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except Exception:
        return None
    p = {"mode": "video", "query": cmd, "size": None, "voice": None,
         "sub_style": None, "no_music": False, "cover": None, "seo": None,
         "trim": None, "script": None}
    if d.get("mode") in ("video", "script", "mix"):
        p["mode"] = d["mode"]
    if d.get("query"):
        p["query"] = str(d["query"])[:300]
    if d.get("size") in ("Shorts", "1080p"):
        p["size"] = d["size"]
    if d.get("voice") in ("Поліна", "Остап"):
        p["voice"] = d["voice"]
    if d.get("sub_style") in ("Караоке 🎤", "Жовті з тінню (CapCut)", "Класичні"):
        p["sub_style"] = d["sub_style"]
    p["no_music"] = bool(d.get("no_music"))
    for k in ("cover", "seo", "trim"):
        p[k] = bool(d[k]) if isinstance(d.get(k), bool) else None
    if d.get("script") and len(str(d["script"])) > 10:
        p["script"] = str(d["script"])[:8000]
    return p


def ollama_write_script(theme, url, model, provider="ollama"):
    """🧠 v29: LLM-сценарист — тема → сценарій по частинах для режиму 📜
    (частини через порожній рядок; «Пошук: …» — підказка фону частини).
    Не вийшло — порожній рядок (fail-open)."""
    system = ("Ти — сценарист коротких українських відео. Пиши сценарій "
              "частинами: частини розділяй ПОРОЖНІМ рядком. Кожна частина — "
              "2–4 речення тексту озвучки; за потреби на початку частини "
              "керуючий рядок «Пошук: <запит для фону YouTube>». "
              "3–6 частин. Без заголовків і нумерації — тільки текст.")
    rules = project_rules()  # 📏 v32: правила проєкту (abide-урок) — обов'язкові для моделі
    if rules:
        system += "\nПравила проєкту (обов'язкові):\n- " + "\n- ".join(rules)
    return llm_chat(provider, url, model, "Напиши сценарій відео на тему: " + (theme or ""),
                       system=system, timeout=300)


def router_list_models(url, timeout=8):
    """🌐 v31: 9Router — список моделей через OpenAI-сумісний /v1/models.
    Нема роутера або помилка — порожній список (fail-open, api-free, нуль ключів)."""
    try:
        r = requests.get((url or "").rstrip("/") + "/v1/models", timeout=timeout)
        if r.status_code != 200:
            return []
        return [m.get("id") for m in (r.json().get("data") or []) if m.get("id")]
    except Exception:
        return []


def router_chat(url, model, prompt, system=None, timeout=90, history=None):
    """🌐 v31: 9Router — один запит /v1/chat/completions (OpenAI-формат).
    Повертає текст відповіді або "" — нема роутера/таймаут/помилка (fail-open)."""
    try:
        body = {"model": model,
                "messages": ([{"role": "system", "content": system}] if system else [])
                + (history or []) + [{"role": "user", "content": prompt}]}  # 💬 v41
        r = requests.post((url or "").rstrip("/") + "/v1/chat/completions",
                          json=body, timeout=timeout)
        if r.status_code != 200:
            return ""
        ch = (r.json().get("choices") or [{}])[0]
        return (((ch.get("message") or {}).get("content") or "")).strip()
    except Exception:
        return ""


def pollinations_list_models(url, timeout=8):
    """🌐 v35: Pollinations — БЕЗКОШТОВНИЙ онлайн-LLM без ключів (text.pollinations.ai):
    список моделей через GET /models. Лишаю лише анонімні (tier=anonymous) —
    решта хоче ключ. Нема відповіді/помилка — базовий gpt-oss-20b (fail-open)."""
    try:
        r = requests.get((url or POLLINATIONS_URL).rstrip("/") + "/models",
                         timeout=timeout, headers={"User-Agent": UA_STRING})
        if r.status_code != 200:
            return ["gpt-oss-20b"]
        data = r.json()
        if isinstance(data, dict):  # на всяк випадок: і масив, і {"models": []}
            data = data.get("models") or data.get("data") or []
        out = []
        for m in data:
            if not isinstance(m, dict):
                continue
            name = m.get("name") or m.get("id")
            tier = str(m.get("tier") or "anonymous").lower()
            if name and tier == "anonymous":
                out.append(str(name))
        return out or ["gpt-oss-20b"]
    except Exception:
        return ["gpt-oss-20b"]


def pollinations_chat(url, model, prompt, system=None, timeout=120, history=None):
    """🌐 v35: один запит до Pollinations — POST /openai (OpenAI-формат, БЕЗ ключа).
    Не вдався (429/402 — анонімний ліміт, ~1 запит/15 с) — GET-фолбек:
    /<промпт>?model=…&system=… . Повертає текст або "" (fail-open, нуль ключів)."""
    base = (url or POLLINATIONS_URL).rstrip("/")
    body = {"model": (model or "gpt-oss-20b").strip() or "gpt-oss-20b",
            "messages": ([{"role": "system", "content": system}] if system else [])
            + (history or []) + [{"role": "user", "content": prompt}]}  # 💬 v41
    try:
        r = requests.post(base + "/openai", json=body, timeout=timeout,
                          headers={"User-Agent": UA_STRING})
        if r.status_code == 200:
            ch = (r.json().get("choices") or [{}])[0]
            txt = (((ch.get("message") or {}).get("content") or "")).strip()
            if txt:
                return txt
    except Exception:
        pass
    try:  # GET-фолбек: промпт прямо в URL (той самий безключовий сервіс)
        p_full = chat_history_prompt(history, prompt) if history else prompt  # 💬 v41
        q = (base + "/" + quote_plus((p_full or "")[:1500])
             + "?model=" + quote_plus((model or "gpt-oss-20b").strip() or "gpt-oss-20b"))
        if system:
            q += "&system=" + quote_plus(system[:1500])
        r = requests.get(q, timeout=timeout, headers={"User-Agent": UA_STRING})
        if r.status_code == 200 and (r.text or "").strip():
            return r.text.strip()
    except Exception:
        pass
    return ""


def load_freekeys():
    """🔑 v36/v39: безкоштовні ключі (puter/groq/github/gemini) з tools/freekeys.json —
    файл лише на комп'ютері користувача, у код і GitHub не потрапляє (патерн Pixabay).
    Кривий або нема — порожній словник (fail-open, гроші — нуль)."""
    try:
        with open(FREEKEYS_FILE, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def open_in_chrome(url):
    """🌐 v44: відкрити сторінку у Google Chrome — там, де отримують ключі.
    Шукаю chrome.exe у типових місцях Windows; нема Chrome — браузер за
    замовчуванням. Нічого не знайшлося — тихо (fail-open)."""
    cands = (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
             os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"))
    for p in cands:
        if p and os.path.exists(p):
            try:
                subprocess.Popen([p, url])
                return True
            except Exception:
                pass
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False


def freekey_engine():
    """🔑 v36/v39/v40/v43: який безкоштовний ключ є у freekeys.json
    (пріоритет — драбина FREEKEY_ORDER: 🤖 Claude (Puter/Anthropic) →
    Cerebras → Groq → Mistral → GitHub → Google AI Studio → OpenRouter →
    NVIDIA → SambaNova → HF; Claude як мозок Асистента, Groq окремо
    лишається для Whisper-субтитрів).
    Нема жодного — None (fail-open)."""
    keys = load_freekeys()
    for name in FREEKEY_ORDER:
        if len(str(keys.get(name) or "").strip()) >= 20:
            return name
    return None


def freekey_engine_for(model):
    """🔑 v46: шлюз, якому НАЛЕЖИТЬ обрана модель (раніше «Ключ» брав
    перший-попало шлюз з ключем — модель GLM могла летіти до Groq, Claude
    до SiliconFlow: 404, чат мовчав). Тепер: модель з меню → шлюз, у чиєму
    списку вона є (і ключ наявний); не збіглась — перший живий (fail-open)."""
    m = (model or "").strip()
    if m and m != "модель не обрана":
        keys = load_freekeys()
        for name in FREEKEY_ORDER:
            if len(str(keys.get(name) or "").strip()) < 20:
                continue
            models = list(FREEKEY_MODELS.get(name) or [])
            conf = FREEKEY_ENGINES.get(name) or {}
            if conf.get("model"):
                models.append(conf["model"])
            if m in models:
                return name
    return freekey_engine()


def chat_pick_steps(name):
    """💬 v46: джерело, обране в шапці чату → драбина кроків. Три онлайнові
    режими (Claude/ChatGPT/Mistral), кожен шлюз з ключем окремо, безключові
    Kilo/LLM7/Pollinations. Нема ключа взагалі — (None, текст-підказка):
    чат чесно пояснює, що зробити, а не мовчить (fail-open, гроші — нуль)."""
    keys = load_freekeys()

    def have(n):
        return len(str(keys.get(n) or "").strip()) >= 20

    def eng(n):
        c = FREEKEY_ENGINES.get(n) or {}
        return {"label": n, "kind": "oai", "url": c.get("url", ""),
                "model": c.get("model", ""), "key": str(keys.get(n) or "").strip()}
    if "Claude онлайн" in name:
        st = ([eng("puter")] if have("puter") else []) + \
             ([eng("anthropic")] if have("anthropic") else [])
        if st:
            return st, ""
        return None, ("🔑 Claude ще без ключа — кнопка «🔑 Ключі» у картці "
                      "Асистента → «🤖 Claude (Puter)» → «🌐 Отримати ключ» "
                      "(puter.com, без картки) → встав ключ → «💾 Запам'ятати "
                      "назавжди» — і Claude заговорить у чаті.")
    if "ChatGPT онлайн" in name:
        st = ([eng("groq")] if have("groq") else [])
        st.append({"label": "kilo", "kind": "kilo", "url": KILO_URL,
                   "model": "kilo-auto/free", "key": None})
        st.append({"label": "llm7", "kind": "llm7", "url": LLM7_URL,
                   "model": "gpt-5.5", "key": None})
        st.append({"label": "pollinations", "kind": "pollinations",
                   "url": POLLINATIONS_URL, "model": "gpt-oss-20b",
                   "key": None})  # 🆕 v49: останній безключовий запас — чат не мовчить
        return st, ""
    if "Gemini онлайн" in name:  # 🤖 v49: ГУГЛ у чаті — Gemini (Google AI Studio)
        st = ([eng("gemini")] if have("gemini") else []) \
            + ([eng("openrouter")] if have("openrouter") else [])
        if not have("gemini"):
            st.append({"label": "kilo", "kind": "kilo", "url": KILO_URL,
                       "model": "kilo-auto/free", "key": None})
        st.append({"label": "pollinations", "kind": "pollinations",
                   "url": POLLINATIONS_URL, "model": "gpt-oss-20b",
                   "key": None})  # безключовий запас — чат не мовчить ніколи
        return st, ""
    if "Mistral онлайн" in name:
        if have("mistral"):
            return [eng("mistral")], ""
        return None, ("🔑 Mistral ще без ключа — кнопка «🔑 Ключі» у картці "
                      "Асистента → «🇪🇺 Mistral» → «🌐 Отримати ключ» "
                      "(console.mistral.ai, experiment-план — безкоштовні "
                      "запити) → встав → «💾 Запам'ятати назавжди».")
    if "LLMFaucet" in name:  # 🚰 v52: безключовий агрегатор — окреме джерело чату
        return [{"label": "faucet", "kind": "faucet", "url": LLMFAUCET_URL,
                 "model": "auto", "key": None}], ""
    if "AI Horde" in name:  # 🐎 v52: волонтерська сітка — окреме джерело чату
        return [{"label": "horde", "kind": "horde", "url": HORDE_URL,
                 "model": "horde", "key": None}], ""
    if "Kilo" in name:
        return [{"label": "kilo", "kind": "kilo", "url": KILO_URL,
                 "model": "kilo-auto/free", "key": None}], ""
    if "LLM7" in name:
        return [{"label": "llm7", "kind": "llm7", "url": LLM7_URL,
                 "model": "gpt-5.5", "key": None}], ""
    if "Pollinations" in name:
        return [{"label": "pollinations", "kind": "pollinations",
                  "url": POLLINATIONS_URL, "model": "gpt-oss-20b",
                  "key": None}], ""
    if name in FREEKEY_ENGINES:
        if have(name):
            return [eng(name)], ""
        return None, ("🔑 Цей шлюз ще без ключа — кнопка «🔑 Ключі» у картці "
                      "Асистента → обери шлюз → «🌐 Отримати ключ» (сторінка "
                      "відкриється у Chrome) → встав → «💾 Запам'ятати "
                      "назавжди».")
    return None, ("💬 Невідоме джерело — перемкни у шапці чату на "
                  "«🔄 Як в картці».")


PAGE_CACHE = {}  # 🌐 v47/2.0: url → (текст, час) — кеш 10 хв для агента і «🔗 URL» у чаті


def fetch_page_text(url, timeout=20, limit=48000):
    """🌐 v47: сторінка → ЧИТАБЕЛЬНИЙ текст (міні-браузер без важкого
    движка: сценарії/стилі прибираю, теги — у переноси рядків, мнемоніки
    HTML — у звичайні символи). Кеш 10 хв у пам'яті — повторні відкриття
    миттєві, браузер не тупить. Нема мережі/404 — виняток нагору, той,
    хто викликав, показує свою підказку (fail-open)."""
    now = time.time()
    hit = PAGE_CACHE.get(url)
    if hit and now - hit[1] < 600:
        return hit[0]
    r = requests.get(url, timeout=timeout,
                     headers={"User-Agent": WEB_UA,  # 🔎 v50: сайти пускають «браузер»
                              "Accept-Language": "uk,en;q=0.8"})
    if r.status_code != 200:
        raise Exception("HTTP " + str(r.status_code))
    if not r.encoding or r.encoding.lower() in ("iso-8859-1", "ascii"):
        r.encoding = "utf-8"
    h = r.text
    h = re.sub(r"(?is)<(script|style|noscript|svg|iframe|head)[^>]*>.*?</\1>",
               " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|li|h[1-6]|tr|section|article|blockquote)>",
               "\n", h)
    h = re.sub(r"(?i)<li[^>]*>", " • ", h)
    h = re.sub(r"<[^>]+>", " ", h)
    txt = html.unescape(h).replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in txt.split("\n")]
    out = "\n".join(ln for ln in lines if ln)
    if len(out) > limit:
        out = out[:limit] + "\n… (дальше обрізав — «🌍 У Chrome» побачиш усе)"
    if len(PAGE_CACHE) > 40:  # не роздуваємо пам'ять
        try:
            PAGE_CACHE.pop(next(iter(PAGE_CACHE)))
        except Exception:
            pass
    PAGE_CACHE[url] = (out, now)
    return out


def _uddg_unwrap(u):
    """🔎 v50: DuckDuckGo ховає посилання у редірект uddg=… — розгортаю."""
    try:
        m = re.search(r"[?&]uddg=([^&\"']+)", u or "")
        return unquote_plus(m.group(1)) if m else (u or "")
    except Exception:
        return u or ""


def _ddg_parse(page, max_hits):
    """🔎 v50: розмітка DuckDuckGo (html І lite) → [{title,url,snip}]."""
    hits = []
    links = (re.findall(r"<a[^>]*class=['\"]result-link['\"][^>]*href=['\"]"
                       r"([^'\"]+)['\"][^>]*>(.*?)</a>", page, re.S)
             or re.findall(r"<a[^>]*class=['\"]result__a['\"][^>]*href=['\"]"
                           r"([^'\"]+)['\"][^>]*>(.*?)</a>", page, re.S))
    snips = re.findall(r"class=['\"](?:result-snippet|result__snippet)"
                       r"['\"][^>]*>(.*?)</(?:td|a|div|span)>", page, re.S)
    for i, (u, t) in enumerate(links):
        title = html.unescape(re.sub(r"<[^>]+>", " ", t)).strip()
        url = _uddg_unwrap(html.unescape(u))
        snip = ""
        if i < len(snips):
            snip = html.unescape(re.sub(r"<[^>]+>", " ",
                                        snips[i])).strip()
        if url.startswith("http") and title:
            hits.append({"title": title, "url": url, "snip": snip,
                         "engine": "DuckDuckGo"})
        if len(hits) >= max_hits:
            break
    return hits


def _mojeek_parse(page, max_hits):
    """🔎 v50: розмітка Mojeek (запасний рушій) → [{title,url,snip}]."""
    hits = []
    links = re.findall(r"<a[^>]*class=['\"]ob['\"][^>]*href=['\"]"
                       r"([^'\"]+)['\"][^>]*>(.*?)</a>", page, re.S)
    snips = re.findall(r"<p[^>]*class=['\"]s['\"][^>]*>(.*?)</p>",
                      page, re.S)
    for i, (u, t) in enumerate(links):
        title = html.unescape(re.sub(r"<[^>]+>", " ", t)).strip()
        snip = ""
        if i < len(snips):
            snip = html.unescape(re.sub(r"<[^>]+>", " ",
                                        snips[i])).strip()
        if u.startswith("http") and title:
            hits.append({"title": title, "url": u, "snip": snip,
                         "engine": "Mojeek"})
        if len(hits) >= max_hits:
            break
    return hits


def ddg_search(query, timeout=15, max_hits=5):
    """🔎 v47/v50: ПОШУК БЕЗ КЛЮЧІВ — ДРАБИНА РУШІЇВ: спершу DuckDuckGo
    (html → lite) зі справжнім браузерним UA (VideoGenerator вони
    блокували — ось чому пошук не працював), а як DDG лежить/429 —
    ЗАПАСНИЙ Mojeek (незалежний, майже не блокує). Повертає
    [{title, url, snip, engine}] — заголовок, посилання, витяг, рушій;
    нічого не знайшлось — [] (fail-open, гроші — нуль)."""
    q = (query or "").strip()
    if not q:
        return []
    now = time.time()
    hit = PAGE_CACHE.get("ddg:" + q)
    if hit and now - hit[1] < 600:
        return hit[0]
    hits = []
    try:  # 1) DuckDuckGo html — стабільна розмітка, браузерний UA
        r = requests.get("https://html.duckduckgo.com/html/?q="
                         + quote_plus(q), timeout=timeout,
                         headers={"User-Agent": WEB_UA,
                                  "Accept-Language": "uk,en;q=0.8"})
        if r.status_code == 200:
            hits = _ddg_parse(r.text, max_hits)
    except Exception:
        hits = []
    if not hits:  # 2) DuckDuckGo Lite — старий POST, раптом оживе
        try:
            r = requests.post("https://lite.duckduckgo.com/lite/",
                              data={"q": q}, timeout=timeout,
                              headers={"User-Agent": WEB_UA})
            if r.status_code == 200:
                hits = _ddg_parse(r.text, max_hits)
        except Exception:
            hits = []
    if not hits:  # 3) Mojeek — запасний рушій, без ключів (не мовчимо)
        try:
            r = requests.get("https://www.mojeek.com/search?q="
                             + quote_plus(q), timeout=timeout,
                             headers={"User-Agent": WEB_UA,
                                      "Accept-Language": "uk,en;q=0.8"})
            if r.status_code == 200:
                hits = _mojeek_parse(r.text, max_hits)
        except Exception:
            hits = []
    hits = hits[:max_hits]
    PAGE_CACHE["ddg:" + q] = (hits, now)
    return hits


AGENT_WEB_WORDS = ("знайди", "пошукай", "погугли", "новин", "актуальн",
                   "сьогодн", "погода", "курс ", "рейтин", "search",
                   "find latest", "who is", "скільки кошту", "цін",
                   "прогноз", "розклад", "release", "latest")


def agent_wants_web(text):
    """🕵️ v47: чи просить користувач свіжого з мережі — агент сам бере
    DuckDuckGo і не мучить модель застарілими знаннями."""
    t = " " + (text or "").lower() + " "
    return any(w in t for w in AGENT_WEB_WORDS)


def agent_query_clean(text):
    """🕵️ v52: прибрати «знайди/пошукай/покажи/search/find» на початку —
    у DuckDuckGo летить ЧИСТИЙ запит без прохань, а не «знайди мені
    свіжі новини ШІ», який рушій розуміє гірше. Слова не в початку
    НЕ чіпаю (сенс зберігається, fail-open)."""
    t = " ".join((text or "").split()).strip()
    for _ in range(4):
        m = re.match(r"(?iu)^(знайди|пошукай|покажи|погугли|знайдіть|пошукайте|search|find|look\s?up)\s+", t)
        if not m:
            break
        t = t[m.end():].strip()
    m2 = re.match(r"(?iu)^(мені|будь ласка|зараз|свіжі|нові|останні)\s+", t)
    if m2:
        t = t[m2.end():].strip()
    return t or (text or "").strip()


def agent_web_context(query, timeout=15):
    """🕵️ v47/2.0: АГЕНТ — свіжі дані з мережі для відповіді: 5 хітів
    DuckDuckGo → Mojeek (заголовок+посилання+витяг) + витяги ПЕРШИХ
    ДВОХ сторінок + сьогоднішня дата (модель знає, який зараз день).
    (ctx, note) — note для мітки чату; нічого не знайшлось — ("", "")."""
    hits = ddg_search(query, timeout=timeout)
    if not hits:
        return "", ""
    parts = []
    for i, h in enumerate(hits, 1):
        parts.append("[{}] {} — {}\n{}".format(i, h["title"], h["url"],
                                               h["snip"]))
    ctx = ("Сьогоднішня дата: " + datetime.now().strftime("%d.%m.%Y")
           + ".\nСвіжі дані з мережі (пошук DuckDuckGo → Mojeek, без "
           "ключів) — обов'язково використай їх у відповіді і зазнач "
           "джерела ПОСИЛАННЯМИ (просто URL у тексті):\n"
           + "\n".join(parts))
    for h in hits[:2]:  # 🕵️ v52: глибина — витяги ПЕРШИХ ДВОХ сторінок
        try:
            page = fetch_page_text(h["url"], timeout=timeout, limit=2500)
            if page:
                ctx += ("\n\nВитяг з " + h["url"] + ":\n" + page[:2500])
        except Exception:
            pass  # сторінка не далась — хітів і так вистачить (fail-open)
    eng = (hits[0].get("engine") if hits else "") or "мережі"
    return ctx, ("знайшов " + str(len(hits)) + " свіжих джерел (" + eng
                 + ", без ключів)")


LLM_REPLY_CACHE = {}  # 💾 v48: ключ кешу → (відповідь, час) — те саме питання без повторної оплати
LAST_STREAM_SOURCE = {"src": "", "t": 0.0}  # 📡 v48: який шлюз САМЕ щойно відповів стрімом


def llm_cache_key(provider, model, prompt, system, history):
    """💾 v48: ключ кешу відповіді — провайдер+модель+запит+система+історія.
    Щось змінилось (навіть пам'ять або свіжі дані агента) — інший ключ,
    застаріле не підсовую. Помилка — "" (кеш просто вимкнувся, fail-open)."""
    try:
        raw = "|".join([str(provider or ""), str(model or ""),
                        str(prompt or ""), str(system or ""),
                        json.dumps(history or [], ensure_ascii=False)])
        return hashlib.md5(raw.encode("utf-8", "ignore")).hexdigest()
    except Exception:
        return ""


LLM_CACHE_FILE = os.path.join(TOOLS_DIR, "llm_cache.jsonl")  # 💾 v51: диск-кеш LLM — відповіді переживають перезапуск програми


def _llm_disk_get(key):
    """💾 v51: знайти відповідь у дисковому кеші (jsonl, лінивий лінійний
    скан — файл малий; швидкий фільтр "key in ln" ще до JSON-парсингу).
    Нема файла/ключа — None (fail-open: кеш просто не працює)."""
    try:
        if not key or not os.path.isfile(LLM_CACHE_FILE):
            return None
        with open(LLM_CACHE_FILE, "r", encoding="utf-8") as fh:
            for ln in fh:
                if key not in ln:
                    continue  # рядок точно не про наш ключ — мимо, дешево
                try:
                    row = json.loads(ln)
                except Exception:
                    continue
                if row.get("k") == key:
                    return str(row.get("v") or "")
        return None
    except Exception:
        return None


def _llm_disk_add(key, val):
    """💾 v51: дописати відповідь у диск-кеш (append-only jsonl). Файл
    підріс до ~2 МБ — переписую, лишаючи свіжі 400 записів. Нема диска
    або прав — живу без кешу (fail-open)."""
    try:
        if not key or not val:
            return
        os.makedirs(TOOLS_DIR, exist_ok=True)
        with open(LLM_CACHE_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"k": key, "v": val,
                                 "t": int(time.time())},
                                ensure_ascii=False) + "\n")
        try:
            if os.path.getsize(LLM_CACHE_FILE) > 2 * 1024 * 1024:
                rows = []
                with open(LLM_CACHE_FILE, "r", encoding="utf-8") as fh:
                    for ln in fh:
                        if ln.strip():
                            rows.append(ln)
                with open(LLM_CACHE_FILE, "w", encoding="utf-8") as fh:
                    fh.writelines(rows[-400:])
        except Exception:
            pass  # обрізка не вийшла — файл і так читається (fail-open)
    except Exception:
        pass


KEY_ROTATE_IDX = {}  # 🔑 2.0: шлюз → наступний індекс ключа в ротації


def key_pool(raw):
    """🔑 2.0: РОТАЦІЯ КЛЮЧІВ — у freekeys.json можна писати кілька ключів
    одного шлюзу через кому ("sk-…,sk-…"). Повертаю список живих ключів
    у порядку round-robin: 429/ліміт одного ключа ≠ стоп, беру наступний
    (llm-apipool-патерн). Один ключ — список з одного (як раніше)."""
    try:
        pool = [k.strip() for k in str(raw or "").split(",") if len(k.strip()) >= 20]
        return pool or []
    except Exception:
        return []


def key_rotate(name, raw):
    """🔑 2.0: обрати ключ із пулу шлюзу по черзі (round-robin)."""
    pool = key_pool(raw)
    if not pool:
        return ""
    if len(pool) == 1:
        return pool[0]
    try:
        i = int(KEY_ROTATE_IDX.get(str(name), 0)) % len(pool)
        KEY_ROTATE_IDX[str(name)] = i + 1
        return pool[i]
    except Exception:
        return pool[0]


def kilo_list_models(url, timeout=10):
    """⚡ v36: Kilo Code — публічний OpenAI-сумісний шлюз БЕЗ ключа (free-пул
    ~200 запитів/год). Список моделей через GET /models; лишаю безкоштовні
    (суфікс free) — решта після реєстрації. Помилка — kilo-auto/free (fail-open)."""
    try:
        r = requests.get((url or KILO_URL).rstrip("/") + "/models",
                         timeout=timeout, headers={"User-Agent": UA_STRING})
        if r.status_code != 200:
            return ["kilo-auto/free"]
        data = r.json()
        if isinstance(data, dict):
            data = data.get("data") or data.get("models") or []
        ids = [str(m.get("id")) for m in data if isinstance(m, dict) and m.get("id")]
        free = [i for i in ids if "free" in i.lower()]
        return free or ["kilo-auto/free"]
    except Exception:
        return ["kilo-auto/free"]


def kilo_chat(url, model, prompt, system=None, timeout=120, history=None):
    """⚡ v36: один запит до Kilo Code БЕЗ ключа (POST /chat/completions,
    OpenAI-формат; ~200 зап/год — у рази щільніше за Pollinations).
    Не вдався (429 — вичерпали годинний пул) — "" (fail-open, нуль ключів)."""
    body = {"model": (model or "").strip() or "kilo-auto/free",
            "messages": ([{"role": "system", "content": system}] if system else [])
            + (history or []) + [{"role": "user", "content": prompt}]}  # 💬 v41
    try:
        r = requests.post((url or KILO_URL).rstrip("/") + "/chat/completions",
                          json=body, timeout=timeout, headers={"User-Agent": UA_STRING})
        if r.status_code != 200:
            return ""
        ch = (r.json().get("choices") or [{}])[0]
        return (((ch.get("message") or {}).get("content") or "")).strip()
    except Exception:
        return ""


def freekey_list_models(url, timeout=10):
    """🔑 v36/v39/v40: список моделей безкоштовного ключа (OpenAI-сумісний GET /models,
    Bearer). Нема ключа/помилка — порожній список (fail-open).
    🤖 v39/v40: Puter/Anthropic-ключ → лишаю родину Claude; ендпоінт не дав
    списку — чесна трійка поточних Claude-моделей."""
    eng = freekey_engine()
    if not eng:
        return []
    conf = FREEKEY_ENGINES[eng]
    if eng == "puter":
        claude3 = ["anthropic/claude-sonnet-5-5", "anthropic/claude-haiku-5-5",
                   "anthropic/claude-opus-5-5"]
    elif eng == "anthropic":
        claude3 = ["claude-sonnet-5-5", "claude-haiku-5-5", "claude-opus-5-5"]
    else:
        claude3 = []
    try:
        r = requests.get(conf["url"].rstrip("/") + "/models", timeout=timeout,
                         headers={"Authorization": "Bearer " +
                                  str(load_freekeys().get(eng) or "").strip()})
        if r.status_code != 200:
            return claude3
        data = r.json().get("data") or []
        ids = [str(m.get("id")) for m in data if isinstance(m, dict) and m.get("id")]
        if eng == "puter":
            ids = [i for i in ids if "anthropic/" in i] or claude3
        elif eng == "anthropic":
            ids = [i for i in ids if "claude" in i.lower()] or claude3
        return ids[:30]
    except Exception:
        return claude3


def freekey_chat(url, model, prompt, system=None, timeout=120, history=None):
    """🔑 v36/v39/v46: запит через безкоштовний ключ — шлюз під ОБРАНУ
    модель (freekey_engine_for), а як шлюз лежить/ліміт — драбина решти
    живих ключів (кожен зі своєю безкоштовною моделлю): чат не мовчить.
    Нема жодного — "" (fail-open, гроші — нуль)."""
    keys = load_freekeys()
    eng = freekey_engine_for(model)
    m = (model or "").strip()
    if not m or m == "модель не обрана":
        m = ""
    order = [n for n in ([eng] + [x for x in FREEKEY_ORDER if x != eng])
             if n in FREEKEY_ENGINES
             and len(str(keys.get(n) or "").strip()) >= 20]
    for name in order:
        conf = FREEKEY_ENGINES[name]
        txt = _oai_chat(conf["url"], str(keys.get(name) or "").strip(),
                        m if (name == eng and m) else conf["model"],
                        prompt, system=system, timeout=timeout,
                        history=history)
        if txt:
            return txt
    return ""


def llm7_list_models(url, timeout=10):
    """🌐 v40: LLM7 — анонімний OpenAI-сумісний шлюз (api.llm7.io, Bearer
    "unused", ~20–30 зап/хв без реєстрації; третя особа — без чутливого).
    Помилка — порожній список (fail-open)."""
    try:
        r = requests.get((url or LLM7_URL).rstrip("/") + "/models", timeout=timeout,
                         headers={"Authorization": "Bearer unused",
                                  "User-Agent": UA_STRING})
        if r.status_code != 200:
            return []
        data = r.json().get("data") or []
        return [str(m.get("id")) for m in data if isinstance(m, dict) and m.get("id")][:40]
    except Exception:
        return []


def llm7_chat(url, model, prompt, system=None, timeout=120, history=None):
    """🌐 v40: один запит до LLM7 БЕЗ реєстрації (Bearer "unused"). Не вдався
    (429/модель зникла/шлюз лежить) — "" (fail-open, нуль ключів)."""
    body = {"model": (model or "").strip() or "gpt-5.5",
            "messages": ([{"role": "system", "content": system}] if system else [])
            + (history or []) + [{"role": "user", "content": prompt}]}  # 💬 v41
    try:
        r = requests.post((url or LLM7_URL).rstrip("/") + "/chat/completions",
                          json=body, timeout=timeout,
                          headers={"Authorization": "Bearer unused",
                                   "User-Agent": UA_STRING})
        if r.status_code != 200:
            return ""
        ch = (r.json().get("choices") or [{}])[0]
        return (((ch.get("message") or {}).get("content") or "")).strip()
    except Exception:
        return ""


def _oai_chat(url, key, model, prompt, system=None, timeout=120, history=None):
    """🔑 v40: один OpenAI-сумісний запит з Bearer-ключем (ступінь драбини
    «Авто»: Puter/Anthropic/Groq/GitHub/Gemini). Помилка/429/402 — ""
    (fail-open)."""
    body = {"model": (model or "").strip(),
            "messages": ([{"role": "system", "content": system}] if system else [])
            + (history or []) + [{"role": "user", "content": prompt}]}  # 💬 v41
    try:
        r = requests.post((url or "").rstrip("/") + "/chat/completions", json=body,
                          timeout=timeout,
                          headers={"Authorization": "Bearer " + (key or ""),
                                   "User-Agent": UA_STRING})
        if r.status_code != 200:
            return ""
        ch = (r.json().get("choices") or [{}])[0]
        return (((ch.get("message") or {}).get("content") or "")).strip()
    except Exception:
        return ""


def faucet_chat(url, model, prompt, system=None, timeout=75, history=None):
    """🚰 v52: LLMFaucet — «сірий», але ЧЕСНИЙ безключовий агрегатор
    (джерела: Pollinations+LLM7+OVH+AI Horde): POST /chat/completions,
    Authorization: Bearer "free", модель-селектор auto/auto:fast/
    auto:smart/auto:coding. Автор сам попереджає: «для прототипів» —
    тому це СТУПІНЬ драбини, а не опора. Мовчить — "" (fail-open)."""
    try:
        msgs = ([{"role": "system", "content": system}] if system else []) \
            + (history or []) + [{"role": "user", "content": prompt}]
        r = requests.post((url or LLMFAUCET_URL).rstrip("/") + "/chat/completions",
                          json={"model": (model or "auto").strip(),
                                "messages": msgs, "stream": False},
                          headers={"Authorization": "Bearer free",
                                   "User-Agent": UA_STRING}, timeout=timeout)
        if r.status_code != 200:
            return ""
        j = r.json()
        ch = (j.get("choices") or [{}])[0]
        return str(((ch.get("message") or {}).get("content"))
                   or ((ch.get("text") or ""))).strip()
    except Exception:
        return ""


def horde_chat(prompt, system=None, timeout=90, history=None):
    """🐎 v52: AI HORDE — краудсорс-сітка волонтерських GPU/LLM (без
    реєстрації, анонімний apikey "0000000000"). Черга async: віддаю
    завдання → полю статус кожні 2.5 с → done беру generations[0].text;
    дедлайн — DELETE завдання (зняти з черги: повага до волонтерів).
    До хвилини очікування — НОРМА для Horde. Мовчить — "" (fail-open)."""
    try:
        full = (system or "").strip()
        for m in (history or [])[-6:]:
            who = "Юзер" if m.get("role") == "user" else "Асистент"
            full += "\n" + who + ": " + str(m.get("content") or "")[:1000]
        full += "\nЮзер: " + (prompt or "")
        r = requests.post(HORDE_URL.rstrip("/") + "/generate/text/async",
                          json={"prompt": full[:12000],
                                "params": {"max_new_tokens": 700,
                                           "temperature": 0.7}},
                          headers={"apikey": "0000000000",
                                   "Client-Agent": UA_STRING}, timeout=20)
        if r.status_code not in (200, 201, 202):
            return ""
        jid = (r.json() or {}).get("id")
        if not jid:
            return ""
        deadline = time.time() + max(30, min(int(timeout or 90), 150))
        try:
            while time.time() < deadline:
                time.sleep(2.5)
                s = requests.get(HORDE_URL.rstrip("/") + "/generate/text/status/"
                                 + str(jid),
                                 headers={"Client-Agent": UA_STRING},
                                 timeout=15)
                if s.status_code != 200:
                    continue
                sj = s.json()
                if sj.get("done"):
                    gens = sj.get("generations") or []
                    if gens:
                        return str((gens[0] or {}).get("text") or "").strip()
                    break
                if sj.get("faulted") or sj.get("is_possible") is False:
                    break
        finally:
            try:  # прибрати за собою — зняти завдання з черги волонтерів
                requests.delete(HORDE_URL.rstrip("/") + "/generate/text/status/"
                                + str(jid),
                                headers={"Client-Agent": UA_STRING}, timeout=10)
            except Exception:
                pass
        return ""
    except Exception:
        return ""


def auto_chain_steps(prompt=None):
    """🔄 v40–v52: драбина джерел «Авто»: усі шлюзи з живими ключами
    (freekeys.json) → ⚡ Kilo → 🌐 LLM7 → 🚰 LLMFaucet → 🌐 Pollinations
    → 🐎 AI Horde — всього до 21 ступеня; кожен fail-open. 🎯 2.0:
    важке питання (prompt) — Faucet-ступінь іде з селектором auto:smart
    (сам підбирає розумнішу модель); просте — auto (швидка)."""
    keys = load_freekeys()
    steps = []
    for name in FREEKEY_ORDER:
        pool = key_pool(keys.get(name))  # 🔑 2.0: ротація — ключів може бути кілька через кому
        if pool and name in FREEKEY_ENGINES:
            conf = FREEKEY_ENGINES[name]
            steps.append({"label": name, "kind": "oai", "url": conf["url"],
                          "model": conf["model"], "key": pool[0],
                          "pool": pool})
    smart = False
    try:
        p = str(prompt or "").lower()
        smart = len(p) > 240 or any(w in p for w in
                                    ("чому", "порівня", "розпиши", "аналіз",
                                     "код", "python", "кодекс", "покроков"))
    except Exception:
        smart = False
    steps.append({"label": "kilo", "kind": "kilo", "url": KILO_URL,
                  "model": "kilo-auto/free", "key": None, "pool": []})
    steps.append({"label": "llm7", "kind": "llm7", "url": LLM7_URL,
                  "model": "gpt-5.5", "key": None, "pool": []})
    steps.append({"label": "faucet", "kind": "faucet", "url": LLMFAUCET_URL,
                  "model": ("auto:smart" if smart else "auto"),
                  "key": None, "pool": []})  # 🚰 v52: між LLM7 і Pollinations
    steps.append({"label": "pollinations", "kind": "pollinations",
                  "url": POLLINATIONS_URL, "model": "gpt-oss-20b",
                  "key": None, "pool": []})
    steps.append({"label": "horde", "kind": "horde", "url": HORDE_URL,
                  "model": "horde", "key": None, "pool": []})  # 🐎 останній ступінь
    return steps


def chat_history_prompt(history, last):
    """💬 v41: історія діалогу → текстовий промпт (для GET-фолбеку Pollinations:
    у URL messages не вмістити). Формат — простий діалог, щоб модель тримала
    контекст розмови. Порожня історія — останнє повідомлення як є."""
    if not history:
        return last
    lines = []
    for m in (history or [])[-12:]:
        if not isinstance(m, dict) or not m.get("content"):
            continue
        who = "Юзер" if m.get("role") == "user" else "Асистент"
        lines.append(who + ": " + str(m["content"])[:1000])
    lines.append("Юзер: " + (last or ""))
    return ("Це діалог користувача з Асистентом. Відповісти ЛИШЕ на останнє "
            "повідомлення юзера, пам'ятаючи попередні відповіді:\n" + "\n".join(lines))


def auto_llm_chat(prompt, system=None, timeout=120, history=None):
    """🔄 v40/2.0: «Авто» — зграя джерел: пробує по драбині, поки хтось не
    відповість змістом. Вичерпаний ліміт (402/429) або лежачий шлюз —
    чесно пропускаю, іду далі (кожен ступінь у llm_trace). 🔑 2.0: у
    ступені з кількома ключами (через кому у freekeys.json) — спершу
    всі його ключі по черзі, і лише потім наступний шлюз. Дефолтних
    моделей — не обираю вручну: драбина сама знає. Гроші — нуль."""
    step_t = min(int(timeout or 120), 90)  # щедро для одного джерела, але не вічно
    for st in auto_chain_steps(prompt):
        keys_for_step = st.get("pool") or ([st["key"]] if st.get("key") else [])
        if st["kind"] in ("faucet", "horde", "kilo", "llm7",
                          "pollinations"):
            keys_for_step = [""]  # безключові ступені — один «порожній» прохід
        for k in keys_for_step:  # 🔑 2.0: ротація — 429 одного ключа ≠ стоп
            t0 = time.time()
            try:
                if st["kind"] == "kilo":
                    txt = kilo_chat(st["url"], st["model"], prompt,
                                    system=system, timeout=step_t,
                                    history=history)
                elif st["kind"] == "llm7":
                    txt = llm7_chat(st["url"], st["model"], prompt,
                                    system=system, timeout=step_t,
                                    history=history)
                elif st["kind"] == "faucet":  # 🚰 v52
                    txt = faucet_chat(st["url"], st["model"], prompt,
                                      system=system, timeout=step_t,
                                      history=history)
                elif st["kind"] == "horde":  # 🐎 v52
                    txt = horde_chat(prompt, system=system,
                                     timeout=step_t + 30, history=history)
                elif st["kind"] == "pollinations":
                    txt = pollinations_chat(st["url"], st["model"], prompt,
                                            system=system, timeout=step_t,
                                            history=history)
                else:
                    kk = key_rotate(st["label"], k) if len(keys_for_step) > 1 else k
                    txt = _oai_chat(st["url"], kk, st["model"], prompt,
                                    system=system, timeout=step_t,
                                    history=history)
            except Exception:
                txt = ""
            llm_trace("auto", st["label"], st["model"], t0, bool(txt),
                      len(txt or ""))
            if txt:
                return txt
    return ""



def groq_transcribe_srt(video, say):
    """🎤 v36: авто-субтитри для будь-якого відео — Whisper на Groq (безкоштовний
    фрітір ~8 год аудіо/день, ключ з tools/freekeys.json, картка не потрібна).
    Витягує звук (16 кГц моно mp3), transcription verbose_json → сегменти →
    .srt + .txt поруч з відео (відео не чіпаю). Fail-open: нема ключа/мережі/
    файл >25 МБ — чесно кажу чому і не ламаюсь."""
    key = str(load_freekeys().get("groq") or "").strip()
    if len(key) < 20:
        say("🔑 Нема ключа Groq — додай безкоштовний у freekeys.json (папка "
            "AppData/Local/VideoGenerator): {\"groq\": \"gsk_…\"} — console.groq.com "
            "→ API Keys, 2 хвилини, без картки")
        return None
    ensure_ffmpeg(say)
    ff = ffmpeg_path()
    aud = os.path.splitext(video)[0] + "._stt.mp3"
    try:
        run([ff, "-y", "-hide_banner", "-nostdin", "-i", video,
             "-vn", "-ac", "1", "-ar", "16000", "-c:a", "libmp3lame", "-q:a", "9", aud])
        if os.path.getsize(aud) > 25 * 1024 * 1024:
            say("🎤 Аудіо більше за 25 МБ — ліміт безкоштовного Groq; поріж відео на частини")
            return None
        say("🎤 Розпізнаю мову (Whisper на Groq — швидко і безкоштовно)…")
        with open(aud, "rb") as fh:
            r = requests.post(
                FREEKEY_ENGINES["groq"]["url"].rstrip("/") + "/audio/transcriptions",
                files={"file": (os.path.basename(aud), fh, "audio/mpeg")},
                data={"model": "whisper-large-v3-turbo", "response_format": "verbose_json"},
                headers={"Authorization": "Bearer " + key}, timeout=600)
        if r.status_code != 200:
            say("🎤 Groq не прийняв аудіо (HTTP " + str(r.status_code) + ") — спробуй ще раз")
            return None
        d = r.json()
        text = (d.get("text") or "").strip()
        segs = d.get("segments") or []

        def _fmt(t):
            h, rem = divmod(max(float(t), 0.0), 3600)
            mi, s = divmod(rem, 60)
            return "{:02d}:{:02d}:{:06.3f}".format(int(h), int(mi), s).replace(".", ",")
        srt = os.path.splitext(video)[0] + ".srt"
        if segs:
            blocks = []
            for i, g in enumerate(segs, 1):
                blocks.append("{}\n{} --> {}\n{}\n".format(
                    i, _fmt(g.get("start") or 0), _fmt(g.get("end") or 0),
                    str(g.get("text") or "").strip()))
            with open(srt, "w", encoding="utf-8") as f:
                f.write("\n".join(blocks))
        elif text:
            with open(srt, "w", encoding="utf-8") as f:
                f.write("1\n00:00:00,000 --> 00:10:00,000\n" + text + "\n")
        else:
            say("🎤 Whisper нічого не розпізнав — у відео нема мовлення?")
            return None
        with open(os.path.splitext(video)[0] + ".txt", "w", encoding="utf-8") as f:
            f.write(text + "\n")
        say("🎤 Готово: {} реплік — {} (+ .txt з текстом)".format(
            len(segs) or 1, os.path.basename(srt)))
        return srt
    except Exception as e:
        say("🎤 Субтитри не вийшли: " + str(e)[:160])
        return None
    finally:
        try:
            os.remove(aud)
        except OSError:
            pass


def groq_stt_text(wav_path, timeout=90):
    """🎤 v51: голос → текст (STT): Whisper whisper-large-v3-turbo на Groq —
    той самий безкоштовний фрітір-ключ, що для авто-субтитрів; нових
    залежностей нуль. Помилка/нема ключа — "" (fail-open)."""
    try:
        key = str(load_freekeys().get("groq") or "").strip()
        if len(key) < 20:
            return ""
        with open(wav_path, "rb") as fh:
            r = requests.post(
                FREEKEY_ENGINES["groq"]["url"].rstrip("/") + "/audio/transcriptions",
                files={"file": (os.path.basename(wav_path), fh, "audio/wav")},
                data={"model": "whisper-large-v3-turbo",
                      "response_format": "text"},
                headers={"Authorization": "Bearer " + key,
                         "User-Agent": UA_STRING}, timeout=timeout)
        if r.status_code != 200:
            return ""
        return (r.text or "").strip()
    except Exception:
        return ""


def _dshow_mic_name():
    """🎤 v51: ім'я ПЕРШОГО мікрофона Windows (DirectShow): ffmpeg
    -list_devices → парсинг секції «DirectShow audio devices» (рядки
    «[dshow @ …] "Назва мікрофона"»); микрофонів нема/ffmpeg лежить —
    "" (fail-open — запис тоді не стартне і чесно скажу чому)."""
    try:
        ff = ffmpeg_path()
        pr = subprocess.run([ff, "-hide_banner", "-list_devices", "true",
                             "-f", "dshow", "-i", "dummy"],
                            capture_output=True, text=True,
                            encoding="utf-8", errors="ignore", timeout=20)
        out = (pr.stderr or "") + (pr.stdout or "")
        if "DirectShow audio devices" not in out:
            return ""
        tail = out.split("DirectShow audio devices", 1)[1]
        m = re.search(r'"([^"]+)"\s*\(\w', tail)
        if m:
            return m.group(1).strip()
        m2 = re.search(r'"([^"]+)"', tail)  # фолбек: будь-яка цитована назва
        return (m2.group(1).strip() if m2 else "")
    except Exception:
        return ""


LIBRE_INSTANCES = ("https://libretranslate.de",
                   "https://translate.terraprint.xyz",
                   "https://libretranslate.com")  # 🌐 v51: публічні LibreTranslate (без ключів), драбина


def libre_translate(text, target, timeout=25):
    """🌐 v51: перекладач БЕЗ ключів — публічні інстанси LibreTranslate,
    по черзі (як лежить один — наступний). Повертаю (текст, інстанс);
    усі мовчать/лімітять — ("", "") і викликач падає на драбину LLM
    (її гарантовано наша ж інфраструктура тримає). Fail-open."""
    for base in LIBRE_INSTANCES:
        try:
            r = requests.post(base.rstrip("/") + "/translate",
                              json={"q": str(text or "")[:4000],
                                    "source": "auto", "target": str(target or "en"),
                                    "format": "text"},
                              timeout=timeout,
                              headers={"User-Agent": WEB_UA})
            if r.status_code == 200:
                j = r.json()
                if j.get("translatedText"):
                    return str(j["translatedText"]), base
        except Exception:
            continue  # цей інстанс мовчить — пробую наступний (fail-open)
    return "", ""


def translate_srt_file(srt_path, lang, say):
    """🌐 v51: переклад .srt-субтитрів на будь-яку мову: LibreTranslate
    (публічні інстанси, без ключів), а як вони мовчать — драбина LLM
    («auto» — теж без грошей). Блоки (до 200) перекладаю ПОРЯДОК-у-порядок:
    нумерацію і таймінги НЕ чіпаю, лише текст; прогрес — нота кожні 25
    блоків. Вивід — <ім'я>_<мова>.srt поруч з оригіналом. Fail-open."""
    try:
        if not srt_path or not os.path.isfile(srt_path):
            say("🌐 Спершу обери файл .srt 🙂")
            return None
        lang = (lang or "en").strip().lower()[:5] or "en"
        with open(srt_path, "r", encoding="utf-8", errors="ignore") as fh:
            raw = fh.read()
        blocks = re.split(r"\n\s*\n", raw.strip())
        blocks = [b for b in blocks if b.strip()][:200]  # ліміт: 200 блоків
        if not blocks:
            say("🌐 У файлі нема блоків субтитрів")
            return None
        say("🌐 Перекладаю {} блоків субтитрів на «{}»…".format(len(blocks), lang))
        via = ""
        out_blocks, done = [], 0
        for b in blocks:
            lines = b.splitlines()
            text_i = next((i for i, ln in enumerate(lines)
                           if "-->" not in ln
                           and not ln.strip().isdigit()), min(2, len(lines) - 1))
            src_text = "\n".join(lines[text_i:]).strip()
            new_text = src_text
            if src_text:
                t, inst = libre_translate(src_text, lang)
                if t:
                    new_text = t
                    via = via or ("LibreTranslate: " + inst.replace("https://", ""))
                else:  # інстанси мовчать — драбина LLM (гарантований запас)
                    t2 = llm_chat("auto", "", "",
                                  "Переклади текст субтитрів на мову з кодом "
                                  + lang + ". Дай ЛИШЕ переклад, без пояснень.",
                                  system="Ти — точний перекладач субтитрів. "
                                         "Збережи тон; коротко; без приміток.",
                                  timeout=60)
                    if t2:
                        new_text = " ".join(str(t2).split())[:1500]
                        via = via or "драбина LLM"
            out_blocks.append("\n".join(lines[:text_i] + [new_text]))
            done += 1
            if done % 25 == 0:
                say("🌐 {} з {} блоків…".format(done, len(blocks)))
        out_path = os.path.splitext(srt_path)[0] + "_" + lang + ".srt"
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write("\n\n".join(out_blocks) + "\n")
        say("🌐 Готово: {} ({} блоків{}{})".format(
            os.path.basename(out_path), len(blocks),
            " — " if via else "", via))
        try:
            os.startfile(os.path.dirname(out_path) or ".")
        except Exception:
            pass
        return out_path
    except Exception as e:
        say("🌐 Переклад субтитрів не вийшов: " + str(e)[:160])
        return None


def srt_blocks_parse(srt_path):
    """🎙 2.0: розібрати .srt на блоки [(початок_с, кінець_с, текст)] —
    для ДУБЛЯЖУ субтитрів (озвука кожної репліки edge-tts і фіт у
    таймінги). Кривий файл — [] (fail-open: дубляж тоді не стартне)."""
    try:
        with open(srt_path, "r", encoding="utf-8", errors="ignore") as fh:
            raw = fh.read()
        out = []

        def _t(s):
            try:
                hh, mm, rest = s.strip().split(":")
                ss, ms = rest.split(",")
                return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000.0
            except Exception:
                return 0.0
        for b in re.split(r"\n\s*\n", raw.strip()):
            lines = [ln for ln in b.splitlines() if ln.strip()]
            if not lines:
                continue
            m = None
            for ln in lines:
                m = re.match(r"(\d+:\d+:\d+,\d+)\s*-->\s*(\d+:\d+:\d+,\d+)", ln)
                if m:
                    break
            if not m:
                continue
            text = " ".join(ln for ln in lines
                            if "-->" not in ln and not ln.strip().isdigit()).strip()
            if text:
                out.append((_t(m.group(1)), _t(m.group(2)), text))
        return out
    except Exception:
        return []


def dub_srt_file(srt_path, voice_label, say):
    """🎙 2.0: ДУБЛЯЖ ЗА СУБТИТРАМИ (.srt → edge-tts репліка-на-репліку):
    кожен рядок озвучується окремо, потім atempo-фіт У ТАЙМІНГИ
    оригіналу (скорочення не >1.35x — інакше репліка вільна, паузу не
    ріжу), на паузах між репліками — тиша. Вихід: <ім'я>_дубляж.mp3;
    поруч є відео з тим самим ім'ям — і <ім'я>_дубляж.mp4 з новою
    доріжкою (ShortGPT-патерн дубляжу). Fail-open на кожному кроці."""
    try:
        blocks = srt_blocks_parse(srt_path)
        if not blocks:
            say("🎙 Не вийшло прочитати репліки з .srt — перевір формат")
            return None
        workdir = os.path.dirname(os.path.abspath(srt_path))
        parts, names = [], []
        for i, (a, b, text) in enumerate(blocks):
            if not text.strip():
                continue
            mp3 = os.path.join(workdir, "dub_{:03d}.mp3".format(i))
            if not tts_save(text.strip()[:1500], voice_label, mp3, say):
                continue
            span = max(float(b) - float(a), 0.5)
            fitted = speed_fit(mp3, span, workdir, say) if span else mp3
            parts.append(fitted or mp3)
            names.append((a, fitted or mp3))
        if not parts:
            say("🎙 Озвучка реплік не вийшла — дубляжу нема")
            return None
        say("🎙 Зшиваю дубляж: {} реплік у таймлайні…".format(len(parts)))
        # таймлайн з тишинами: аудіо кожної репліки стає на СВІЙ момент
        ff = ffmpeg_path()
        inputs, flt, t = [], [], 0.0
        for idx, (a, p) in enumerate(names):
            gap = max(float(a) - t, 0.0)
            if gap > 0.05:
                inputs += ["-f", "lavfi",
                           "-t", "{:.2f}".format(gap),
                           "-i", "anullsrc=r=24000:cl=mono"]
                flt.append("[{}:a]atrim=duration={:.2f}[s{}]".format(
                    len(inputs) // 3 - 1, gap, idx))
                flt.append("[s{}]aresample=24000[a{}]".format(idx, idx))
            inputs.append("-i")
            inputs.append(p)
            flt.append("[{}:a]aresample=24000[r{}]".format(
                len(inputs) // 3 - 1, idx))
            try:
                d = audio_duration(p)
            except Exception:
                d = 1.0
            t = float(a) + max(float(d), 0.2)
        concat = "".join("[a{0}][r{0}]".format(i) for i, _ in enumerate(names))
        flt.append(concat + "concat=n={}:v=0:a=1[out]".format(len(names) * 2))
        out_mp3 = os.path.splitext(srt_path)[0] + "_дубляж.mp3"
        run([ff, "-y", "-hide_banner", "-nostdin"] + inputs +
            ["-filter_complex", ";".join(flt), "-map", "[out]",
             "-c:a", "libmp3lame", "-q:a", "4", out_mp3], cwd=workdir)
        for p in parts:
            try:
                if os.path.basename(p).startswith("dub_"):
                    os.remove(p)
            except OSError:
                pass
        if not os.path.isfile(out_mp3) or os.path.getsize(out_mp3) < 200:
            say("🎙 Дубляж не зшився — перевір ffmpeg у журналі вище")
            return None
        say("🎙 Дубляж-доріжка готова: " + os.path.basename(out_mp3))
        video = os.path.splitext(srt_path)[0] + ".mp4"  # поруч те саме відео?
        if os.path.isfile(video):
            out_mp4 = os.path.splitext(srt_path)[0] + "_дубляж.mp4"
            run([ff, "-y", "-hide_banner", "-nostdin", "-i", video,
                 "-i", out_mp3, "-map", "0:v", "-map", "1:a",
                 "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                 "-shortest", out_mp4], cwd=workdir)
            if os.path.isfile(out_mp4):
                say("🎬 Дубляж-ролик: " + os.path.basename(out_mp4)
                    + " (оригінальне відео з новою озвучкою)")
        try:
            os.startfile(workdir)
        except Exception:
            pass
        return out_mp3
    except Exception as e:
        say("🎙 Дубляж не вийшов: " + str(e)[:160])
        return None


def hf_space_call(base, api, data, timeout=900):
    """🤝 v37: публічний Gradio-API HF Space БЕЗ ключа (fail-open):
    POST /gradio_api/call → event_id → SSE-очікування результату."""
    r = requests.post(base.rstrip("/") + "/gradio_api/call" + api,
                      json={"data": data}, timeout=30,
                      headers={"User-Agent": UA_STRING})
    r.raise_for_status()
    ev = (r.json() or {}).get("event_id")
    if not ev:
        raise RuntimeError("Space не дав event_id (черга зайнята?) — спробуй ще раз")
    s = requests.get(base.rstrip("/") + "/gradio_api/call" + api + "/" + ev,
                     stream=True, timeout=timeout,
                     headers={"User-Agent": UA_STRING})
    kind, payload = None, None
    for raw in s.iter_lines(decode_unicode=True):
        if not raw:
            if kind == "error":
                raise RuntimeError("Space відповів помилкою: " + str(payload)[:200])
            if kind == "complete" and payload is not None:
                return json.loads(payload)
            kind, payload = None, None
            continue
        if raw.startswith("event:"):
            kind = raw.split(":", 1)[1].strip()
        elif raw.startswith("data:"):
            payload = raw.split(":", 1)[1].strip()
    if kind == "complete" and payload is not None:
        return json.loads(payload)
    raise RuntimeError("Space не відповів у час (ZeroGPU-черга) — спробуй пізніше")


def hf_upload(base, path):
    """🤝 v37: завантажити локальний файл у Space → об'єкт gradio.FileData."""
    with open(path, "rb") as f:
        r = requests.post(base.rstrip("/") + "/gradio_api/upload",
                          files={"files": (os.path.basename(path), f)},
                          timeout=180, headers={"User-Agent": UA_STRING})
    r.raise_for_status()
    arr = r.json()
    p = None
    if isinstance(arr, list) and arr:
        p = arr[0] if isinstance(arr[0], str) else (arr[0] or {}).get("path")
    elif isinstance(arr, dict):
        p = arr.get("path")
    if not p:
        raise RuntimeError("Space не прийняв файл")
    return {"path": p, "meta": {"_type": "gradio.FileData"}}


def hf_download(base, fileinfo, out_path):
    """🤝 v37: забрати файл-результат зі Space (url або шлях → локальний файл)."""
    url = None
    if isinstance(fileinfo, dict):
        url = fileinfo.get("url")
        if not url and fileinfo.get("path"):
            url = base.rstrip("/") + "/gradio_api/file=" + quote_plus(fileinfo["path"])
    elif isinstance(fileinfo, str) and fileinfo.startswith("http"):
        url = fileinfo
    elif isinstance(fileinfo, str) and fileinfo.strip():
        url = base.rstrip("/") + "/gradio_api/file=" + quote_plus(fileinfo)
    if not url:
        raise RuntimeError("Space не дав файл-результат")
    with requests.get(url, stream=True, timeout=300,
                      headers={"User-Agent": UA_STRING}) as resp:
        resp.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(65536):
                f.write(chunk)
    return out_path


def hf_split300(text, limit=280):
    """🗣 v37: ріжемо текст на шматки по реченнях до ~300 символів (Chatterbox)."""
    parts, cur = [], ""
    for sent in re.split(r"(?<=[.!?…])\s+", (text or "").strip()):
        while len(sent) > limit:
            if cur:
                parts.append(cur)
                cur = ""
            parts.append(sent[:limit])
            sent = sent[limit:]
        if cur and len(cur) + len(sent) + 1 > limit:
            parts.append(cur)
            cur = ""
        cur = (cur + " " + sent).strip() if cur else sent
    if cur:
        parts.append(cur)
    return [p for p in parts if p.strip()]


def hf_tts_clone(text, ref_audio, out_path, say=None):
    """🗣 v37: клонування голосу з зразка (Chatterbox, HF Space, БЕЗ ключа)."""
    parts = hf_split300(text)
    if not parts:
        raise RuntimeError("Текст порожній")
    base = HF_SPACES["tts"]
    ref = None
    if ref_audio and os.path.isfile(ref_audio):
        ref = hf_upload(base, ref_audio)
        if say:
            say("🗣 Зразок голосу завантажено у Space")
    tmpdir = out_path + ".parts"
    os.makedirs(tmpdir, exist_ok=True)
    try:
        tmps = []
        for i, piece in enumerate(parts, 1):
            if say:
                say("🗣 Клон: шматок {}/{} (Space чергує — до хвилини)…".format(i, len(parts)))
            res = hf_space_call(base, "/generate_tts_audio",
                                [piece, ref, 0.5, 0.8, 0, 0.5, False])
            audio = res[0] if isinstance(res, list) and res else res
            tmp = os.path.join(tmpdir, "part_{:03d}".format(i))
            hf_download(base, audio, tmp)
            tmps.append(tmp)
        ff = ffmpeg_path()
        if len(tmps) == 1:
            run([ff, "-y", "-hide_banner", "-nostdin", "-i", tmps[0],
                 "-c:a", "libmp3lame", "-q:a", "3", out_path])
        else:
            lst = os.path.join(tmpdir, "list.txt")
            with open(lst, "w", encoding="utf-8") as f:
                for t in tmps:
                    f.write("file '{}'\n".format(t))
            run([ff, "-y", "-hide_banner", "-nostdin", "-f", "concat", "-safe", "0",
                 "-i", lst, "-c:a", "libmp3lame", "-q:a", "3", out_path])
        return out_path
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def hf_image(prompt, out_path, say=None):
    """🖼 v37: зображення з тексту (FLUX.1-schnell, HF Space, БЕЗ ключа)."""
    if not (prompt or "").strip():
        raise RuntimeError("Опиши картинку")
    res = hf_space_call(HF_SPACES["img"], "/infer",
                        [prompt.strip(), 0, True, 1024, 1024, 4])
    img = res[0] if isinstance(res, list) and res else res
    return hf_download(HF_SPACES["img"], img, out_path)


def hf_image_to_video(image_path, prompt, out_path, say=None):
    """🎬 v37: оживити картинку (WAN 2.2, HF Space, БЕЗ ключа)."""
    if not (image_path and os.path.isfile(image_path)):
        raise RuntimeError("Спершу обери картинку")
    base = HF_SPACES["vid"]
    img = hf_upload(base, image_path)
    res = hf_space_call(base, "/generate_video",
                        [img, (prompt or "").strip(), 6, "",
                         3.5, 1.0, 1.0, 42, True], timeout=1800)
    vid = res[0] if isinstance(res, list) and res else res
    return hf_download(base, vid, out_path)


def hf_edit_image(image_path, prompt, out_path, say=None):
    """🖌 v38: редагування картинки промптом (FLUX.1 Kontext, HF Space, БЕЗ ключа)."""
    if not (prompt or "").strip():
        raise RuntimeError("Напиши, що змінити у картинці")
    if not (image_path and os.path.isfile(image_path)):
        raise RuntimeError("Спершу обери картинку")
    base = HF_SPACES["edit"]
    img = hf_upload(base, image_path)
    res = hf_space_call(base, "/infer",
                        [img, prompt.strip(), 0, True, 2.5, 28], timeout=1200)
    out = res[0] if isinstance(res, list) and res else res
    return hf_download(base, out, out_path)


def hf_remove_bg(image_path, out_path, say=None):
    """✂️ v38: видалення фону (not-lain/background-removal, HF Space, БЕЗ ключа)."""
    if not (image_path and os.path.isfile(image_path)):
        raise RuntimeError("Спершу обери картинку")
    base = HF_SPACES["nobg"]
    img = hf_upload(base, image_path)
    res = hf_space_call(base, "/image", [img], timeout=600)
    out = res[-1] if isinstance(res, list) and res else res  # ImageSlider: [до, після]
    return hf_download(base, out, out_path)


def hf_ocr(image_path, out_txt, say=None):
    """🔍 v38: текст з картинки (DeepSeek-OCR, HF Space, БЕЗ ключа) → .txt (Markdown)."""
    if not (image_path and os.path.isfile(image_path)):
        raise RuntimeError("Спершу обери картинку або скріншот")
    base = HF_SPACES["ocr"]
    img = hf_upload(base, image_path)
    res = hf_space_call(base, "/run",
                        [img, None, "📋 Markdown", None, 1], timeout=900)
    text = None
    cand = res if isinstance(res, list) else [res]
    for c in cand:
        if isinstance(c, str) and c.strip():
            text = c
            break
    if not (text or "").strip():
        raise RuntimeError("OCR не знайшов тексту (маленький шрифт?)")
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
    return out_txt


def hf_frames_to_video(img1, img2, prompt, out_path, say=None):
    """🎬 v38: перший кадр → останній кадр (WAN 2.2, HF Space, БЕЗ ключа):
    два пости/кадри → плавний перехід-відео між ними."""
    if not (img1 and os.path.isfile(img1)) or not (img2 and os.path.isfile(img2)):
        raise RuntimeError("Спершу обери ДВІ картинки (перший і останній кадр)")
    base = HF_SPACES["fl"]
    a = hf_upload(base, img1)
    b = hf_upload(base, img2)
    res = hf_space_call(base, "/generate_video",
                        [a, b, (prompt or "").strip(), "", 2.1, 8, 1.0, 1.0, 42, True],
                        timeout=1800)
    out = res[0] if isinstance(res, list) and res else res
    return hf_download(base, out, out_path)


def clone_cfg_load():
    """🗣 v38: tools/clone.json — зразок голосу і стан перемикача клону
    (лише локально, як ключ Pixabay; fail-open: нема файла — порожній словник)."""
    try:
        with open(CLONE_FILE, "r", encoding="utf-8") as f:
            d = json.load(f) or {}
    except Exception:
        d = {}
    return d if isinstance(d, dict) else {}


def clone_cfg_save(d):
    """🗣 v38: зберегти налаштування клону локально (нічого не летить у репо)."""
    try:
        os.makedirs(TOOLS_DIR, exist_ok=True)
        with open(CLONE_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def llm_list_models(provider, url, timeout=8):
    """🌐 v31/v35/v36: список моделей за провайдером: Ollama, 9Router, Pollinations,
    Kilo Code або безкоштовний ключ (Groq/GitHub/Gemini)."""
    if provider == "9router":
        return router_list_models(url, timeout)
    if provider == "pollinations":
        return pollinations_list_models(url, timeout)
    if provider == "kilo":
        return kilo_list_models(url, timeout)
    if provider == "freekey":
        return freekey_list_models(url, timeout)
    return ollama_list_models(url, timeout)


def llm_chat(provider, url, model, prompt, system=None, timeout=90, history=None):
    """🌐 v31/v35/v36/v40: один запит за провайдером: Ollama, 9Router,
    Pollinations, Kilo Code, безкоштовний ключ (Claude/Groq/GitHub/Gemini)
    або 🔄 «Авто» — драбина всіх джерел (fail-open на кожному ступені).
    💬 v41: history — список {"role","content"} попередніх реплік діалогу
    (чат Асистента): моделі бачать усю розмову, а не лише останню фразу."""
    if provider == "auto":
        return auto_llm_chat(prompt, system=system, timeout=timeout,
                             history=history)
    if provider == "9router":
        return router_chat(url, model, prompt, system=system, timeout=timeout,
                          history=history)
    if provider == "pollinations":
        return pollinations_chat(url, model, prompt, system=system,
                                 timeout=timeout, history=history)
    if provider == "kilo":
        return kilo_chat(url, model, prompt, system=system, timeout=timeout,
                         history=history)
    if provider == "faucet":  # 🚰 v52
        return faucet_chat(url, model, prompt, system=system, timeout=timeout,
                           history=history)
    if provider == "horde":  # 🐎 v52
        return horde_chat(prompt, system=system, timeout=timeout,
                          history=history)
    if provider == "freekey":
        return freekey_chat(url, model, prompt, system=system, timeout=timeout,
                           history=history)
    return ollama_chat(url, model, prompt, system=system, timeout=timeout,
                       history=history)


def _sse_stream_chat(url, key, model, messages, on_delta, stop=None, timeout=180):
    """⚡ v42: справжній СТРІМІНГ (stream=True, SSE-рядки "data: …") — як у
    Claude: токени малюються одразу, а не «в效екти» друку після відповіді.
    Обрив/ліміт — повертаю те, що встигло прилетіти (fail-open)."""
    body = {"model": (model or "").strip(), "messages": messages, "stream": True}
    headers = {"User-Agent": UA_STRING}
    if key:
        headers["Authorization"] = "Bearer " + (key or "")
    got = []
    try:
        with requests.post((url or "").rstrip("/") + "/chat/completions",
                           json=body, stream=True, timeout=timeout,
                           headers=headers) as r:
            if r.status_code != 200:
                return ""
            if not r.encoding:
                r.encoding = "utf-8"  # SSE-чанки точно як текст
            for line in r.iter_lines(decode_unicode=True):
                if stop is not None and stop():
                    break  # ⏹ Стоп — стрім обриваю, часткову відповідь лишаю
                if not line or not line.startswith("data:"):
                    continue
                d = line[5:].strip()
                if d == "[DONE]":
                    break
                try:
                    j = json.loads(d)
                except Exception:
                    continue
                ch = (j.get("choices") or [{}])[0]
                piece = ((ch.get("delta") or {}).get("content")
                         or (ch.get("message") or {}).get("content") or "")
                if piece:
                    got.append(piece)
                    if on_delta:
                        on_delta(piece)
    except Exception:
        pass
    return "".join(got).strip()


def _ollama_stream_chat(url, model, messages, on_delta, stop=None, timeout=180):
    """⚡ v42: стрімінг локального Ollama (/api/chat, stream=True, JSON-рядки
    {"message":{"content":…},"done":…}) — токени одразу, як у Claude."""
    got = []
    try:
        with requests.post((url or "").rstrip("/") + "/api/chat",
                           json={"model": model, "messages": messages,
                                 "stream": True},
                           stream=True, timeout=timeout) as r:
            if r.status_code != 200:
                return ""
            for line in r.iter_lines(decode_unicode=True):
                if stop is not None and stop():
                    break
                if not line:
                    continue
                try:
                    j = json.loads(line)
                except Exception:
                    continue
                piece = ((j.get("message") or {}).get("content")) or ""
                if piece:
                    got.append(piece)
                    if on_delta:
                        on_delta(piece)
    except Exception:
        pass
    return "".join(got).strip()


GATEWAY_PRETTY = {  # 📡 v49: гарні імена шлюзів для нот драбини (модульний рівень)
    "puter": "🤖 Claude (Puter)", "anthropic": "🤖 Claude (Anthropic)",
    "groq": "🔑 Groq", "github": "🔑 GitHub", "gemini": "🤖 Google AI Studio",
    "cerebras": "⚡ Cerebras", "mistral": "🇪🇺 Mistral",
    "openrouter": "🧭 OpenRouter", "nvidia": "🟩 NVIDIA NIM",
    "sambanova": "🟧 SambaNova", "huggingface": "🤗 HF Router",
    "zhipu": "🟣 GLM (Zhipu)", "zai": "🟣 GLM (Z.AI)",
    "siliconflow": "🌊 SiliconFlow", "modelscope": "🟠 ModelScope",
    "cohere": "🧩 Cohere",
    "kilo": "⚡ Kilo", "llm7": "🌐 LLM7", "faucet": "🚰 LLMFaucet",
    "pollinations": "🌐 Pollinations", "horde": "🐎 AI Horde"}


def llm_stream(provider, url, model, prompt, system=None, history=None,
               on_delta=None, stop=None, timeout=180, on_note=None):
    """⚡ v42: один запит зі СТРІМІНГОМ за провайдером — так Claude віддає
    відповідь по шматках: on_delta(шматок) малює одразу, повертаю весь текст.
    «Авто» — драбина: ступінь стрімить, вперто мовчить — наступний; Pollinations
    не засмітився — звичайний запит і «зліт» одним шматком. ⏳ v49 on_note —
    драбина чесно повідомляє, ЯКИЙ шлюз мовчить: видно, ЧОГО нема відповіді.
    Fail-open всюди."""
    msgs = ([{"role": "system", "content": system}] if system else []) \
        + (history or []) + [{"role": "user", "content": prompt}]
    step_t = min(int(timeout or 180), 90)
    if provider == "auto":
        for st in auto_chain_steps():
            t0 = time.time()
            try:
                if st["kind"] == "kilo":
                    txt = _sse_stream_chat(st["url"].rstrip("/") + "/chat/completions",
                                           None, st["model"], msgs, on_delta,
                                           stop, step_t)
                elif st["kind"] == "llm7":
                    txt = _sse_stream_chat(st["url"].rstrip("/") + "/chat/completions",
                                           "unused", st["model"], msgs, on_delta,
                                           stop, step_t)
                elif st["kind"] == "faucet":  # 🚰 v52: не засмітився — одним шматком
                    txt = faucet_chat(st["url"], st["model"], prompt,
                                      system=system, timeout=step_t,
                                      history=history)
                    if txt and on_delta:
                        on_delta(txt)
                elif st["kind"] == "horde":  # 🐎 v52: останній ступінь — черга до хвилини
                    txt = horde_chat(prompt, system=system,
                                     timeout=step_t + 60, history=history)
                    if txt and on_delta:
                        on_delta(txt)
                elif st["kind"] == "pollinations":
                    txt = _sse_stream_chat(st["url"].rstrip("/") + "/openai",
                                           None, st["model"], msgs, on_delta,
                                           stop, step_t)
                    if not txt:
                        txt = pollinations_chat(st["url"], st["model"], prompt,
                                                system=system, timeout=step_t,
                                                history=history)
                        if txt and on_delta:
                            on_delta(txt)  # не засмітився — одним шматком
                else:
                    txt = _sse_stream_chat(st["url"].rstrip("/") + "/chat/completions",
                                           st["key"], st["model"], msgs, on_delta,
                                           stop, step_t)
            except Exception:
                txt = ""
            llm_trace("stream", st["label"], st["model"], t0, bool(txt),
                      len(txt or ""))
            if txt:
                return txt
            try:  # ⏳ v49: драбина не мовчить — показую, хто не відповів
                if on_note and callable(on_note):
                    on_note("⏳ " + GATEWAY_PRETTY.get(st["label"], st["label"])
                            + " мовчить — пробую далі…")
            except Exception:
                pass
        return ""
    try:
        if provider == "9router":
            return _sse_stream_chat((url or "").rstrip("/") + "/v1/chat/completions",
                                    None, model, msgs, on_delta, stop, timeout)
        if provider == "pollinations":
            base = (url or POLLINATIONS_URL).rstrip("/")
            txt = _sse_stream_chat(base + "/openai", None, model, msgs,
                                   on_delta, stop, timeout)
            if txt:
                return txt
            txt = pollinations_chat(url, model, prompt, system=system,
                                    timeout=timeout, history=history)
            if txt and on_delta:
                on_delta(txt)
            return txt
        if provider == "kilo":
            return _sse_stream_chat((url or KILO_URL).rstrip("/")
                                    + "/chat/completions", None, model, msgs,
                                    on_delta, stop, timeout)
        if provider == "freekey":
            keys = load_freekeys()
            eng = freekey_engine_for(model)
            m = (model or "").strip()
            order = [n for n in ([eng] + [x for x in FREEKEY_ORDER if x != eng])
                     if n in FREEKEY_ENGINES
                     and key_pool(keys.get(n))]
            step_t2 = min(int(timeout or 180), 90)
            for name in order:  # 🪜 v46: обраний шлюз першим, за ним — жива драбина
                conf = FREEKEY_ENGINES[name]
                mm = m if (name == eng and m and m != "модель не обрана") \
                    else conf["model"]
                pool = key_pool(keys.get(name))  # 🔑 2.0: ротація — ключів може бути кілька
                for k in pool:  # 429/ліміт одного ключа — беру наступний його ж ключ
                    t0 = time.time()
                    kk = key_rotate(name, keys.get(name)) if len(pool) > 1 else pool[0]
                    txt = _sse_stream_chat(conf["url"].rstrip("/") + "/chat/completions",
                                           kk, mm, msgs, on_delta, stop, step_t2)
                    llm_trace("stream", name, mm, t0, bool(txt), len(txt or ""))
                    if txt:
                        return txt
                try:  # ⏳ v49: який шлюз мовчить — видно у чаті
                    if on_note and callable(on_note):
                        on_note("⏳ " + GATEWAY_PRETTY.get(name, name)
                                + " мовчить — пробую далі…")
                except Exception:
                    pass
            return ""
        if provider.startswith("chat:"):  # 💬 v46: джерело з меню у шапці чату
            steps, hint = chat_pick_steps(provider[5:].strip())
            if hint:
                return hint
            step_t2 = min(int(timeout or 180), 90)
            for st in steps:
                t0 = time.time()
                mm = st["model"]  # 🧠 v49: модель з перемикача чату — якщо вона з цього шлюзу
                try:
                    if model and model in (FREEKEY_MODELS.get(st["label"]) or []):
                        mm = model
                    elif st["kind"] == "faucet" and model in FAUCET_MODELS:  # 🚰 v52: селектори auto:*
                        mm = model
                except Exception:
                    mm = st["model"]
                try:
                    if st["kind"] == "kilo":
                        txt = _sse_stream_chat(st["url"].rstrip("/")
                                               + "/chat/completions",
                                               None, mm, msgs, on_delta,
                                               stop, step_t2)
                    elif st["kind"] == "llm7":
                        txt = _sse_stream_chat(st["url"].rstrip("/")
                                               + "/chat/completions",
                                               "unused", mm, msgs,
                                               on_delta, stop, step_t2)
                    elif st["kind"] == "faucet":  # 🚰 v52: не засмічився — шматком
                        txt = faucet_chat(st["url"], mm, prompt,
                                          system=system, timeout=step_t2,
                                          history=history)
                        if txt and on_delta:
                            on_delta(txt)
                    elif st["kind"] == "horde":  # 🐎 v52: черга волонтерів
                        txt = horde_chat(prompt, system=system,
                                         timeout=step_t2 + 60,
                                         history=history)
                        if txt and on_delta:
                            on_delta(txt)
                    elif st["kind"] == "pollinations":
                        txt = _sse_stream_chat(st["url"].rstrip("/") + "/openai",
                                               None, mm, msgs, on_delta,
                                               stop, step_t2)
                        if not txt:
                            txt = pollinations_chat(st["url"], mm,
                                                    prompt, system=system,
                                                    timeout=step_t2,
                                                    history=history)
                            if txt and on_delta:
                                on_delta(txt)
                    else:
                        pool2 = key_pool(st.get("key")) or [st.get("key") or ""]  # 🔑 2.0
                        txt = ""
                        for k2 in pool2:  # ротація ключів обраного шлюзу
                            txt = _sse_stream_chat(st["url"].rstrip("/")
                                                   + "/chat/completions",
                                                   k2, mm, msgs,
                                                   on_delta, stop, step_t2)
                            if txt:
                                break
                except Exception:
                    txt = ""
                llm_trace("stream", st["label"], mm, t0,
                          bool(txt), len(txt or ""))
                if txt:
                    return txt
                try:  # ⏳ v49: який шлюз мовчить — видно у чаті
                    if on_note and callable(on_note):
                        on_note("⏳ " + GATEWAY_PRETTY.get(st["label"],
                                st["label"]) + " мовчить — пробую далі…")
                except Exception:
                    pass
            return ""
        return _ollama_stream_chat(url, model, msgs, on_delta, stop, timeout)
    except Exception:
        return ""

def llm_trace(kind, provider, model, t0, ok, chars):
    """📝 v32: llm_trace.jsonl — журнал запитів Tier 2 (opik @track-патерн):
    провайдер/модель/вид/мс/успіх/символи. Ротація: >64 КБ — лишаю останні
    500 рядків. Fail-open: журнал — лише діагностика, ніколи не ламає запит."""
    try:
        if kind == "stream" and ok:  # 📡 v48: хто САМЕ відповів стрімом (робоча ступінь драбини)
            LAST_STREAM_SOURCE["src"] = (provider or "").strip()
            LAST_STREAM_SOURCE["t"] = time.time()
        os.makedirs(TOOLS_DIR, exist_ok=True)
        p = LLM_TRACE_FILE
        if os.path.isfile(p) and os.path.getsize(p) > 64 * 1024:
            try:
                with open(p, encoding="utf-8") as f:
                    tail = "".join(f.readlines()[-500:])
            except Exception:
                tail = ""
            with open(p, "w", encoding="utf-8") as f:
                f.write(tail)
        rec = {"t": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "provider": (provider or "ollama").strip() or "ollama",
               "model": (model or "")[:60], "kind": kind,
               "ms": int((time.time() - t0) * 1000), "ok": bool(ok),
               "chars": int(chars or 0)}
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass  # 📝 v32: журнал — лише діагностика, ніколи не ламає Tier 2


def remove_pauses(mp3_path, out_path, say):
    """✂️ v14: вирізає з озвучки тихі паузи (довші за 0.7 с) — як «Remove silences»
    у Pictory/InVideo. Головна фішка модних автонарізок: мовлення стає щільним.
    Повертає (шлях, тривалість) — або оригінал, якщо прибирати нічого/не вийшло."""
    ff = ffmpeg_path()
    try:
        before = audio_duration(mp3_path)
        run([ff, "-y", "-hide_banner", "-nostdin", "-i", mp3_path, "-af",
             "silenceremove=stop_periods=-1:stop_duration=0.7:stop_threshold=-38dB",
             "-c:a", "libmp3lame", "-b:a", "48k", "-ar", "24000", out_path])
        after = audio_duration(out_path)
        if after < 1.5 or after >= before - 0.05:
            say("ℹ️ Довгих пауз в озвучці не знайшов — лишаю як є")
            return mp3_path, before
        say("✂️ Прибрав паузи: {:.1f} с → {:.1f} с (−{:.1f} с)".format(before, after, before - after))
        return out_path, after
    except Exception as e:
        say("⚠️ Прибирання пауз не вийшло ({}), лишаю озвучку як є".format(str(e)[:120]))
        return mp3_path, 0.0


def make_cover(workdir, title, say):
    """📷 v14: обкладинка для YouTube (cover.jpg) — кадр з готового відео + назва теми.
    Кадр бере ffmpeg, назву накладає Pillow — обидва вже є в застосунку, без нових залежностей."""
    ff = ffmpeg_path()
    cover = os.path.join(workdir, "cover.jpg")
    tmp = os.path.join(workdir, "_cover_frame.jpg")
    try:
        run([ff, "-y", "-hide_banner", "-nostdin", "-ss", "0.7", "-i", "final.mp4",
             "-frames:v", "1", "-q:v", "2", "_cover_frame.jpg"], cwd=workdir)
    except Exception as e:
        say("⚠️ Кадр для обкладинки не вийшов: " + str(e)[:120])
        return
    if PILImage is None:
        try:
            os.replace(tmp, cover)
            say("📷 Обкладинка: кадр з відео (cover.jpg)")
        except OSError:
            pass
        return
    try:
        from PIL import ImageDraw, ImageFont
        img = PILImage.open(tmp).convert("RGB")
        W, H = img.size
        d = ImageDraw.Draw(img, "RGBA")
        # градієнтна підкладка знизу — текст читається на будь-якому кадрі
        gh = int(H * 0.45)
        for k in range(gh):
            d.line([(0, H - gh + k), (W, H - gh + k)], fill=(10, 10, 18, int(210 * (k + 1) / gh)))
        font = None
        fs = max(24, int(W / 14))
        for fp in ("C:\\Windows\\Fonts\\segoeuib.ttf",
                   "C:\\Windows\\Fonts\\arialbd.ttf",
                   "C:\\Windows\\Fonts\\segoeui.ttf"):
            try:
                font = ImageFont.truetype(fp, fs)
                break
            except Exception:
                font = None
        if font is None:
            raise RuntimeError("системний шрифт не знайшовся")
        # назва: без емодзі (у шрифті їх нема), перенос по словах, максимум 3 рядки
        clean = "".join(ch for ch in (title or "Моє відео") if ord(ch) <= 65535)
        words = " ".join(clean.split()).split(" ")
        lines, cur = [], ""
        for wd in words:
            cand = (cur + " " + wd).strip()
            if cur and d.textlength(cand, font=font) > W * 0.84:
                lines.append(cur)
                cur = wd
            else:
                cur = cand
        if cur:
            lines.append(cur)
        lines = lines[:3]
        lh = int(fs * 1.3)
        y = H - int(H * 0.06) - lh * len(lines)
        for ln in lines:
            tw = d.textlength(ln, font=font)
            d.text(((W - tw) / 2, y), ln, font=font, fill=(255, 255, 255, 255))
            y += lh
        img.save(cover, quality=90)
        say("📷 Обкладинка для YouTube: cover.jpg у робочій папці")
    except Exception as e:
        try:
            os.replace(tmp, cover)
            say("📷 Обкладинка: кадр без тексту (cover.jpg) — " + str(e)[:80])
        except OSError:
            pass
    try:
        os.remove(tmp)
    except OSError:
        pass


IMG_TRANSLATE_LANGS = (("ru", "російську"), ("es", "іспанську"),
                        ("it", "італійську"), ("en", "англійську"))  # 🌍 v49


def make_cover_from_image(src_img, title, out_path, say=None):
    """🌍 v49: обкладинка ІНШОЮ МОВОЮ — фон = завантажена картинка (без
    відео), назва = перекладений заголовок: той самий стиль, що й
    make_cover (градієнт знизу + білий текст по центру, до 3 рядків).
    Pillow нема/не зловився — просто копія картинки (fail-open)."""
    try:
        if PILImage is None:
            raise RuntimeError("Pillow не знайшовся")
        from PIL import ImageDraw, ImageFont
        img = PILImage.open(src_img).convert("RGB")
        W, H = img.size
        d = ImageDraw.Draw(img, "RGBA")
        gh = int(H * 0.45)  # градієнтна підкладка знизу — текст читається завжди
        for k in range(gh):
            d.line([(0, H - gh + k), (W, H - gh + k)],
                   fill=(10, 10, 18, int(210 * (k + 1) / gh)))
        font = None
        fs = max(24, int(W / 14))
        for fp in ("C:\\Windows\\Fonts\\segoeuib.ttf",
                   "C:\\Windows\\Fonts\\arialbd.ttf",
                   "C:\\Windows\\Fonts\\segoeui.ttf"):
            try:
                font = ImageFont.truetype(fp, fs)
                break
            except Exception:
                font = None
        if font is None:
            raise RuntimeError("системний шрифт не знайшовся")
        clean = "".join(ch for ch in (title or "Cover") if ord(ch) <= 65535)
        words = " ".join(clean.split()).split(" ")
        lines, cur = [], ""
        for wd in words:
            cand = (cur + " " + wd).strip()
            if cur and d.textlength(cand, font=font) > W * 0.84:
                lines.append(cur)
                cur = wd
            else:
                cur = cand
        if cur:
            lines.append(cur)
        lines = lines[:3]
        lh = int(fs * 1.3)
        y = H - int(H * 0.06) - lh * len(lines)
        for ln in lines:
            tw = d.textlength(ln, font=font)
            d.text(((W - tw) / 2, y), ln, font=font, fill=(255, 255, 255, 255))
            y += lh
        img.save(out_path, quality=90)
        if say:
            say("📷 Обкладинка: " + os.path.basename(out_path))
    except Exception as e:
        try:  # малювати не вийшло — хоча б копія оригіналу (fail-open)
            shutil.copyfile(src_img, out_path)
        except Exception:
            pass
        if say:
            say("⚠️ Обкладинка без тексту (копія) — " + str(e)[:80])
    return out_path


def parse_vtt_text(vtt_path):
    """📜 v15: чистить WebVTT-субтитри: прибирає часові мітки, теги <…>,
    службові рядки і ковзні дублікати авто-субтитрів (новий рядок, що починається
    з попереднього, замінює його). Повертає чистий текст в одну лінію."""
    lines = []
    with open(vtt_path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            s = raw.strip()
            if not s or "-->" in s or s.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
                continue
            if re.match(r"^\d+$", s):  # номери блоків
                continue
            s = re.sub(r"<[^>]*>", " ", s)  # теги <c>, <00:00:01.000> тощо
            s = re.sub(r"&nbsp;", " ", s)
            s = re.sub(r"\s+", " ", s).strip()
            if s:
                lines.append(s)
    out = []
    for s in lines:
        if out:
            if s.startswith(out[-1]) or out[-1].startswith(s):
                out[-1] = s if len(s) >= len(out[-1]) else out[-1]
                continue
            if s == out[-1]:
                continue
        out.append(s)
    text = " ".join(out)
    return re.sub(r"\s+", " ", text).strip()


def fetch_transcript(url, say):
    """📜 v15: тягне субтитри (авто або ручні) з YouTube-відео через yt-dlp —
    українською, англійською або російською, без жодних ключів.
    Повертає (назва відео, текст транскрипції, мова)."""
    exe = ensure_ytdlp(say)
    outdir = os.path.join(TOOLS_DIR, "transcripts")
    os.makedirs(outdir, exist_ok=True)
    for old in os.listdir(outdir):  # чистимо минулі завантаження, щоб не переплутати відео
        try:
            os.remove(os.path.join(outdir, old))
        except OSError:
            pass
    out_tmpl = os.path.join(outdir, "tr.%(ext)s")
    cmd = [exe, "--no-playlist", "--no-warnings", "--skip-download",
           "--write-subs", "--write-auto-subs", "--convert-subs", "vtt",
           "--sub-langs", "uk.*,en.*,ru.*,-live_chat",
           "--ffmpeg-location", os.path.dirname(os.path.abspath(ffmpeg_path())),
           "--print", "%(title)s", "-o", out_tmpl, url]
    say("📜 Тягну субтитри з YouTube (українська → англійська → російська)…")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=240)
    except Exception as e:
        raise RuntimeError("yt-dlp не запустився: " + str(e)[:150])
    title = ""
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line and not line.startswith("["):
            title = line
            break
    vtt, lang = None, ""
    for fname in sorted(os.listdir(outdir)):
        if fname.lower().endswith(".vtt"):
            vtt = os.path.join(outdir, fname)
            m = re.search(r"\.([A-Za-z]{2}(?:[-_][A-Za-z0-9]{2,8})?)\.vtt$", fname)
            if m:
                lang = m.group(1)
            break
    if not vtt:
        detail = ""
        for line in ((proc.stderr or "") + (proc.stdout or "")).splitlines():
            if "ERROR" in line or "no subtitles" in line.lower():
                detail = line.strip()[:200]
                break
        raise RuntimeError("субтитри не знайшов ({}). Спробуй інше відео — транскрипція є не всюди".format(detail or "відео без субтитрів"))
    text = parse_vtt_text(vtt)
    if len(text) < 20:
        raise RuntimeError("субтитри порожні або не читаються — спробуй інше відео")
    say("📜 Транскрипція готова: {} символів, мова {}".format(len(text), lang or "невідома"))
    return (title or "YouTube-відео"), text, lang


def summarize_to_seconds(text, seconds, wps=2.4):
    """📜 v15: стискає текст приблизно до потрібної тривалості озвучки
    (wps — слів на секунду; edge-tts читає українською ~2.4 слова/с).
    Екстрактивно: лишає найвагоміші речення (частотні слова), перше й останнє — завжди."""
    budget = max(20, int(seconds * wps))
    sents = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text or "") if len(s.strip()) > 1]
    # авто-субтитри часто без крапок: надто довгі куски ріжемо по комах і двокрапках
    fine = []
    for s in sents:
        if len(s.split()) > 40:
            fine += [p.strip() for p in re.split(r"(?<=[,;:])\s+", s) if len(p.strip()) > 1]
        else:
            fine.append(s)
    sents = fine or sents
    if not sents:
        return (text or "").strip()
    if sum(len(s.split()) for s in sents) <= budget:
        return " ".join(sents)
    words = re.findall(r"[A-Za-zА-Яа-яІіЇїЄєҐґ']+", text or "")
    freq = Counter(w.lower() for w in words if w.lower() not in UA_STOPWORDS and len(w) > 2)

    def weight(s):
        ws = re.findall(r"[A-Za-zА-Яа-яІіЇїЄєҐґ']+", s.lower())
        if not ws:
            return 0.0
        sc = sum(freq.get(w, 0) for w in ws if len(w) > 2)
        return sc / ((len(ws) + 2) ** 0.6)

    order = sorted(range(len(sents)), key=lambda i: -weight(sents[i]))
    keep, used = set(), 0
    for i in order:
        n = len(sents[i].split())
        if used + n > budget and keep:
            continue
        keep.add(i)
        used += n
        if len(keep) >= 80:
            break
    keep.update({0, len(sents) - 1})  # вступ і фінал — завжди лишаємо
    return " ".join(sents[i] for i in sorted(keep))


def chunk_script_parts(text, max_parts=SCRIPT_MAX_SCENES):
    """🎬 v15: ділить текст на частини сценарію приблизно порівними блоками
    речень (частина = блок, розділювач частин — порожній рядок).
    12 частин × ~50 с = відео на ~10 хвилин."""
    sents = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text or "") if s.strip()]
    if not sents:
        return ""
    n = max(1, min(max_parts, len(sents)))
    if len(sents) < n:
        # немає крапок (типово для авто-субтитрів) — ділимо порівно за словами
        words = " ".join(text.split()).split(" ")
        per_w = max(10, (len(words) + n - 1) // n)
        return "\n\n".join(" ".join(words[k:k + per_w]).strip()
                           for k in range(0, len(words), per_w) if words[k:k + per_w])
    per = max(1, (len(sents) + n - 1) // n)
    parts = []
    for k in range(0, len(sents), per):
        parts.append(" ".join(sents[k:k + per]))
    return "\n\n".join(parts)


def _face_cascades():
    """🚫 v15: готові Haar-каскади OpenCV для пошуку обличчя
    (анфас ×2 + профіль). Порожній список — OpenCV нема або каскади не знайшлись."""
    if cv2 is None:
        return []
    roots = []
    try:
        roots.append(cv2.data.haarcascades)
    except Exception:
        pass
    try:
        roots.append(os.path.join(os.path.dirname(os.path.abspath(cv2.__file__)),
                                  "data", "haarcascades"))
    except Exception:
        pass
    names = ("haarcascade_frontalface_default.xml",
             "haarcascade_frontalface_alt2.xml",
             "haarcascade_profileface.xml")
    out, seen = [], set()
    for root in roots:
        for nm in names:
            p = os.path.join(root, nm)
            if p in seen:
                continue
            seen.add(p)
            try:
                if os.path.isfile(p) and os.path.getsize(p) > 1024:
                    cc = cv2.CascadeClassifier(p)
                    if not cc.empty():
                        out.append(cc)
            except Exception:
                continue
    return out


def frame_grab(clip, sec, out_jpg, workdir):
    """📷 v15: кадр з кліпу на потрібній секунді (для перевірки на обличчя)."""
    run([ffmpeg_path(), "-y", "-hide_banner", "-nostdin", "-ss", "{:.2f}".format(sec),
         "-i", clip, "-frames:v", "1", "-q:v", "2", out_jpg], cwd=workdir)
    return out_jpg


def _frame_has_face(jpg, cascades):
    """🚫 v15: чи є обличчя на кадрі (Haar-каскади OpenCV).
    Буд-який збій = вважаємо, що обличчя є (консервативно — безпечніше)."""
    try:
        img = cv2.imread(jpg)
        if img is None:
            return True
        h, w = img.shape[:2]
        if w > 480:  # зменшуємо — Haar працює швидше і стабільніше
            img = cv2.resize(img, (480, max(1, int(h * 480 / w))))
        gray = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        for cc in cascades:
            faces = cc.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5,
                                        minSize=(48, 48))
            if len(faces):
                return True
        return False
    except Exception:
        return True


def face_free_windows(clip, cascades, win=6.0, workdir=None):
    """🚫 v15: шукає у кліпі вікна по win секунд, на яких не видно обличчя:
    у кожному вікні дивлюся 2 пробні кадри (на 25% і 75% віконця).
    Повертає список (початок_с, тривалість_с)."""
    try:
        total = audio_duration(clip)
    except Exception:
        return []
    workdir = workdir or os.path.dirname(os.path.abspath(clip)) or "."
    jpg = os.path.join(workdir, "_facechk.jpg")
    windows = []
    t = 0.0
    while t < total - 0.5:
        dur = min(win, total - t)
        if dur < 1.0:
            break
        clean = True
        for off in (dur * 0.25, dur * 0.75):
            try:
                frame_grab(clip, t + off, jpg, workdir)
            except Exception:
                clean = False
                break
            if _frame_has_face(jpg, cascades):
                clean = False
                break
        if clean:
            windows.append((t, dur))
        t += dur
    try:
        os.remove(jpg)
    except OSError:
        pass
    return windows


def noface_pool(clips, need, workdir, say=None):
    """🚫 v15: збирає з кліпів пул фрагментів без обличчя (noface_XX.mp4).
    З кожного чистого вікна вирізається фрагмент; далі вони монтуються як звичайні
    кліпи. Повертає список шляхів; порожній — OpenCV нема або чистих вікон не знайшлось
    (тоді фон монтую зі звичайних кліпів як є)."""
    cascades = _face_cascades()
    if not cascades:
        if say:
            say("ℹ️ OpenCV не встановлено — фільтр обличчя пропускаю")
        return []
    want = min(24, max(int(need * 1.5), need + 4))
    out = []
    for clip in clips:
        if len(out) >= want:
            break
        try:
            wins = face_free_windows(clip, cascades, workdir=workdir)
        except Exception as e:
            if say:
                say("⚠️ Перевірка обличчя не вийшла ({}), кліп пропускаю".format(str(e)[:100]))
            continue
        if not wins:
            if say:
                say("🚫 {}: скрізь обличчя або чистих вікон не знайшов".format(os.path.basename(clip)))
            continue
        for (start, dur) in wins:
            if len(out) >= want:
                break
            frag = os.path.join(workdir, "noface_{:02d}.mp4".format(len(out)))
            try:
                run([ffmpeg_path(), "-y", "-hide_banner", "-nostdin",
                     "-ss", "{:.2f}".format(start), "-i", clip,
                     "-t", "{:.2f}".format(dur), "-an",
                     "-c:v", "libx264", "-crf", "23", "-preset", "veryfast",
                     "-pix_fmt", "yuv420p", frag])
                out.append(frag)
            except Exception:
                continue
    if out and say:
        say("🚫 Зібрав фрагментів без обличчя: {}".format(len(out)))
    elif not out and say:
        say("ℹ️ Чистих фрагментів без обличчя не знайшов — беру кліпи як є")
    return out


def _seo_keywords(text, limit=16):
    """📈 v15: ключові слова з тексту: фрази-біграми (частота ≥ 2) + частотні слова,
    без стоп-слів. Чиста логіка, без ключів і сервісів."""
    tokens = [w for w in re.findall(r"[A-Za-zА-Яа-яІіЇїЄєҐґ][A-Za-zА-Яа-яІіЇїЄєҐґ\-']*",
                                    (text or "").lower())
              if len(w) > 2 and w not in UA_STOPWORDS]
    if not tokens:
        return []
    uni = Counter(tokens)
    bi = Counter()
    for a, b in zip(tokens, tokens[1:]):
        if len(b) > 2 and b not in UA_STOPWORDS:
            bi[a + " " + b] += 1
    picked = [g for g, c in bi.most_common() if c >= 2][:8]
    for w, c in uni.most_common():
        if len(picked) >= limit:
            break
        if not any(w == p or w in p.split() for p in picked):
            picked.append(w)
    return picked[:limit]


def make_seo_pack(theme, text, workdir, say):
    """📈 v15: SEO-пак для YouTube — файл youtube-seo.txt у робочій папці:
    3 варіанти назви, опис, теги (лиміт YouTube ~500 символів), ключові слова,
    хештеги і закріплений коментар. Усе оптимізовано під пошук українською."""
    theme = " ".join((theme or "").split()) or "Моє відео"
    kws = _seo_keywords(theme + " " + (text or ""))
    short_theme = theme if len(theme) <= 55 else theme[:52].rstrip() + "…"
    titles = [
        "{} — огляд українською".format(short_theme),
        "Що варто знати про {}?".format(short_theme[:40]),
        "{}: усе головне за 10 хвилин".format(short_theme[:40]),
    ]
    tags = []
    for k in kws[:12]:
        if k not in tags:
            tags.append(k)
    for extra in (theme.lower(), "огляд українською", "українською",
                  "відео огляд", "для початківців"):
        if extra not in tags:
            tags.append(extra)
    tags_line = ", ".join(tags)
    if len(tags_line) > 480:  # YouTube: теги до 500 символів
        tags_line = tags_line[:480].rsplit(",", 1)[0]
    hashtags = []
    for k in kws[:5]:
        h = "#" + re.sub(r"[^\w]", "", k.replace(" ", "_"))
        if len(h) > 1 and h not in hashtags:
            hashtags.append(h)
    for h in ("#огляд", "#українською"):
        if h not in hashtags:
            hashtags.append(h)
    desc = [
        "{} — у цьому відео розбираємо головне простими словами.".format(short_theme),
        "",
        "Що всередині:",
        "• ключові моменти теми «{}»;".format(short_theme),
        "• з чого почати і на що звернути увагу;",
        "• короткі висновки, які легко застосувати.",
        "",
        "Подобається? Підпишися, щоб не пропустити нові огляди! 🔔",
        "",
        "Ключові слова: {}.".format(", ".join(kws[:10]) if kws else theme.lower()),
        "",
        " ".join(hashtags),
    ]
    pinned = ("Дякую за перегляд! 🙌 Напиши у коментарях, що ще розібрати "
              "по темі «{}» — читаю всі коментарі.").format(short_theme)
    lines = ["НАЗВА (обери один із трьох варіантів):"]
    lines += ["{}. {}".format(i, t) for i, t in enumerate(titles, 1)]
    lines += ["", "ОПИС:"] + desc
    lines += ["", "ТЕГИ (у YouTube через кому, лиміт 500 символів):", tags_line]
    lines += ["", "КЛЮЧОВІ СЛОВА:", ", ".join(kws) if kws else theme.lower()]
    lines += ["", "ХЕШТЕГИ (додай у кінець опису):", " ".join(hashtags)]
    lines += ["", "ЗАКРІПЛЕНИЙ КОМЕНТАР:", pinned]
    with open(os.path.join(workdir, "youtube-seo.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("📈 SEO-пак для YouTube: назва, опис, теги, хештеги, коментар — youtube-seo.txt")


def generate_video(query, voice_label, size_str, music, say, on_workdir=None, yt_url="", bg_files=None, yt_search_urls=None, auto_yt=True, yt_many=None, pin_images=None, sub_style="Класичні", vid_style="Без стилю", transition="Різко", trim_sil=False, cover=False, no_faces=False, seo=False, master=False, pack_mb=None, rate_pct=0, platform=None, upscale4k=False, autoscrape=False, overlays=False):
    """Повний цикл генерації. say — колбек журналу. Повертає робочу папку."""
    base = os.path.join(os.path.expanduser("~"), "Videos", "Generated")
    workdir = os.path.join(base, datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + re.sub(r'[^\w-]', '_', query[:30]))
    os.makedirs(workdir, exist_ok=True)
    if on_workdir:
        on_workdir(workdir)
    say("🔍 Перевіряю ffmpeg (якщо немає — встановлю сам, один раз)…")
    ensure_ffmpeg(say)
    ff = ffmpeg_path()
    w, h = size_str.split(" ")[0].split("x")
    say(f"▶️ Запит: {query}")
    say("📁 Робоча папка створена")

    text = narration_for(query)
    voice = VOICES[voice_label]
    say(f"🎙️ Озвучую голосом {voice_label}…")
    karaoke_words = tts_save_karaoke(text, voice, os.path.join(workdir, "voice.mp3"), say, rate_pct=rate_pct) if not trim_sil else None
    if karaoke_words is None:
        tts_save(text, voice, os.path.join(workdir, "voice.mp3"), say, rate_pct=rate_pct)
    else:
        say("🎤 Караоке-мітки зібрано: {} слів з точним таймінгом".format(len(karaoke_words)))
    if trim_sil:  # ✂️ v14: прибираємо довгі паузи з озвучки
        trim_out = os.path.join(workdir, "voice_trim.mp3")
        p, _ = remove_pauses(os.path.join(workdir, "voice.mp3"), trim_out, say)
        if os.path.abspath(p) == os.path.abspath(trim_out):
            try:
                os.replace(os.path.join(workdir, "voice.mp3"),
                           os.path.join(workdir, "voice_raw.mp3"))  # оригінал лишаємо поруч
                os.replace(trim_out, os.path.join(workdir, "voice.mp3"))
            except OSError:
                pass

    dur = audio_duration(os.path.join(workdir, "voice.mp3"))
    say(f"⏱️ Тривалість: {dur:.1f} с")
    beats = None  # 🥁 v23: битова сітка музики — фон розріжується у такт
    mpath = (music or "").strip()
    if mpath and os.path.isfile(mpath):
        say("🥁 Аналізую ритм музики (beat-sync фону)…")
        bgrid = beat_grid(mpath, dur)
        if bgrid:
            beats = bgrid[1]
            say("🥁 Ритм: ~{:.0f} BPM — зміни кадрів підішлю під бити".format(bgrid[0]))
        else:
            say("ℹ️ Ритм музики невиразний — монтую фон як звичайно")

    if karaoke_words:
        n = make_karaoke_srt(karaoke_words, dur, workdir)
        say("🎤 Караоке-субтитри: {} фраз синхронно з голосом".format(n))
    else:
        make_srt([s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()], dur, workdir)
    say("💬 Субтитри готові")

    bg = None
    if (yt_url or "").strip():
        try:
            say("▶️ Завантажую твоє відео з YouTube як фон")
            p = youtube_download(yt_url.strip(), workdir, 720, say, fixed_name="bg")
            if p and os.path.exists(p):
                bg_mp4 = os.path.join(workdir, "bg.mp4")
                if os.path.abspath(p) != os.path.abspath(bg_mp4):
                    if p.lower().endswith(".mp4"):
                        os.replace(p, bg_mp4)
                    else:
                        say("🔄 Конвертую у MP4…")
                        run([ff, "-y", "-hide_banner", "-nostdin", "-i", p,
                             "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", bg_mp4],
                            cwd=workdir)
                bg = bg_mp4
                say("🎬 Фон: твоє відео з YouTube")
        except Exception as e:
            say("⚠️ YouTube не вийшов ({}), шукаю фон сам…".format(str(e)[:200]))
            bg = None
    if not bg and yt_many:
        got = []
        for i, u in enumerate(yt_many):
            try:
                say("🔗 Посилання {}/{}: завантажую відео…".format(i + 1, len(yt_many)))
                p = youtube_download(u.strip(), workdir, 720, say,
                                     fixed_name="many{:02d}".format(i), max_sec=YT_CLIP_MAX_SEC)
                if p and os.path.exists(p):
                    got.append(p)
            except Exception as e:
                say("⚠️ Посилання не завантажилось: " + str(e)[:150])
        if got:
            try:
                say("✂️ Нарізаю фрагменти з {} відео для компіляції…".format(len(got)))
                bg = build_bg_from_clips(got, dur, w, h, workdir, transition=transition,
                                         no_faces=no_faces, say=say, beats=beats)
                say("🎬 Фон: компіляція фрагментів твоїх відео з YouTube")
            except Exception as e:
                say("⚠️ Фрагменти не зібралися ({}), шукаю фон далі…".format(str(e)[:200]))
                bg = None
        else:
            say("⚠️ З посилань нічого не завантажилось — шукаю фон далі")
    if not bg and yt_search_urls:
        got = []
        for i, u in enumerate(yt_search_urls):
            try:
                say("▶️ Обране з пошуку {}/{}: завантажую…".format(i + 1, len(yt_search_urls)))
                p = youtube_download(u, workdir, 720, say,
                                     fixed_name="ytsrc{:02d}".format(i), max_sec=YT_CLIP_MAX_SEC)
                if p and os.path.exists(p):
                    got.append(p)
            except Exception as e:
                say("⚠️ Обраний кліп не вдався: " + str(e)[:150])
        if got:
            say("🎞 Додано з пошуку: {} кліпів — ідуть у фон".format(len(got)))
            bg_files = list(bg_files or []) + got
        else:
            say("⚠️ З обраних у пошуку нічого не завантажилось — шукаю фон сам")

    if not bg and bg_files:
        try:
            say("🎞 Монтую фон з твоїх {} відео…".format(len(bg_files)))
            bg = build_bg_from_clips(list(bg_files), dur, w, h, workdir, transition=transition,
                                     no_faces=no_faces, say=say, beats=beats)
            say("🎬 Фон: твоя компіляція з кількох відео")
        except Exception as e:
            say("⚠️ Твої відео не зібралися ({}), шукаю фон сам…".format(str(e)[:200]))
            bg = None
    if not bg and pin_images:  # 🖼 v18: зображення, обрані у пошуку (Openverse / Pixabay / Pinterest)
        try:
            say("🖼 Монтую фон з {} обраних зображень…".format(len(pin_images)))
            bg = build_bg_from_images(list(pin_images), dur, w, h, workdir)
            say("🖼 Фон: твої обрані зображення")
        except Exception as e:
            say("⚠️ Зображення не зібралися ({}), шукаю фон сам…".format(str(e)[:200]))
            bg = None
    if not bg and auto_yt:
        # v9: сам шукаю на YouTube відео по словах теми (нуль ключів) і монтую у фон
        say("🔎 Шукаю на YouTube відео по темі «{}»…".format(query[:60]))
        results, err = yt_search(query, YT_SEARCH_LIMIT, say)
        got = []
        if not results:
            say("ℹ️ YouTube: " + (err or "нічого") + " — шукаю відкриті кліпи")
        for r in (results or [])[:4]:
            if len(got) >= 3:
                break
            d = int(r.get("dur") or 0)
            if d and (d < 10 or d > 3600):
                say("↩️ Пропускаю (тривалість {} с): {}".format(d, r["title"][:50]))
                continue
            try:
                say("🎬 Беру у фон: " + r["title"][:70])
                p = youtube_download(r["url"], workdir, 720, say,
                                     fixed_name="auto{:02d}".format(len(got)),
                                     max_sec=YT_CLIP_MAX_SEC)
                if p and os.path.exists(p):
                    got.append(p)
            except Exception as e:
                say("⚠️ Не завантажилось, пробую наступне: " + str(e)[:120])
        if got:
            try:
                say("🎞 Монтую фон з {} відео з YouTube по темі…".format(len(got)))
                bg = build_bg_from_clips(got, dur, w, h, workdir, transition=transition,
                                        no_faces=no_faces, say=say, beats=beats)
                say("🎬 Фон: відео, знайдені на YouTube по словах теми")
            except Exception as e:
                say("⚠️ YouTube-фон не зібрався ({}), шукаю відкриті кліпи…".format(str(e)[:200]))
                bg = None
        else:
            say("ℹ️ На YouTube нічого не підійшло — шукаю відкриті кліпи")
    if not bg:
        # Відео-кліпи: два незалежні джерела без ключів — Openverse, потім Wikimedia
        for source_name, fetch_fn in (("Openverse", fetch_openverse_videos),
                                      ("Wikimedia", fetch_wikimedia_videos)):
            if bg:
                break
            say("🎞️ Шукаю відкриті відео-кліпи (" + source_name + ", без API-ключа)...")
            clips, reason = fetch_fn(query, workdir, need=dur)
            if not clips:
                say("ℹ️ " + (reason or "кліпів не знайшов") + " — пробую далі")
                continue
            say("🎞️ Завантажено кліпів: " + str(len(clips)) + " (" + source_name + ", CC-ліцензії)")
            try:
                bg = build_bg_from_clips(clips, dur, w, h, workdir,
                                         no_faces=no_faces, say=say, beats=beats)
                say("🎬 Відеоряд змонтовано зі справжніх кліпів")
            except Exception as e:
                say("⚠️ Кліпи не зібралися ({}), пробую далі…".format(str(e)[:200]))
                bg = None
    if not bg:
        # Фото: два незалежні джерела без ключів — Openverse, потім Wikimedia
        say("🖼️ Шукаю зображення (Openverse → Wikimedia)...")
        imgs, reason = fetch_openverse_images(query, workdir)
        if not imgs:
            say("ℹ️ " + (reason or "Openverse недоступний") + " — пробую Wikimedia Commons")
            imgs, reason = fetch_wikimedia_images(query, workdir)
        if imgs:
            say("🖼️ Знайдено зображень: " + str(len(imgs)))
            try:
                bg = build_bg_from_images(imgs, dur, w, h, workdir)
            except Exception as e:
                say("⚠️ Фото не зібралися ({}), буде градієнтний фон".format(str(e)[:200]))
                bg = None
        else:
            say("⚠️ " + (reason or "джерела недоступні") + " — буде градієнтний фон")
    if os.path.exists(os.path.join(workdir, "credits.txt")):
        say("📄 Ліцензії та автори матеріалів: credits.txt у робочій папці")
    music = (music or "").strip()

    # Відеодоріжка
    if bg:
        vf_in = ["-stream_loop", "-1", "-i", "bg.mp4"]
        say("🖼️ Фон: зображення/відео")
    else:
        vf_in = ["-f", "lavfi", "-i", f"gradients=s={w}x{h}:c0=0x0f2027:c1=0x2c5364:speed=0.03"]
        say("🖼️ Генерую анімований градієнтний фон")

    # v14: стиль субтитрів (💬) і стилістика картинки (🎨) — один рядок фільтрів ffmpeg
    stl = SUBTITLE_STYLES.get(sub_style) or "FontSize=16"
    vfx = VIDEO_STYLES.get(vid_style) or ""
    vf_base = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
               "scale=out_color_matrix=bt709:out_range=tv,"
               "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv")
    if vfx:
        vf_base += "," + vfx

    cmd = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", "voice.mp3"]
    if music:
        cmd += ["-i", music]

    if music:
        cmd += ["-filter_complex",
                f"[0:v]{vf_base},"
                f"subtitles=sub.srt:force_style='{stl}'[v];"
                f"[2:a]volume=0.5[duck];"
                f"[duck][1:a]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck2];"
                f"[1:a][duck2]amix=inputs=2:duration=first:weights='1 1',loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a", "-shortest",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-vf",
                f"{vf_base},"
                f"subtitles=sub.srt:force_style='{stl}'"]

    enc = best_video_encoder_args()
    if enc[1] != "libx264":
        say("⚡ Апаратний кодек: " + enc[1])
    cmd += [*enc, "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-b:a", "160k", "final.mp4"]

    say("🚀 Рендерю відео…")
    try:
        run(cmd, cwd=workdir)
    except Exception as err:
        say("⚠️ Рендер із субтитрами не вдався — спробую простіший, без субтитрів…")
        say("📝 Причина: " + str(err)[:400])
        cmd2 = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", "voice.mp3",
                "-map", "0:v", "-map", "1:a", "-shortest"]
        cmd2 += ["-vf", vf_base, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11"]
        cmd2 += ["-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-b:a", "160k", "final.mp4"]
        run(cmd2, cwd=workdir)
        say("ℹ️ Відео готове без субтитрів; повний лог: ffmpeg-error.txt у робочій папці")
    if overlays:  # 🏷️ 2.0: плашка-заголовок + водяний знак + смуга прогресу
        overlays_pass(os.path.join(workdir, "final.mp4"), query, workdir, say)
    if cover:  # 📷 v14: обкладинка для YouTube
        try:
            make_cover(workdir, query, say)
        except Exception as e:
            say("⚠️ Обкладинка не вийшла: " + str(e)[:120])
    if seo:  # 📈 v15: SEO-пак для YouTube
        try:
            make_seo_pack(query, text, workdir, say)
        except Exception as e:
            say("⚠️ SEO-пак не вийшов: " + str(e)[:120])
    try:  # 🔍 v24: аудіо-лікар — тиша/кліпінг/довгі паузи у готовому відео
        audio_health_check(workdir, say)
    except Exception:
        pass
    try:  # 📄 v28: структуровані кредити всіх джерел — credits.json у робочій папці
        credits_to_json(workdir, say)
    except Exception:
        pass
    try:  # 🛡️ v28: QC-звіт — декодування -xerror, кадр-проби, підсумок qc.txt
        qc_report(workdir, say)
        qc_visual(workdir, say)  # 🛡️ 2.0: QC+ (контакт-шит, спалахи, пік гучності)
    except Exception:
        pass
    try:  # 📋 v28: маніфест генерації — manifest.json (артефакт-тека)
        write_manifest({"mode": "video", "theme": query, "voice": voice_label,
                        "size": size_str, "sub_style": sub_style, "vid_style": vid_style,
                        "transition": transition, "platform": platform}, workdir, say)
    except Exception:
        pass
    if master:  # 🔊 v27: two-pass EBU R128 — прозорий linear-майстеринг (−14 LUFS)
        try:
            loudnorm_master(os.path.join(workdir, "final.mp4"), say, workdir)
        except Exception as e:
            say("⚠️ Майстеринг гучності не вийшов ({}), лишаю як є".format(str(e)[:120]))
    if upscale4k:  # 📈 v34: фінал у 4К — YouTube дає 4К-завантаженням вищий бітрейт
        try:
            say("📈 Апскейл фіналу до 4К…")
            p4 = upscale_4k(os.path.join(workdir, "final.mp4"), say)
            if p4:
                os.replace(p4, os.path.join(workdir, "final.mp4"))
                say("📈 Фінал тепер 4К")
        except Exception as e:
            say("⚠️ Апскейл до 4К не вийшов ({}), лишаю вихідну роздільність".format(str(e)[:120]))
    if autoscrape:  # 🧹 v34: авто-чистка метаданих фіналу (нуль тегів, випадкова дата)
        try:
            scrub_metadata(os.path.join(workdir, "final.mp4"), False, say,
                           out_path=os.path.join(workdir, "final.mp4"))
            say("🧹 Метадані фіналу очищено (final.mp4 без тегів, дата випадкова)")
        except Exception as e:
            say("⚠️ Чистка метаданих не вийшла ({}), фінал лишається як є".format(str(e)[:120]))
    if pack_mb:  # 📦 v27: копія під точний розмір (Discord/пошта/Shorts) — поруч з оригіналом
        try:
            compress_to_size(os.path.join(workdir, "final.mp4"), pack_mb, say, workdir)
        except Exception as e:
            say("⚠️ Стиснення до розміру не вийшло ({}), оригінал лишається".format(str(e)[:120]))
    try:  # 📝 v30: approval.txt — чек-лист перед публікацією
        write_approval({"режим": "відео", "тема": query, "голос": voice_label, "платформа": platform},
                       workdir, say)
    except Exception:
        pass
    say(f"✅ ГОТОВО: {os.path.join(workdir, 'final.mp4')}")
    return workdir


def parse_script(text):
    """Сценарій у частини: блоки розділені порожніми рядками.
    Керуючі рядки на початку частини (будь-яким порядком, далі — текст озвучки):
      «Пошук: запит» (або «Знайти:», «Search:») — запит для YouTube-пошуку фону частини;
      «Кліп: посилання» (або «Відео:», «Clip:») — ТВОЄ конкретне YouTube-відео у фон
      частини (якщо не завантажиться — шукаю автоматично за запитом);
      «Тривалість: 12» (або «Час:», «Duration:») — цільова тривалість частини
      в секундах: озвучка підганяється темпом (голос лишається природним),
      фон — рівно стільки; караоке-мітки стискаються разом зі звуком."""
    scenes = []
    for block in re.split(r"\n[ \t]*\n+", (text or "").strip()):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        q, url, dur = None, None, None
        while lines:
            m = re.match(r"(?i)^(?:пошук|знайти|search)\s*[:\-—]\s*(.+)$", lines[0])
            u = re.match(r"(?i)^(?:кліп|відео|clip)\s*[:\-—]\s*(\S+)$", lines[0])
            t = re.match(r"(?i)^(?:тривалість|час|duration|dur)\s*[:\-—]\s*([0-9]+(?:[.,][0-9]+)?)\s*(?:с(?:ек)?)?\s*$", lines[0])
            if m and not q:
                q = m.group(1).strip()
                lines = lines[1:]
            elif u and not url:
                url = u.group(1).strip()
                lines = lines[1:]
            elif t and dur is None:
                dur = float(t.group(1).replace(",", "."))
                lines = lines[1:]
            else:
                break
        body = " ".join(lines).strip()
        if not body:
            continue
        if url and not re.match(r"(?i)^https?://", url):
            url = None
        if dur and not (2 <= dur <= 600):  # 🎯 v27: поза розумним діапазоном — ігнорую
            dur = None
        if not q:
            words = [w for w in re.sub(r"[^\w\s\-]", " ", body).split() if len(w) > 2]
            q = " ".join(words[:6]) if words else body[:40]
        scenes.append({"q": q, "text": body, "url": url, "dur": dur})
    return scenes


def scene_segment(clip, dur, w, h, workdir, idx, start=0.0):
    """Фон однієї частини: нормалізується під розмір і триває рівно dur секунд
    (короткий кліп зациклюється, довгий обрізається).
    v15: start — з якої секунди кліпу брати фрагмент (чисте від обличчя вікно)."""
    ff = ffmpeg_path()
    seg = os.path.join(workdir, "pseg{:02d}.mp4".format(idx))
    vf = ("scale={}:{}:force_original_aspect_ratio=increase,crop={}:{},"
          "fps=25,setsar=1,format=yuv420p").format(int(w), int(h), int(w), int(h))
    pre = ["-ss", "{:.2f}".format(start)] if start > 0.01 else []
    run([ff, "-y", "-hide_banner", "-nostdin", *pre, "-stream_loop", "-1", "-i", clip,
         "-t", "{:.2f}".format(dur + 0.2), "-an", "-vf", vf,
         "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", seg])
    return seg


def gradient_segment(dur, w, h, workdir, idx):
    """Резервний фон частини, коли на YouTube нічого не знайшлось."""
    ff = ffmpeg_path()
    seg = os.path.join(workdir, "pseg{:02d}.mp4".format(idx))
    run([ff, "-y", "-hide_banner", "-nostdin",
         "-f", "lavfi", "-i", "gradients=s={0}x{1}:c0=0x0f2027:c1=0x2c5364:speed=0.03".format(int(w), int(h)),
         "-t", "{:.2f}".format(dur + 0.2),
         "-vf", "fps=25,setsar=1,format=yuv420p",
         "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", seg])
    return seg


def concat_audio(mp3s, out_mp3):
    """Склеює озвучки частин в один voice.mp3."""
    if len(mp3s) == 1:
        shutil.copyfile(mp3s[0], out_mp3)
        return out_mp3
    ff = ffmpeg_path()
    cmd = [ff, "-y", "-hide_banner", "-nostdin"]
    for m in mp3s:
        cmd += ["-i", m]
    cmd += ["-filter_complex", "concat=n={}:v=0:a=1".format(len(mp3s)),
            "-c:a", "libmp3lame", "-b:a", "48k", "-ar", "24000", out_mp3]
    run(cmd)
    return out_mp3


def make_srt_scenes(scenes, durs, workdir):
    """Субтитри для сценарію: речення кожної частини вкладаються у її час."""
    def fmt(t):
        h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")
    lines, t0 = [], 0.0
    for sc, d in zip(scenes, durs):
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", sc["text"]) if s.strip()]
        if not sents:
            sents = [sc["text"]]
        weights = [max(len(s), 1) for s in sents]
        scale = d / sum(weights)
        t = t0
        for s, wgt in zip(sents, weights):
            end = min(t + wgt * scale, t0 + d)
            lines.append(f"{len(lines)+1}\n{fmt(t)} --> {fmt(end)}\n{s}\n")
            t = end
        t0 += d
    with open(os.path.join(workdir, "sub.srt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def generate_script_video(script_text, voice_label, size_str, music, say, on_workdir=None, sub_style="Класичні", vid_style="Без стилю", trim_sil=False, cover=False, no_faces=False, seo=False, master=False, pack_mb=None, rate_pct=0, platform=None, upscale4k=False, autoscrape=False, overlays=False):
    """Генерація за сценарієм: кожна частина озвучується окремо і отримує
    ВЛАСНИЙ фон — кліп знайдений на YouTube автоматичним пошуком (нуль ключів).
    Порядок фону частин = порядку частин у сценарії."""
    scenes = parse_script(script_text)
    if not scenes:
        raise RuntimeError("Сценарій порожній — розділи частини порожнім рядком")
    if len(scenes) > SCRIPT_MAX_SCENES:
        say("⚠️ Частин {} — беру перші {}".format(len(scenes), SCRIPT_MAX_SCENES))
        scenes = scenes[:SCRIPT_MAX_SCENES]
    base = os.path.join(os.path.expanduser("~"), "Videos", "Generated")
    workdir = os.path.join(base, datetime.now().strftime("%Y%m%d_%H%M%S") + "_scenario")
    os.makedirs(workdir, exist_ok=True)
    if on_workdir:
        on_workdir(workdir)
    say("🔍 Перевіряю ffmpeg (якщо немає — встановлю сам, один раз)…")
    ensure_ffmpeg(say)
    ff = ffmpeg_path()
    w, h = size_str.split(" ")[0].split("x")
    voice = VOICES[voice_label]
    say("🎬 Сценарій прийнято: {} частин".format(len(scenes)))

    # 1) Озвучка кожної частини окремо
    say("🎙️ Озвучую частини голосом {}…".format(voice_label))
    part_words = []  # 🎤 v25: мітки слів кожної частини (None — якщо караоке недоступне)
    mp3s, durs = [], []
    for i, sc in enumerate(scenes):
        m = os.path.join(workdir, "voice_{:02d}.mp3".format(i))
        pw = tts_save_karaoke(sc["text"], voice, m, say, rate_pct=rate_pct) if not trim_sil else None
        if pw is None:
            tts_save(sc["text"], voice, m, say, rate_pct=rate_pct)
        part_words.append(pw)
        if trim_sil:  # ✂️ v14: прибираємо паузи в кожній частині окремо
            t_out = os.path.join(workdir, "vtrim_{:02d}.mp3".format(i))
            p, _ = remove_pauses(m, t_out, say)
            if os.path.abspath(p) == os.path.abspath(t_out):
                try:
                    os.replace(t_out, m)
                except OSError:
                    pass
        if sc.get("dur"):  # 🎯 v27: озвучка «під рядок» — підганяю темп під ціль
            try:
                d0 = audio_duration(m)
                fitted = speed_fit(m, sc["dur"], workdir, say)
                if fitted != m:
                    m = fitted
                    if part_words[i]:  # 🎤 караоке-мітки стискаються разом зі звуком
                        k = max(audio_duration(m), 0.01) / d0
                        part_words[i] = [(w, s0 * k, e0 * k) for (w, s0, e0) in part_words[i]]
            except Exception as e:
                say("⚠️ Підгонка тривалості не вийшла ({}), лишаю як є".format(str(e)[:100]))
        d = audio_duration(m)
        mp3s.append(m)
        durs.append(max(d, 1.0))
        say("🎙️ Частина {}/{} готова: {:.1f} с".format(i + 1, len(scenes), d))
    concat_audio(mp3s, os.path.join(workdir, "voice.mp3"))
    total = sum(durs)
    say("⏱️ Загальна тривалість: {:.1f} с".format(total))

    # 2) Субтитри по частинах
    karaoke_all = []  # 🎤 v25: мітки всіх частин зі зсувом на старт кожної у склеєнці
    acc = 0.0
    for pw, d in zip(part_words, durs):
        if pw:
            karaoke_all.extend((w, s0 + acc, e0 + acc) for (w, s0, e0) in pw)
        acc += d
    if karaoke_all:
        n = make_karaoke_srt(karaoke_all, total, workdir)
        say("🎤 Караоке-субтитри: {} фраз синхронно з голосом".format(n))
    else:
        make_srt_scenes(scenes, durs, workdir)
    say("💬 Субтитри готові")

    # 3) Фон кожної частини: своє відео («Кліп: …») або авто-пошук YouTube
    segs = []
    face_cascades = _face_cascades() if no_faces else []  # 🚫 v15
    if no_faces and not face_cascades:
        say("ℹ️ OpenCV не встановлено — фільтр обличчя пропускаю")
    for i, sc in enumerate(scenes):
        clip = None
        if sc.get("url"):
            say("🔗 Частина {}/{}: беру ТВОЄ відео {}".format(i + 1, len(scenes), sc["url"][:70]))
            try:
                clip = youtube_download(sc["url"], workdir, 720, say,
                                        fixed_name="scene{:02d}".format(i),
                                        max_sec=YT_CLIP_MAX_SEC)
            except Exception as e:
                say("⚠️ Твоє відео не завантажилось ({}), шукаю заміну…".format(str(e)[:120]))
                clip = None
        if not clip:
            say("🔎 Частина {}/{}: шукаю фон «{}»".format(i + 1, len(scenes), sc["q"]))
            results, err = yt_search(sc["q"], YT_SEARCH_LIMIT, say)
            if not results:
                say("ℹ️ Пошук: " + (err or "нічого") + " — буде градієнт")
            for r in (results or [])[:4]:
                d = int(r.get("dur") or 0)
                if d and (d < 10 or d > 3600):
                    say("↩️ Пропускаю (тривалість {} с): {}".format(d, r["title"][:50]))
                    continue
                try:
                    say("🎬 Беру: " + r["title"][:70])
                    clip = youtube_download(r["url"], workdir, 720, say,
                                            fixed_name="scene{:02d}".format(i),
                                            max_sec=YT_CLIP_MAX_SEC)
                    break
                except Exception as e:
                    say("⚠️ Не завантажилось, пробую наступне: " + str(e)[:120])
                    clip = None
        if clip:
            start = 0.0
            if face_cascades:  # 🚫 v15: чисте від обличчя вікно цього кліпу
                try:
                    wins = face_free_windows(clip, face_cascades, workdir=workdir)
                    if wins:
                        start = wins[0][0]
                        say("🚫 Частині {}: фрагмент без обличчя з {:.1f} с".format(i + 1, start))
                    else:
                        say("ℹ️ Частині {}: чистих вікон без обличчя нема — беру кліп як є".format(i + 1))
                except Exception as e:
                    say("⚠️ Перевірка обличчя не вийшла ({}), беру кліп як є".format(str(e)[:100]))
            try:
                segs.append(scene_segment(clip, durs[i], w, h, workdir, i, start=start))
                say("✅ Фон частини {} змонтовано".format(i + 1))
            except Exception as e:
                say("⚠️ Кліп частини {} не обробився ({}), буде градієнт".format(i + 1, str(e)[:120]))
                segs.append(gradient_segment(durs[i], w, h, workdir, i))
        else:
            segs.append(gradient_segment(durs[i], w, h, workdir, i))

    # 4) Склеюємо фон частин у один відеоряд
    lst = os.path.join(workdir, "plist.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for s in segs:
            f.write("file '{}'\n".format(s))
    bg = os.path.join(workdir, "bg.mp4")
    try:
        run([ff, "-y", "-hide_banner", "-nostdin", "-f", "concat", "-safe", "0",
             "-i", lst, "-c", "copy", bg])
    except Exception:
        say("🔄 Склеюю фон повторним кодуванням…")
        run([ff, "-y", "-hide_banner", "-nostdin", "-f", "concat", "-safe", "0",
             "-i", lst, "-c:v", "libx264", "-crf", "22", "-preset", "veryfast",
             "-pix_fmt", "yuv420p", "-an", bg])
    say("🎞 Відеоряд змонтовано по частинах сценарію")

    # 5) Фінальний рендер: фон + озвучка + субтитри (+ музика)
    music = (music or "").strip()
    vf_in = ["-stream_loop", "-1", "-i", "bg.mp4"]
    stl = SUBTITLE_STYLES.get(sub_style) or "FontSize=16"  # v14 💬: стиль субтитрів
    vfx = VIDEO_STYLES.get(vid_style) or ""               # v14 🎨: стилістика картинки
    vf_base = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
               "scale=out_color_matrix=bt709:out_range=tv,"
               "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv")
    if vfx:
        vf_base += "," + vfx
    cmd = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", "voice.mp3"]
    if music:
        cmd += ["-i", music]
    if music:
        cmd += ["-filter_complex",
                f"[0:v]{vf_base},"
                f"subtitles=sub.srt:force_style='{stl}'[v];"
                f"[2:a]volume=0.5[duck];"
                f"[duck][1:a]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck2];"
                f"[1:a][duck2]amix=inputs=2:duration=first:weights='1 1',loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a", "-shortest",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-vf",
                f"{vf_base},"
                f"subtitles=sub.srt:force_style='{stl}'"]
    enc = best_video_encoder_args()
    if enc[1] != "libx264":
        say("⚡ Апаратний кодек: " + enc[1])
    cmd += [*enc, "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-b:a", "160k", "final.mp4"]
    say("🚀 Рендерю відео…")
    try:
        run(cmd, cwd=workdir)
    except Exception as err:
        say("⚠️ Рендер із субтитрами не вдався — рендерю без субтитрів…")
        say("📝 Причина: " + str(err)[:400])
        cmd2 = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", "voice.mp3",
                "-map", "0:v", "-map", "1:a", "-shortest"]
        cmd2 += ["-vf", vf_base, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11"]
        cmd2 += ["-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-b:a", "160k", "final.mp4"]
        run(cmd2, cwd=workdir)
        say("ℹ️ Відео готове без субтитрів; повний лог: ffmpeg-error.txt у робочій папці")
    if overlays:  # 🏷️ 2.0: плашка-заголовок (перша частина) + знак + смуга прогресу
        overlays_pass(os.path.join(workdir, "final.mp4"),
                      (scenes[0]["text"].splitlines()[0].strip()
                       if scenes and scenes[0]["text"].splitlines()
                       else (scenes[0]["q"] if scenes else "")),
                      workdir, say)
    if cover:  # 📷 v14: обкладинка — назва з першої частини сценарію
        try:
            first_line = scenes[0]["text"].splitlines()[0].strip() if scenes else ""
            make_cover(workdir, first_line or "Моє відео", say)
        except Exception as e:
            say("⚠️ Обкладинка не вийшла: " + str(e)[:120])
    if seo:  # 📈 v15: SEO-пак — тема з першої частини + текст усього сценарію
        try:
            make_seo_pack(scenes[0]["q"] if scenes else "Моє відео",
                          " ".join(sc["text"] for sc in scenes), workdir, say)
        except Exception as e:
            say("⚠️ SEO-пак не вийшов: " + str(e)[:120])
    try:  # 📑 v30: розділи YouTube за частинами сценарію — chapters.txt
        make_chapters(scenes, durs, workdir, say)
    except Exception:
        pass
    try:  # 🔍 v24: аудіо-лікар — тиша/кліпінг/довгі паузи у готовому відео
        audio_health_check(workdir, say)
    except Exception:
        pass
    try:  # 📄 v28: структуровані кредити всіх джерел — credits.json у робочій папці
        credits_to_json(workdir, say)
    except Exception:
        pass
    try:  # 🛡️ v28: QC-звіт — декодування -xerror, кадр-проби, підсумок qc.txt
        qc_report(workdir, say)
        qc_visual(workdir, say)  # 🛡️ 2.0: QC+ (контакт-шит, спалахи, пік гучності)
    except Exception:
        pass
    try:  # 📋 v28: маніфест генерації — manifest.json (артефакт-тека)
        write_manifest({"mode": "script", "voice": voice_label, "size": size_str,
                        "sub_style": sub_style, "vid_style": vid_style,
                        "scenes": [{"text": sc.get("text"), "q": sc.get("q"),
                                    "url": sc.get("url"), "dur": sc.get("dur")}
                                   for sc in scenes], "platform": platform}, workdir, say)
    except Exception:
        pass
    if master:  # 🔊 v27: two-pass EBU R128 — прозорий linear-майстеринг (−14 LUFS)
        try:
            loudnorm_master(os.path.join(workdir, "final.mp4"), say, workdir)
        except Exception as e:
            say("⚠️ Майстеринг гучності не вийшов ({}), лишаю як є".format(str(e)[:120]))
    if upscale4k:  # 📈 v34: фінал у 4К — YouTube дає 4К-завантаженням вищий бітрейт
        try:
            say("📈 Апскейл фіналу до 4К…")
            p4 = upscale_4k(os.path.join(workdir, "final.mp4"), say)
            if p4:
                os.replace(p4, os.path.join(workdir, "final.mp4"))
                say("📈 Фінал тепер 4К")
        except Exception as e:
            say("⚠️ Апскейл до 4К не вийшов ({}), лишаю вихідну роздільність".format(str(e)[:120]))
    if autoscrape:  # 🧹 v34: авто-чистка метаданих фіналу (нуль тегів, випадкова дата)
        try:
            scrub_metadata(os.path.join(workdir, "final.mp4"), False, say,
                           out_path=os.path.join(workdir, "final.mp4"))
            say("🧹 Метадані фіналу очищено (final.mp4 без тегів, дата випадкова)")
        except Exception as e:
            say("⚠️ Чистка метаданих не вийшла ({}), фінал лишається як є".format(str(e)[:120]))
    if pack_mb:  # 📦 v27: копія під точний розмір (Discord/пошта/Shorts) — поруч з оригіналом
        try:
            compress_to_size(os.path.join(workdir, "final.mp4"), pack_mb, say, workdir)
        except Exception as e:
            say("⚠️ Стиснення до розміру не вийшло ({}), оригінал лишається".format(str(e)[:120]))
    try:  # 📝 v30: approval.txt — чек-лист перед публікацією
        write_approval({"режим": "сценарій", "частин": len(scenes),
                        "голос": voice_label, "платформа": platform}, workdir, say)
    except Exception:
        pass
    say(f"✅ ГОТОВО: {os.path.join(workdir, 'final.mp4')}")
    return workdir


def load_pixabay_key():
    """🎵 v16: ключ Pixabay живе лише на цьому комп'ютері (у папці інструментів)."""
    try:
        with open(PIXABAY_KEY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


def save_pixabay_key(key):
    """Зберігає ключ локально — у код і GitHub він не потрапляє."""
    os.makedirs(TOOLS_DIR, exist_ok=True)
    with open(PIXABAY_KEY_FILE, "w", encoding="utf-8") as f:
        f.write(key.strip())


def load_ollama_conf():
    """🧠 v29: URL і модель Ollama — лише на цьому комп'ютері (як ключ Pixabay).
    Файла нема — дефолти: локальний сервер, модель ще не обрана (Tier 2 спить)."""
    try:
        with open(OLLAMA_CONF_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {"url": "http://localhost:11434", "model": "", "models": [], "provider": "ollama"}


def save_ollama_conf(url, model, models, provider="ollama"):
    """🧠 v29 / 🌐 v31 / 📏 v32: зберігає URL/модель/список/провайдер локально —
    у код і GitHub не потрапляє. Поле "rules" (правила проєкту) не затираю."""
    try:
        os.makedirs(TOOLS_DIR, exist_ok=True)
        old = load_ollama_conf()  # 📏 v32: читаю старе — "rules" лишаються
        if not isinstance(old, dict):
            old = {}
        old.update({"url": (url or "").strip(), "model": (model or "").strip(),
                    "provider": (provider or "ollama").strip() or "ollama",
                    "models": list(models or [])[:30]})
        with open(OLLAMA_CONF_FILE, "w", encoding="utf-8") as f:
            json.dump(old, f, ensure_ascii=False, indent=1)
    except OSError:
        pass


def project_rules():
    """📏 v32: правила проєкту для Асистента (abide-урок) — список рядків із
    поля "rules" локального tools/ollama.json. Криве або порожнє — дефолти.
    Fail-open: правила — надбудова над Tier 2, не ламають його."""
    try:
        rules = load_ollama_conf().get("rules")
        if isinstance(rules, list) and rules:
            ok = [str(r).strip() for r in rules if str(r or "").strip()]
            if ok:
                return ok[:12]
    except Exception:
        pass
    return ["Відповідай українською, простими словами.",
            "Не пропонуй API-ключі й платні сервіси.",
            "Сценарій: 3–6 частин, 2–4 речення в частині."]


def pixabay_music_search(key, query, limit, say):
    """🎵 v16: пошук безкоштовної музики Pixabay (Content License: комерційне
    використання без згадки автора). Ключ користувача — не частина програми."""
    try:
        r = requests.get("https://pixabay.com/api/music/",
                         params={"key": key, "q": query, "per_page": min(int(limit), 20)},
                         headers={"User-Agent": UA_STRING}, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return [], "Pixabay не відповів: " + str(e)[:120]
    results = []
    for h in (data.get("hits") or []):
        url = h.get("audio") or h.get("audio_url") or h.get("download_url") or ""
        if not url:
            continue
        results.append({
            "url": url,
            "title": " ".join(((h.get("title") or "трек")).split()),
            "dur": int(h.get("duration") or 0),
            "author": " ".join(((h.get("user") or "")).split()),
        })
    return results, ""


def pixabay_download(url, outdir, say):
    """⬇️ v16: один mp3 з Pixabay у папку треків (пряме посилання, без ключа)."""
    os.makedirs(outdir, exist_ok=True)
    name = re.sub(r"[^\w\-. ]", "_", (url.rsplit("?", 1)[0].rsplit("/", 1)[-1] or "track"))[:60]
    if not name.lower().endswith(".mp3"):
        name += ".mp3"
    path = os.path.join(outdir, name)
    base, n = path[:-4], 1
    while os.path.exists(path):
        path = "{}_{}.mp3".format(base, n)
        n += 1
    with requests.get(url, stream=True, timeout=180,
                      headers={"User-Agent": UA_STRING}) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(65536):
                if chunk:
                    f.write(chunk)
    return path


def pinterest_search(query, limit, say):
    """🖼 v17: пошук зображень Pinterest по запиту — публічний веб-ендпоінт
    пошуку, без жодних ключів. Зображення на Pinterest належать їхнім авторам:
    для особистих відео — ок, для монетизації — лише свої або вільні."""
    q = " ".join((query or "").split())
    if not q:
        return [], "порожній запит"
    data = json.dumps({"options": {"query": q, "bookmarks": None,
                                   "auto_correction_disabled": False,
                                   "redux_normalize_feed": True},
                       "context": {}}, separators=(",", ":"))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*, q=0.01",
        "Referer": "https://www.pinterest.com/",
        "X-Requested-With": "XMLHttpRequest",
    }
    try:
        r = requests.get("https://www.pinterest.com/resource/BaseSearchResource/get/",
                         params={"source_url": "/search/pins/?q=" + quote_plus(q),
                                 "data": data},
                         headers=headers, timeout=30)
        r.raise_for_status()
        js = r.json()
    except Exception as e:
        return [], "Pinterest не відповів: " + str(e)[:120]
    raw = []
    try:
        raw = (js.get("resource_response", {}).get("data", {})
                .get("results") or [])
    except Exception:
        raw = []
    out = []
    for p in raw:
        if not isinstance(p, dict):
            continue
        imgs = p.get("images") or {}
        big = imgs.get("orig") or imgs.get("736x") or imgs.get("474x") or {}
        u = big.get("url") or p.get("image_large_url") or ""
        if not u:
            continue
        title = " ".join(((p.get("grid_title") or p.get("title")
                           or p.get("description") or "зображення")[:60]).split())
        out.append({"url": u, "title": title})
        if len(out) >= int(limit):
            break
    return out, ""


def pinterest_download(url, say):
    """⬇️ v18: одне обране зображення пошуку (Openverse / Pixabay / Pinterest) у папку інструментів."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = os.path.join(PINS_DIR, ts)
    os.makedirs(outdir, exist_ok=True)
    ext = ".jpg"
    low = url.rsplit("?", 1)[0].lower()
    for e in (".png", ".webp", ".gif"):
        if low.endswith(e):
            ext = e
            break
    path = os.path.join(outdir, "pin{:03d}{}".format(len(os.listdir(outdir)) + 1, ext))
    with requests.get(url, stream=True, timeout=120,
                      headers={"User-Agent": "Mozilla/5.0"}) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(65536):
                if chunk:
                    f.write(chunk)
    return path


def openverse_images_search(query, limit, say):
    """🌍 v18: пошук фото Openverse — відкриті ліцензії, БЕЗ ключа (як і кліпи)."""
    try:
        r = requests.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query, "page_size": min(limit, 20),
                    "license_type": "commercial,modification"},
            headers={"User-Agent": UA_STRING, "Api-User-Agent": UA_STRING}, timeout=25)
        if r.status_code != 200:
            return [], "Openverse: HTTP {}".format(r.status_code)
        out = []
        for it in r.json().get("results", []):
            u = it.get("url")
            if not u or (it.get("width") or 0) < 800:
                continue
            out.append({
                "url": u,
                "title": (it.get("title") or "фото Openverse")[:70],
                "credit": "🖼 {} — ліцензія {} — {} — {}".format(
                    (it.get("title") or "?")[:60], it.get("license") or "?",
                    it.get("creator") or "?", it.get("foreign_landing_url") or "")})
        if not out:
            return [], "Openverse: нічого підходящого за запитом"
        return out, None
    except Exception as e:
        return [], ("Openverse: {}".format(e))[:150]


def pixabay_images_search(key, query, limit, say):
    """🖼 v18: пошук фото Pixabay — офіційний API; той самий локальний ключ, що для музики.
    Ліцензія Pixabay: вільне використання, атрибуція не потрібна."""
    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={"key": key, "q": query, "per_page": min(limit, 24),
                    "image_type": "photo", "orientation": "horizontal",
                    "min_width": 1280, "safesearch": "true"},
            headers={"User-Agent": UA_STRING}, timeout=25)
        if r.status_code != 200:
            return [], "Pixabay: HTTP {} — {}".format(r.status_code, r.text[:140])
        out = []
        for h in r.json().get("hits", []):
            u = h.get("largeImageURL") or h.get("fullHDURL") or h.get("webformatURL")
            if not u:
                continue
            out.append({
                "url": u,
                "title": (h.get("tags") or "фото Pixabay")[:70],
                "credit": "🖼 Pixabay — {} — {}".format(
                    h.get("user") or "?", h.get("pageURL") or "")})
        if not out:
            return [], "Pixabay: нічого не знайшов за запитом"
        return out, None
    except Exception as e:
        return [], ("Pixabay: {}".format(e))[:150]


def load_suno_cookie():
    """🎼 v19: cookie сесії Suno живе лише на цьому комп'ютері (у папці інструментів)."""
    try:
        with open(SUNO_COOKIE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


def save_suno_cookie(cookie):
    """Зберігає cookie локально — у код і GitHub він не потрапляє."""
    os.makedirs(TOOLS_DIR, exist_ok=True)
    with open(SUNO_COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write(cookie.strip())


def _suno_headers(jwt, cookie):
    """Заголовки мобільного клієнта Suno (реверс-інжиніринг Android-застосунку)."""
    did = ""
    for part in cookie.split(";"):
        p = part.strip()
        if p.startswith("ajs_anonymous_id="):
            did = p.split("=", 1)[1].strip('"')
            break
    return {
        "Authorization": "Bearer " + jwt,
        "Cookie": cookie,
        "Affiliate-Id": "undefined",
        "Device-Id": did or str(uuid.uuid4()),
        "x-suno-client": "Android prerelease-4nt180t 1.0.42",
        "X-Requested-With": "com.suno.android",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
    }


def suno_get_jwt(cookie, say):
    """🔑 v19: cookie сесії → короткий JWT-токен (~50 хв) через auth-сервіс Clerk."""
    client = ""
    for part in cookie.split(";"):
        p = part.strip()
        if p.startswith("__client="):
            client = p.split("=", 1)[1]
            break
    if not client:
        raise RuntimeError("у cookie нема __client — скопіюй ЦІЛИЙ заголовок Cookie з браузера")
    common = {"Authorization": client, "Cookie": cookie,
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
    qs = "?__clerk_api_version=2025-11-10&_clerk_js_version=" + SUNO_CLERK_V
    say("🎼 Запитую сесію Suno…")
    r = requests.get(SUNO_AUTH + "/v1/client" + qs, headers=common, timeout=30)
    r.raise_for_status()
    sid = (r.json().get("response") or {}).get("last_active_session_id")
    if not sid:
        raise RuntimeError("у cookie нема активної сесії — увійди на suno.com і скопіюй cookie знову")
    r = requests.post(SUNO_AUTH + "/v1/client/sessions/" + sid + "/tokens" + qs,
                      headers=common, timeout=30)
    r.raise_for_status()
    jwt = r.json().get("jwt")
    if not jwt:
        raise RuntimeError("Suno не дав токен — cookie, схоже, прострочений")
    return jwt


def suno_generate(cookie, description, tags, instrumental, say):
    """🎼 v19: замовляю 2 треки в Suno за описом/стилем. Повертаю (jwt, список id кліпів)."""
    jwt = suno_get_jwt(cookie, say)
    h = _suno_headers(jwt, cookie)
    try:
        r = requests.post(SUNO_API + "/api/c/check", headers=h,
                          json={"ctype": "generation"}, timeout=30)
        if r.status_code == 200 and (r.json() or {}).get("required"):
            raise RuntimeError("Suno просить капчу на цьому запиті — згенеруй трек у браузері на suno.com і скачай його там")
    except RuntimeError:
        raise
    except Exception:
        pass  # перевірка капчі не критична — пробую сам запит
    desc = description or ""
    if tags:
        desc = (desc + " | Стиль: " + tags).strip(" |")
    if not desc:
        desc = "calm instrumental background track"
    body = {"make_instrumental": bool(instrumental), "mv": "chirp-v4",
            "prompt": "", "generation_type": "TEXT", "continue_at": None,
            "continue_clip_id": None, "task": None, "token": None,
            "gpt_description_prompt": desc[:900]}
    say("🎼 Генерую 2 треки в Suno (1–3 хв)…")
    r = requests.post(SUNO_API + "/api/generate/v2/", headers=h, json=body, timeout=60)
    if r.status_code != 200:
        say("… модель chirp-v4 недоступна, пробую chirp-v3-5")
        body["mv"] = "chirp-v3-5"
        r = requests.post(SUNO_API + "/api/generate/v2/", headers=h, json=body, timeout=60)
    r.raise_for_status()
    clips = r.json().get("clips") or []
    ids = [c.get("id") for c in clips if c.get("id")]
    if not ids:
        raise RuntimeError("Suno не повернув кліпи (HTTP " + str(r.status_code) + ")")
    return jwt, ids


def suno_wait_and_download(cookie, jwt, ids, say, timeout=300):
    """⏳ v19: чекаю, поки Suno згенерує треки, і скачую готові mp3 у папку MixTracks."""
    h = _suno_headers(jwt, cookie)
    os.makedirs(MIX_TRACKS_DIR, exist_ok=True)
    deadline = time.time() + timeout
    done, saved = set(), []
    while time.time() < deadline and len(done) < len(ids):
        time.sleep(6)
        try:
            r = requests.get(SUNO_API + "/api/feed/v2",
                             params={"ids": ",".join(ids)}, headers=h, timeout=30)
            r.raise_for_status()
            clips = r.json().get("clips") or []
        except Exception as e:
            say("… ще перевіряю (" + str(e)[:60] + ")")
            continue
        for c in clips:
            cid = c.get("id")
            if not cid or cid in done:
                continue
            st = (c.get("status") or "").lower()
            if st == "error":
                done.add(cid)
                say("⚠️ Трек не вийшов: " + ((c.get("metadata") or {}).get("error_message") or "помилка Suno"))
            elif st in ("streaming", "complete") and c.get("audio_url"):
                done.add(cid)
                title = re.sub(r"[^\w\-. ]", "_", " ".join((c.get("title") or "suno_track").split()))[:60]
                if not title:
                    title = "suno_track"
                path = os.path.join(MIX_TRACKS_DIR, title + ".mp3")
                base, n = path[:-4], 1
                while os.path.exists(path):
                    path = "{}_{}.mp3".format(base, n)
                    n += 1
                try:
                    rr = requests.get(c["audio_url"], timeout=120)
                    rr.raise_for_status()
                    with open(path, "wb") as f:
                        f.write(rr.content)
                    saved.append(path)
                    say("⬇️ Скачав {} у папку MixTracks".format(os.path.basename(path)))
                except Exception as e:
                    say("⚠️ Не вдалось скачати трек: " + str(e)[:120])
    return saved


def suno_credits(cookie, say):
    """💰 v19: скільки кредитів зосталось на акаунті Suno."""
    jwt = suno_get_jwt(cookie, say)
    r = requests.get(SUNO_API + "/api/billing/info/",
                     headers=_suno_headers(jwt, cookie), timeout=30)
    r.raise_for_status()
    return r.json()


def mix_plan(tracks_dir, target_sec, say):
    """📋 v16: які треки з папки йдуть у мікс і в якому порядку (до ~target_sec)."""
    plan = []
    try:
        names = sorted(os.listdir(tracks_dir))
    except OSError:
        return []
    for name in names:
        if not name.lower().endswith((".mp3", ".wav", ".m4a")):
            continue
        p = os.path.join(tracks_dir, name)
        d = audio_duration(p)
        if d >= 5:
            plan.append((p, d))
    if not plan:
        return []
    out, t = [], 0.0
    for p, d in plan:
        out.append((p, d))
        t += max(1.0, d - MIX_CROSSFADE)
        if t >= target_sec:
            break
    return out


def mix_render_audio(plan, workdir, say):
    """🎚 v16: зшиваю треки в одну доріжку — кросфейди + гучність -14 LUFS
    (стандарт YouTube). Повертає (шлях, тривалість, треклист із таймкодами)."""
    ff = ffmpeg_path()
    tracklist, cur, act = [], None, 0.0
    for i, (p, d) in enumerate(plan):
        norm = os.path.join(workdir, "mixnorm{}.mp3".format(i))
        run([ff, "-y", "-hide_banner", "-nostdin", "-i", p,
             "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
             "-ar", "44100", "-ac", "2", "-b:a", "192k", norm])
        say("🎚 Гучність вирівняно: " + os.path.basename(p)[:50])
        if cur is None:
            cur = norm
            act = audio_duration(cur)
            tracklist.append((0.0, os.path.splitext(os.path.basename(p))[0]))
        else:
            tracklist.append((max(0.0, act - MIX_CROSSFADE),
                              os.path.splitext(os.path.basename(p))[0]))
            joined = os.path.join(workdir, "mixjoin{}.mp3".format(i))
            run([ff, "-y", "-hide_banner", "-nostdin", "-i", cur, "-i", norm,
                 "-filter_complex",
                 "acrossfade=d={:.2f}:c1=tri:c2=tri".format(MIX_CROSSFADE),
                 "-ar", "44100", "-ac", "2", "-b:a", "192k", joined])
            try:
                os.remove(cur)  # проміжні файли не потрібні
            except OSError:
                pass
            cur = joined
            act = audio_duration(cur)
    return cur, act, tracklist


def make_mix_seo_pack(title, tracklist, workdir, say):
    """📈 v16: SEO-пак для музичного міксу + треклист із таймкодами (сердце
    описів у ніші chill-міксів)."""
    theme = " ".join((title or "Chill Mix").split()) or "Chill Mix"
    short = theme if len(theme) <= 55 else theme[:52].rstrip() + "…"
    tl = []
    for start, name in tracklist:
        mm, ss = divmod(int(start), 60)
        tl.append("{:02d}:{:02d} — {}".format(mm, ss, name.replace("_", " ")))
    titles = [
        "{} — Chill Mix 2026 | Deep House for Relax & Study".format(short),
        "{} | 1 Hour Chill Vibes • Deep House Mix".format(short),
        "{} — Night Chill Mix • Music for Stress Relief".format(short),
    ]
    tags = [theme.lower(), "chill mix", "deep house mix", "chill house",
            "relaxing music", "study music", "night vibes", "stress relief",
            "music for work", "long mix", "chill music", "background music"]
    tags_line = ", ".join(dict.fromkeys(tags))[:480]
    hashtags = "#chillmix #deephouse #nightvibes #relaxingmusic #studymusic"
    desc = ["{} — атмосферний мікс: м'який chill/deep house для відпочинку, роботи й навчання.".format(short),
            "Включай і розслабляйся 🎧",
            "",
            "ТРЕКЛИСТ:"] + tl + [
        "",
        "Подобається? Підпишися — нові мікси щотижня! 🔔",
        "",
        "Ключові слова: {}.".format(tags_line[:200]),
        "",
        hashtags]
    pinned = "🎵 Який трек сподобався найбільше? Напиши таймкод у коментарях!"
    lines = ["НАЗВА (обери один із трьох варіантів):"]
    lines += ["{}. {}".format(i, t) for i, t in enumerate(titles, 1)]
    lines += ["", "ОПИС:"] + desc
    lines += ["", "ТЕГИ (через кому, лиміт 500 символів):", tags_line]
    lines += ["", "ХЕШТЕГИ (додай у кінець опису):", hashtags]
    lines += ["", "ЗАКРІПЛЕНИЙ КОМЕНТАР:", pinned]
    with open(os.path.join(workdir, "youtube-seo.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("📈 SEO-пак міксу з треклистом і таймкодами — youtube-seo.txt")


def generate_mix(title, minutes, size_str, say, on_workdir=None,
                 bg_files=None, yt_search_urls=None, cover=True, seo=True):
    """🎧 v16: музичний мікс — треки з папки MixTracks зшиваються з кросфейдами
    у одну доріжку (гучність -14 LUFS), фон — петля з кліпів або градієнт,
    плюс обкладинка і SEO-пак із треклистом. Повертає робочу папку."""
    base = os.path.join(os.path.expanduser("~"), "Videos", "Generated")
    workdir = os.path.join(base, datetime.now().strftime("%Y%m%d_%H%M%S")
                           + "_mix_" + re.sub(r'[^\w-]', '_', (title or "mix")[:30]))
    os.makedirs(workdir, exist_ok=True)
    if on_workdir:
        on_workdir(workdir)
    say("🎧 Мікс: " + (title or "Night Chill Mix"))
    say("🔍 Перевіряю ffmpeg (якщо немає — встановлю сам, один раз)…")
    ensure_ffmpeg(say)
    ff = ffmpeg_path()
    w, h = size_str.split(" ")[0].split("x")
    say("📁 Робоча папка створена")
    target_sec = max(10, min(180, int(minutes))) * 60
    say("🎵 Збираю треки з папки MixTracks (мета ~{} хв)…".format(int(target_sec // 60)))
    plan = mix_plan(MIX_TRACKS_DIR, target_sec, say)
    if not plan:
        raise RuntimeError("у папці MixTracks нема придатних треків")
    say("🎵 Треків у міксі: {}".format(len(plan)))
    mix_path, dur, tracklist = mix_render_audio(plan, workdir, say)
    say("⏱ Тривалість міксу: {}:{:02d}".format(int(dur // 60), int(dur % 60)))
    say("📝 Треклист з таймкодами — у youtube-seo.txt")
    # Фон: свої файли → обрані з YouTube-пошуку → градієнт
    bg = None
    clips = [c for c in (bg_files or []) if os.path.isfile(c)]
    if not clips and yt_search_urls:
        say("🔎 Шукаю відео для фону на YouTube…")
        try:
            ensure_ytdlp(say)
            got = []
            for u in yt_search_urls[:4]:
                p = youtube_download(u, workdir, int(h), say,
                                    fixed_name="mixbg{:02d}".format(len(got)),
                                    max_sec=YT_CLIP_MAX_SEC)
                if p and os.path.isfile(p):
                    got.append(p)
            clips = got
        except Exception as e:
            say("⚠️ Фон з YouTube не вийшов ({}), буде градієнт".format(str(e)[:150]))
    if clips:
        try:
            bg = build_bg_from_clips(clips, dur, w, h, workdir)
            say("🎬 Фон змонтовано з кліпів")
        except Exception as e:
            say("⚠️ Кліпи не зібралися ({}), буде градієнт".format(str(e)[:150]))
            bg = None
    if bg:
        vf_in = ["-stream_loop", "-1", "-i", "bg.mp4"]
        say("🖼️ Фон: петля з кліпів")
    else:
        vf_in = ["-f", "lavfi", "-i", f"gradients=s={w}x{h}:c0=0x0f2027:c1=0x2c5364:speed=0.03"]
        say("🖼️ Генерую анімований градієнтний фон")
    say("🚀 Рендерю мікс (це найдовший крок, ~10–20 хв)…")
    cmd = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", mix_path,
           "-map", "0:v", "-map", "1:a", "-shortest",
           "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-r", "25",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "final.mp4"]
    run(cmd, cwd=workdir)
    if cover:  # 📷 обкладинка для YouTube
        try:
            make_cover(workdir, title or "Night Chill Mix", say)
        except Exception as e:
            say("⚠️ Обкладинка не вийшла: " + str(e)[:120])
    if seo:  # 📈 SEO-пак із треклистом
        try:
            make_mix_seo_pack(title or "Night Chill Mix", tracklist, workdir, say)
        except Exception as e:
            say("⚠️ SEO-пак не вийшов: " + str(e)[:120])
    try:  # 🔍 v24: аудіо-лікар — тиша/кліпінг/довгі паузи у готовому відео
        audio_health_check(workdir, say)
    except Exception:
        pass
    say("✅ ГОТОВО: {}".format(os.path.join(workdir, "final.mp4")))
    return workdir


class App:
    """Інтерфейс у стилі MoneyPrinterTurbo (harry0703): темна тема з фіолетовим
    акцентом, таби «Генерація / Історія / Налаштування», сайдбар налаштувань,
    прев'ю готового відео з кадром, кроки пайплайну і журнал збоку.
    Лишаємось десктопом на CustomTkinter — беремо лише UX-патерни."""

    BG = "#0B0B12"        # нічний фон
    CARD = "#15151F"      # картки
    INSET = "#20202E"     # вкладені поля і кнопки
    HOVER = "#2A2A3C"     # наведення
    ACCENT = "#7C3AED"    # фіолетовий акцент
    ACCENT_H = "#8B5CF6"  # акцент при наведенні
    GREEN = "#10B981"     # готово
    MUTED = "#8E8E9C"     # приглушений текст
    SEP = "#2A2A38"       # розділювачі/рамки
    CLAUDE_BG = "#FAF9F5"      # 💬 v41: чат — крем claude (ivory)
    CLAUDE_CARD = "#F0EEE6"    # бульбашки і панелі чату
    CLAUDE_ACCENT = "#D97757"  # теракота claude
    CLAUDE_ACCENT_H = "#C15F3C"
    CLAUDE_TEXT = "#141413"    # текст чату
    CLAUDE_MUTED = "#87867F"   # приглушений текст чату
    CLAUDE_LINE = "#E8E6DC"    # рамки чату
    CLAUDE_BAR = "#FFFFFF"     # 🌙 v48: панель введення чату (світла)
    CLAUDE_HOVER = "#E8E5D9"   # 🌙 v48: ховер кнопок чату (світла)
    CHAT_THEMES = {  # 🌙 v48: теми чату — світла Claude і темна нічна
        "light": {"BG": "#FAF9F5", "CARD": "#F0EEE6", "TEXT": "#141413",
                  "MUTED": "#87867F", "ACCENT": "#D97757",
                  "ACCENT_H": "#C15F3C", "LINE": "#E8E6DC",
                  "BAR": "#FFFFFF", "HOVER": "#E8E5D9"},
        "dark": {"BG": "#1F1E1D", "CARD": "#2A2926", "TEXT": "#F5F4F0",
                 "MUTED": "#A8A29E", "ACCENT": "#D97757",
                 "ACCENT_H": "#C15F3C", "LINE": "#3A3936",
                 "BAR": "#2A2926", "HOVER": "#3A3936"}}
    GEN_BASE = os.path.join(os.path.expanduser("~"), "Videos", "Generated")
    STEPS = ("📝 Текст", "🎙 Озвучка", "💬 Субтитри", "🎬 Фон", "⚙️ Рендер")
    STEP_KEYS = (
        ("Запит:", "Сценар", "Робоча папка", "Перевіряю ffmpeg", "Мікс"),
        ("Озвуч", "озвуч", "Голосів немає", "системним голосом", "Тривалість", "Прибрав пауз", "Трек", "треки"),
        ("убтитр", "Треклист"),
        ("Фон", "фон", "кліп", "Openverse", "Wikimedia", "градієнт",
         "відеоряд", "YouTube", "Посилання", "пошуку", "Шукаю", "зображення", "Pinterest", "Pixabay", "Облич"),
        ("Рендер", "рендер", "ГОТОВО", "Зшиваю"),
    )

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Генератор відео")
        try:
            dpi = self.root.winfo_fpixels("1i")
        except Exception:
            dpi = 96.0
        scale = max(1.0, dpi / 96.0)
        scr_w = self.root.winfo_screenwidth() / scale
        scr_h = self.root.winfo_screenheight() / scale
        h = int(max(640, min(820, scr_h - 60)))
        w = int(max(1040, min(1360, scr_w - 80)))
        try:
            px_w = self.root.winfo_screenwidth()
            px_h = self.root.winfo_screenheight()
            x = max(0, int((px_w - w * scale) / 2))
            y = max(0, int((px_h - h * scale) / 2))
            self.root.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            self.root.geometry(f"{w}x{h}")
        self.root.minsize(1150, 620)
        self.root.configure(fg_color=self.BG)
        self.q = queue.Queue()
        self.workdir = None
        self.yt_checked = {}   # url -> BooleanVar (обране в пошуку YouTube)
        self.merge_files = []
        self.music_path = ""
        self._gen_running = False
        self._step = -1
        self.final_path = None
        self._hist_thumbs = {}
        self._poster_img = None
        self._build()
        self.root.after(150, self._poll)
        self.root.after(1000, self._tick_clock)
        threading.Thread(target=self._startup_check, daemon=True).start()

    def _card(self, master, **pack):
        card = ctk.CTkFrame(master, fg_color=self.CARD, corner_radius=16)
        card.pack(**pack)
        return card

    def _f(self, size=13, weight="normal"):
        return ctk.CTkFont(family="Segoe UI", size=size, weight=weight)

    def _tick_clock(self):
        """Годинник у шапці, оновлюється раз на 20 секунд."""
        try:
            self.clock.configure(text=datetime.now().strftime("%H:%M"))
        except Exception:
            pass
        self.root.after(20000, self._tick_clock)

    def _startup_check(self):
        """Стартова перевірка: ffmpeg + останнє готове відео одразу в прев'ю."""
        if ffmpeg_available():
            self.say("✅ ffmpeg знайдено — усе готове до генерації")
        else:
            self.say("ℹ️ ffmpeg ще не встановлено — при першій генерації завантажу його сам (один раз, ~100 МБ)")
        best, best_mt = None, 0.0
        if os.path.isdir(self.GEN_BASE):
            for name in os.listdir(self.GEN_BASE):
                f = os.path.join(self.GEN_BASE, name, "final.mp4")
                try:
                    if not os.path.isfile(f):
                        continue
                    mt = os.path.getmtime(f)
                    if mt > best_mt:
                        best, best_mt = f, mt
                except OSError:
                    pass
        if best:
            self.say("📼 Знайшов твоє останнє відео — показую його в прев'ю")
            self.q.put(("poster", best))

    def _build(self):
        # === ШАПКА: логотип, таби, статус, годинник ===
        head = ctk.CTkFrame(self.root, fg_color=self.CARD, corner_radius=0)
        head.pack(side="top", fill="x")
        head.pack_propagate(False)
        head.configure(height=56)
        ctk.CTkLabel(head, text="🎬 Генератор відео", font=self._f(16, "bold"),
                     text_color="#FFFFFF").pack(side="left", padx=(16, 0))
        ctk.CTkLabel(head, text="v14", font=self._f(11, "bold"),
                     text_color=self.ACCENT_H).pack(side="left", padx=(8, 0))
        self.tabs = ctk.CTkSegmentedButton(
            head, values=["🎬 Генерація", "💬 Чат", "🗂 Історія", "⚙️ Налаштування"],
            font=self._f(12), fg_color=self.INSET, unselected_color=self.INSET,
            unselected_hover_color=self.HOVER, selected_color=self.ACCENT,
            selected_hover_color=self.ACCENT_H, command=self._show_tab)
        self.tabs.set("🎬 Генерація")
        self.tabs.pack(side="left", padx=(28, 0))
        self.status_lbl = ctk.CTkLabel(head, text="● Очікує", font=self._f(12, "bold"),
                                      text_color=self.MUTED)
        self.status_lbl.pack(side="right", padx=(0, 16))
        self.clock = ctk.CTkLabel(head, text="", font=self._f(12, "bold"), text_color="#FFFFFF")
        self.clock.pack(side="right", padx=(0, 14))

        # === ЧОТИРИ ТАБИ (v43: чат — вкладка, без спливного вікна) ===
        self.tab_gen = ctk.CTkFrame(self.root, fg_color="transparent")
        self.tab_chat = ctk.CTkFrame(self.root, fg_color="transparent")
        self.tab_hist = ctk.CTkFrame(self.root, fg_color="transparent")
        self.tab_set = ctk.CTkFrame(self.root, fg_color="transparent")
        self._build_gen_tab()
        self._build_hist_tab()
        self._build_set_tab()
        self._show_tab("🎬 Генерація")
        # v13: меню правого кліку («📋 Вставити / 📄 Копіювати») для всіх текстових полів
        # v43: + поле Асистента і URL джерела; журнал — лише «📄 Копіювати»
        for w in (self.query, self.script, self.yt_many, self.yt_search_entry, self.pins_entry, self.tr_entry, self.px_key, self.px_query, self.suno_cookie, self.suno_desc, self.suno_tags, self.agent_entry, self.ollama_url):
            self.attach_paste_menu(w)
        self.attach_paste_menu(self.log, can_paste=False, can_clear=False)

    def _show_tab(self, val):
        for t in (self.tab_gen, self.tab_chat, self.tab_hist, self.tab_set):
            t.pack_forget()
        if "Чат" in val:
            self.tab_chat.pack(side="top", fill="both", expand=True)
        elif "Історія" in val:
            self.tab_hist.pack(side="top", fill="both", expand=True)
            self._refresh_history()
        elif "Налаштування" in val:
            self.tab_set.pack(side="top", fill="both", expand=True)
            self._refresh_tools_status()
        else:
            self.tab_gen.pack(side="top", fill="both", expand=True)

    def _build_gen_tab(self):
        # === ПРАВА КОЛОНКА: журнал (фіксована ширина) ===
        right = ctk.CTkFrame(self.tab_gen, fg_color=self.CARD, width=330)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        ctk.CTkLabel(right, text="Журнал", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        self.log = ctk.CTkTextbox(right, state="disabled", font=self._f(12),
                                  wrap="word", fg_color=self.BG, corner_radius=10)
        self.log.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # === ЦЕНТР ===
        center = ctk.CTkScrollableFrame(self.tab_gen, fg_color="transparent")
        center.pack(side="right", fill="both", expand=True, padx=(8, 0), pady=(8, 8))

        # --- Картка «Що робимо?» — один вибір режиму (v17) ---
        mc = self._card(center, fill="x", pady=(0, 8))
        ctk.CTkLabel(mc, text="Що робимо?", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        mrow = ctk.CTkFrame(mc, fg_color="transparent")
        mrow.pack(fill="x", padx=16, pady=(2, 12))
        self.mode_btns = {}
        for mid, txt in (("video", "🎬\nВідео"), ("script", "📜\nСценарій"),
                         ("mix", "🎧\nМікс")):
            b = ctk.CTkButton(mrow, text=txt, height=64, font=self._f(14, "bold"),
                              corner_radius=12, command=lambda m=mid: self._set_mode(m))
            b.pack(side="left", fill="x", expand=True, padx=3)
            self.mode_btns[mid] = b
        ctk.CTkLabel(mc, text="🎬 Відео — напиши тему, зроблю все сам • 📜 Сценарій — своє текстом по частинах • 🎧 Мікс — годинна музика з безкоштовних треків",
                     font=self._f(10), text_color=self.MUTED, justify="left",
                     wraplength=560).pack(fill="x", padx=16, pady=(0, 12))

        # --- Режимні фрейми ---
        self.frame_video = ctk.CTkFrame(center, fg_color="transparent")
        self.frame_script = ctk.CTkFrame(center, fg_color="transparent")
        self.frame_mix = ctk.CTkFrame(center, fg_color="transparent")

        # === РЕЖИМ 🎬 ВІДЕО ===
        qc = self._card(self.frame_video, fill="x", pady=(0, 8))
        ctk.CTkLabel(qc, text="Про що зняти відео?", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        self.query = ctk.CTkTextbox(qc, height=64, font=self._f(13), wrap="word",
                                    fg_color=self.INSET, corner_radius=10)
        self.query.pack(fill="x", padx=16, pady=(0, 4))
        for seq in ("<Control-v>", "<Control-V>", "<Shift-Insert>"):
            self._bind_safe(self.query, seq, self._paste_event)
        self._bind_safe(self.query, "<Control-Return>", self._ctrl_enter)
        qrow = ctk.CTkFrame(qc, fg_color="transparent")
        qrow.pack(fill="x", padx=16, pady=(2, 2))
        ctk.CTkButton(qrow, text="📥 Вставити", width=100, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.paste_query).pack(side="left")
        ctk.CTkButton(qrow, text="🧲 Оцінити", width=100, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.score_now).pack(side="left", padx=(8, 0))
        ctk.CTkButton(qrow, text="🧪 A/B-заголовки", width=128, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.ab_now).pack(side="left", padx=(8, 0))
        ctk.CTkButton(qrow, text="🌐 YouTube", width=100, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.open_youtube_search).pack(side="left", padx=(8, 0))
        self.batch = ctk.BooleanVar(value=False)  # 📚 v14: батч-генерація
        ctk.CTkSwitch(qc, text="📚 Кілька відео батчем (кожен рядок теми — окреме відео)",
                      variable=self.batch, font=self._f(12),
                      progress_color=self.ACCENT).pack(anchor="w", padx=16, pady=(2, 0))

        # 🤖 v26: агентне поле — фраза звичайною мовою, парсер налаштує поля сам
        ac = self._card(self.frame_video, fill="x", pady=(0, 8))
        ctk.CTkLabel(ac, text="🤖 Асистент — напиши фразу, а я налаштую поля",
                     font=self._f(13, "bold"), anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        # поле — багаторядкове (CTkTextbox): приймає вставлений текст будь-якої
        # довжини, вертикальний скролінг; Enter — виконати (без переносу рядка)
        self.agent_entry = ctk.CTkTextbox(ac, height=96, font=self._f(13), wrap="word",
                                          fg_color=self.INSET, corner_radius=10)
        self.agent_entry.pack(fill="x", padx=16, pady=(0, 4))

        def _agent_enter(_e):
            self._agent_send()
            return "break"
        self._bind_safe(self.agent_entry, "<Return>", _agent_enter)
        ctk.CTkLabel(ac, text="📥 Вставити — скопійований текст з буфера • 🤖 Виконати фразу або Enter — налаштувати поля",
                     font=self._f(10), text_color=self.MUTED).pack(anchor="w",
                                                                   padx=16, pady=(0, 2))
        abtn = ctk.CTkFrame(ac, fg_color="transparent")
        abtn.pack(fill="x", padx=16, pady=(2, 4))
        ctk.CTkButton(abtn, text="📥 Вставити", height=36, corner_radius=18,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13, "bold"),
                      command=lambda: self.paste_into(self.agent_entry)).pack(
                          side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkButton(abtn, text="💬 Чат", width=112, height=36, corner_radius=18,
                      fg_color=self.CLAUDE_CARD, hover_color="#E8E5D9",
                      text_color=self.CLAUDE_TEXT, font=self._f(13, "bold"),
                      command=self.open_chat_window).pack(side="left", padx=(4, 4))
        ctk.CTkButton(abtn, text="🤖  Виконати фразу", height=36, corner_radius=18,
                      font=self._f(13, "bold"), command=self._agent_send).pack(
                          side="left", fill="x", expand=True, padx=(4, 0))

        # 🧠 v29: Tier 2 — опційний локальний Ollama: сильніший розбір фраз і сценарії
        ctk.CTkLabel(ac, text="🧠 AI-мозок Асистента: 🤖 Claude — безкоштовний Puter-токен (puter.com, без картки; вікно «🔑 Ключі» — сторінка у Chrome, ключ запам'ятається назавжди, лише локально); 🌐 Pollinations / ⚡ Kilo / 🌐 LLM7 — безкоштовно, БЕЗ ключів (ChatGPT-подібні моделі); 🔑 ключі: Groq / GitHub / 🤖 Google AI Studio (авторизація через Google) / ⚡ Cerebras / 🇪🇺 Mistral / 🧭 OpenRouter / 🟩 NVIDIA / 🟧 SambaNova / 🤗 HF / 🟣 GLM Zhipu / 🟣 GLM Z.AI / 🌊 SiliconFlow / 🟠 ModelScope — усе безкоштовні фрітіри, без картки; моделі на вибір: Claude Sonnet/Haiku/Opus, GLM (glm-4.7-flash безкоштовна, 200K), Qwen, gpt-oss, Mistral-лінійка; 🔄 Авто (за замовчуванням) — драбина всіх джерел: вичерпався — сам перескакує; або локальні Ollama / 9Router (api-free) — краще розбирає фрази, вміє писати сценарій",
                     font=self._f(11), text_color=self.MUTED, anchor="w",
                     wraplength=560).pack(fill="x", padx=16, pady=(8, 2))
        _oc = load_ollama_conf()
        prow = ctk.CTkFrame(ac, fg_color="transparent")
        prow.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(prow, text="Джерело:", font=self._f(11),
                     text_color=self.MUTED).pack(side="left", padx=(0, 6))
        self.llm_provider = ctk.CTkSegmentedButton(
            prow, values=["Ollama", "9Router", "🌐 Онлайн", "⚡ Kilo", "🔑 Ключ", "🔄 Авто"],
            font=self._f(11), height=28,
            fg_color=self.INSET, selected_color=self.ACCENT,
            selected_hover_color=self.ACCENT_H, unselected_color=self.HOVER,
            command=self._switch_llm_provider)
        _prov0 = (_oc.get("provider") or "auto")  # 🔄 v43: дефолт — Авто-драбина
        self.llm_provider.set("🌐 Онлайн" if _prov0 == "pollinations"
                              else ("9Router" if _prov0 == "9router"
                                    else ("⚡ Kilo" if _prov0 == "kilo"
                                          else ("🔑 Ключ" if _prov0 == "freekey"
                                                else ("Ollama" if _prov0 == "ollama"
                                                      else "🔄 Авто")))))
        self.llm_provider.pack(side="left")
        self.ollama_url = ctk.CTkEntry(ac, placeholder_text="http://localhost:11434",
                                       height=32, corner_radius=10, fg_color=self.INSET,
                                       font=self._f(12))
        self.ollama_url.pack(fill="x", padx=16, pady=(0, 4))
        self.ollama_url.insert(0, (_oc.get("url") or "http://localhost:11434"))
        orow = ctk.CTkFrame(ac, fg_color="transparent")
        orow.pack(fill="x", padx=16, pady=(0, 4))
        self.ollama_model = ctk.CTkOptionMenu(
            orow, values=(_oc.get("models") or ["модель не обрана"]), width=240,
            height=32, corner_radius=10, fg_color=self.INSET, button_color=self.HOVER,
            font=self._f(12))
        self.ollama_model.pack(side="left", fill="x", expand=True)
        if _oc.get("model") and _oc["model"] in (_oc.get("models") or []):
            self.ollama_model.set(_oc["model"])
        if _prov0 == "freekey":  # 🧠 v44: старт із збереженим «Ключем» — моделі шлюзу
            self._freekey_model_menu(freekey_engine())
        ctk.CTkButton(orow, text="🔄 Перевірити", height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.ollama_check_now).pack(side="left", padx=(8, 0))
        ctk.CTkButton(orow, text="🔑 Ключі", height=32, corner_radius=16,  # 🔑 v44: вікно ключів
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self._key_window).pack(side="left", padx=(8, 0))
        self.ollama_status = ctk.CTkLabel(
            ac, text="🌐 Онлайн працює одразу — нічого не встановлювати. Перевір — підпишу модель. Налаштування лише локально; без AI — Асистент як раніше (парсер).",
            font=self._f(10), text_color=self.MUTED, anchor="w", wraplength=560)
        self.ollama_status.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkLabel(qc, text="Ctrl+V вставити • Ctrl+Enter згенерувати • фон підберу сам",
                     font=self._f(10), text_color=self.MUTED).pack(anchor="w",
                                                                    padx=16, pady=(2, 12))

        bc = self._card(self.frame_video, fill="x", pady=(0, 8))  # 🔍 Свій фон
        ctk.CTkLabel(bc, text="🔍 Свій фон (не обов'язково)", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        self.bg_src = ctk.CTkSegmentedButton(bc, values=["🎬 Відео YouTube", "🌍 Openverse", "🖼 Pixabay", "📌 Pinterest"],
                                              font=self._f(12), height=32,
                                              fg_color=self.INSET, selected_color=self.ACCENT,
                                              selected_hover_color=self.ACCENT_H,
                                              unselected_color=self.HOVER,
                                              command=self._switch_bg_src)
        self.bg_src.set("🎬 Відео YouTube")
        self.bg_kind = "yt"  # 🖼 v18: поточне джерело фону: yt / ov / px / pin
        self.bg_src.pack(fill="x", padx=16, pady=(0, 6))
        self.yt_bg_row = ctk.CTkFrame(bc, fg_color="transparent")
        self.yt_bg_row.pack(fill="x", padx=16, pady=(0, 6))
        self.yt_search_entry = ctk.CTkEntry(
            self.yt_bg_row, placeholder_text="Що шукати? (наприклад: нічне місто 4k)",
            height=38, corner_radius=10, fg_color=self.INSET, font=self._f(13))
        self.yt_search_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(self.yt_bg_row, text="📋", width=48, height=38, corner_radius=10,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(15),
                      command=lambda: self.paste_into(self.yt_search_entry)).pack(side="left", padx=(8, 0))
        ctk.CTkButton(self.yt_bg_row, text="🔎 Шукати", width=110, height=38, corner_radius=10,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=self.yt_search_now).pack(side="left", padx=(8, 0))
        self.pins_row = ctk.CTkFrame(bc, fg_color="transparent")  # 🖼 v18: Openverse / Pixabay / Pinterest
        self.pins_entry = ctk.CTkEntry(
            self.pins_row, placeholder_text="Які зображення? (наприклад: neon city night)",
            height=38, corner_radius=10, fg_color=self.INSET, font=self._f(13))
        self.pins_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(self.pins_row, text="📋", width=48, height=38, corner_radius=10,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(15),
                      command=lambda: self.paste_into(self.pins_entry)).pack(side="left", padx=(8, 0))
        ctk.CTkButton(self.pins_row, text="🖼 Шукати", width=110, height=38, corner_radius=10,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=self.pins_search_now).pack(side="left", padx=(8, 0))
        self.pins_results_frame = ctk.CTkScrollableFrame(bc, height=170, fg_color=self.INSET,
                                                         corner_radius=12)
        ctk.CTkLabel(self.pins_results_frame, text="Тут з'являться знайдені зображення",
                     font=self._f(11), text_color=self.MUTED).pack(anchor="w")
        self.yt_results_frame = ctk.CTkScrollableFrame(bc, height=170, fg_color=self.INSET,
                                                       corner_radius=12)
        self.yt_results_frame.pack(fill="x", padx=16, pady=(0, 6))
        ctk.CTkLabel(self.yt_results_frame, text="Тут з'являться результати пошуку",
                     font=self._f(11), text_color=self.MUTED).pack(anchor="w")
        ctk.CTkLabel(bc, text="обране піде у фон • нічого не обрав — підберу сам по темі • 🖼 Pinterest: зображення належать авторам — ок для особистих відео",
                     font=self._f(10), text_color=self.MUTED, justify="left",
                     wraplength=560).pack(fill="x", padx=16, pady=(0, 12))

        # === РЕЖИМ 📜 СЦЕНАРІЙ ===
        tc = self._card(self.frame_script, fill="x", pady=(0, 8))
        ctk.CTkLabel(tc, text="📜 Сценарій (по частинах)", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(tc, text="Частини через порожній рядок. «Пошук: запит» задає пошук фону, «Кліп: посилання» — твоє відео; «Тривалість: 12» — цільові секунди частини (озвучка підженеться темпом).",
                     font=self._f(10), text_color=self.MUTED, justify="left",
                     wraplength=560).pack(fill="x", padx=16, pady=(0, 4))
        self.script = ctk.CTkTextbox(tc, height=110, font=self._f(13), wrap="word",
                                     fg_color=self.INSET, corner_radius=10)
        self.script.pack(fill="x", padx=16, pady=(0, 4))
        for seq in ("<Control-v>", "<Control-V>", "<Shift-Insert>"):
            self._bind_safe(self.script, seq, self._paste_script_event)
        self._bind_safe(self.script, "<Control-Return>", self._ctrl_enter)
        trow = ctk.CTkFrame(tc, fg_color="transparent")
        trow.pack(fill="x", padx=16, pady=(2, 2))
        ctk.CTkButton(trow, text="📋", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=lambda: self.paste_into(self.script)).pack(side="left")
        ctk.CTkButton(trow, text="📂", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=self.load_script_file).pack(side="left", padx=(8, 0))
        ctk.CTkButton(trow, text="💾", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=self.save_script_file).pack(side="left", padx=(8, 0))
        ctk.CTkButton(trow, text="📦", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=self.import_manifest_now).pack(side="left", padx=(8, 0))
        ctk.CTkLabel(tc, text="Ctrl+Enter згенерувати • 📦 — відновити з manifest.json",
                     font=self._f(10), text_color=self.MUTED).pack(anchor="w",
                                                                    padx=16, pady=(2, 0))
        trc = self._card(self.frame_script, fill="x", pady=(0, 8))  # 📜 транскрипція поруч
        ctk.CTkLabel(trc, text="📜 З YouTube в сценарій (не обов'язково)",
                     font=self._f(13, "bold"), anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(trc, text="Встав посилання — витягну субтитри, стисну до ~10 хвилин озвучки і зроблю сценарій.",
                     font=self._f(10), text_color=self.MUTED, justify="left",
                     wraplength=560).pack(fill="x", padx=16, pady=(0, 4))
        self.tr_entry = ctk.CTkEntry(trc, placeholder_text="Посилання на відео YouTube…",
                                    height=38, corner_radius=10, fg_color=self.INSET,
                                    font=self._f(13))
        self.tr_entry.pack(side="left", fill="x", expand=True, padx=16)
        ctk.CTkButton(trc, text="📜 Витягнути", height=38, corner_radius=10,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=self.transcript_now).pack(side="left", padx=(8, 0), pady=(0, 4))
        ctk.CTkLabel(trc, text="", font=self._f(10)).pack(anchor="w", padx=16, pady=(0, 8))

        # === РЕЖИМ 🎧 МІКС ===
        # 🎼 Suno AI — генерація музики за описом (v19)
        sc = self._card(self.frame_mix, fill="x", pady=(0, 8))
        ctk.CTkLabel(sc, text="🎼 Suno AI — своя музика за описом",
                     font=self._f(13, "bold"), anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(sc, text="Опиши трек — Suno згенерує 2 варіанти, я скачаю готові mp3 у папку MixTracks (для міксу або фону відео).",
                     font=self._f(10), text_color=self.MUTED, anchor="w",
                     wraplength=560).pack(fill="x", padx=16, pady=(0, 4))
        self.suno_cookie = ctk.CTkEntry(sc, placeholder_text="Cookie сесії Suno: suno.com → F12 → Network → заголовок Cookie (рядок з __client=…)",
                                        height=34, corner_radius=10, fg_color=self.INSET,
                                        font=self._f(12))
        self.suno_cookie.pack(fill="x", padx=16, pady=(0, 4))
        self.suno_cookie.insert(0, load_suno_cookie())
        self.suno_desc = ctk.CTkEntry(sc, placeholder_text="Опиши трек (напр.: заспокійливий lo-fi про вечірній Київ)",
                                      height=34, corner_radius=10, fg_color=self.INSET,
                                      font=self._f(12))
        self.suno_desc.pack(fill="x", padx=16, pady=(0, 4))
        self.suno_tags = ctk.CTkEntry(sc, placeholder_text="Стиль, якщо хочеш точніше (lo-fi, deep house, epic…)",
                                      height=34, corner_radius=10, fg_color=self.INSET,
                                      font=self._f(12))
        self.suno_tags.pack(fill="x", padx=16, pady=(0, 4))
        self.suno_inst = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(sc, text="🎙 Без вокалу (інструментал)", variable=self.suno_inst,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=16, pady=(2, 4))
        srow = ctk.CTkFrame(sc, fg_color="transparent")
        srow.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkButton(srow, text="🎼 Згенерувати трек", height=34, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.suno_gen_now).pack(side="left")
        ctk.CTkButton(srow, text="💰 Кредити Suno", height=34, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.suno_credits_now).pack(side="left", padx=(8, 0))
        ctk.CTkLabel(sc, text="Cookie зберігається лише на цьому комп'ютері — у код і GitHub не потрапляє.\nУ Suno нема офіційного API: це неформальний клієнт твого власного акаунта — тримай обсяг невеликим.",
                     font=self._f(10), text_color=self.MUTED, justify="left",
                     wraplength=560).pack(fill="x", padx=16, pady=(2, 12))

        xc = self._card(self.frame_mix, fill="x", pady=(0, 8))
        ctk.CTkLabel(xc, text="🎧 Музика для міксу (Pixabay — безкоштовно, без авторських прав)",
                     font=self._f(13, "bold"), anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(xc, text="Тема відео вище стане назвою міксу (порожня — «Night Chill Mix»).",
                     font=self._f(10), text_color=self.MUTED, anchor="w",
                     wraplength=560).pack(fill="x", padx=16, pady=(0, 4))
        self.px_key = ctk.CTkEntry(xc, placeholder_text="Ключ Pixabay (pixabay.com/api/docs)",
                                   height=34, corner_radius=10, fg_color=self.INSET,
                                   font=self._f(12))
        self.px_key.pack(fill="x", padx=16, pady=(0, 4))
        self.px_key.insert(0, load_pixabay_key())
        xrow = ctk.CTkFrame(xc, fg_color="transparent")
        xrow.pack(fill="x", padx=16, pady=(0, 4))
        self.px_query = ctk.CTkEntry(xrow, placeholder_text="Жанр/настрій (deep house, chill)",
                                     height=34, corner_radius=10, fg_color=self.INSET,
                                     font=self._f(12))
        self.px_query.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(xrow, text="🎵", width=48, height=34, corner_radius=10,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(14),
                      command=self.px_search_now).pack(side="left", padx=(8, 0))
        self.px_results_frame = ctk.CTkScrollableFrame(xc, height=150, fg_color=self.INSET,
                                                       corner_radius=12)
        self.px_results_frame.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(self.px_results_frame, text="Тут з'являться знайдені треки",
                     font=self._f(11), text_color=self.MUTED).pack(anchor="w")
        xrow2 = ctk.CTkFrame(xc, fg_color="transparent")
        xrow2.pack(fill="x", padx=16, pady=(0, 4))
        self.px_tracks_lbl = ctk.CTkLabel(xrow2, text="Треків у папці: 0",
                                          font=self._f(11), text_color=self.MUTED, anchor="w")
        self.px_tracks_lbl.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(xrow2, text="⬇️ Завантажити обране", height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.px_download_now).pack(side="right")
        xrow3 = ctk.CTkFrame(xc, fg_color="transparent")
        xrow3.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(xrow3, text="⏱ Хвилин міксу:", font=self._f(12),
                     text_color=self.MUTED).pack(side="left")
        self.mix_minutes = ctk.CTkEntry(xrow3, width=64, height=32, corner_radius=10,
                                        fg_color=self.INSET, font=self._f(12), justify="center")
        self.mix_minutes.insert(0, "60")
        self.mix_minutes.pack(side="left", padx=(6, 0))
        ctk.CTkButton(xrow3, text="📂 Папка з треками", height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.open_mix_folder).pack(side="right")
        ctk.CTkLabel(xc, text="Ключ Pixabay зберігається лише на цьому комп'ютері — у код і GitHub не потрапляє.",
                     font=self._f(10), text_color=self.MUTED, wraplength=560,
                     justify="left").pack(fill="x", padx=16, pady=(2, 12))

        # --- Головна кнопка + кроки + прев'ю ---
        self.btn = ctk.CTkButton(center, text="🎬  ЗГЕНЕРУВАТИ ВІДЕО",
                                 height=54, corner_radius=27, font=self._f(16, "bold"),
                                 fg_color=self.ACCENT, hover_color=self.ACCENT_H,
                                 command=self.start)
        self.btn.pack(fill="x", pady=(0, 2))
        self.bar = ctk.CTkProgressBar(center, mode="indeterminate", height=6,
                                      corner_radius=3, progress_color=self.ACCENT)
        self.bar.pack(fill="x", pady=(2, 8))
        self.bar.set(0)

        lc = self._card(center, fill="x", pady=(0, 8))
        ctk.CTkLabel(lc, text="Пайплайн", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        steps_row = ctk.CTkFrame(lc, fg_color="transparent")
        steps_row.pack(fill="x", padx=12, pady=(2, 12))
        self.step_lbls = []
        for st in self.STEPS:
            lbl = ctk.CTkLabel(steps_row, text="○ " + st, font=self._f(12, "bold"),
                               text_color=self.MUTED, fg_color=self.INSET,
                               corner_radius=14, height=30)
            lbl.pack(side="left", padx=4)
            self.step_lbls.append(lbl)

        pc = self._card(center, fill="x", pady=(0, 8))
        ctk.CTkLabel(pc, text="Прев'ю", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        self.poster_lbl = ctk.CTkLabel(
            pc, text="🎞\nТут з'явиться кадр твого відео", width=560, height=315,
            font=self._f(14), text_color=self.MUTED, fg_color=self.INSET, corner_radius=12)
        self.poster_lbl.pack(padx=16, pady=(4, 2))
        self.poster_title = ctk.CTkLabel(pc, text="Ще нічого не згенеровано",
                                         font=self._f(13, "bold"), text_color=self.MUTED,
                                         anchor="w")
        self.poster_title.pack(fill="x", padx=16, pady=(2, 0))
        prow = ctk.CTkFrame(pc, fg_color="transparent")
        prow.pack(fill="x", padx=16, pady=(4, 12))
        ctk.CTkButton(prow, text="▶️ Відкрити відео", height=36, corner_radius=18,
                      font=self._f(13, "bold"), fg_color=self.ACCENT,
                      hover_color=self.ACCENT_H, command=self.open_final).pack(side="left")
        ctk.CTkButton(prow, text="📂 Папка", width=110, height=36, corner_radius=18,
                      font=self._f(13), fg_color="transparent", border_width=1,
                      border_color=self.SEP, hover_color=self.HOVER,
                      command=self.open_folder).pack(side="left", padx=(8, 0))

        # === САЙДБАР (3 картки) ===
        side = ctk.CTkScrollableFrame(self.tab_gen, width=310, fg_color="transparent")
        side.pack(side="left", fill="y", padx=(8, 0), pady=(8, 0))

        vc = self._card(side, fill="x", pady=(0, 8))
        ctk.CTkLabel(vc, text="🎙 Голос озвучки", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        self.voice = ctk.CTkOptionMenu(vc, values=list(VOICES), height=36,
                                       fg_color=self.INSET, button_color=self.HOVER,
                                       button_hover_color=self.HOVER, font=self._f(12))
        self.voice.set("Остап")
        self.voice.pack(fill="x", padx=14, pady=(0, 12))
        ctk.CTkLabel(vc, text="Потрібен лише для 🎬 Відео та 📜 Сценарій",
                     font=self._f(10), text_color=self.MUTED).pack(anchor="w",
                                                                    padx=14, pady=(0, 12))

        # ⚙️ Додатково (згорнуто за замовчуванням)
        ec = self._card(side, fill="x", pady=(0, 8))
        self.extra_toggle = ctk.CTkButton(ec, text="⚙️ Додатково (стилі, розмір, музика)  ▸",
                                          height=36, corner_radius=12, anchor="w",
                                          fg_color="transparent", hover_color=self.HOVER,
                                          font=self._f(12, "bold"),
                                          command=self._toggle_extra)
        self.extra_toggle.pack(fill="x", padx=8, pady=(8, 0))
        self.extra_body = ctk.CTkFrame(ec, fg_color="transparent")
        ctk.CTkLabel(self.extra_body, text="Дефолти вже гарні — міняй, лише якщо хочеш.",
                     font=self._f(10), text_color=self.MUTED).pack(anchor="w", padx=14, pady=(8, 0))
        ctk.CTkLabel(self.extra_body, text="Розмір відео", font=self._f(11),
                     text_color=self.MUTED, anchor="w").pack(fill="x", padx=14, pady=(6, 0))
        self.size = ctk.CTkOptionMenu(self.extra_body, values=list(SIZES), height=32,
                                      fg_color=self.INSET, button_color=self.HOVER,
                                      button_hover_color=self.HOVER, font=self._f(12))
        self.size.set("720p")
        self.size.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.extra_body, text="💬 Стиль субтитрів", font=self._f(11),
                     text_color=self.MUTED, anchor="w").pack(fill="x", padx=14, pady=(4, 0))
        self.sub_style = ctk.CTkOptionMenu(self.extra_body, values=list(SUBTITLE_STYLES), height=32,
                                          fg_color=self.INSET, button_color=self.HOVER,
                                          button_hover_color=self.HOVER, font=self._f(12))
        self.sub_style.set("Класичні")
        self.sub_style.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.extra_body, text="🎨 Стилістика картинки", font=self._f(11),
                     text_color=self.MUTED, anchor="w").pack(fill="x", padx=14, pady=(4, 0))
        self.vid_style = ctk.CTkOptionMenu(self.extra_body, values=list(VIDEO_STYLES), height=32,
                                           fg_color=self.INSET, button_color=self.HOVER,
                                           button_hover_color=self.HOVER, font=self._f(12))
        self.vid_style.set("Без стилю")
        self.vid_style.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.extra_body, text="🎞 Переходи між фрагментами", font=self._f(11),
                     text_color=self.MUTED, anchor="w").pack(fill="x", padx=14, pady=(4, 0))
        self.transition = ctk.CTkOptionMenu(self.extra_body, values=list(TRANSITIONS), height=32,
                                            fg_color=self.INSET, button_color=self.HOVER,
                                            button_hover_color=self.HOVER, font=self._f(12))
        self.transition.set("Різко")
        self.transition.pack(fill="x", padx=14, pady=(0, 6))
        mrow = ctk.CTkFrame(self.extra_body, fg_color="transparent")
        mrow.pack(fill="x", padx=14, pady=(0, 6))
        self.music_lbl = ctk.CTkLabel(mrow, text="🎵 Музика: не обрано",
                                      font=self._f(11), text_color=self.MUTED, anchor="w")
        self.music_lbl.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(mrow, text="Обрати…", width=90, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_music).pack(side="left")
        self.trim_sil = ctk.BooleanVar(value=False)  # ✂️ v14: паузи з озвучки
        ctk.CTkSwitch(self.extra_body, text="✂️ Прибирати паузи з озвучки", variable=self.trim_sil,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 0))
        self.overlays_on = ctk.BooleanVar(value=False)  # 🏷️ 2.0: оверлеї на фіналі
        ctk.CTkSwitch(self.extra_body, text="🏷️ Оверлеї (плашка, знак, прогрес)", variable=self.overlays_on,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 0))
        self.cover_on = ctk.BooleanVar(value=True)  # 📷 v14: обкладинка YouTube
        ctk.CTkSwitch(self.extra_body, text="📷 Обкладинка YouTube (cover.jpg)", variable=self.cover_on,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 0))
        self.no_faces = ctk.BooleanVar(value=False)  # 🚫 v15: фрагменти без обличчя
        ctk.CTkSwitch(self.extra_body, text="🚫 Без обличчя у кадрі (OpenCV)", variable=self.no_faces,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 0))
        self.seo = ctk.BooleanVar(value=True)  # 📈 v15: SEO-пак
        ctk.CTkSwitch(self.extra_body, text="📈 SEO-пак для YouTube (youtube-seo.txt)", variable=self.seo,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 0))
        self.loudnorm = ctk.BooleanVar(value=False)  # 🔊 v27: майстеринг гучності
        ctk.CTkSwitch(self.extra_body, text="🔊 Майстеринг −14 LUFS (EBU R128)", variable=self.loudnorm,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 0))
        self.pack_size = ctk.StringVar(value="Не стискати")  # 📦 v27: цільовий розмір копії
        ctk.CTkSegmentedButton(self.extra_body, values=["Не стискати", "10 МБ", "25 МБ", "50 МБ", "100 МБ"],
                               variable=self.pack_size, font=self._f(11), height=28,
                               fg_color=self.INSET, selected_color=self.ACCENT,
                               selected_hover_color=self.ACCENT_H,
                               unselected_color=self.HOVER).pack(anchor="w", padx=14, pady=(4, 0))
        ctk.CTkLabel(self.extra_body, text="📺 Платформа публікації (пресет 📦 і поради):",
                     font=self._f(11), text_color=self.MUTED, anchor="w").pack(
            anchor="w", padx=14, pady=(8, 0))  # 📺 v32: HandBrake-пресети платформ
        self.pub_platform = ctk.StringVar(value="Не")
        ctk.CTkSegmentedButton(self.extra_body, values=["Не", "YouTube", "Shorts", "Telegram"],
                               variable=self.pub_platform, font=self._f(11), height=28,
                               fg_color=self.INSET, selected_color=self.ACCENT,
                               selected_hover_color=self.ACCENT_H,
                               unselected_color=self.HOVER,
                               command=self._switch_pub_platform).pack(anchor="w", padx=14, pady=(4, 0))
        self.upscale4k = ctk.BooleanVar(value=False)  # 📈 v34: апскейл фіналу до 4К
        ctk.CTkSwitch(self.extra_body, text="📈 Апскейл фіналу до 4К (вищий бітрейт YouTube)",
                      variable=self.upscale4k, font=self._f(12),
                      progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(4, 0))
        self.autoscrape = ctk.BooleanVar(value=False)  # 🧹 v34: авто-чистка метаданих фіналу
        ctk.CTkSwitch(self.extra_body, text="🧹 Авоскраб — авто-чистка метаданих фіналу",
                      variable=self.autoscrape, font=self._f(12),
                      progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 4))
        self.tts_rate = ctk.DoubleVar(value=0)  # 🎚 v28: темп озвучки edge-tts (−20…+30%)
        self.tts_rate_lbl = ctk.CTkLabel(self.extra_body, text="🎚 Темп озвучки: +0%",
                                         font=self._f(11), text_color=self.MUTED, anchor="w")
        self.tts_rate_lbl.pack(anchor="w", padx=14, pady=(6, 0))
        ctk.CTkSlider(self.extra_body, from_=-20, to=30, number_of_steps=10,
                      variable=self.tts_rate, progress_color=self.ACCENT,
                      command=lambda v: self.tts_rate_lbl.configure(
                          text="🎚 Темп озвучки: {:+.0f}%".format(v))
                      ).pack(anchor="w", padx=14, pady=(2, 12))

        # 🧰 Інструменти (згорнуто за замовчуванням)
        ic = self._card(side, fill="x", pady=(0, 8))
        self.tools_toggle = ctk.CTkButton(ic, text="🧰 Інструменти (рідко потрібні)  ▸",
                                          height=36, corner_radius=12, anchor="w",
                                          fg_color="transparent", hover_color=self.HOVER,
                                          font=self._f(12, "bold"),
                                          command=self._toggle_tools)
        self.tools_toggle.pack(fill="x", padx=8, pady=(8, 0))
        self.tools_body = ctk.CTkFrame(ic, fg_color="transparent")
        ctk.CTkLabel(self.tools_body, text="🔗 Відео з YouTube у фон (кілька посилань)",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(10, 2))
        self.yt_many = ctk.CTkTextbox(self.tools_body, height=72, font=self._f(12), wrap="word",
                                     fg_color=self.INSET, corner_radius=10)
        self.yt_many.pack(fill="x", padx=14, pady=(0, 4))
        for seq in ("<Control-v>", "<Control-V>", "<Shift-Insert>"):
            self._bind_safe(self.yt_many, seq, self._paste_many_event)
        yrow = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        yrow.pack(fill="x", padx=14, pady=(2, 4))
        ctk.CTkButton(yrow, text="📋", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=lambda: self.paste_into(self.yt_many)).pack(side="left")
        ctk.CTkButton(yrow, text="⬇️ Завантажити все", height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.download_yt_many).pack(side="left", padx=(8, 0))
        self.yt_many_bg = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(self.tools_body, text="✂️ Нарізати фрагменти у фон", variable=self.yt_many_bg,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 4))
        ctk.CTkLabel(self.tools_body, text="🎞 Компіляція з кількох відео",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.merge_lbl = ctk.CTkLabel(self.tools_body, text="Не обрано жодного відео",
                                      font=self._f(11), text_color=self.MUTED, anchor="w")
        self.merge_lbl.pack(fill="x", padx=14, pady=(0, 4))
        grow = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        grow.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(grow, text="➕ Додати", width=84, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_merge_files).pack(side="left")
        ctk.CTkButton(grow, text="✖️", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.clear_merge_files).pack(side="left", padx=(6, 0))
        ctk.CTkButton(grow, text="🎞 Зшити", width=84, height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.merge_now).pack(side="right")
        self.merge_bg = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(self.tools_body, text="🎬 Ці відео у фон генерації", variable=self.merge_bg,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 4))
        ctk.CTkLabel(self.tools_body, text="🧬 Метадані — змінити до невпізнаваності",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.meta_lbl = ctk.CTkLabel(self.tools_body, text="Не обрано відео",
                                     font=self._f(11), text_color=self.MUTED, anchor="w")
        self.meta_lbl.pack(fill="x", padx=14, pady=(0, 4))
        mrow = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        mrow.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(mrow, text="➕ Додати", width=84, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_meta_file).pack(side="left")
        ctk.CTkButton(mrow, text="✖️", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.clear_meta_file).pack(side="left", padx=(6, 0))
        self.meta_mode = ctk.StringVar(value="Швидко")
        ctk.CTkSegmentedButton(self.tools_body, values=["Швидко", "Глибоко"],
                               variable=self.meta_mode, font=self._f(11), height=28,
                               fg_color=self.INSET, selected_color=self.ACCENT,
                               selected_hover_color=self.ACCENT_H,
                               unselected_color=self.HOVER).pack(anchor="w", padx=14, pady=(0, 4))
        ctk.CTkButton(mrow, text="🧬 Змінити", width=110, height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.meta_now).pack(side="right")
        ctk.CTkLabel(self.tools_body, text="🎤 Авто-субтитри (Whisper на Groq — безкоштовний ключ)",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.stt_lbl = ctk.CTkLabel(self.tools_body, text="Не обрано відео",
                                    font=self._f(11), text_color=self.MUTED, anchor="w")
        self.stt_lbl.pack(fill="x", padx=14, pady=(0, 4))
        sttrow = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        sttrow.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(sttrow, text="➕ Додати", width=84, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_stt_file).pack(side="left")
        ctk.CTkButton(sttrow, text="✖️", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.clear_stt_file).pack(side="left", padx=(6, 0))
        ctk.CTkButton(sttrow, text="🎤 Згенерувати", width=130, height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.stt_now).pack(side="right")
        ctk.CTkLabel(self.tools_body, text="🗣 Клон голосу (Chatterbox — HF Space, без ключа)",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.clone_lbl = ctk.CTkLabel(self.tools_body, text="Не обрано зразок голосу (mp3/wav, 5–20 с)",
                                      font=self._f(11), text_color=self.MUTED, anchor="w")
        self.clone_lbl.pack(fill="x", padx=14, pady=(0, 4))
        clonerow = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        clonerow.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(clonerow, text="➕ Зразок", width=104, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_clone_ref).pack(side="left")
        ctk.CTkButton(clonerow, text="✖️", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.clear_clone_ref).pack(side="left", padx=(6, 0))
        self.clone_txt = ctk.CTkEntry(self.tools_body, height=32, font=self._f(12),
                                      placeholder_text="Текст, який скаже клон голосу")
        self.clone_txt.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(self.tools_body, text="🗣 Озвучити клоном", height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.clone_now).pack(fill="x", padx=14, pady=(0, 4))
        self.clone_voice_on = ctk.BooleanVar(value=bool(clone_cfg_load().get("enabled")))
        ctk.CTkSwitch(self.tools_body, text="🗣 Озвучувати ВІДЕО клоном (замість edge-tts)",
                      variable=self.clone_voice_on, progress_color=self.ACCENT,
                      font=self._f(11), command=self.clone_voice_toggle).pack(fill="x", padx=14, pady=(0, 4))
        saved_ref = (clone_cfg_load().get("sample") or "").strip()
        if saved_ref and os.path.isfile(saved_ref):
            self.clone_ref = saved_ref
            self.clone_lbl.configure(text="Зразок: " + os.path.basename(saved_ref) + " (збережений)",
                                     text_color="#FFFFFF")
        ctk.CTkLabel(self.tools_body, text="🖼 AI-картинка (FLUX — HF Space, без ключа)",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.img_txt = ctk.CTkEntry(self.tools_body, height=32, font=self._f(12),
                                    placeholder_text="Опиши картинку («киоск з кавою під дощем, кіно-стиль»)")
        self.img_txt.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(self.tools_body, text="🖼 Згенерувати картинку", height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.img_now).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.tools_body, text="🎬 Оживити картинку (WAN 2.2 — HF Space, без ключа)",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.anim_lbl = ctk.CTkLabel(self.tools_body, text="Не обрано картинку",
                                     font=self._f(11), text_color=self.MUTED, anchor="w")
        self.anim_lbl.pack(fill="x", padx=14, pady=(0, 4))
        animrow = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        animrow.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(animrow, text="➕ Картинка", width=110, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_anim_img).pack(side="left")
        ctk.CTkButton(animrow, text="✖️", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.clear_anim_img).pack(side="left", padx=(6, 0))
        self.anim_txt = ctk.CTkEntry(self.tools_body, height=32, font=self._f(12),
                                     placeholder_text="Що відбувається у кадрі (необов'язково)")
        self.anim_txt.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(self.tools_body, text="🎬 Зробити відео", height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.anim_now).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.tools_body, text="🖌 Редагування картинки промптом (FLUX.1 Kontext — HF Space)",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.edit_lbl = ctk.CTkLabel(self.tools_body, text="Не обрано картинку",
                                     font=self._f(11), text_color=self.MUTED, anchor="w")
        self.edit_lbl.pack(fill="x", padx=14, pady=(0, 4))
        editrow = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        editrow.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(editrow, text="➕ Картинка", width=110, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_edit_img).pack(side="left")
        ctk.CTkButton(editrow, text="✖️", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.clear_edit_img).pack(side="left", padx=(6, 0))
        self.edit_txt = ctk.CTkEntry(self.tools_body, height=32, font=self._f(12),
                                     placeholder_text="Що змінити («зробити вечір, додати дощ»)")
        self.edit_txt.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(self.tools_body, text="🖌 Змінити картинку", height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.edit_now).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.tools_body, text="✂️ Видалення фону (HF Space — прозорий png, без ключа)",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.nobg_lbl = ctk.CTkLabel(self.tools_body, text="Не обрано картинку",
                                     font=self._f(11), text_color=self.MUTED, anchor="w")
        self.nobg_lbl.pack(fill="x", padx=14, pady=(0, 4))
        nobgrow = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        nobgrow.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(nobgrow, text="➕ Картинка", width=110, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_nobg_img).pack(side="left")
        ctk.CTkButton(nobgrow, text="✖️", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.clear_nobg_img).pack(side="left", padx=(6, 0))
        ctk.CTkButton(self.tools_body, text="✂️ Прибрати фон", height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.nobg_now).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.tools_body, text="🔍 OCR — текст з картинки (DeepSeek-OCR — HF Space)",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.ocr_lbl = ctk.CTkLabel(self.tools_body, text="Не обрано картинку чи скріншот",
                                    font=self._f(11), text_color=self.MUTED, anchor="w")
        self.ocr_lbl.pack(fill="x", padx=14, pady=(0, 4))
        ocrow = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        ocrow.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(ocrow, text="➕ Картинка", width=110, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_ocr_img).pack(side="left")
        ctk.CTkButton(self.tools_body, text="🔍 Витягти текст (.txt, Markdown)", height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.ocr_now).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(self.tools_body, text="🌍 Перекласти текст на картинці (🇷🇺 🇪🇸 🇮🇹 🇬🇧)",  # 🌍 v49
                      height=32, corner_radius=16, fg_color=self.INSET,
                      hover_color=self.HOVER, font=self._f(12),
                      command=self.img_translate_now).pack(fill="x", padx=14,
                                                         pady=(0, 2))
        ctk.CTkButton(self.tools_body, text="📷 Обкладинка іншою мовою (та сама картинка ×4)",  # 🌍 v49
                      height=32, corner_radius=16, fg_color=self.INSET,
                      hover_color=self.HOVER, font=self._f(12),
                      command=self.cover_lang_now).pack(fill="x", padx=14,
                                                       pady=(0, 4))
        ctk.CTkLabel(self.tools_body, text="🎬 Перший кадр → останній (WAN 2.2 — HF Space)",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.fl_lbl = ctk.CTkLabel(self.tools_body, text="Обери ДВІ картинки: початок і кінець",
                                   font=self._f(11), text_color=self.MUTED, anchor="w")
        self.fl_lbl.pack(fill="x", padx=14, pady=(0, 4))
        flrow = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        flrow.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(flrow, text="1️⃣ Перший", width=110, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_fl_first).pack(side="left")
        ctk.CTkButton(flrow, text="2️⃣ Останній", width=110, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_fl_second).pack(side="left", padx=(6, 0))
        ctk.CTkButton(flrow, text="✖️", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.clear_fl_imgs).pack(side="left", padx=(6, 0))
        self.fl_txt = ctk.CTkEntry(self.tools_body, height=32, font=self._f(12),
                                   placeholder_text="Що відбувається між кадрами (необов'язково)")
        self.fl_txt.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(self.tools_body, text="🎬 Зшити кадри у відео", height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.fl_now).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.tools_body, text="🧠 Нейро-ядро — 7 нейромереж на HF Spaces, усі без ключа",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        ctk.CTkLabel(self.tools_body,
                     text="🗣 клон • 🖼 картинка • 🎬 оживлення • 🖌 редагування • ✂️ фон • 🔍 OCR • 🎬 2 кадри",
                     font=self._f(11), text_color=self.MUTED, anchor="w").pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(self.tools_body, text="🔄 Перевірити всі нейромережі", height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.core_check).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.tools_body, text="🎭 Пост-обробка готового відео",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        ctk.CTkButton(self.tools_body, text="✂️ Прибрати тишу з відео", height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.trim_silence_now).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(self.tools_body, text="🌐 Перекласти субтитри (.srt)", height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.translate_srt_now).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(self.tools_body, text="🎙 Озвучити субтитри (дубляж)", height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.dub_srt_now).pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.tools_body,
                     text="✂️ тиша (auto-editor) • 🌐 LibreTranslate (3 інстанси, фолбек LLM) • 🎙 дубляж з TC-дубляжем",
                     font=self._f(11), text_color=self.MUTED, anchor="w").pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(self.tools_body, text="💾 Пресети налаштувань",
                     font=self._f(11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(8, 2))
        self.preset_menu = ctk.CTkOptionMenu(self.tools_body, values=["(порожньо)"], height=32,
                                             fg_color=self.INSET, button_color=self.HOVER,
                                             button_hover_color=self.HOVER, font=self._f(12))
        self.preset_menu.pack(fill="x", padx=14, pady=(0, 4))
        prow2 = ctk.CTkFrame(self.tools_body, fg_color="transparent")
        prow2.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkButton(prow2, text="💾", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.save_preset).pack(side="left")
        ctk.CTkButton(prow2, text="📂 Застосувати", width=104, height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.apply_preset).pack(side="left", padx=(6, 0))
        ctk.CTkButton(prow2, text="🗑", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.delete_preset).pack(side="left", padx=(6, 0))
        self._refresh_presets()

        self._set_mode("video")

    def _set_mode(self, mode):
        """v17: перемикання режиму — показую лише потрібні поля."""
        self.mode = mode
        for m, b in self.mode_btns.items():
            if m == mode:
                b.configure(fg_color=self.ACCENT, hover_color=self.ACCENT_H)
            else:
                b.configure(fg_color=self.INSET, hover_color=self.HOVER)
        self.frame_video.pack_forget()
        self.frame_script.pack_forget()
        self.frame_mix.pack_forget()
        frame = {"video": self.frame_video, "script": self.frame_script,
                 "mix": self.frame_mix}.get(mode, self.frame_video)
        # фрейми режимів стоять одразу за карткою «Що робимо?» — пакуємо вручну
        frame.pack(fill="x", pady=(0, 2), before=self.btn)

    def _toggle_extra(self):
        """⚙️: розгорнути/згорнути додаткові налаштування."""
        if self.extra_body.winfo_ismapped():
            self.extra_body.pack_forget()
            self.extra_toggle.configure(text="⚙️ Додатково (стилі, розмір, музика)  ▸")
        else:
            self.extra_body.pack(fill="x")
            self.extra_toggle.configure(text="⚙️ Додатково (стилі, розмір, музика)  ▾")

    def _toggle_tools(self):
        """🧰: розгорнути/згорнути інструменти."""
        if self.tools_body.winfo_ismapped():
            self.tools_body.pack_forget()
            self.tools_toggle.configure(text="🧰 Інструменти (рідко потрібні)  ▸")
        else:
            self.tools_body.pack(fill="x")
            self.tools_toggle.configure(text="🧰 Інструменти (рідко потрібні)  ▾")

    def _switch_bg_src(self, val):
        """🔍: перемикання джерела фону — Відео YouTube / Openverse / Pixabay / Pinterest."""
        if "YouTube" in val:
            self.bg_kind = "yt"
            self.pins_row.pack_forget()
            self.pins_results_frame.pack_forget()
            self.yt_bg_row.pack(fill="x", padx=16, pady=(0, 6))
            self.yt_results_frame.pack(fill="x", padx=16, pady=(0, 6))
            return
        if "Pixabay" in val:
            self.bg_kind = "px"
        elif "Pinterest" in val:
            self.bg_kind = "pin"
        else:
            self.bg_kind = "ov"
        self.yt_bg_row.pack_forget()
        self.yt_results_frame.pack_forget()
        self.pins_row.pack(fill="x", padx=16, pady=(0, 6))
        self.pins_results_frame.pack(fill="x", padx=16, pady=(0, 6))
        if self.bg_kind == "pin":
            self.say("📌 Pinterest: зображення належать авторам — ок для особистих відео")
        elif self.bg_kind == "ov":
            self.say("🌍 Openverse: відкриті ліцензії, автори пишуться у credits.txt")
    def pins_search_now(self):
        """🖼 v18: пошук фото (Openverse / Pixabay / Pinterest) у фоновому потоці."""
        q = self.pins_entry.get().strip()
        if len(q) < 2:
            messagebox.showwarning("Стоп", "Напиши, які зображення шукати 🙂 (наприклад: neon city)")
            return
        kind = getattr(self, "bg_kind", "ov")
        if kind == "px" and not load_pixabay_key():
            self.say("⚠️ Pixabay: спершу встав ключ у картці 🎧 Мікс (режим Мікс) — він один для музики і фото")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        self.say("🖼 Шукаю зображення ({}): {}…".format(
            {"ov": "Openverse", "px": "Pixabay", "pin": "Pinterest"}.get(kind, "Openverse"), q))
        threading.Thread(target=self._pins_search_thread, args=(q, kind), daemon=True).start()

    def _pins_search_thread(self, q, kind):
        try:
            if kind == "px":
                results, err = pixabay_images_search(load_pixabay_key() or "", q, 12, self.say)
            elif kind == "pin":
                results, err = pinterest_search(q, 12, self.say)
            else:
                results, err = openverse_images_search(q, 12, self.say)
            self.q.put(("pins_results", results, err))
        except Exception as e:
            self.q.put(("pins_results", [], "помилка: " + str(e)[:150]))
        finally:
            self.q.put(None)

    def _show_pins_results(self, results, err):
        """Малює знайдені зображення з чекбоксами (головний потік)."""
        for w in self.pins_results_frame.winfo_children():
            w.destroy()
        self.pins_checked = {}
        self.pins_info = {}
        if not results:
            ctk.CTkLabel(self.pins_results_frame, text=(err or "Нічого не знайшов") + " — спробуй інший запит",
                         font=ctk.CTkFont(family="Segoe UI", size=12),
                         text_color=self.MUTED).pack(anchor="w", pady=6)
            return
        for r in results:
            var = ctk.BooleanVar(value=False)
            self.pins_checked[r["url"]] = var
            self.pins_info[r["url"]] = r.get("credit", "")
            row = ctk.CTkFrame(self.pins_results_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkCheckBox(row, variable=var, text="",
                            checkbox_width=22, checkbox_height=22,
                            fg_color=self.ACCENT, hover_color=self.ACCENT_H).pack(side="left", padx=(4, 6))
            ctk.CTkLabel(row, text=r["title"][:70], font=ctk.CTkFont(family="Segoe UI", size=12),
                         anchor="w", justify="left", wraplength=520).pack(side="left", fill="x", expand=True)
        self.say("✅ Знайдено {} зображень — познач потрібні і генеруй (скачаю сам)".format(len(results)))

    def _build_hist_tab(self):
        htop = ctk.CTkFrame(self.tab_hist, fg_color="transparent")
        htop.pack(side="top", fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(htop, text="🗂 Історія відео", font=self._f(18, "bold"),
                     text_color="#FFFFFF").pack(side="left")
        ctk.CTkButton(htop, text="📂 Папка", width=110, height=34, corner_radius=17,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.open_history_folder).pack(side="right")
        ctk.CTkButton(htop, text="🔄 Оновити", width=110, height=34, corner_radius=17,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self._refresh_history).pack(side="right", padx=(0, 8))
        self.hist_list = ctk.CTkScrollableFrame(self.tab_hist, fg_color="transparent")
        self.hist_list.pack(side="top", fill="both", expand=True, padx=16, pady=(4, 12))
        ctk.CTkLabel(self.hist_list, text="Тут з'являться всі твої згенеровані відео 🎬",
                     font=self._f(12), text_color=self.MUTED).pack(anchor="w", pady=8)

    def _build_set_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_set, fg_color="transparent")
        scroll.pack(side="top", fill="both", expand=True)

        tc = self._card(scroll, fill="x", padx=24, pady=(16, 8))
        ctk.CTkLabel(tc, text="Готовність інструментів", font=self._f(14, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        self.ff_lbl = ctk.CTkLabel(tc, text="ffmpeg: перевіряю…", font=self._f(12),
                                   text_color=self.MUTED, anchor="w")
        self.ff_lbl.pack(fill="x", padx=16, pady=2)
        self.ytdlp_lbl = ctk.CTkLabel(tc, text="yt-dlp: перевіряю…", font=self._f(12),
                                      text_color=self.MUTED, anchor="w")
        self.ytdlp_lbl.pack(fill="x", padx=16, pady=2)
        ctk.CTkButton(tc, text="🔄 Перевірити ще раз", width=170, height=34, corner_radius=17,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self._refresh_tools_status).pack(anchor="w", padx=16, pady=(6, 12))

        dc = self._card(scroll, fill="x", padx=24, pady=8)
        ctk.CTkLabel(dc, text="Папки результатів", font=self._f(14, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        for title, path in (("🎬 Результати генерації", self.GEN_BASE),
                            ("⬇️ Завантажене з YouTube", YT_OUT_DIR),
                            ("🎞 Компіляції", MERGE_OUT_DIR)):
            row = ctk.CTkFrame(dc, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(row, text=title + " — " + path, font=self._f(11),
                         text_color=self.MUTED, anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(row, text="📂", width=44, height=32, corner_radius=16,
                          fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                          command=lambda p=path: self._open_dir(p)).pack(side="right")

        hc = self._card(scroll, fill="x", padx=24, pady=8)
        ctk.CTkLabel(hc, text="Як шукається фон відео (за пріоритетом)", font=self._f(14, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        levels = ("1. 🔗 Твої посилання з поля «Відео з YouTube»",
                  "2. 🔍 Обрані відео з пошуку YouTube",
                  "3. 🎞 Твої власні файли (компіляція)",
                  "4. 🎯 Автопошук на YouTube по словах теми",
                  "5. 🌐 Відкриті кліпи та фото (Openverse → Wikimedia) → градієнт")
        for lv in levels:
            ctk.CTkLabel(hc, text=lv, font=self._f(12), anchor="w").pack(fill="x", padx=16, pady=2)
        ctk.CTkLabel(hc, text="Ключ Pixabay і cookie Suno зберігаються лише на цьому комп'ютері — у код і GitHub вони не потрапляють.",
                     font=self._f(11), text_color=self.MUTED, anchor="w").pack(fill="x", padx=16, pady=(2, 12))

        ac = self._card(scroll, fill="x", padx=24, pady=(8, 16))
        ctk.CTkLabel(ac, text="Про застосунок", font=self._f(14, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(ac, text="Генератор відео 2.0 — простий інтерфейс: обери режим (🎬 Відео / 📜 Сценарій / 🎧 Мікс) і натисни кнопку.\nТема → озвучка → субтитри → фон (YouTube / фото: Openverse, Pixabay, Pinterest) → рендер. Додатково: 🎼 музика Suno AI, стилі, пресети, транскрипція, SEO-пак, 🧬 метадані (змінити до невпізнаваності + ⏱ ETA), 🧹 авто-чистка, 📈 4К-апскейл, 🏷️ ОВЕРЛЕЇ (плашка-заголовок, водяний знак, смуга прогресу — 2.0), 🛡️ QC+ (контакт-шит, спалахи кадру, пік гучності — 2.0), 📋 EDL-таймлайн фону (Resolve — 2.0), 🧪 A/B-заголовки (8 варіантів, топ-3 — 2.0), ✂️ прибирання тиші з готового відео, 🌐 переклад субтитрів, 🎙 дубляж (.srt → озвучка у таймінги), 🌐 онлайн AI-асистент (Pollinations, ⚡ Kilo, 🌐 LLM7, 🚰 LLMFaucet, 🐎 AI Horde — без ключів; 🔑 безкоштовні ключі (Groq, GitHub, 🤖 Google AI Studio, ⚡ Cerebras, 🇪🇺 Mistral, 🧭 OpenRouter, 🟩 NVIDIA, 🟧 SambaNova, 🤗 HF, 🟣 GLM Zhipu, 🟣 GLM Z.AI, 🌊 SiliconFlow, 🟠 ModelScope, 🟣 Cohere) і 🤖 Claude через Puter-токен — вікно «🔑 Ключі»: сторінка шлюзу відкриється у Chrome, ключ запам'ятається назавжди (лише локально); 🔑 РОТАЦІЯ КЛЮЧІВ (2.0): кілька ключів одного шлюзу через кому — кожен запит ходить по колу, ліміти не впираються; вибір моделей: Claude Sonnet/Haiku/Opus, GLM (glm-4.7-flash — безкоштовна, 200K), Qwen, gpt-oss; 🔄 Авто (за замовчуванням) — драбина 21 джерела, не впирається в ліміти) і 🎤 авто-субтитри (Whisper на Groq), а ще 💬 чат з Асистентом у стилі Claude — вкладка у головному вікні: 🎯 власне меню джерела у шапці чату (🤖 Claude онлайн, 💬 ChatGPT онлайн, 🤖 Gemini онлайн, 🇪🇺 Mistral онлайн, усі 16 шлюзів, ⚡ Kilo/🌐 LLM7/🚰 LLMFaucet/🐎 AI Horde без ключів) і 🧠 ПЕРЕМИКАЧ МОДЕЛЕЙ поруч (Claude-трійка, gpt-oss, Gemini, GLM, Qwen), «🔑 Ключ» іде до шлюзу обраної моделі, а лежачий шлюз сам обмінюється драбиною живих ключів — чат не мовчить; ⏳ драбина показує нотами, який шлюз мовчить; 💾 ДВОЙНИЙ КЕШ (2.0): RAM + диск — повторне питання миттєве навіть після перезапуску; 🔐 Google — кнопка у шапці чату: одразу вікно входу Google → ключ Gemini; 🕵️ АГЕНТ (2.0): «знайди/новини…» або кнопка «🌐 Пошук» — до 2 раундів: свіжі дані з DuckDuckGo, а як лежить — запасний Mojeek (без ключів) у відповіді з посиланнями й витягами сторінок; 🎤 ГОЛОС У ЧАТІ (2.0): кнопка 🎤 — сказав питання в мікрофон, Whisper на Groq розшифрував; 📄 ЕКСПОРТ чату у txt (2.0); 🖱 ПКМ у будь-якому полі — СТАНДАРТНЕ меню Вирізати/Копіювати/Вставити/Виділити все/Очистити (виправлено — раніше могло не відкриватись); стрімінг токенів, Markdown-рендер, 📦 артефакти, 🧠 локальна пам'ять, 📎 вкладення файлів, ✏️ редагування повідомлень, 🖱 правий клік — Вставити/Копіювати, відповіді виділяються і копіюються, 📊 таблиці Markdown у відповідях, ⚡ швидкість стріму (симв/с) у мітці, 🔗 кинь URL у повідомлення — агент прочитає сторінку, 🤖 tool-use «🔍ПОШУК:» — модель сама просить мережу, 🌙 темна тема чату (кнопка у шапці), 📡 мітка показує, який шлюз фактично відповів, 🌍 переклад картинки на 🇷🇺🇪🇸🇮🇹🇬🇧 (OCR → 4 txt) і 📷 обкладинка іншою мовою (перекладений заголовок на тій самій картинці ×4), 🗣 клон голосу, 🖼 AI-картинки і 🎬 оживлення кадру, а ще 🧠 нейро-ядро: 🖌 редагування промптом, ✂️ видалення фону, 🔍 OCR, 🎬 перехід двох кадрів і 🗣 озвучка відео клоном твого голосу (усе — безкоштовні HF Spaces, без ключа).\nКлючі Pixabay/Groq і cookie Suno — лише локально на комп'ютері. Дизайн надихався MoneyPrinterTurbo. Репозиторій: khomyak75roman-dotcom/video-generator",
                     font=self._f(12), text_color=self.MUTED, justify="left",
                     anchor="w").pack(fill="x", padx=16, pady=(2, 12))

    # === КРОКИ ПАЙПЛАЙНУ ===

    def _reset_steps(self):
        self._step = -1
        for i, lbl in enumerate(self.step_lbls):
            lbl.configure(text="○ " + self.STEPS[i], text_color=self.MUTED)

    def _set_step(self, i):
        self._step = i
        for j, lbl in enumerate(self.step_lbls):
            if j < i:
                lbl.configure(text="✓ " + self.STEPS[j], text_color=self.GREEN)
            elif j == i:
                lbl.configure(text="● " + self.STEPS[j], text_color=self.ACCENT_H)
            else:
                lbl.configure(text="○ " + self.STEPS[j], text_color=self.MUTED)

    def _finish_steps(self, ok=True):
        for i, lbl in enumerate(self.step_lbls):
            if ok:
                lbl.configure(text="✓ " + self.STEPS[i], text_color=self.GREEN)
            else:
                lbl.configure(text="✗ " + self.STEPS[i], text_color="#EF4444")
        self._step = len(self.step_lbls) - 1

    # === ПРЕВ'Ю ГОТОВОГО ВІДЕО ===

    def _set_poster(self, path):
        """Показати відео в прев'ю: назва + кадр (кадр тягнеться у фоновому потоці)."""
        self.final_path = path
        try:
            name = os.path.basename(os.path.dirname(path))
            self.poster_title.configure(text=self._pretty_name(name), text_color="#FFFFFF")
        except Exception:
            pass
        threading.Thread(target=self._poster_job, args=(path,), daemon=True).start()

    def _poster_job(self, path):
        """Фонова задача: дістає кадр з final.mp4 через ffmpeg → poster.jpg."""
        try:
            os.makedirs(TOOLS_DIR, exist_ok=True)
            out = os.path.join(TOOLS_DIR, "poster.jpg")
            try:
                os.remove(out)
            except OSError:
                pass
            subprocess.run([ffmpeg_path(), "-y", "-hide_banner", "-nostdin",
                            "-ss", "0.7", "-i", path, "-frames:v", "1", "-vf",
                            "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720",
                            out], capture_output=True, timeout=90)
            if os.path.isfile(out):
                self.q.put(("poster_img", out))
            else:
                self.q.put(("poster_img", None))
        except Exception:
            self.q.put(("poster_img", None))

    def _apply_poster(self, path):
        if not path or PILImage is None:
            return
        try:
            img = PILImage.open(path)
            ph = ctk.CTkImage(light_image=img, dark_image=img, size=(560, 315))
            self.poster_lbl.configure(image=ph, text="", fg_color=self.CARD)
            self._poster_img = ph  # тримаю посилання, щоб картинку не зібрав GC
        except Exception:
            pass

    def open_final(self):
        """▶️ Відкрити відео з прев'ю у системному плеєрі."""
        if self.final_path and os.path.isfile(self.final_path):
            try:
                os.startfile(self.final_path)
                return
            except Exception:
                pass
        messagebox.showinfo("Генератор відео",
                            "Спершу згенеруй відео 🙂 Або відкрий його в табі «🗂 Історія»")

    # === ІСТОРІЯ ВІДЕО ===

    def _refresh_history(self):
        """Перечитує папку результатів і малює список готових відео."""
        for w in self.hist_list.winfo_children():
            w.destroy()
        self._hist_thumbs = {}
        rows = []
        if os.path.isdir(self.GEN_BASE):
            for name in os.listdir(self.GEN_BASE):
                f = os.path.join(self.GEN_BASE, name, "final.mp4")
                try:
                    if not os.path.isfile(f):
                        continue
                    rows.append((os.path.getmtime(f), name, f))
                except OSError:
                    pass
        rows.sort(reverse=True)
        if not rows:
            ctk.CTkLabel(self.hist_list, text="Поки нічого — згенеруй перше відео 🎬",
                         font=self._f(12), text_color=self.MUTED).pack(anchor="w", pady=8)
            return
        for mt, name, f in rows[:30]:
            row = self._card(self.hist_list, fill="x", pady=(0, 8))
            thumb = ctk.CTkLabel(row, text="🎞", width=120, height=68, fg_color=self.INSET,
                                 corner_radius=8, font=self._f(20))
            thumb.pack(side="left", padx=(12, 10), pady=12)
            self._hist_thumbs[name] = thumb
            mid = ctk.CTkFrame(row, fg_color="transparent")
            mid.pack(side="left", fill="x", expand=True, pady=12)
            ctk.CTkLabel(mid, text=self._pretty_name(name), font=self._f(13, "bold"),
                         anchor="w", text_color="#FFFFFF").pack(fill="x")
            m = re.match(r"^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})", name)
            if m:
                date_txt = "{}.{}.{} {}:{}".format(m.group(3), m.group(2), m.group(1),
                                                   m.group(4), m.group(5))
            else:
                try:
                    date_txt = datetime.fromtimestamp(mt).strftime("%d.%m.%Y %H:%M")
                except Exception:
                    date_txt = ""
            try:
                size_txt = "{:.1f} МБ".format(os.path.getsize(f) / 1048576.0)
            except OSError:
                size_txt = ""
            ctk.CTkLabel(mid, text=(date_txt + " • " + size_txt).strip(" •"),
                         font=self._f(11), text_color=self.MUTED, anchor="w").pack(fill="x")
            ctk.CTkButton(row, text="▶️ Дивитись", width=110, height=34, corner_radius=17,
                          fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                          command=lambda p=f: self._open_final(p)).pack(side="right", padx=(8, 12), pady=12)
            ctk.CTkButton(row, text="📂", width=44, height=34, corner_radius=17,
                          fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                          command=lambda p=f: self._open_final_folder(p)).pack(side="right", pady=12)
        threading.Thread(target=self._hist_thumb_thread,
                         args=([name for _, name, _ in rows[:8]],), daemon=True).start()

    def _pretty_name(self, name):
        """«20261015_0731_Мій_кліп» → «Мій кліп» (дату відрізаємо — вона в рядку під назвою)."""
        m = re.match(r"^\d{8}_\d{4}_?", name)
        if m:
            name = name[m.end():]
        return name.replace("_", " ") or "Відео"

    def _hist_thumb_thread(self, names):
        """Мініатюри для історії: кадр з final.mp4 → jpg (до 8 штук)."""
        try:
            os.makedirs(TOOLS_DIR, exist_ok=True)
            exe = ffmpeg_path()
            for i, name in enumerate(names[:8]):
                src = os.path.join(self.GEN_BASE, name, "final.mp4")
                if not os.path.isfile(src):
                    continue
                out = os.path.join(TOOLS_DIR, "hist_thumb_{}.jpg".format(i))
                try:
                    subprocess.run([exe, "-y", "-hide_banner", "-nostdin",
                                    "-ss", "0.7", "-i", src, "-frames:v", "1", "-vf",
                                    "scale=240:135:force_original_aspect_ratio=increase,crop=240:135",
                                    out], capture_output=True, timeout=60)
                    if os.path.isfile(out):
                        self.q.put(("thumb", name, out))
                except Exception:
                    pass
        except Exception:
            pass

    def _apply_hist_thumb(self, name, path):
        lbl = self._hist_thumbs.get(name)
        if lbl is None or PILImage is None or not path:
            return
        try:
            img = PILImage.open(path)
            ph = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 68))
            lbl.configure(image=ph, text="", fg_color=self.CARD)
            lbl._thumb_img = ph
        except Exception:
            pass

    def _open_final(self, path):
        try:
            os.startfile(path)
        except Exception:
            pass

    def _open_final_folder(self, path):
        try:
            os.startfile(os.path.dirname(path))
        except Exception:
            pass

    def open_history_folder(self):
        self._open_dir(self.GEN_BASE)

    def _open_dir(self, path):
        try:
            os.makedirs(path, exist_ok=True)
            os.startfile(path)
        except Exception:
            pass

    # === ГОТОВНІСТЬ ІНСТРУМЕНТІВ ===

    def _refresh_tools_status(self):
        self.ff_lbl.configure(text="ffmpeg: перевіряю…", text_color=self.MUTED)
        self.ytdlp_lbl.configure(text="yt-dlp: перевіряю…", text_color=self.MUTED)

        def work():
            ff = ffmpeg_available()
            yt = os.path.isfile(YTDLP_EXE)
            self.q.put(("tools", ff, yt))

        threading.Thread(target=work, daemon=True).start()

    def _apply_tools_status(self, ff, yt):
        self.ff_lbl.configure(
            text=("ffmpeg: ✅ встановлено" if ff else
                  "ffmpeg: завантажиться при першій генерації (~100 МБ, один раз)"),
            text_color=(self.GREEN if ff else self.MUTED))
        self.ytdlp_lbl.configure(
            text=("yt-dlp: ✅ встановлено" if yt else
                  "yt-dlp: завантажиться при першому запуску пошуку YouTube (~18 МБ)"),
            text_color=(self.GREEN if yt else self.MUTED))
    def paste_into(self, widget):
        """Вставляє текст із буфера обміну в будь-яке поле (кнопки 📋)."""
        try:
            clip = self.root.clipboard_get()
        except Exception:
            messagebox.showwarning("Стоп", "Буфер обміну порожній — спершу скопіюй текст або посилання 🙂")
            return
        clip = clip.strip()
        if not clip:
            messagebox.showwarning("Стоп", "Буфер обміну порожній — спершу скопіюй текст або посилання 🙂")
            return
        if isinstance(widget, ctk.CTkTextbox):
            widget.insert("insert", clip)
            widget.see("insert")
        else:
            widget.delete(0, "end")
            widget.insert(0, clip)
        self.say("📋 Вставлено: " + clip[:80])

    def attach_paste_menu(self, widget, can_paste=True, can_clear=True):
        """🖱 v43/v47: ПКМ у полі — СТАНДАРТНЕ меню, як у будь-яких програмах:
        «✂️ Вирізати» / «📄 Копіювати» / «📋 Вставити» / «☑️ Виділити все» /
        «🧹 Очистити». v47 ВИПРАВЛЕННЯ: байнд <Button-3> раніше жив усередині
        copy_from — меню НІКОЛИ не відкривалось (казус курки й яйця);
        тепер байнд тут, при створенні меню. Read-only поля — лише копіювання."""
        menu = tkinter.Menu(widget, tearoff=0, bg="#1C1C1E", fg="#F5F5F7",
                            activebackground="#3A3A3C", activeforeground="#FFFFFF",
                            font=("Segoe UI", 11))
        if can_paste:
            menu.add_command(label="✂️ Вирізати",
                             command=lambda: self.cut_from(widget))
        menu.add_command(label="📄 Копіювати", command=lambda: self.copy_from(widget))
        if can_paste:
            menu.add_command(label="📋 Вставити", command=lambda: self.paste_into(widget))
        menu.add_command(label="☑️ Виділити все",
                         command=lambda: self.select_all_in(widget))
        if can_clear:
            menu.add_command(label="🧹 Очистити", command=lambda: self.clear_field(widget))
        widget._paste_menu = menu

        def _popup(event):  # 🖱 v47: байнд тут — ПКМ працює з першого кліку
            try:
                menu.tk_popup(event.x_root, event.y_root)
            except Exception:
                pass
            finally:
                try:
                    menu.grab_release()
                except Exception:
                    pass
        self._bind_safe(widget, "<Button-3>", _popup, add="+")

    def cut_from(self, widget):
        """✂️ v47: Вирізати — копіюю виділене (нема виділення — усе поле)
        і прибираю його з поля; read-only захищений (не редагується — тихо)."""
        try:
            if isinstance(widget, ctk.CTkTextbox):
                txt = ""
                try:
                    txt = widget.get("sel.first", "sel.last")
                except Exception:
                    txt = ""
                if txt.strip():
                    self.root.clipboard_clear()
                    self.root.clipboard_append(txt)
                    widget.delete("sel.first", "sel.last")
                    self.say("✂️ Вирізано: " + txt[:80].replace("\n", " "))
                else:
                    self.copy_from(widget)
            else:
                try:
                    txt = widget.selection_get()
                except Exception:
                    txt = widget.get()
                self.root.clipboard_clear()
                self.root.clipboard_append(txt)
                widget.delete(0, "end")
                self.say("✂️ Вирізано: " + str(txt)[:80])
        except Exception:
            pass  # read-only поле — без трагедій, fail-open

    def select_all_in(self, widget):
        """☑️ v47: Виділити все — як у будь-яких програмах (Ctrl+A мишею)."""
        try:
            if isinstance(widget, ctk.CTkTextbox):
                widget.tag_add("sel", "1.0", "end")
                widget.focus_set()
            else:
                widget.select_range(0, "end")
                widget.focus_set()
        except Exception:
            pass  # fail-open

    def copy_from(self, widget):
        """📄 v43: копіювати з поля у буфер обміну — виділене, а нема
        виділення — увесь текст (ПКМ «Копіювати» працює і в журналі,
        і в відповідях чату)."""
        txt = ""
        try:
            if isinstance(widget, ctk.CTkTextbox):
                try:
                    txt = widget.get("sel.first", "sel.last")
                except Exception:
                    txt = ""
                if not txt.strip():
                    txt = widget.get("1.0", "end").rstrip("\n")
            else:
                try:
                    txt = widget.selection_get()
                except Exception:
                    txt = widget.get()
        except Exception:
            txt = ""
        if not txt.strip():
            self.say("⚠️ Нема чого копіювати — порожньо")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(txt)
        self.say("📄 Скопійовано: " + txt[:80].replace("\n", " "))

    def clear_field(self, widget):
        """🧹 Очистити поле (пункт меню ПКМ)."""
        if isinstance(widget, ctk.CTkTextbox):
            widget.delete("1.0", "end")
        else:
            widget.delete(0, "end")
        self.say("🧹 Поле очищено")

    def paste_query(self):
        """Вставляє текст із буфера обміну в поле запиту."""
        self.paste_into(self.query)

    def _bind_safe(self, widget, seq, handler, add=None):
        """v26.2: байнд без права на збій (fail-open). Різні збірки
        customtkinter/tk по-різному приймають байнди, а впалий байнд на
        старті = не відкрилось вікно. Середовище відмовило — живемо без
        хоткея: кнопка і нативні байнди Tk усе одно працюють."""
        try:
            if add:
                widget.bind(seq, handler, add)
            else:
                widget.bind(seq, handler)
            return True
        except Exception:
            try:
                widget.bind(sequence=seq, command=handler, add=True)
                return True
            except Exception:
                return False

    def _paste_event(self, event):
        self.paste_query()
        return "break"

    def _paste_script_event(self, event):
        """Ctrl+V у полі сценарію — вставка з буфера."""
        self.paste_into(self.script)
        return "break"

    def _paste_many_event(self, event):
        """Ctrl+V у полі посилань YouTube — вставка з буфера."""
        self.paste_into(self.yt_many)
        return "break"

    def load_script_file(self):
        """📂 Відкрити свій сценарій з txt-файлу — зручно для довгих сценаріїв."""
        path = filedialog.askopenfilename(
            title="Відкрити сценарій",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")])
        if not path:
            return
        text = None
        for enc in ("utf-8-sig", "utf-8", "cp1251"):
            try:
                with open(path, "r", encoding=enc) as f:
                    text = f.read()
                break
            except Exception:
                text = None
        if text is None:
            messagebox.showerror("Генератор відео", "Не вдалось прочитати файл — збережи його у кодуванні UTF-8.")
            return
        self.script.delete("1.0", "end")
        self.script.insert("1.0", text.strip())
        self._set_mode("script")
        self.say("📂 Сценарій відкрито: {} — {} частин".format(
            os.path.basename(path), len(parse_script(text))))

    def save_script_file(self):
        """💾 Зберегти сценарій у txt-файл — щоб повернутись до нього потім."""
        path = filedialog.asksaveasfilename(
            title="Зберегти сценарій", defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt")])
        if not path:
            return
        text = self.script.get("1.0", "end").strip()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            self.say("💾 Сценарій збережено: " + path)
        except Exception as e:
            messagebox.showerror("Генератор відео", "Не вдалось зберегти: " + str(e)[:200])

    def import_manifest_now(self):
        """📦 v30: відновити сценарій з manifest.json минулого запуску —
        частини (Пошук/Кліп/Тривалість + текст) збираються назад у поле."""
        path = filedialog.askopenfilename(
            title="Відкрити маніфест генерації",
            filetypes=[("Маніфест генерації", "*.json"), ("Усі файли", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            blocks = []
            for sc in (data.get("scenes") or []):
                if not isinstance(sc, dict):
                    continue
                lines = []
                if sc.get("q"):
                    lines.append("Пошук: " + str(sc["q"]))
                if sc.get("url"):
                    lines.append("Кліп: " + str(sc["url"]))
                d = sc.get("dur")
                if isinstance(d, (int, float)) and d:
                    lines.append("Тривалість: " + (str(int(d)) if float(d) == int(d) else str(d)))
                if sc.get("text"):
                    lines.append(str(sc["text"]))
                if lines:
                    blocks.append("\n".join(lines))
            if not blocks:
                messagebox.showerror("Генератор відео", "У цьому маніфесті нема частин сценарію (це, схоже, маніфест режиму «Відео»).")
                return
            self.script.delete("1.0", "end")
            self.script.insert("1.0", "\n\n".join(blocks))
            self._set_mode("script")
            self.say("📦 Сценарій відновлено з маніфесту: {} частин".format(len(blocks)))
        except Exception as e:
            messagebox.showerror("Генератор відео", "Не вдалось прочитати маніфест: " + str(e)[:200])

    def _ctrl_enter(self, event):
        self.start()
        return "break"

    def score_now(self):
        """🧲 Оцінка заголовка з поля запиту (поради — у журнал)."""
        score_hook(self.query.get("1.0", "end").strip(), self.say)

    def open_youtube_search(self, entry=None):
        """🌐 Відкриває YouTube у браузері — назва відео вже стоїть у полі пошуку YouTube."""
        q = ""
        if entry is not None:
            q = entry.get().strip()
        if not q:
            q = self.query.get("1.0", "end").strip()
        if not q and getattr(self, "yt_search_entry", None):
            q = self.yt_search_entry.get().strip()
        if not q:
            messagebox.showwarning("Стоп", "Спершу напиши тему або назву відео 🙂")
            return
        webbrowser.open("https://www.youtube.com/results?search_query=" + quote_plus(q))
        self.say("🌐 Відкрив YouTube з пошуком: " + q[:80])

    def pick_music(self):
        p = filedialog.askopenfilename(filetypes=[("Аудіо", "*.mp3 *.wav *.m4a *.ogg")])
        if p:
            self.music_lbl.configure(text=os.path.basename(p), text_color="#FFFFFF")
            self.music_path = p

    # === 💾 ПРЕСЕТИ НАЛАШТУВАНЬ (v14) ===

    def _preset_dir(self):
        os.makedirs(PRESET_DIR, exist_ok=True)
        return PRESET_DIR

    def _preset_list(self):
        try:
            return sorted(f[:-5] for f in os.listdir(self._preset_dir()) if f.endswith(".json"))
        except OSError:
            return []

    def _refresh_presets(self):
        vals = self._preset_list() or ["(порожньо)"]
        try:
            self.preset_menu.configure(values=vals)
            self.preset_menu.set(vals[0])
        except Exception:
            pass

    def save_preset(self):
        name = simpledialog.askstring("Пресет", "Назва пресету:")
        if not name or not name.strip():
            return
        name = re.sub(r"[^\w\- ]", "_", name.strip())
        data = {
            "voice": self.voice.get(),
            "size": self.size.get(),
            "sub_style": self.sub_style.get(),
            "vid_style": self.vid_style.get(),
            "transition": self.transition.get(),
            "trim": bool(self.trim_sil.get()),
            "cover": bool(self.cover_on.get()),
            "no_faces": bool(self.no_faces.get()),
            "seo": bool(self.seo.get()),
            "loudnorm": bool(self.loudnorm.get()) if hasattr(self, "loudnorm") else False,  # 🔊 v27
            "pack": (self.pack_size.get() if hasattr(self, "pack_size") else "Не стискати"),  # 📦 v27
            "platform": ((self.pub_platform.get() or "") if hasattr(self, "pub_platform") else ""),  # 📺 v32
            "tts_rate": int(self.tts_rate.get()) if hasattr(self, "tts_rate") else 0,  # 🎚 v28
            "yt_q": self.yt_q.get(),
        }
        try:
            with open(os.path.join(self._preset_dir(), name + ".json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.say("💾 Пресет «{}» збережено".format(name))
            self._refresh_presets()
            self.preset_menu.set(name)
        except Exception as e:
            self.say("⚠️ Пресет не вдалося зберегти: " + str(e)[:120])

    def apply_preset(self):
        name = self.preset_menu.get()
        if not name or name == "(порожньо)":
            self.say("ℹ️ Пресетів ще нема — спершу збережи свій 💾")
            return
        path = os.path.join(self._preset_dir(), name + ".json")
        if not os.path.isfile(path):
            self.say("ℹ️ Такого пресету нема")
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.say("⚠️ Пресет не читається: " + str(e)[:120])
            return
        if data.get("voice") in VOICES:
            self.voice.set(data["voice"])
        if data.get("size") in SIZES:
            self.size.set(data["size"])
        if data.get("sub_style") in SUBTITLE_STYLES:
            self.sub_style.set(data["sub_style"])
        if data.get("vid_style") in VIDEO_STYLES:
            self.vid_style.set(data["vid_style"])
        if data.get("transition") in TRANSITIONS:
            self.transition.set(data["transition"])
        if "trim" in data:
            self.trim_sil.set(bool(data["trim"]))
        if "cover" in data:
            self.cover_on.set(bool(data["cover"]))
        if "no_faces" in data:
            self.no_faces.set(bool(data["no_faces"]))
        if "seo" in data:
            self.seo.set(bool(data["seo"]))
        if "loudnorm" in data and hasattr(self, "loudnorm"):
            self.loudnorm.set(bool(data["loudnorm"]))
        if data.get("pack") and hasattr(self, "pack_size"):
            try:
                self.pack_size.set(str(data["pack"]))
            except Exception:
                pass
        if data.get("platform") and hasattr(self, "pub_platform"):  # 📺 v32
            try:
                self.pub_platform.set(str(data["platform"]))
            except Exception:
                pass
        if "tts_rate" in data and hasattr(self, "tts_rate"):
            try:
                self.tts_rate.set(int(data["tts_rate"]))
            except Exception:
                pass
        if data.get("yt_q") in YT_QUALITY:
            self.yt_q.set(data["yt_q"])
        self.say("📂 Пресет «{}» застосовано".format(name))

    def delete_preset(self):
        name = self.preset_menu.get()
        path = os.path.join(self._preset_dir(), name + ".json")
        if os.path.isfile(path):
            try:
                os.remove(path)
                self.say("🗑 Пресет «{}» видалено".format(name))
            except OSError as e:
                self.say("⚠️ Не вдалося видалити: " + str(e)[:120])
        self._refresh_presets()

    def transcript_now(self):
        """📜 v15: витягнути транскрипцію з YouTube-відео (окремий потік)."""
        url = self.tr_entry.get().strip()
        if not url.startswith("http"):
            messagebox.showwarning("Стоп", "Встав посилання на YouTube-відео у поле транскрипції 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        self.say("📜 Тягну транскрипцію: " + url[:70])
        threading.Thread(target=self._transcript_thread, args=(url,), daemon=True).start()

    def _transcript_thread(self, url):
        try:
            ensure_ffmpeg(self.say)
            title, text, lang = fetch_transcript(url, self.say)
            self.q.put(("transcript", title, text))
        except Exception as e:
            self.say("❌ Транскрипція не вийшла: " + str(e)[:250])
        finally:
            self.q.put(None)

    def _show_transcript(self, title, text):
        """📜 v15: вікно транскрипції — читати, стиснути до ~10 хв, зробити сценарій."""
        win = ctk.CTkToplevel(self.root)
        win.title("📜 Транскрипція")
        win.geometry("900x640")
        win.attributes("-topmost", True)
        win.after(400, lambda: win.attributes("-topmost", False))
        try:
            win.grab_set()
        except Exception:
            pass
        ctk.CTkLabel(win, text="📜 " + (title or "YouTube-відео")[:90],
                     font=self._f(14, "bold"), anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(win, text="{} символів".format(len(text)), font=self._f(11),
                     text_color=self.MUTED, anchor="w").pack(fill="x", padx=16, pady=(0, 4))
        box = ctk.CTkTextbox(win, font=self._f(12), wrap="word",
                             fg_color=self.INSET, corner_radius=10)
        box.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        box.insert("1.0", text)

        def do_shorten():
            short = summarize_to_seconds(box.get("1.0", "end").strip(), 600)
            box.delete("1.0", "end")
            box.insert("1.0", short)
            messagebox.showinfo("Готово", "Стиснув до ~10 хвилин озвучки (≈{} слів)".format(len(short.split())))

        def do_script():
            short = summarize_to_seconds(box.get("1.0", "end").strip(), 600)
            parts = chunk_script_parts(short)
            self.script.delete("1.0", "end")
            self.script.insert("1.0", parts)
            self._set_mode("script")
            n = len([b for b in parts.split("\n\n") if b.strip()])
            messagebox.showinfo("Готово", "Сценарій з {} частин вставлено у картку «🎬 Сценарій» —\nперемикач «Генерувати за сценарієм» уже увімкнений ✓".format(n))
            win.destroy()

        def do_save():
            path = filedialog.asksaveasfilename(title="Зберегти транскрипцію",
                                                defaultextension=".txt",
                                                filetypes=[("Текстові файли", "*.txt")])
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(box.get("1.0", "end").strip())
                self.say("💾 Транскрипцію збережено: " + path)

        row = ctk.CTkFrame(win, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkButton(row, text="✂️ Стиснути до ~10 хв", height=34, corner_radius=17,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=do_shorten).pack(side="left")
        ctk.CTkButton(row, text="🎬 У сценарій", height=34, corner_radius=17,
                      fg_color=self.GREEN, hover_color="#0E9F6E", font=self._f(12),
                      command=do_script).pack(side="left", padx=(8, 0))
        ctk.CTkButton(row, text="💾 Зберегти .txt", height=34, corner_radius=17,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=do_save).pack(side="left", padx=(8, 0))
        ctk.CTkButton(row, text="Закрити", height=34, corner_radius=17,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=win.destroy).pack(side="right")

    def download_yt_many(self):
        """Завантаження всіх відео з поля посилань (окремий потік)."""
        links = self.parse_yt_links(self.yt_many.get("1.0", "end"))
        if not links:
            messagebox.showwarning("Стоп", "Встав посилання на відео — кожне з нового рядка 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._yt_thread, args=(links,), daemon=True).start()

    def _yt_thread(self, links):
        try:
            ensure_ffmpeg(self.say)
            ok = 0
            for i, url in enumerate(links):
                try:
                    self.say("⬇️ {}/{}: {}…".format(i + 1, len(links), url[:70]))
                    p = youtube_download(url, YT_OUT_DIR, YT_QUALITY[self.yt_q.get()], self.say)
                    self.say("✅ Готово: " + p)
                    ok += 1
                except Exception as e:
                    self.say("❌ Це посилання не вийшло: " + str(e)[:200])
            self.say("📂 Завантажено {} з {} — папка Відео\\YouTube".format(ok, len(links)))
        except Exception as e:
            self.say("❌ " + str(e)[:300])
        finally:
            self.q.put(None)

    def parse_yt_links(self, text):
        """Збирає всі посилання з тексту: з нових рядків або через пробіл/кому."""
        links = []
        for ln in (text or "").split("\n"):
            for part in re.split(r"[\s,;]+", ln):
                p = part.strip()
                if p.startswith("http") and p not in links:
                    links.append(p)
        return links

    def yt_search_now(self):
        """Пошук YouTube у фоновому потоці (без жодних API-ключів)."""
        q = self.yt_search_entry.get().strip()
        if q.startswith("http"):
            messagebox.showwarning("Стоп", "Це схоже на посилання 🙂 Встав його у поле «🔗 Відео з YouTube» вище, а тут пиши запит для пошуку")
            return
        if len(q) < 2:
            messagebox.showwarning("Стоп", "Введи, що шукати 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        self.say("🔎 Шукаю на YouTube: " + q + "…")
        threading.Thread(target=self._yt_search_thread, args=(q,), daemon=True).start()

    def _yt_search_thread(self, q):
        try:
            results, err = yt_search(q, YT_SEARCH_LIMIT, self.say)
            self.q.put(("yt_search_results", results, err))
        except Exception as e:
            self.q.put(("yt_search_results", [], "помилка: " + str(e)[:150]))
        finally:
            self.q.put(None)

    def _show_yt_results(self, results, err):
        """Малює знайдені відео з чекбоксами (тільки з головного потоку)."""
        for w in self.yt_results_frame.winfo_children():
            w.destroy()
        self.yt_checked = {}
        if not results:
            ctk.CTkLabel(self.yt_results_frame, text=(err or "Нічого не знайшов") + " — спробуй інший запит",
                         font=ctk.CTkFont(family="Segoe UI", size=12),
                         text_color=self.MUTED).pack(anchor="w", pady=6)
            return
        for r in results:
            mm, ss = divmod(int(r["dur"]), 60)
            views = int(r["views"])
            if views >= 1000000:
                vtxt = "{:.1f} млн перегл.".format(views / 1000000.0)
            elif views >= 1000:
                vtxt = "{:.1f} тис. перегл.".format(views / 1000.0)
            else:
                vtxt = str(views) + " перегл."
            var = ctk.BooleanVar(value=False)
            self.yt_checked[r["url"]] = var
            row = ctk.CTkFrame(self.yt_results_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkCheckBox(row, variable=var, text="",
                             checkbox_width=22, checkbox_height=22,
                             fg_color=self.ACCENT, hover_color="#3395FF").pack(side="left", padx=(4, 6))
            ctk.CTkLabel(row, text="{} • {:02d}:{:02d} • {}".format(r["title"], mm, ss, vtxt),
                         font=ctk.CTkFont(family="Segoe UI", size=12), anchor="w",
                         justify="left", wraplength=640).pack(side="left", fill="x", expand=True)
        self.say("✅ Знайдено {} відео — познач потрібні і тисни ЗГЕНЕРУВАТИ".format(len(results)))


    def _refresh_mix_count(self):
        """🎧 v16: скільки придатних треків у папці MixTracks."""
        n = 0
        if os.path.isdir(MIX_TRACKS_DIR):
            n = sum(1 for f in os.listdir(MIX_TRACKS_DIR)
                    if f.lower().endswith((".mp3", ".wav", ".m4a")))
        try:
            self.px_tracks_lbl.configure(text="Треків у папці: {}".format(n))
        except Exception:
            pass

    def open_mix_folder(self):
        os.makedirs(MIX_TRACKS_DIR, exist_ok=True)
        os.startfile(MIX_TRACKS_DIR)  # Windows

    def px_search_now(self):
        """🎵 v16: пошук музики Pixabay у фоновому потоці."""
        key = self.px_key.get().strip()
        q = self.px_query.get().strip()
        if len(key) < 10:
            messagebox.showwarning("Стоп", "Встав ключ Pixabay 🙂 (безкоштовний — на сторінці pixabay.com/api/docs після входу в акаунт)")
            return
        if len(q) < 2:
            messagebox.showwarning("Стоп", "Напиши, яку музику шукати 🙂 (наприклад: deep house)")
            return
        save_pixabay_key(key)
        self.btn.configure(state="disabled")
        self.bar.start()
        self.say("🎵 Шукаю музику на Pixabay: " + q + "…")
        threading.Thread(target=self._px_search_thread, args=(key, q), daemon=True).start()

    def _px_search_thread(self, key, q):
        try:
            results, err = pixabay_music_search(key, q, 20, self.say)
            self.q.put(("px_results", results, err))
        except Exception as e:
            self.q.put(("px_results", [], "помилка: " + str(e)[:150]))
        finally:
            self.q.put(None)

    def _show_px_results(self, results, err):
        """Малює знайдені треки з чекбоксами (тільки з головного потоку)."""
        for w in self.px_results_frame.winfo_children():
            w.destroy()
        self.px_checked = {}
        if not results:
            ctk.CTkLabel(self.px_results_frame, text=(err or "Нічого не знайшов") + " — спробуй інший запит",
                         font=ctk.CTkFont(family="Segoe UI", size=12),
                         text_color=self.MUTED).pack(anchor="w", pady=6)
            return
        for r in results:
            mm, ss = divmod(int(r["dur"]), 60)
            var = ctk.BooleanVar(value=False)
            self.px_checked[r["url"]] = var
            row = ctk.CTkFrame(self.px_results_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkCheckBox(row, variable=var, text="",
                            checkbox_width=22, checkbox_height=22,
                            fg_color=self.ACCENT, hover_color=self.ACCENT_H).pack(side="left", padx=(4, 6))
            ctk.CTkLabel(row, text="{} • {:02d}:{:02d} • {}".format(r["title"], mm, ss, r["author"]),
                         font=ctk.CTkFont(family="Segoe UI", size=12), anchor="w",
                         justify="left", wraplength=220).pack(side="left", fill="x", expand=True)
        self.say("✅ Знайдено {} треків — познач потрібні і натисни «⬇️ Завантажити обране»".format(len(results)))

    def px_download_now(self):
        """⬇️ v16: обрані треки з Pixabay → папка MixTracks."""
        sel = [u for u, v in self.px_checked.items() if v.get()]
        if not sel:
            messagebox.showwarning("Стоп", "Спершу познач треки в результатах пошуку 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        self.say("⬇️ Завантажую {} треків у папку MixTracks…".format(len(sel)))
        threading.Thread(target=self._px_download_thread, args=(sel,), daemon=True).start()

    def _px_download_thread(self, sel):
        try:
            for i, u in enumerate(sel, 1):
                try:
                    p = pixabay_download(u, MIX_TRACKS_DIR, self.say)
                    self.say("✔️ {}/{}: {}".format(i, len(sel), os.path.basename(p)))
                except Exception as e:
                    self.say("⚠️ Трек не завантажився: " + str(e)[:120])
            self.q.put(("mix_tracks", 0))
        finally:
            self.q.put(None)

    def suno_gen_now(self):
        """🎼 v19: генерація треку Suno у фоновому потоці."""
        cookie = self.suno_cookie.get().strip()
        desc = self.suno_desc.get().strip()
        tags = self.suno_tags.get().strip()
        if len(cookie) < 40 or "__client" not in cookie:
            messagebox.showwarning("Стоп", "Встав cookie сесії Suno 🙂\n\nsuno.com → F12 → Network → будь-який запит → заголовок Cookie — скопіюй ЦІЛИЙ рядок (з __client=…)")
            return
        if not desc and not tags:
            messagebox.showwarning("Стоп", "Напиши опис треку або стиль 🙂 (наприклад: заспокійливий lo-fi, вечірнє місто)")
            return
        save_suno_cookie(cookie)
        self.btn.configure(state="disabled")
        self.bar.start()
        self.say("🎼 Suno: готую запит…")
        threading.Thread(target=self._suno_gen_thread,
                         args=(cookie, desc, tags, self.suno_inst.get()), daemon=True).start()

    def _suno_gen_thread(self, cookie, desc, tags, instrumental):
        try:
            jwt, ids = suno_generate(cookie, desc, tags, instrumental, self.say)
            saved = suno_wait_and_download(cookie, jwt, ids, self.say, timeout=300)
            if saved:
                self.say("✅ Готово — {} трек(и) Suno у папці MixTracks, можна міксувати".format(len(saved)))
                self.q.put(("mix_tracks", 0))
            else:
                self.say("⚠️ Suno не дав готових треків за 5 хв — спробуй ще раз або згенеруй на suno.com")
        except Exception as e:
            self.say("⚠️ Suno: " + str(e)[:200])
        finally:
            self.q.put(None)

    def suno_credits_now(self):
        """💰 v19: перевірка кредитів акаунта Suno."""
        cookie = self.suno_cookie.get().strip()
        if len(cookie) < 40 or "__client" not in cookie:
            messagebox.showwarning("Стоп", "Встав cookie сесії Suno 🙂 (suno.com → F12 → Network → заголовок Cookie)")
            return
        save_suno_cookie(cookie)
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._suno_credits_thread, args=(cookie,), daemon=True).start()

    def _suno_credits_thread(self, cookie):
        try:
            d = suno_credits(cookie, self.say)
            self.say("💰 Кредити Suno: зосталось {}, ліміт на місяць {}, використано {}".format(
                d.get("total_credits_left"), d.get("monthly_limit"), d.get("monthly_usage")))
        except Exception as e:
            self.say("⚠️ Suno: " + str(e)[:200])
        finally:
            self.q.put(None)

    def pipeline_mix(self, title):
        """🎧 v16: пайплайн міксу — окремий від класичного, щоб не плутались."""
        ok = False
        try:
            self.preflight_notes()  # 🧪 v24: місце на диску / музика / cv2 — до старту
            minutes = 60
            try:
                minutes = max(10, min(180, int(float(self.mix_minutes.get()))))
            except Exception:
                minutes = 60
            files = None
            if getattr(self, "merge_bg", None) and self.merge_bg.get() and self.merge_files:
                files = list(self.merge_files)
            sel = [u for u, v in getattr(self, "yt_checked", {}).items() if v.get()]
            generate_mix(title, minutes, SIZES[self.size.get()], self.say,
                         on_workdir=lambda wd: setattr(self, "workdir", wd),
                         bg_files=files, yt_search_urls=sel,
                         cover=bool(self.cover_on.get()), seo=bool(self.seo.get()))
            ok = True
            if self.workdir and os.path.isdir(self.workdir):
                f = os.path.join(self.workdir, "final.mp4")
                if os.path.isfile(f):
                    self.final_path = f
                    self.q.put(("poster", f))
                try:
                    os.startfile(self.workdir)
                    self.say("📂 Відкрив папку з готовим міксом")
                except Exception:
                    pass
        except Exception as e:
            self.say("❌ Помилка міксу: " + str(e)[:300])
        finally:
            self.q.put(("gen_end", ok))

    def pick_merge_files(self):
        """Вибір кількох відео для компіляції."""
        ps = filedialog.askopenfilenames(filetypes=[("Відео", "*.mp4 *.mov *.mkv *.avi *.webm")])
        if ps:
            self.merge_files = list(ps)
            names = ", ".join(os.path.basename(p) for p in self.merge_files[:3])
            if len(self.merge_files) > 3:
                names += " +" + str(len(self.merge_files) - 3) + " ще"
            self.merge_lbl.configure(text="Обрано: " + names, text_color="#FFFFFF")
            self.say("🎞 Обрано відео: " + str(len(self.merge_files)))

    def clear_merge_files(self):
        self.merge_files = []
        self.merge_lbl.configure(text="Не обрано жодного відео", text_color=self.MUTED)

    def merge_now(self):
        """Компіляція обраних відео в одне — окремим потоком."""
        if not self.merge_files:
            messagebox.showwarning("Стоп", "Спершу додай хоча б одне відео 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._merge_thread, daemon=True).start()

    def _merge_thread(self):
        try:
            ensure_ffmpeg(self.say)
            p = merge_videos(self.merge_files, self.say)
            self.say("✅ ГОТОВО: " + p)
            self.say("📂 Папка: Відео\\Compiled")
        except Exception as e:
            self.say("❌ " + str(e)[:300])
        finally:
            self.q.put(None)

    def pick_meta_file(self):
        """🧬 v33: обрати відео для переписування метаданих."""
        p = filedialog.askopenfilename(filetypes=[("Відео", "*.mp4 *.mov *.mkv *.avi *.webm")])
        if p:
            self.meta_file = p
            self.meta_lbl.configure(text="Обрано: " + os.path.basename(p), text_color="#FFFFFF")
            self.say("🧬 Обрано: " + os.path.basename(p))

    def clear_meta_file(self):
        self.meta_file = None
        self.meta_lbl.configure(text="Не обрано відео", text_color=self.MUTED)

    def meta_now(self):
        """🧬 v33: переписати метадані обраного відео — окремим потоком."""
        if not getattr(self, "meta_file", None) or not os.path.isfile(self.meta_file):
            messagebox.showwarning("Стоп", "Спершу додай відео 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._meta_thread, daemon=True).start()

    def _meta_thread(self):
        p = getattr(self, "meta_file", None)
        try:
            ensure_ffmpeg(self.say)
            before = metadata_snapshot(p)
            fields = ", ".join("{}={}".format(k, str(v)[:40])
                               for k, v in sorted(before.items()) if k != "duration")
            self.say("🧬 Було: " + (fields[:200] if fields else "тегів нема"))
            out = scrub_metadata(p, self.meta_mode.get() == "Глибоко", self.say)
            after = metadata_snapshot(out)
            tail = ", ".join("{}={}".format(k, str(v)[:30])
                             for k, v in sorted(after.items()) if k != "duration")
            self.say("🧬 Стало: " + (tail[:200] if tail else "порожньо"))
            self.say("ℹ️ Вихідний файл не змінено — результат поруч з ним")
            try:
                os.startfile(os.path.dirname(out))  # Windows: показати результат
            except Exception:
                pass
        except Exception as e:
            self.say("❌ Метадані: " + str(e)[:300])
            if self.meta_mode.get() != "Глибоко":
                self.say("💡 Швидко не потягнув цей формат — спробуй «Глибоко» (перекодування)")
        finally:
            self.q.put(None)

    def pick_stt_file(self):
        """🎤 v36: обрати відео для авто-субтитрів (Whisper на Groq)."""
        p = filedialog.askopenfilename(filetypes=[("Відео", "*.mp4 *.mov *.mkv *.avi *.webm")])
        if p:
            self.stt_file = p
            self.stt_lbl.configure(text="Обрано: " + os.path.basename(p), text_color="#FFFFFF")
            self.say("🎤 Обрано: " + os.path.basename(p))

    def clear_stt_file(self):
        self.stt_file = None
        self.stt_lbl.configure(text="Не обрано відео", text_color=self.MUTED)

    def stt_now(self):
        """🎤 v36: субтитри з відео — окремим потоком (ffmpeg + Whisper, Tk не блокується)."""
        if not getattr(self, "stt_file", None) or not os.path.isfile(self.stt_file):
            messagebox.showwarning("Стоп", "Спершу додай відео 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._stt_thread, daemon=True).start()

    def _stt_thread(self):
        p = getattr(self, "stt_file", None)
        try:
            groq_transcribe_srt(p, self.say)
        except Exception as e:
            self.say("❌ Субтитри: " + str(e)[:300])
        finally:
            self.q.put(None)

    def trim_silence_now(self):
        """✂️ 2.0: прибрати тишу з готового відео — окремим потоком."""
        p = filedialog.askopenfilename(title="Відео, з якого прибрати тишу",
                                       filetypes=[("Відео", "*.mp4 *.mkv *.mov *.avi *.webm")])
        if not p:
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._trim_silence_thread, args=(p,), daemon=True).start()

    def _trim_silence_thread(self, p):
        try:
            silence_trim_video(p, self.say)
        except Exception as e:
            self.say("❌ Прибрання тиші: " + str(e)[:300])
        finally:
            self.q.put(None)

    def translate_srt_now(self):
        """🌐 2.0: переклад .srt (LibreTranslate → фолбек LLM-драбина)."""
        p = filedialog.askopenfilename(title="Субтитри (.srt)",
                                       filetypes=[("Субтитри", "*.srt")])
        if not p:
            return
        lang = simpledialog.askstring("Мова перекладу",
                                     "Двокод мови (наприклад: en, es, it, ru, de, pl):",
                                     initialvalue="en", parent=self)
        if not lang:
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._translate_srt_thread, args=(p, lang.strip().lower()), daemon=True).start()

    def _translate_srt_thread(self, p, lang):
        try:
            translate_srt_file(p, lang, self.say)
        except Exception as e:
            self.say("❌ Переклад субтитрів: " + str(e)[:300])
        finally:
            self.q.put(None)

    def dub_srt_now(self):
        """🎙 2.0: дубляж — озвучити .srt голосом із поля голосу, притиснувши
        кожну репліку у її таймінг; поруч є .mp4 — перезапишу йому доріжку."""
        p = filedialog.askopenfilename(title="Субтитри для дубляжу (.srt)",
                                       filetypes=[("Субтитри", "*.srt")])
        if not p:
            return
        voice = self.voice.get() if hasattr(self, "voice") else ""
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._dub_srt_thread, args=(p, voice), daemon=True).start()

    def _dub_srt_thread(self, p, voice):
        try:
            dub_srt_file(p, voice, self.say)
        except Exception as e:
            self.say("❌ Дубляж: " + str(e)[:300])
        finally:
            self.q.put(None)

    def ab_now(self):
        """🧪 2.0: A/B-заголовки за темою з поля запиту — окремим потоком."""
        q = self.query.get("1.0", "end").strip() if hasattr(self, "query") else ""
        if len(q) < 4:
            messagebox.showwarning("Стоп", "Спершу напиши тему у поле «Тема» 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._ab_thread, args=(q,), daemon=True).start()

    def _ab_thread(self, q):
        try:
            ab_titles(q, self.say)
        except Exception as e:
            self.say("❌ A/B-заголовки: " + str(e)[:300])
        finally:
            self.q.put(None)

    def pick_clone_ref(self):
        """🗣 v37: обрати зразок голосу (5–20 с чистої мови без музики)."""
        p = filedialog.askopenfilename(filetypes=[("Аудіо", "*.mp3 *.wav *.m4a *.ogg")])
        if p:
            self.clone_ref = p
            d = clone_cfg_load()
            d["sample"] = p
            clone_cfg_save(d)
            self.clone_lbl.configure(text="Зразок: " + os.path.basename(p), text_color="#FFFFFF")
            self.say("🗣 Зразок голосу: " + os.path.basename(p) + " (збережено для озвучки відео)")

    def clear_clone_ref(self):
        self.clone_ref = None
        self.clone_lbl.configure(text="Не обрано зразок голосу (mp3/wav, 5–20 с)",
                                 text_color=self.MUTED)

    def clone_now(self):
        """🗣 v37: клонувати голос — окремим потоком (Space, Tk не блокується)."""
        text = self.clone_txt.get().strip()
        if not text:
            messagebox.showwarning("Стоп", "Напиши текст, який скаже клон голосу 🙂")
            return
        ref = getattr(self, "clone_ref", None)
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._clone_thread, args=(text, ref), daemon=True).start()

    def _clone_thread(self, text, ref):
        try:
            if ref:
                out = os.path.splitext(ref)[0] + "_clone.mp3"
            else:
                out = os.path.join(os.path.expanduser("~"), "voice_clone.mp3")
            self.say("🗣 Chatterbox (HF Space, без ключа): генерую клон — перший запит може тривати до хвилини")
            hf_tts_clone(text, ref, out, self.say)
            self.say("🗣 Готово: " + os.path.basename(out))
            try:
                os.startfile(os.path.dirname(out) or ".")
            except Exception:
                pass
        except Exception as e:
            self.say("🗣 Клон не вийшов: " + str(e)[:200] + " (Space-черги публічні — спробуй пізніше)")
        finally:
            self.q.put(None)

    def img_now(self):
        """🖼 v37: AI-картинка з тексту — окремим потоком (FLUX, HF Space)."""
        prompt = self.img_txt.get().strip()
        if not prompt:
            messagebox.showwarning("Стоп", "Опиши картинку 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._img_thread, args=(prompt,), daemon=True).start()

    def _img_thread(self, prompt):
        try:
            stamp = time.strftime("%Y%m%d_%H%M%S")
            folder = os.path.join(os.path.expanduser("~"), "Pictures")
            try:
                os.makedirs(folder, exist_ok=True)
            except OSError:
                folder = os.path.expanduser("~")
            out = os.path.join(folder, "ai_" + stamp + ".png")
            self.say("🖼 FLUX.1-schnell (HF Space, без ключа): малюю…")
            hf_image(prompt, out, self.say)
            self.say("🖼 Готово: " + os.path.basename(out))
            try:
                os.startfile(folder)
            except Exception:
                pass
        except Exception as e:
            self.say("🖼 Картинка не вийшла: " + str(e)[:200] + " (Space-черги публічні — спробуй пізніше)")
        finally:
            self.q.put(None)

    def pick_anim_img(self):
        """🎬 v37: обрати картинку для оживлення (WAN 2.2)."""
        p = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.jpeg *.webp")])
        if p:
            self.anim_img = p
            self.anim_lbl.configure(text="Обрано: " + os.path.basename(p), text_color="#FFFFFF")
            self.say("🎬 Обрано: " + os.path.basename(p))

    def clear_anim_img(self):
        self.anim_img = None
        self.anim_lbl.configure(text="Не обрано картинку", text_color=self.MUTED)

    def anim_now(self):
        """🎬 v37: оживити картинку — окремим потоком (WAN 2.2, HF Space)."""
        p = getattr(self, "anim_img", None)
        if not p or not os.path.isfile(p):
            messagebox.showwarning("Стоп", "Спершу додай картинку 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._anim_thread, args=(p, self.anim_txt.get().strip()),
                         daemon=True).start()

    def _anim_thread(self, p, prompt):
        try:
            out = os.path.splitext(p)[0] + "_wan.mp4"
            self.say("🎬 WAN 2.2 (HF Space, без ключа): оживляю кадр — це довго, до кількох хвилин")
            hf_image_to_video(p, prompt, out, self.say)
            self.say("🎬 Готово: " + os.path.basename(out) + " (поруч з картинкою)")
            try:
                os.startfile(os.path.dirname(p) or ".")
            except Exception:
                pass
        except Exception as e:
            self.say("🎬 Відео не вийшло: " + str(e)[:200] + " (Space-черги публічні — спробуй пізніше)")
        finally:
            self.q.put(None)

    def pick_edit_img(self):
        """🖌 v38: обрати картинку для редагування промптом (FLUX.1 Kontext)."""
        p = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.jpeg *.webp")])
        if p:
            self.edit_img = p
            self.edit_lbl.configure(text="Обрано: " + os.path.basename(p), text_color="#FFFFFF")
            self.say("🖌 Обрано: " + os.path.basename(p))

    def clear_edit_img(self):
        self.edit_img = None
        self.edit_lbl.configure(text="Не обрано картинку", text_color=self.MUTED)

    def edit_now(self):
        """🖌 v38: редагувати картинку промптом — окремим потоком (Kontext)."""
        p = getattr(self, "edit_img", None)
        if not p or not os.path.isfile(p):
            messagebox.showwarning("Стоп", "Спершу додай картинку 🙂")
            return
        if not self.edit_txt.get().strip():
            messagebox.showwarning("Стоп", "Напиши, що змінити («вечір, додай дощ») 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._edit_thread, args=(p, self.edit_txt.get().strip()),
                         daemon=True).start()

    def _edit_thread(self, p, prompt):
        try:
            out = os.path.splitext(p)[0] + "_edit.png"
            self.say("🖌 FLUX.1 Kontext (HF Space, без ключа): редагую — до пари хвилин")
            hf_edit_image(p, prompt, out, self.say)
            self.say("🖌 Готово: " + os.path.basename(out) + " (поруч з картинкою)")
            try:
                os.startfile(os.path.dirname(p) or ".")
            except Exception:
                pass
        except Exception as e:
            self.say("🖌 Редагування не вийшло: " + str(e)[:200] + " (Space-черги публічні — спробуй пізніше)")
        finally:
            self.q.put(None)

    def pick_nobg_img(self):
        """✂️ v38: обрати картинку для видалення фону."""
        p = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.jpeg *.webp")])
        if p:
            self.nobg_img = p
            self.nobg_lbl.configure(text="Обрано: " + os.path.basename(p), text_color="#FFFFFF")
            self.say("✂️ Обрано: " + os.path.basename(p))

    def clear_nobg_img(self):
        self.nobg_img = None
        self.nobg_lbl.configure(text="Не обрано картинку", text_color=self.MUTED)

    def nobg_now(self):
        """✂️ v38: видалити фон — окремим потоком (HF Space)."""
        p = getattr(self, "nobg_img", None)
        if not p or not os.path.isfile(p):
            messagebox.showwarning("Стоп", "Спершу додай картинку 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._nobg_thread, args=(p,), daemon=True).start()

    def _nobg_thread(self, p):
        try:
            out = os.path.splitext(p)[0] + "_nobg.png"
            self.say("✂️ Видаляю фон (HF Space, без ключа)…")
            hf_remove_bg(p, out, self.say)
            self.say("✂️ Готово: " + os.path.basename(out) + " (прозорий png)")
            try:
                os.startfile(os.path.dirname(p) or ".")
            except Exception:
                pass
        except Exception as e:
            self.say("✂️ Не вийшло: " + str(e)[:200] + " (Space-черги публічні — спробуй пізніше)")
        finally:
            self.q.put(None)

    def pick_ocr_img(self):
        """🔍 v38: обрати картинку або скріншот для OCR (DeepSeek-OCR)."""
        p = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.jpeg *.webp *.bmp")])
        if p:
            self.ocr_img = p
            self.ocr_lbl.configure(text="Обрано: " + os.path.basename(p), text_color="#FFFFFF")
            self.say("🔍 Обрано: " + os.path.basename(p))

    def ocr_now(self):
        """🔍 v38: витягти текст з картинки — окремим потоком (DeepSeek-OCR)."""
        p = getattr(self, "ocr_img", None)
        if not p or not os.path.isfile(p):
            messagebox.showwarning("Стоп", "Спершу додай картинку або скріншот 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._ocr_thread, args=(p,), daemon=True).start()

    def _ocr_thread(self, p):
        try:
            out = os.path.splitext(p)[0] + "_текст.txt"
            self.say("🔍 DeepSeek-OCR (HF Space, без ключа): читаю текст…")
            hf_ocr(p, out, self.say)
            self.say("🔍 Готово: " + os.path.basename(out) + " (поруч з картинкою)")
            try:
                os.startfile(os.path.dirname(p) or ".")
            except Exception:
                pass
        except Exception as e:
            self.say("🔍 OCR не вийшов: " + str(e)[:200] + " (Space-черги публічні — спробуй пізніше)")
        finally:
            self.q.put(None)

    def img_translate_now(self):
        """🌍 v49: текст з картинки → 4 мови (🇷🇺 російська, 🇪🇸 іспанська,
        🇮🇹 італійська, 🇬🇧 англійська): OCR (DeepSeek, без ключа) → переклад
        драбиною «Авто» → 4 txt-файли поруч з картинкою. Одна кнопка."""
        p = getattr(self, "ocr_img", None)
        if not p or not os.path.isfile(p):
            messagebox.showwarning("Стоп", "Спершу додай картинку через «➕ Картинка» 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._img_translate_thread, args=(p,),
                         daemon=True).start()

    def _img_translate_thread(self, p):
        try:
            tmp = os.path.splitext(p)[0] + "_ocr_tmp.txt"
            self.say("🌍 Читаю текст з картинки (DeepSeek-OCR)…")
            hf_ocr(p, tmp, self.say)
            with open(tmp, encoding="utf-8") as f:
                text = (f.read() or "").strip()
            if not text:
                raise RuntimeError("OCR не знайшов тексту на картинці")
            base = os.path.splitext(p)[0]
            made = []
            for code, lang in IMG_TRANSLATE_LANGS:
                self.say("🌍 Перекладаю на " + lang + "…")
                sys_p = ("Ти — точний перекладач. Переклади ВСЕ надане "
                         "повідомлення на " + lang + ". Поверни ЛИШЕ "
                         "перекладений текст, без пояснень.")
                tr = (llm_chat("auto", "", "", text[:6000],
                               system=sys_p, timeout=90) or "").strip()
                if tr:
                    out = base + "_переклад_" + code + ".txt"
                    with open(out, "w", encoding="utf-8") as f:
                        f.write(tr + "\n")
                    made.append(code)
                else:
                    self.say("🌍 " + lang + ": усі джерела мовчать — спробуй ще раз")
            if made:
                self.say("🌍 Готово: " + str(len(made)) + " переклади ("
                         + ", ".join(made) + ") — поруч з картинкою")
                try:
                    os.startfile(os.path.dirname(p) or ".")
                except Exception:
                    pass
            try:
                os.remove(tmp)
            except OSError:
                pass
        except Exception as e:
            self.say("🌍 Переклад не вийшов: " + str(e)[:200])
        finally:
            self.q.put(None)

    def cover_lang_now(self):
        """📷 v49: обкладинка ІНШОЮ МОВОЮ — завантажена обкладинка: читаю
        заголовок (OCR) → перекладаю на 4 мови → генерую 4 нові обкладинки
        з ПЕРЕКЛАДЕНИМ заголовком на тій самій картинці (стиль як make_cover)."""
        p = getattr(self, "ocr_img", None)
        if not p or not os.path.isfile(p):
            messagebox.showwarning("Стоп", "Спершу додай обкладинку через «➕ Картинка» 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._cover_lang_thread, args=(p,),
                         daemon=True).start()

    def _cover_lang_thread(self, p):
        try:
            tmp = os.path.splitext(p)[0] + "_ocr_tmp.txt"
            self.say("📷 Обкладинка: читаю заголовок (OCR)…")
            hf_ocr(p, tmp, self.say)
            with open(tmp, encoding="utf-8") as f:
                text = (f.read() or "").strip()[:600]
            if not text:
                raise RuntimeError("OCR не знайшов тексту на обкладинці")
            base = os.path.splitext(p)[0]
            made = []
            for code, lang in IMG_TRANSLATE_LANGS:
                self.say("📷 Обкладинка: заголовок на " + lang + "…")
                sys_p = ("Ти — перекладач обкладинок YouTube. Дай ЛИШЕ "
                         "перекладений ЗАГОЛОВОК цієї обкладинки на " + lang
                         + " — коротко, як назва відео, без пояснень.")
                tr = (llm_chat("auto", "", "", text, system=sys_p,
                               timeout=90) or "").strip()
                if tr:
                    out = base + "_cover_" + code + ".jpg"
                    make_cover_from_image(p, tr[:120], out, self.say)
                    made.append(code)
                else:
                    self.say("📷 " + lang + ": джерела мовчать — спробуй ще раз")
            if made:
                self.say("📷 Готово: " + str(len(made)) + " обкладинки ("
                         + ", ".join(made) + ") — поруч з оригіналом")
                try:
                    os.startfile(os.path.dirname(p) or ".")
                except Exception:
                    pass
            try:
                os.remove(tmp)
            except OSError:
                pass
        except Exception as e:
            self.say("📷 Обкладинки не вийшло: " + str(e)[:200])
        finally:
            self.q.put(None)

    def pick_fl_first(self):
        """🎬 v38: перший кадр переходу (WAN 2.2)."""
        p = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.jpeg *.webp")])
        if p:
            self.fl_first = p
            self._fl_refresh()

    def pick_fl_second(self):
        """🎬 v38: останній кадр переходу (WAN 2.2)."""
        p = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.jpeg *.webp")])
        if p:
            self.fl_second = p
            self._fl_refresh()

    def clear_fl_imgs(self):
        self.fl_first = None
        self.fl_second = None
        self.fl_lbl.configure(text="Обери ДВІ картинки: початок і кінець", text_color=self.MUTED)

    def _fl_refresh(self):
        a, b = getattr(self, "fl_first", None), getattr(self, "fl_second", None)
        if a and b:
            self.fl_lbl.configure(text="1️⃣ {}  →  2️⃣ {}".format(os.path.basename(a), os.path.basename(b)),
                                  text_color="#FFFFFF")
        elif a or b:
            self.fl_lbl.configure(text="Обрано один кадр — додай другий", text_color="#FFFFFF")
        else:
            self.fl_lbl.configure(text="Обери ДВІ картинки: початок і кінець", text_color=self.MUTED)

    def fl_now(self):
        """🎬 v38: перший кадр → останній — окремим потоком (WAN 2.2 Space)."""
        a, b = getattr(self, "fl_first", None), getattr(self, "fl_second", None)
        if not (a and os.path.isfile(a)) or not (b and os.path.isfile(b)):
            messagebox.showwarning("Стоп", "Спершу додай ДВІ картинки: перший і останній кадр 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._fl_thread, args=(a, b, self.fl_txt.get().strip()),
                         daemon=True).start()

    def _fl_thread(self, a, b, prompt):
        try:
            out = os.path.splitext(a)[0] + "_perexid.mp4"
            self.say("🎬 WAN 2.2 (HF Space, без ключа): зшиваю кадри — це довго, до кількох хвилин")
            hf_frames_to_video(a, b, prompt, out, self.say)
            self.say("🎬 Готово: " + os.path.basename(out) + " (поруч з першою картинкою)")
            try:
                os.startfile(os.path.dirname(a) or ".")
            except Exception:
                pass
        except Exception as e:
            self.say("🎬 Перехід не вийшов: " + str(e)[:200] + " (Space-черги публічні — спробуй пізніше)")
        finally:
            self.q.put(None)

    def core_check(self):
        """🧠 v38: перевірити живість усіх 7 нейромереж — окремим потоком."""
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._core_thread, daemon=True).start()

    def _core_thread(self):
        names = {"tts": "🗣 клон голосу", "img": "🖼 AI-картинка", "vid": "🎬 оживлення кадру",
                 "edit": "🖌 редагування промптом", "nobg": "✂️ видалення фону",
                 "ocr": "🔍 OCR", "fl": "🎬 перший→останній кадр"}
        self.say("🧠 Перевіряю {} нейромереж на HF Spaces (до півхвилини)…".format(len(names)))
        ok = 0
        try:
            for key in sorted(names):
                base = HF_SPACES.get(key, "")
                try:
                    r = requests.get(base.rstrip("/") + "/gradio_api/info", timeout=12,
                                     headers={"User-Agent": UA_STRING})
                    if r.status_code == 200:
                        ok += 1
                        self.say("🟢 " + names[key] + " — живий")
                    else:
                        self.say("🔴 " + names[key] + " — код " + str(r.status_code))
                except Exception as e:
                    self.say("🔴 " + names[key] + " — не відповідає: " + str(e)[:80])
            self.say("🧠 Нейро-ядро: {}/{} нейромереж живі".format(ok, len(names)))
        finally:
            self.q.put(None)

    def clone_voice_toggle(self):
        """🗣 v38: перемикач «озвучувати відео клоном» — стан у tools/clone.json
        (лише локально). Клон повільніший за edge-tts — Space чергує кожен шматок."""
        on = bool(self.clone_voice_on.get())
        cfg = clone_cfg_load()
        if on and not ((cfg.get("sample") or "").strip() and os.path.isfile(cfg["sample"])):
            messagebox.showwarning("Стоп", "Спершу обери зразок голосу (5–20 с) у картці 🗣 🙂")
            self.clone_voice_on.set(False)
            return
        cfg["enabled"] = on
        clone_cfg_save(cfg)
        if on:
            self.say("🗣 Відео озвучуватиметься клоном твого голосу (Chatterbox; повільніше за edge-tts, караоке вимкнено)")
        else:
            self.say("🗣 Озвучка відео — edge-tts, як раніше")

    def open_folder(self):
        if self.workdir and os.path.isdir(self.workdir):
            os.startfile(self.workdir)  # Windows

    def say(self, msg):
        self.q.put(msg)

    def _poll(self):
        while True:
            try:
                msg = self.q.get_nowait()
            except queue.Empty:
                break
            if isinstance(msg, tuple):
                kind = msg[0]
                if kind == "yt_search_results":
                    self._show_yt_results(msg[1], msg[2])
                elif kind == "px_results":  # 🎵 v16: результати пошуку Pixabay
                    self._show_px_results(msg[1], msg[2])
                elif kind == "mix_tracks":  # 🎧 v16: оновити лічильник треків
                    self._refresh_mix_count()
                elif kind == "pins_results":  # 🖼 v17: результати пошуку Pinterest
                    self._show_pins_results(msg[1], msg[2])
                elif kind == "transcript":  # 📜 v15: показати вікно транскрипції
                    self._show_transcript(msg[1], msg[2])
                elif kind == "poster":
                    self._set_poster(msg[1])
                elif kind == "poster_img":
                    self._apply_poster(msg[1])
                elif kind == "thumb":
                    self._apply_hist_thumb(msg[1], msg[2])
                elif kind == "tools":
                    self._apply_tools_status(msg[1], msg[2])
                elif kind == "batch_reset":  # 📚 v14: нова тема батчу — кроки починаються заново
                    self._reset_steps()
                elif kind == "agent_llm":  # 🧠 v29: локальна модель розібрала фразу
                    self._agent_llm_done(msg[1])
                elif kind == "ollama_check":  # 🧠 v29: перевірка Ollama готова
                    self._ollama_check_done(msg[1])
                elif kind == "chat_stream":  # ⚡ v42: токен стріму — малюю одразу
                    self._chat_stream_delta(msg[1])
                elif kind == "voice_text":  # 🎤 v51: диктовка розпізнана
                    self._voice_text_done(msg[1])
                elif kind == "chat_done":  # ⚡ v42: відповідь допливла повністю
                    self._chat_done(msg[1])
                elif kind == "gen_end":
                    ok = msg[1]
                    self.bar.stop()
                    self.bar.set(0)
                    self.btn.configure(state="normal")
                    self._gen_running = False
                    if ok:
                        self._finish_steps(True)
                        self.status_lbl.configure(text="● Готово", text_color=self.GREEN)
                    else:
                        self.status_lbl.configure(text="● Спробуй ще", text_color="#F59E0B")
                continue
            if msg is None:  # завантаження / пошук / компіляція завершені
                self.bar.stop()
                self.bar.set(0)
                self.btn.configure(state="normal")
                continue
            if getattr(self, "_gen_running", False):
                self._advance_step(msg)
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.root.after(150, self._poll)

    def _advance_step(self, msg):
        """Живі кроки пайплайну: повідомлення журналу просувають крок за ключовими словами."""
        nxt = self._step + 1
        if nxt >= len(self.STEPS):
            return
        for k in self.STEP_KEYS[nxt]:
            if k in msg:
                self._set_step(nxt)
                return

    def _agent_send(self):
        """🤖 v26: фраза → поля UI → підказка у журналі; «давай» → старт генерації."""
        cmd = " ".join(self.agent_entry.get("1.0", "end").split())
        if not cmd:
            return
        if cmd.lower() in ("давай", "давай!", "ок", "окей", "старт", "go",
                           "запуск", "погнали", "виконай"):
            if getattr(self, "_gen_running", False):
                return
            self.say("🤖 Поїхали!")
            self.start()
            return
        p = parse_agent_command(cmd)

        # 🧠 v29 / 🌐 v31 Tier 2: локальна модель (Ollama або 9Router) — для
        # слабко-розпізнаних фраз і сценаріїв без тексту; запит у фоні, Tk не блокується
        if hasattr(self, "ollama_model"):
            _om = (self.ollama_model.get() or "").strip()
            _ou = (hasattr(self, "ollama_url") and self.ollama_url.get().strip()) or ""
            if _om and _om != "модель не обрана" and _ou:
                _weak = not (p["size"] or p["voice"] or p["sub_style"] or p["trim"]
                             or p["cover"] or p["seo"] or p["script"])
                _need_sc = p["mode"] == "script" and not p["script"]
                if _weak or _need_sc:
                    _prov = self._llm_provider()
                    self.say("🧠 {} ({}): думаю над фразою у фоні…".format(
                        {"9router": "🌐 9Router", "pollinations": "🌐 Pollinations",
                         "kilo": "⚡ Kilo Code", "freekey": "🔑 Безкошт. ключ"}.get(_prov, "Ollama"), _om))
                    threading.Thread(target=self._agent_llm_thread,
                                    args=(cmd, _ou, _om, _weak, _need_sc, _prov),
                                    daemon=True).start()
        self._agent_apply(p)
        notes = []
        if p["mode"] == "mix":
            notes.append("режим 🎧 Мікс")
        elif p["mode"] == "script":
            notes.append("режим 📜 Сценарій")
        if p["size"]:
            notes.append(p["size"])
        if p["voice"]:
            notes.append("голос " + p["voice"])
        if p["sub_style"]:
            notes.append("субтитри «" + p["sub_style"] + "»")
        if p["no_music"]:
            notes.append("без музики")
        if p["trim"]:
            notes.append("щільна озвучка (без пауз)")
        if p["cover"]:
            notes.append("обкладинка")
        if p["seo"]:
            notes.append("SEO-пак")
        self.say("🤖 Зрозумів: тема «{}»{}".format(
            p["query"][:60], (" • " + ", ".join(notes)) if notes else ""))
        self.say("🤖 Перевір поля й напиши «давай» (або Enter) — згенерую.")

    def _switch_pub_platform(self, val=None):
        """📺 v32: платформа публікації — пресет 📦 (HandBrake-урок): Shorts 25 МБ,
        YouTube 100 МБ, Telegram 50 МБ + поради платформи в approval.txt."""
        try:
            mb = {"Shorts": "25 МБ", "YouTube": "100 МБ", "Telegram": "50 МБ"}.get(val or "")
            if mb and hasattr(self, "pack_size"):
                self.pack_size.set(mb)
                self.say("📺 {}: пресет 📦 {} (поради — в approval.txt)".format(val, mb))
        except Exception:
            pass  # 📺 v32: перемикач — ніколи не ламає інтерфейс

    def _agent_llm_thread(self, cmd, url, model, weak, need_script, provider="ollama"):
        """🧠 v29 / 🌐 v31: Tier 2 у фоновому потоці — LLM-розбір фрази і/або сценарій.
        Tk-поля не чіпаю: результат іде в чергу, застосує головний потік."""
        lp = None
        sc = ""
        if weak:  # 📝 v32: запит Tier 2 — у журнал llm_trace.jsonl (opik-патерн)
            t0 = time.time()
            lp = ollama_parse_command(cmd, url, model, provider)
            llm_trace("parse", provider, model, t0, bool(lp),
                      len(str(lp)) if lp else 0)
        if need_script:
            if provider == "pollinations" and weak:  # 🌐 v35: анонімний ліміт ~1/15 с — пауза між запитами
                self.say("⏳ Онлайн-модель: пауза ~16 с між запитами (безкоштовний ліміт)…")
                time.sleep(16)
            t0 = time.time()
            sc = ollama_write_script(parse_agent_command(cmd)["query"], url, model,
                                     provider) or ""
            llm_trace("script", provider, model, t0, bool(sc), len(sc or ""))
        self.q.put(("agent_llm", (cmd, lp, sc)))

    def _agent_llm_done(self, payload):
        """🧠 v29: результат Ollama — у головному потоці: налаштувати поля."""
        cmd, lp, sc = payload
        if not lp and not sc:
            self.say("🧠 Модель нічого не додумала — лишається, як розібрав парсер")
            return
        p = lp or parse_agent_command(cmd)
        if sc:
            p["script"] = sc
            p["mode"] = "script"
        self._agent_apply(p)
        self.say("🧠 AI-модель підказала{} — перевір поля й пиши «давай»".format(
            " і написала сценарій" if sc else ""))

    # 💬 v42: чат Асистента — функціонал Claude, скопійований чесно:
    # ⚡ справжній стрімінг токенів (SSE, як у Claude), 🎨 Markdown-рендер
    # (жирний/курсив/код/заголовки/списки), 📦 артефакти — великі код-блоки
    # ховаються у картки з кнопками (Копіювати/Зберегти/у поля), 🧠 пам'ять
    # («запам'ятай …» — факт локально у tools/memory.json, підмішується в
    # кожен системний промпт), 📎 вкладення файлів (txt/md/srt/json/py),
    # ✏️ редагування своїх повідомлень з відкатом розмови, Ctrl+K — нова
    # розмова. Палітра claude (ivory + теракота), історія у tools/chat.json —
    # все лише локально (як ключ Pixabay), fail-open, гроші — нуль.

    CHAT_PRETTY = {"puter": "🤖 Claude (Puter)", "anthropic": "🤖 Claude (Anthropic)",
                   "groq": "🔑 Groq", "github": "🔑 GitHub", "gemini": "🤖 Google AI Studio",
                   "cerebras": "⚡ Cerebras", "mistral": "🇪🇺 Mistral",
                   "openrouter": "🧭 OpenRouter", "nvidia": "🟩 NVIDIA NIM",
                   "sambanova": "🟧 SambaNova", "huggingface": "🤗 HF Router",
                   "zhipu": "🟣 GLM (Zhipu)", "zai": "🟣 GLM (Z.AI)",
                   "siliconflow": "🌊 SiliconFlow", "modelscope": "🟠 ModelScope",
                   "cohere": "🧩 Cohere",
                   "pollinations": "🌐 Pollinations", "kilo": "⚡ Kilo",
                   "freekey": "🔑 Ключ", "auto": "🔄 Авто (драбина)",
                   "9router": "🌐 9Router", "ollama": "🧠 Ollama"}
    CHAT_PRETTY_REV = {v: k for k, v in CHAT_PRETTY.items()}  # 💬 v46: назва з меню чату → шлюз
    CHAT_CHIPS = ("Налаштуй Shorts про космос, голосом Поліни, з караоке",
                  "Напиши сценарій: коротка історія штучного інтелекту",
                  "Запам'ятай: я знімаю Shorts про космос і ШІ",
                  "Знайди в мережі свіжі новини про ШІ",  # 🕵️ v47: агент піде у DuckDuckGo
                  "Що ти вмієш і які у тебе джерела думання?")

    def _chat_source(self):
        """💬 v42/v46: гарна назва джерела для шапки і міток чату: меню
        чату головніше за картку; «Ключ» — шлюз обраної моделі (не перший-попало)."""
        try:
            pick = ""
            if getattr(self, "chat_pick", None) is not None:
                pick = (self.chat_pick.get() or "")
            if pick and pick != "🔄 Як в картці":
                return pick
            p = self._llm_provider()
            if p == "freekey":
                eng = freekey_engine_for(self.ollama_model.get())
                if eng:
                    return self.CHAT_PRETTY.get(eng, "🔑 Ключ")
            return self.CHAT_PRETTY.get(p, "🧠 Ollama")
        except Exception:
            return "🧠 Ollama"

    def _chat_pick_switch(self, val):
        """💬 v46/v49: перемкнув джерело у шапці чату — мітка, статус і
        СПИСОК МОДЕЛЕЙ цього джерела одразу (перемикач 🧠 Модель)."""
        try:
            self.chat_src_lbl.configure(text="Джерело думання: "
                                       + self._chat_source())
        except Exception:
            pass
        self._chat_models_refresh(val)  # 🧠 v49: моделі обраного джерела
        if val and val != "🔄 Як в картці":
            self.say("💬 Чат: джерело — " + val)

    def _chat_models_refresh(self, val):
        """🧠 v49: перемикач моделей у чаті — список моделей обраного
        джерела (Claude-трійка, gpt-oss/GPT, Gemini, GLM, Qwen, Mistral).
        «🤖 Як у картці» — модель бере з меню картки Асистента.
        Список не зібрався — лишається як було (fail-open)."""
        try:
            rev = self.CHAT_PRETTY_REV
            v = val or ""
            vals = ["🤖 Як у картці"]
            if "Claude онлайн" in v:
                vals += FREEKEY_MODELS.get("puter", []) \
                    + FREEKEY_MODELS.get("anthropic", [])
            elif "ChatGPT онлайн" in v:
                vals += FREEKEY_MODELS.get("groq", []) \
                    + ["kilo-auto/free", "gpt-5.5", "gpt-oss-20b"]
            elif "Gemini онлайн" in v:
                vals += FREEKEY_MODELS.get("gemini", []) \
                    + ["google/gemma-4-31b-it:free"]  # 🧭 v52: свіжі :free у фолбеку
            elif "Mistral онлайн" in v:
                vals += FREEKEY_MODELS.get("mistral", [])
            elif v in rev and rev[v] in FREEKEY_MODELS:
                vals += FREEKEY_MODELS[rev[v]]
            elif "LLMFaucet" in v:  # 🚰 v52: селектори Faucet
                vals += list(FAUCET_MODELS)
            elif "AI Horde" in v:  # 🐎 v52: перемикача моделей нема — як у картці
                pass
            elif "Kilo" in v:
                vals += ["kilo-auto/free"]
            elif "LLM7" in v:
                vals += ["gpt-5.5"]
            elif "Pollinations" in v:
                vals += ["gpt-oss-20b"]
            seen, out = set(), []
            for x in vals:  # дублікатів моделей не показую
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            self.chat_model_pick.configure(values=out)
            self.chat_model_pick.set(out[0])
        except Exception:
            pass

    def _chat_theme_toggle(self):
        """🌙 v48: темна тема чату одним кліком: палітра — на інстанс
        (клас-світла лишається), вкладка перезбирається цілком — тема
        лягає на бульбашки, шапку, поле введення. Історія і вибране
        джерело не губляться; стрім іде — не міняю (fail-open)."""
        if getattr(self, "_chat_busy", False):
            self.say("💬 Дочекайся відповіді — тоді міняю тему")
            return
        dark = not getattr(self, "_chat_dark", False)
        self._chat_dark = dark
        t = self.CHAT_THEMES["dark" if dark else "light"]
        self.CLAUDE_BG = t["BG"]          # палітра — на інстанс, клас не чіпаю
        self.CLAUDE_CARD = t["CARD"]
        self.CLAUDE_TEXT = t["TEXT"]
        self.CLAUDE_MUTED = t["MUTED"]
        self.CLAUDE_ACCENT = t["ACCENT"]
        self.CLAUDE_ACCENT_H = t["ACCENT_H"]
        self.CLAUDE_LINE = t["LINE"]
        self.CLAUDE_BAR = t["BAR"]
        self.CLAUDE_HOVER = t["HOVER"]
        try:
            pick = (self.chat_pick.get() or "🔄 Як в картці")
        except Exception:
            pick = "🔄 Як в картці"
        try:
            for w in self.tab_chat.winfo_children():
                w.destroy()
        except Exception:
            pass
        self._chat_build()
        try:
            self.chat_pick.set(pick)
        except Exception:
            pass
        self.say("🌙 Темна тема чату" if dark else "☀️ Світла тема чату")

    def _mem_load(self):
        """🧠 v42: пам'ять чату — факти про користувача з tools/memory.json
        (лише локально). Нема/кривий файл — порожній список (fail-open)."""
        try:
            with open(MEMORY_FILE, encoding="utf-8") as f:
                d = json.load(f)
            items = d.get("memory") if isinstance(d, dict) else d
            if isinstance(items, list):
                return [str(i)[:500] for i in items if str(i).strip()][-50:]
        except Exception:
            pass
        return []

    def _mem_save(self, items):
        """🧠 v42: зберегти пам'ять (останні 50 фактів). Не вийшло — тихо:
        чат працює і без пам'яті (fail-open)."""
        try:
            os.makedirs(TOOLS_DIR, exist_ok=True)
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump({"memory": (items or [])[-50:]}, f,
                          ensure_ascii=False, indent=1)
        except Exception:
            pass

    def _chat_remember(self, text):
        """🧠 v42: «запам'ятай: …» — факт зберігається локально і підмішується
        у КОЖЕН системний промпт (пам'ять, як у Claude — але чесна й локальна).
        Не команда пам'яті — None, іде звичайний запит до моделі."""
        m = re.search(r"запам['’]ятай(?:\s+що)?[:\s]+(.+)", text or "",
                      re.IGNORECASE)
        fact = (m.group(1).strip() if m else "")
        if len(fact) < 2:
            return None
        items = self._mem_load()
        if fact not in items:
            items.append(fact)
        self._mem_save(items)
        return fact

    def _chat_memory_win(self):
        """🧠 v42: вікно пам'яті — список фактів з 🗑 і «Очистити все»
        (як керування пам'яттю в Claude: все перед очима, все прибирається)."""
        win = ctk.CTkToplevel(self.root)
        win.title("🧠 Пам'ять чату")
        win.geometry("560x520")
        win.attributes("-topmost", True)
        win.after(400, lambda: win.attributes("-topmost", False))
        win.configure(fg_color=self.CLAUDE_BG)
        ctk.CTkLabel(win, text="🧠 Пам'ять — що Асистент знає про тебе",
                     font=self._f(14, "bold"),
                     text_color=self.CLAUDE_TEXT).pack(fill="x", padx=16,
                                                       pady=(14, 2))
        ctk.CTkLabel(win, text="Лише локально (tools/memory.json) — підмішується "
                     "у кожну розмову. Прибирається одним рухом.",
                     font=self._f(11), text_color=self.CLAUDE_MUTED,
                     wraplength=500, justify="left").pack(fill="x", padx=16)
        box = ctk.CTkScrollableFrame(win, fg_color=self.CLAUDE_BG)
        box.pack(fill="both", expand=True, padx=12, pady=8)

        def rebuild():
            for w in box.winfo_children():
                w.destroy()
            items = self._mem_load()
            if not items:
                ctk.CTkLabel(box, text="Порожньо — скажи в чаті «запам'ятай: …»",
                              font=self._f(12),
                              text_color=self.CLAUDE_MUTED).pack(pady=20)
            for i, it in enumerate(items):
                row = ctk.CTkFrame(box, fg_color=self.CLAUDE_CARD, corner_radius=10)
                row.pack(fill="x", padx=4, pady=3)
                ctk.CTkLabel(row, text="• " + it, font=self._f(12),
                             text_color=self.CLAUDE_TEXT, wraplength=430,
                             justify="left").pack(side="left", padx=10, pady=8)
                ctk.CTkButton(row, text="🗑", width=40, height=30, corner_radius=15,
                              fg_color=self.CLAUDE_BAR, hover_color=self.CLAUDE_LINE,
                              text_color=self.CLAUDE_TEXT, font=self._f(13),
                              command=lambda idx=i: self._mem_forget(idx, rebuild)
                              ).pack(side="right", padx=8)

        rebuild()
        ctk.CTkButton(win, text="Очистити все", height=34, corner_radius=17,
                      fg_color=self.CLAUDE_CARD, hover_color=self.CLAUDE_HOVER,
                      text_color=self.CLAUDE_TEXT, font=self._f(12),
                      command=lambda: (self._mem_save([]), rebuild(),
                                       self.say("🧠 Пам'ять чату очищено"))
                      ).pack(pady=(0, 12))

    def _mem_forget(self, idx, rerender):
        """🧠 v42: забути один факт пам'яті."""
        items = self._mem_load()
        if 0 <= idx < len(items):
            items.pop(idx)
            self._mem_save(items)
            rerender()

    def _chat_system(self):
        """💬 v42/2.0: системний промпт чату — характер, завдання, дата
        і ПАМ'ЯТЬ (агент може шукати до 2 раундів — модель знає межу)."""
        s = ("Ти — Асистент «Генератора відео» (український десктопний генератор "
             "Shorts і відео: озвучка, субтитри, фон з YouTube чи фото, рендер). "
             "Сьогоднішня дата: " + datetime.now().strftime("%d.%m.%Y") + ". "
             "Відповідай українською, тепло і стисло, як Claude: конкретика, без "
             "води. Великий код (сценарій, JSON, команди) оформляй блоком у "
             "три гратки ``` — він стане артефактом з кнопками. Якщо просять "
             "налаштувати генерацію — дай ОДНУ готову фразу для поля Асистента "
             "(наприклад: «Shorts про космос, голос Поліна, караоке»). "
             "Ти ще й АГЕНТ: якщо нижче є «Свіжі дані з мережі» — це твій "
             "інструмент-пошук (DuckDuckGo → Mojeek): відповідай, спираючись на них, "
             "і вкажи джерела URL-посиланнями. 🤖 Якщо для відповіді потрібні "
             "свіжі дані з мережі, а їх у промпті нема — відповісти ЛИШЕ "
             "рядком «🔍ПОШУК: що знайти» — агент шукає ДО 2 РАУНДІВ і "
             "передасть тобі дані для другої відповіді.")
        rules = project_rules()  # 📏 v32: правила проєкту — обов'язкові для моделі
        if rules:
            s += "\nПравила проєкту (обов'язкові):\n- " + "\n- ".join(rules)
        mem = self._mem_load()  # 🧠 v42: пам'ять — у кожен запит
        if mem:
            s += ("\nПро користувача (пам'ять чату):\n- "
                  + "\n- ".join(mem[-20:]))
        return s

    def _chat_history_for_llm(self):
        """💬 v42: останні репліки розмови у форматі messages (контекст чату)."""
        out = []
        for m in (getattr(self, "chat_messages", None) or [])[-12:]:
            if m.get("role") in ("user", "assistant") and m.get("text"):
                out.append({"role": m["role"], "content": str(m["text"])[:1200]})
        return out

    def _chat_load(self):
        """💬 v42: історія чату з tools/chat.json — лише локально; нема/кривий
        файл — порожній список (fail-open)."""
        try:
            with open(CHAT_FILE, encoding="utf-8") as f:
                d = json.load(f)
            msgs = d.get("messages") if isinstance(d, dict) else d
            if isinstance(msgs, list):
                return [{"role": m.get("role"), "text": str(m.get("text") or "")[:6000],
                         "src": m.get("src") or ""}
                        for m in msgs if isinstance(m, dict)
                        and m.get("role") in ("user", "assistant")][-60:]
        except Exception:
            pass
        return []

    def _chat_save(self):
        """💬 v42: зберегти історію чату (останні 60 реплік). Не вийшло —
        тихо пропускаю: чат працює і без збереження (fail-open)."""
        try:
            os.makedirs(TOOLS_DIR, exist_ok=True)
            with open(CHAT_FILE, "w", encoding="utf-8") as f:
                json.dump({"messages": (getattr(self, "chat_messages", None) or [])[-60:]},
                          f, ensure_ascii=False, indent=1)
        except Exception:
            pass

    def open_chat_window(self):
        """💬 v43: чат Асистента — вкладка «💬 Чат» у ГОЛОВНОМУ вікні
        (без спливного вікна); повний функціонал Claude: стрімінг, Markdown,
        артефакти, пам'ять, вкладення, редагування повідомлень."""
        if getattr(self, "chat_win", None) is None:
            self._chat_build()
        self.tabs.set("💬 Чат")
        self._show_tab("💬 Чат")

    def _chat_build(self):
        """💬 v43: збудувати вкладку чату — один раз, при першому відкритті
        (ліниво: головне вікно стартує швидко)."""
        self._chat_busy = False
        self._chat_cancel = False
        self._chat_stream_box = None
        self._chat_stream_frame = None
        self.chat_messages = self._chat_load()
        win = self.tab_chat  # 🪟 v43: чат живе у вкладці — жодного спливного вікна
        win.configure(fg_color=self.CLAUDE_BG)
        self.chat_win = win
        self._bind_safe(self.root, "<Control-k>", lambda e: self._chat_new())  # Ctrl+K — як у Claude

        # шапка: ✳ мітка, джерело, 🧠 пам'ять, ＋ нова розмова
        head = ctk.CTkFrame(win, fg_color=self.CLAUDE_CARD, corner_radius=0)
        head.pack(fill="x", side="top")
        ctk.CTkLabel(head, text="✳ Асистент", font=self._f(16, "bold"),
                     text_color=self.CLAUDE_TEXT).pack(side="left", padx=(16, 8),
                                                       pady=(12, 4))
        self.chat_src_lbl = ctk.CTkLabel(
            head, text="Джерело думання: " + self._chat_source(),
            font=self._f(11), text_color=self.CLAUDE_MUTED)
        self.chat_src_lbl.pack(side="left", padx=(0, 8), pady=(14, 4))
        self.chat_pick = ctk.CTkOptionMenu(  # 🎯 v46: джерело думання чату
            head, width=200, height=28, font=self._f(11),
            fg_color=self.CLAUDE_CARD, button_color=self.CLAUDE_LINE,
            button_hover_color=self.CLAUDE_ACCENT_H, text_color=self.CLAUDE_TEXT,
            dropdown_fg_color=self.CLAUDE_BAR, dropdown_text_color=self.CLAUDE_TEXT,
            dropdown_hover_color=self.CLAUDE_LINE,
            values=["🔄 Як в картці", "🤖 Claude онлайн", "💬 ChatGPT онлайн",
                    "🤖 Gemini онлайн", "🇪🇺 Mistral онлайн"]
            + [self.CHAT_PRETTY[n] for n in FREEKEY_ORDER]
            + ["⚡ Kilo (без ключа)", "🌐 LLM7 (без ключа)",
               "🚰 LLMFaucet (без ключа)",
               "🌐 Pollinations (без ключа)",
               "🐎 AI Horde (без ключа)"],
            command=self._chat_pick_switch)
        self.chat_pick.set("🔄 Як в картці")
        self.chat_pick.pack(side="left", pady=(8, 2))
        self.chat_model_pick = ctk.CTkOptionMenu(  # 🧠 v49: перемикач МОДЕЛЕЙ у чаті
            head, width=230, height=28, font=self._f(11),
            fg_color=self.CLAUDE_CARD, button_color=self.CLAUDE_LINE,
            button_hover_color=self.CLAUDE_ACCENT_H, text_color=self.CLAUDE_TEXT,
            dropdown_fg_color=self.CLAUDE_BAR, dropdown_text_color=self.CLAUDE_TEXT,
            dropdown_hover_color=self.CLAUDE_LINE,
            values=["🤖 Як у картці"])
        self.chat_model_pick.set("🤖 Як у картці")
        self.chat_model_pick.pack(side="left", padx=(8, 0), pady=(8, 2))
        ctk.CTkButton(head, text="＋ Нова розмова", height=30, corner_radius=15,
                      fg_color=self.CLAUDE_ACCENT, hover_color=self.CLAUDE_ACCENT_H,
                      text_color="#FFFFFF", font=self._f(12),
                      command=self._chat_new).pack(side="right", padx=(8, 16),
                                                   pady=(10, 4))
        ctk.CTkButton(head, text="📄 Експорт", height=30, corner_radius=15,  # 📄 v51: розмова → читабельний txt
                      fg_color=self.CLAUDE_BAR, hover_color=self.CLAUDE_LINE,
                      text_color=self.CLAUDE_TEXT, font=self._f(12),
                      command=self._chat_export).pack(side="right",
                                                       padx=(0, 8),
                                                       pady=(10, 4))
        self._voice_btn = ctk.CTkButton(  # 🎤 v51: продиктуй питання — мікрофон → Whisper Groq
            head, text=("⏹️" if getattr(self, "_voice_rec", False) else "🎤"),
            width=44, height=30, corner_radius=15,
            fg_color=self.CLAUDE_BAR, hover_color=self.CLAUDE_LINE,
            text_color=self.CLAUDE_TEXT, font=self._f(12),
            command=self._chat_voice_toggle)
        self._voice_btn.pack(side="right", padx=(0, 8), pady=(10, 4))
        ctk.CTkButton(head, text=("☀️" if getattr(self, "_chat_dark", False)
                                  else "🌙"), width=44, height=30,
                      corner_radius=15,  # 🌙 v48: темна тема чату — одним кліком
                      fg_color=self.CLAUDE_BAR, hover_color=self.CLAUDE_LINE,
                      text_color=self.CLAUDE_TEXT, font=self._f(12),
                      command=self._chat_theme_toggle).pack(side="right",
                                                            padx=(0, 8),
                                                            pady=(10, 4))
        ctk.CTkButton(head, text="🔐 Google", height=30, corner_radius=15,  # 🔐 v49: авторизація Google — віко одразу
                      fg_color=self.CLAUDE_BAR, hover_color=self.CLAUDE_LINE,
                      text_color=self.CLAUDE_TEXT, font=self._f(12),
                      command=self._key_google).pack(side="right",
                                                     padx=(0, 8), pady=(10, 4))
        ctk.CTkButton(head, text="🧠 Пам'ять", height=30, corner_radius=15,
                      fg_color=self.CLAUDE_BAR, hover_color=self.CLAUDE_LINE,
                      text_color=self.CLAUDE_TEXT, font=self._f(12),
                      command=self._chat_memory_win).pack(side="right", pady=(10, 4))

        # стрічка повідомлень
        self.chat_scroll = ctk.CTkScrollableFrame(win, fg_color=self.CLAUDE_BG,
                                                   corner_radius=0)
        self.chat_scroll.pack(fill="both", expand=True, side="top")

        # панель введення — як у Claude: біла картка з рамкою
        bar = ctk.CTkFrame(win, fg_color=self.CLAUDE_BAR, corner_radius=16,
                          border_width=1, border_color=self.CLAUDE_LINE)
        bar.pack(fill="x", side="bottom", padx=12, pady=(4, 12))
        self.chat_input = ctk.CTkTextbox(bar, height=92, font=self._f(13),
                                         wrap="word", fg_color="transparent",
                                         text_color=self.CLAUDE_TEXT)
        self.chat_input.pack(fill="x", padx=10, pady=(10, 2))
        self.attach_paste_menu(self.chat_input)  # 🖱 v43: ПКМ у полі чату

        def _chat_enter(e):
            if e.state & 0x0001:  # Shift+Enter — новий рядок, як у Claude
                return None
            self._chat_send()
            return "break"
        self._bind_safe(self.chat_input, "<Return>", _chat_enter)
        row = ctk.CTkFrame(bar, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(2, 10))
        ctk.CTkButton(row, text="📥 Вставити", height=34, corner_radius=17,
                      fg_color=self.CLAUDE_CARD, hover_color=self.CLAUDE_HOVER,
                      text_color=self.CLAUDE_TEXT, font=self._f(12),
                      command=lambda: self.paste_into(self.chat_input)).pack(
                          side="left")
        ctk.CTkButton(row, text="📎 Файл", height=34, corner_radius=17,
                      fg_color=self.CLAUDE_CARD, hover_color=self.CLAUDE_HOVER,
                      text_color=self.CLAUDE_TEXT, font=self._f(12),
                      command=self._chat_attach).pack(side="left", padx=(8, 0))
        ctk.CTkButton(row, text="🌐 Пошук", height=34, corner_radius=17,  # 🕵️ v47: агент
                      fg_color=self.CLAUDE_CARD, hover_color=self.CLAUDE_HOVER,
                      text_color=self.CLAUDE_TEXT, font=self._f(12),
                      command=self._chat_web_send).pack(side="left", padx=(8, 0))
        ctk.CTkButton(row, text="⚙️ у поля генератора", height=34, corner_radius=17,
                      fg_color=self.CLAUDE_CARD, hover_color=self.CLAUDE_HOVER,
                      text_color=self.CLAUDE_TEXT, font=self._f(12),
                      command=self._chat_to_fields).pack(side="left", padx=(8, 0))
        self.chat_send_btn = ctk.CTkButton(
            row, text="⬆", width=44, height=34, corner_radius=17,
            fg_color=self.CLAUDE_ACCENT, hover_color=self.CLAUDE_ACCENT_H,
            text_color="#FFFFFF", font=self._f(14, "bold"),
            command=self._chat_send)
        self.chat_send_btn.pack(side="right")
        ctk.CTkLabel(win, text="Enter — надіслати • Shift+Enter — новий рядок • "
                     "📎 Файл — додати txt/srt/… у контекст • 🌐 Пошук — агент "
                     "знайде свіже в мережі • 🔗 кинь URL у повідомлення — агент "
                     "прочитає сторінку • ✏️ під своїм повідомленням — "
                     "редагувати • Ctrl+K — нова розмова • 🖱 ПКМ — як у всіх "
                     "програмах • 🎯 джерело думання — меню у шапці • 🧠 Модель "
                     "поруч — перемикач моделей джерела • 🔐 Google — одразу "
                     "віко входу і ключ Gemini • 🌙 — тема • ⏳ нотами видно, "
                     "який шлюз мовчить • ⚡ у мітці під час стріму — швидкість, симв/с",
                     font=self._f(10), text_color=self.CLAUDE_MUTED,
                     anchor="w", wraplength=560).pack(fill="x", padx=16,
                                                     pady=(0, 6))

        if self.chat_messages:
            self._chat_rerender()
        else:
            self._chat_chips()

    def _chat_chips(self):
        """💬 v42: порожній чат — підказки-запити, як стартовий екран Claude."""
        ctk.CTkLabel(self.chat_scroll, text="✳ Привіт! Я Асистент твого "
                     "Генератора відео — питай що завгодно\nабо тапни підказку:",
                     font=self._f(13), text_color=self.CLAUDE_TEXT,
                     justify="left", anchor="w").pack(fill="x", padx=16,
                                                     pady=(16, 8), anchor="w")
        for chip in self.CHAT_CHIPS:
            ctk.CTkButton(self.chat_scroll, text=chip, anchor="w", height=40,
                          corner_radius=16, fg_color=self.CLAUDE_CARD,
                          hover_color=self.CLAUDE_HOVER, text_color=self.CLAUDE_TEXT,
                          font=self._f(12),
                          command=lambda t=chip: self._chat_chip(t)).pack(
                              fill="x", padx=16, pady=3)

    def _chat_chip(self, text):
        """💬 v42: тап на підказку — фраза летить у розмову одразу."""
        self._chat_send_now(text)

    def _md_configure(self, box):
        """🎨 v42: теги Markdown у текстовому полі чату (як Claude рендерить
        розмітку: жирний, курсив, код, заголовки, списки, цитати)."""
        try:
            box.tag_config("mdh", font=self._f(14, "bold"))
            box.tag_config("mdb", font=self._f(13, "bold"))
            box.tag_config("mdi", font=("Segoe UI", 12, "normal", "italic"))
            box.tag_config("mdc", font=("Consolas", 12), foreground="#B45309")
            box.tag_config("mdq", font=("Segoe UI", 12, "normal", "italic"),
                           foreground="#87867F")
            box.tag_config("mdcode", font=("Consolas", 12))
            box.tag_config("mdth", font=("Consolas", 12, "bold"),  # 📊 v48: заголовок таблиці
                           background=getattr(self, "CLAUDE_CARD", "#F0EEE6"))
            box.tag_config("mdtr", font=("Consolas", 11))  # 📊 v48: рядок таблиці
        except Exception:
            pass  # теги не піднялися — текст лишається читабельним (fail-open)

    def _md_inline(self, box, line):
        """🎨 v42: рядок → жирний **…**, курсив *…*, код `…` (як у Claude)."""
        for part in re.split(r"(\*\*.+?\*\*|\*[^*\n]+?\*|`[^`\n]+?`)", line):
            if not part:
                continue
            if part.startswith("**") and part.endswith("**") and len(part) > 4:
                box.insert("end", part[2:-2], "mdb")
            elif (part.startswith("*") and part.endswith("*") and len(part) > 2):
                box.insert("end", part[1:-1], "mdi")
            elif part.startswith("`") and part.endswith("`") and len(part) > 2:
                box.insert("end", part[1:-1], "mdc")
            else:
                box.insert("end", part)

    def _md_text_into(self, box, text):
        """🎨 v42/v48: Markdown-рендер блока тексту: заголовки, списки, цитати,
        інлайн-розмітка + ТАБЛИЦІ (| а | б | + |---|---|) — вирівняні колонки.
        Кожен рядок — з тегом; усе fail-open."""
        lines = (text or "").split("\n")
        first = True
        i = 0
        while i < len(lines):
            s = lines[i].strip()
            # 📊 v48: блок-таблиця — рядок з |, а наступний — розділювач |---|
            if s.startswith("|") and i + 1 < len(lines) \
                    and re.match(r"^\|[\s:\-|]+\|?\s*$", lines[i + 1].strip()):
                j = i
                rows = []
                while j < len(lines) and lines[j].strip().startswith("|"):
                    rows.append(lines[j].strip())
                    j += 1
                if not first:
                    box.insert("end", "\n")
                self._md_table(box, rows)
                first = False
                i = j
                continue
            if not first:
                box.insert("end", "\n")
            first = False
            if s.startswith("### ") or s.startswith("## ") or s.startswith("# "):
                box.insert("end", s.lstrip("# ").strip(), "mdh")
            elif s.startswith("- ") or s.startswith("• ") or s.startswith("* "):
                box.insert("end", "•  ", "mdb")
                self._md_inline(box, s[2:].strip())
            elif s.startswith("> "):
                box.insert("end", "│ " + s[2:].strip(), "mdq")
            else:
                self._md_inline(box, lines[i])
            i += 1

    def _md_table(self, box, rows):
        """📊 v48: Markdown-таблиця → вирівняні колонки (Consolas): заголовок
        тисну жирним на підкладці, розділювач |---| ховаю, маркери **/` у
        клітинках прибираю — чистий текст. Крива таблиця — що встигло,
        те й показав (fail-open)."""
        try:
            cells = []
            for r in rows:
                cells.append([re.sub(r"\*\*|`|\*", "", c.strip()) for c in
                              r.strip().strip("|").split("|")])
            if len(cells) >= 2 and cells[1] and \
                    all(re.match(r"^[\s:\-]*$", c) for c in cells[1]):
                cells.pop(1)  # розділювач |---|---| не показую
            if not cells:
                return
            ncol = max(len(r) for r in cells)
            widths = [0] * ncol
            for r in cells:
                for k in range(min(len(r), ncol)):
                    widths[k] = max(widths[k], len(r[k]))
            for ri, r in enumerate(cells):
                parts = []
                for k in range(ncol):
                    c = r[k] if k < len(r) else ""
                    parts.append(c + " " * max(widths[k] - len(c), 0) + "  ")
                box.insert("end", "│ " + "│ ".join(parts) + "│",
                           "mdth" if ri == 0 else "mdtr")
        except Exception:
            pass  # крива таблиця — що встигло, те й показав (fail-open)

    def _md_split(self, text):
        """📦 v42: розрізати відповідь на текст і код-блоки (``` мова … ```).
        Малі коди лишаються в тексті (рендеряться тегом), великі (від 5
        рядків) стають артефактами — як у Claude."""
        try:
            parts = re.split(r"```(\w*)\n(.*?)```", text or "", flags=re.S)
        except Exception:
            parts = [text or ""]
        out = []
        for i, part in enumerate(parts):
            if not part:
                continue
            if i % 3 == 0:  # звичайний текст між код-блоками
                out.append(("text", "", part))
            else:  # мова (i%3==1) або код (i%3==2)
                if i % 3 == 2:
                    code = part.rstrip("\n")
                    if code.count("\n") + 1 >= 5:
                        out.append(("code", parts[i - 1] or "текст", code))
                    else:  # малий блок — лишаю в тексті, як інлайн-код
                        out.append(("text", "", "```\n" + code + "\n```"))
                # мову пропускаю — вона стане заголовком артефакта
        if not out:  # порожній текст — усе одно один сегмент (стрім-бок)
            out.append(("text", "", text or ""))
        return out

    def _chat_render_user(self, text, idx=None):
        """💬 v42: бульбашка юзера праворуч + ✏️ редагувати (як у Claude:
        правиш своє повідомлення — розмова відкочується і перепитується)."""
        b = ctk.CTkFrame(self.chat_scroll, fg_color=self.CLAUDE_CARD,
                        corner_radius=18)
        b.pack(anchor="e", fill="x", padx=(90, 16), pady=(8, 2))
        ctk.CTkLabel(b, text=text, font=self._f(13), wraplength=440,
                     justify="left", text_color=self.CLAUDE_TEXT).pack(
                         anchor="e", padx=14, pady=(8, 10))
        if idx is not None:
            ctk.CTkButton(b, text="✏️ Редагувати", height=24, corner_radius=12,
                          fg_color="transparent", hover_color=self.CLAUDE_HOVER,
                          text_color=self.CLAUDE_MUTED, font=self._f(10),
                          command=lambda i=idx: self._chat_edit(i)).pack(
                              side="right", padx=(4, 10), pady=(0, 6))

    def _chat_artifact_card(self, master, lang, code):
        """📦 v42: артефакт — великий код-блок ховається в картку (як у
        Claude): заголовок-мова, кнопки 📋 Копіювати / 💾 Зберегти /
        ⤏ у поля (сценарій одразу летить у генератор)."""
        lines = code.count("\n") + 1
        card = ctk.CTkFrame(master, fg_color=self.CLAUDE_CARD, corner_radius=12)
        card.pack(fill="x", pady=(4, 2))
        ctk.CTkLabel(card, text="📦 Артефакт: " + (lang or "текст") + " • "
                     + str(lines) + " рядків", font=self._f(11, "bold"),
                     text_color=self.CLAUDE_TEXT, anchor="w").pack(
                         fill="x", padx=12, pady=(8, 2))
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(2, 8))
        ctk.CTkButton(row, text="📋 Копіювати", height=28, corner_radius=14,
                      fg_color=self.CLAUDE_BAR, hover_color=self.CLAUDE_LINE,
                      text_color=self.CLAUDE_TEXT, font=self._f(11),
                      command=lambda c=code: self._chat_copy(c)).pack(side="left")
        ctk.CTkButton(row, text="💾 Зберегти", height=28, corner_radius=14,
                      fg_color=self.CLAUDE_BAR, hover_color=self.CLAUDE_LINE,
                      text_color=self.CLAUDE_TEXT, font=self._f(11),
                      command=lambda c=code, l=lang: self._chat_artifact_save(
                          c, l)).pack(side="left", padx=(6, 0))
        ctk.CTkButton(row, text="⤏ у поля генератора", height=28, corner_radius=14,
                      fg_color=self.CLAUDE_BAR, hover_color=self.CLAUDE_LINE,
                      text_color=self.CLAUDE_TEXT, font=self._f(11),
                      command=lambda c=code: self._chat_artifact_to_fields(c)
                      ).pack(side="left", padx=(6, 0))

    def _chat_artifact_save(self, code, lang):
        """📦 v42: зберегти артефакт у файл (обираєш місце сам)."""
        try:
            ext = {"python": ".py", "json": ".json", "javascript": ".js",
                   "html": ".html", "markdown": ".md"}.get((lang or "").lower(),
                                                             ".txt")
            p = filedialog.asksaveasfilename(
                defaultextension=ext, filetypes=[("Файл", "*" + ext)])
            if p:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(code)
                self.say("📦 Артефакт збережено: " + os.path.basename(p))
        except Exception as e:
            self.say("📦 Не вийшло зберегти артефакт: " + str(e)[:120])

    def _chat_artifact_to_fields(self, code):
        """📦 v42: артефакт ⤏ поля генератора — сценарій або JSON-команда
        одразу застосовується до головного вікна."""
        self.agent_entry.delete("1.0", "end")
        self.agent_entry.insert("1.0", code.strip()[:8000])
        self._agent_send()

    def _chat_render_assistant(self, text, src, buttons=True):
        """🎨 v42: відповідь асистента — Markdown-сегменти і артефакти,
        мітка джерела і час, кнопки 📋 Копіювати / 🔁 Ще раз під відповіддю."""
        a = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        a.pack(anchor="w", fill="x", padx=(16, 60), pady=(8, 2))
        ctk.CTkLabel(a, text="✳ " + (src or "Асистент") + " • " +
                     time.strftime("%H:%M"), font=self._f(10),
                     text_color=self.CLAUDE_MUTED, anchor="w").pack(fill="x")
        box = None
        for kind, lang, chunk in self._md_split(text):
            if kind == "code":
                self._chat_artifact_card(a, lang, chunk)
                continue
            lines = max(1, chunk.count("\n") + 1)
            t = ctk.CTkTextbox(a, font=self._f(13), wrap="word",
                               fg_color="transparent", height=min(500,
                               max(30, lines * 20 + 10)), corner_radius=4)
            t.pack(fill="x", anchor="w", pady=(2, 2))
            self._md_configure(t)
            self._md_text_into(t, chunk.rstrip("\n"))
            self._ro_selectable(t)  # 🖱 v43: виділяй і копіюй відповідь — як у Claude
            box = box or t
        if buttons:
            acts = ctk.CTkFrame(a, fg_color="transparent")
            acts.pack(fill="x", anchor="w", pady=(0, 2))
            ctk.CTkButton(acts, text="📋 Копіювати", height=26, corner_radius=13,
                          fg_color=self.CLAUDE_CARD, hover_color=self.CLAUDE_HOVER,
                          text_color=self.CLAUDE_MUTED, font=self._f(10),
                          command=lambda tx=text: self._chat_copy(tx)).pack(
                              side="left")
            ctk.CTkButton(acts, text="🔁 Ще раз", height=26, corner_radius=13,
                          fg_color=self.CLAUDE_CARD, hover_color=self.CLAUDE_HOVER,
                          text_color=self.CLAUDE_MUTED, font=self._f(10),
                          command=self._chat_regen).pack(side="left",
                                                         padx=(6, 0))
        self.chat_scroll.after(30, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))
        return a, box

    def _ro_selectable(self, w):
        """🖱 v43: read-only текст з ЖИВИМ виділенням і копіюванням (як у
        Claude): друкувати в відповідь не даю, але виділяй мишею скрізь,
        копіюй ПКМ «📄 Копіювати» / Ctrl+C, «виділиш усе» — Ctrl+A."""
        def _key(e):
            if e.state & 0x0004:  # Ctrl-комбінації — стандартна поведінка Tk
                return None
            return "break"  # звичайні клавіші не друкують у відповідь
        self._bind_safe(w, "<Key>", _key)

        def _cc(e):
            try:
                txt = w.get("sel.first", "sel.last")
                if txt.strip():
                    self.root.clipboard_clear()
                    self.root.clipboard_append(txt)
                    self.say("📄 Скопійовано виділене з відповіді")
            except Exception:
                pass
            return "break"
        self._bind_safe(w, "<Control-c>", _cc)

        def _ca(e):
            w.tag_add("sel", "1.0", "end")
            return "break"
        self._bind_safe(w, "<Control-a>", _ca)
        self.attach_paste_menu(w, can_paste=False, can_clear=False)

    def _chat_rerender(self):
        """💬 v42: перемалювати розмову з історії (великі відповіді — з
        Markdown-ом і артефактами, юзерські — з ✏️)."""
        try:
            for w in self.chat_scroll.winfo_children():
                w.destroy()
        except Exception:
            pass
        for i, m in enumerate(getattr(self, "chat_messages", None) or []):
            if m["role"] == "user":
                self._chat_render_user(m["text"], i)
            else:
                self._chat_render_assistant(m["text"], m.get("src") or "")

    def _chat_typing(self, on):
        """💬 v42: індикатор «✳ Думаю…» + кнопка ⬆↔⏹ — стан під час запиту."""
        try:
            if on:
                self._chat_typ_lbl = ctk.CTkLabel(
                    self.chat_scroll, text="✳ Думаю…", font=self._f(12),
                    text_color=self.CLAUDE_MUTED, anchor="w")
                self._chat_typ_lbl.pack(fill="x", padx=16, pady=(6, 2), anchor="w")
                self.chat_send_btn.configure(text="⏹", command=self._chat_stop)
            else:
                try:
                    self._chat_typ_lbl.destroy()
                except Exception:
                    pass
                self.chat_send_btn.configure(text="⬆", command=self._chat_send)
        except Exception:
            pass  # вікно могло закритись — тихо (fail-open)

    def _chat_send(self):
        """💬 v42: Enter/⬆ — фраза з поля летить у розмову."""
        text = self.chat_input.get("1.0", "end").strip()
        if not text:
            return
        self.chat_input.delete("1.0", "end")
        self._chat_send_now(text)

    def _chat_send_now(self, text, add_user=True, force_web=False, no_cache=False):
        """💬 v42/v47: репліка юзера → СТРІМІНГ у фоні: токени прилітають у чергу
        і малюються одразу (Tk не блокується). «запам'ятай: …» — локальна
        пам'ять, без запиту до моделі. 🕵️ force_web — агент ОБОВ'ЯЗКОВО шукає
        свіже в мережі перед відповіддю (кнопка «🌐 Пошук» у чаті).
        💾 v48 no_cache — «🔁 Ще раз»: кеш оминаю, відповідь свіжа."""
        if getattr(self, "_chat_busy", False):
            self.say("💬 Чат: вже думаю над відповіддю — ⏹ Стоп або зачекай")
            return
        text = " ".join((text or "").split())
        if not text:
            return
        if add_user:
            self.chat_messages.append({"role": "user", "text": text, "src": ""})
            self._chat_render_user(text, len(self.chat_messages) - 1)
            self._chat_save()
        fact = self._chat_remember(text)  # 🧠 v42: пам'ять — локально, миттєво
        if fact:
            reply = ("🧠 Запам'ятав: " + fact +
                      " — триматиму це в кожній розмові (побачиш у 🧠 Пам'ять).")
            self.chat_messages.append({"role": "assistant", "text": reply,
                                       "src": "🧠 Пам'ять"})
            self._chat_save()
            self._chat_render_assistant(reply, "🧠 Пам'ять")
            return
        self._chat_cancel = False
        self._chat_busy = True
        self._chat_stream_box = None
        self._chat_stream_frame = None
        self._chat_typing(True)
        threading.Thread(target=self._chat_thread,
                         args=(text, force_web, no_cache), daemon=True).start()

    def _chat_thread(self, text, force_web=False, no_cache=False):
        """⚡ v42/v47: стрімінг-запит у фоні: джерело з картки + історія
        розмови; кожен токен — у чергу (chat_stream), фінал — chat_done.
        🕵️ v47 АГЕНТ: просиш свіже («знайди/новини/погода…») або тиснеш
        «🌐 Пошук» — спершу DuckDuckGo БЕЗ ключів (у фоні, Tk не тупить),
        знайдене підмішу моделі у системний промпт: відповідь свіжа,
        з джерелами-посиланнями. Нічого не знайшлось — як раніше (fail-open)."""
        t0 = time.time()
        prov = self._llm_provider()
        try:  # 🎯 v46: джерело, обране в шапці чату, головніше за картку
            _pick = (self.chat_pick.get() or "")
            if _pick and _pick != "🔄 Як в картці":
                prov = "chat:" + (self.CHAT_PRETTY_REV.get(_pick) or _pick)
        except Exception:
            pass
        url = model = ""
        try:
            url = self.ollama_url.get().strip()
            model = (self.ollama_model.get() or "").strip()
        except Exception:
            pass
        try:  # 🧠 v49: модель з перемикача у шапці чату (тільки для LLM-шляхів)
            _mp = (self.chat_model_pick.get() or "")
            if _mp and _mp != "🤖 Як у картці" \
                    and (prov == "auto" or prov == "freekey"
                         or str(prov).startswith("chat:")):
                model = _mp
        except Exception:
            pass  # перемикача нема/джерело карткове — модель з картки (fail-open)

        def _note(s):  # ⏳ v49: драбина показує, ЯКИЙ шлюз мовчить
            self.q.put(("chat_stream", s + "\n"))
        system = self._chat_system()
        history = self._chat_history_for_llm()
        try:  # 🔗 v48: URL у повідомленні — агент читає сторінки у фоні
            urls = re.findall(r"https?://[^\s\)\]\">]+", text or "")[:2]
            pages = []
            for u in urls:
                pg = fetch_page_text(u, timeout=15, limit=4000)
                if pg:
                    pages.append("Вміст сторінки " + u + " (витяг):\n" + pg[:4000])
            if pages:
                system = (system or "") + "\n\n" + "\n\n".join(pages)
                self.q.put(("chat_stream",
                            "🔗 Агент: прочитав " + str(len(pages))
                            + " сторінку(і) з твого посилання…\n\n"))
        except Exception:
            pass  # сторінка не далась — модель відповість як вміє (fail-open)
        try:  # 🕵️ v47: агент — свіжі дані з мережі, поки Tk навіть не здогадується
            if force_web or agent_wants_web(text):
                ctx, note = agent_web_context(text, timeout=15)
                if ctx:
                    system = (system or "") + "\n\n" + ctx
                    self.q.put(("chat_stream",
                                "🔎 Агент: " + note + " — відповідаю з ними…\n\n"))
        except Exception:
            pass  # пошук впав — модель відповість як вміє (fail-open)
        key = ""  # 💾 v48: кеш — постав те саме питання, відповідь миттєва
        try:
            key = llm_cache_key(prov, model, text, system, history)
            if no_cache:  # «🔁 Ще раз» — стару відповідь викидаю зі свіжого життя
                LLM_REPLY_CACHE.pop(key, None)
            hit = None if no_cache else LLM_REPLY_CACHE.get(key)
            if not hit:  # 💾 v51: RAM-промах — гляну у ДИСКОВИЙ кеш (переживає перезапуск)
                dval = None if no_cache else _llm_disk_get(key)
                if dval:
                    hit = (dval, time.time())
                    LLM_REPLY_CACHE[key] = hit  # прогрів RAM-кешу з диска
            if hit and time.time() - hit[1] < 86400:  # свіжість кешу — 24 год
                self.q.put(("chat_stream", hit[0]))
                llm_trace("cache", prov, model or "-", t0, True,
                          len(hit[0] or ""))
                self.q.put(("chat_done", hit[0]))
                return
        except Exception:
            pass  # кеш закапризував — живу як без нього (fail-open)
        full = llm_stream(prov, url, model, text, system=system,
                          history=history,
                          on_delta=lambda d: self.q.put(("chat_stream", d)),
                          stop=lambda: getattr(self, "_chat_cancel", False),
                          timeout=180, on_note=_note)
        try:  # 🤖 v48/v49/v52: СПРАВЖНІЙ tool-use — модель просить мережу, агент дає дані (ДО 2 РАУНДІВ)
            for _round in range(2):  # 🕵️ v52: другий раунд — якщо знову «🔍ПОШУК:»
                m = re.match(r"^\s*🔍ПОШУК:\s*(.+?)\s*$", (full or "").strip(), re.S)
                if not m or getattr(self, "_chat_cancel", False):
                    break
                query = agent_query_clean(m.group(1))[:300]  # 🕵️ v52: чистий запит у рушій
                self.q.put(("chat_stream",
                            "🔎 Агент шукає (раунд " + str(_round + 1) + "/2): "
                            + query + "…\n\n"))
                try:
                    ctx, note = agent_web_context(query, timeout=15)
                except Exception:
                    ctx, note = "", ""
                if not ctx:
                    break  # мережа мовчить — на чесне пояснення нижче
                self.q.put(("chat_stream", "🔎 " + note
                            + " — відповідаю з ними…\n\n"))
                second = ""
                try:
                    second = llm_stream(prov, url, model, text,
                                        system=(system or "") + "\n\n" + ctx,
                                        history=history,
                                        on_delta=lambda d: self.q.put(
                                            ("chat_stream", d)),
                                        stop=lambda: getattr(self,
                                                             "_chat_cancel",
                                                             False),
                                        timeout=180, on_note=_note) or ""
                except Exception:
                    second = ""
                if second:
                    full = second
            if (full or "").strip().startswith("🔍ПОШУК:"):
                # 🆕 v49/v52: модель просила мережу, мережа мовчить (2 раунди) —
                # чесно пояснюю, а не показую сирий «🔍ПОШУК: …» як відповідь
                full = ("🔎 Агент не зміг дістати свіжі дані з мережі "
                        "(мережа мовчить або DuckDuckGo лімітує) — "
                        "спробуй «🌐 Пошук» ще раз, перемкни джерело у "
                        "шапці або питай без свіжих даних.")
        except Exception:
            pass  # раунд агента впав — лишається перша відповідь (fail-open)
        try:  # 💾 v48/v51: зберегти у кеш — наступне таке саме питання миттєве
            if key and full:
                LLM_REPLY_CACHE[key] = (full, time.time())
                _llm_disk_add(key, full)  # 💾 v51: і на диск — переживе перезапуск
                if len(LLM_REPLY_CACHE) > 300:  # не роздуваємо пам'ять
                    LLM_REPLY_CACHE.pop(next(iter(LLM_REPLY_CACHE)))
        except Exception:
            pass  # не збереглось — просто без кешу (fail-open)
        llm_trace("chat", prov, model or "-", t0, bool(full), len(full or ""))
        self.q.put(("chat_done", full))

    def _chat_web_send(self):
        """🌐 v47: «Пошук» у чаті — фраза з поля летить АГЕНТУ: спершу
        DuckDuckGo (без ключів), потім модель відповідає зі свіжими
        даними і посиланнями. Порожньо — підказка, не тупить."""
        text = ""
        try:
            text = self.chat_input.get("1.0", "end").strip()
        except Exception:
            pass
        if not text:
            self.say("🌐 Напиши у полі, ЩО знайти — потім «🌐 Пошук»")
            return
        try:
            self.chat_input.delete("1.0", "end")
        except Exception:
            pass
        self._chat_send_now(text, force_web=True)

    def _chat_stream_delta(self, piece):
        """⚡ v42: токени стріму — малюються ОДРАЗУ, як у Claude; перший
        токен прибирає «✳ Думаю…» і створює бульбашку відповіді."""
        try:
            if getattr(self, "chat_win", None) is None:
                return
            if not self.chat_win.winfo_exists():
                return
            if getattr(self, "_chat_stream_box", None) is None:
                self._chat_typing(False)
                self._chat_stream_frame, self._chat_stream_box = \
                    self._chat_render_assistant("", self._chat_source(),
                                                buttons=False)
                self._chat_stream_chars = 0   # ⚡ v48: лічильник швидкості стріму
                self._chat_stream_t0 = time.time()
                self._chat_speed_tick = 0.0
            box = self._chat_stream_box
            box.insert("end", piece)  # v43: бокс read-only через _ro_selectable — нормальний стан не шкодить
            lines = int(box.index("end-1c").split(".")[0])
            box.configure(height=min(500, max(30, lines * 20 + 10)))
            box.see("end")
            self.chat_scroll._parent_canvas.yview_moveto(1.0)
            # ⚡ v48: швидкість стріму — симв/с у мітці джерела (не частіше 0.4 с)
            self._chat_stream_chars = getattr(self, "_chat_stream_chars", 0) \
                + len(piece)
            now = time.time()
            if now - getattr(self, "_chat_speed_tick", 0.0) > 0.4:
                self._chat_speed_tick = now
                el = max(now - getattr(self, "_chat_stream_t0", now), 0.2)
                try:
                    self.chat_src_lbl.configure(
                        text="Джерело думання: " + self._chat_source()
                        + " • ⚡ " + str(int(self._chat_stream_chars / el))
                        + " симв/с")
                except Exception:
                    pass
        except Exception:
            pass  # вікно закрили — тихо (fail-open)

    def _chat_done(self, full):
        """⚡ v42: стрім доплив — фінальний Markdown-рендер (як Claude:
        після стріму відповідь «переукладається» у красу) + кнопки."""
        self._chat_busy = False
        self._chat_typing(False)
        if getattr(self, "chat_win", None) is None:
            self._chat_stream_box = None
            return
        try:
            if not self.chat_win.winfo_exists():
                self._chat_stream_box = None
                return
        except Exception:
            return
        try:  # прибрати стрім-місток: фінал малюю з Markdown-ом і артефактами
            if getattr(self, "_chat_stream_frame", None) is not None:
                self._chat_stream_frame.destroy()
        except Exception:
            pass
        self._chat_stream_box = None
        if not full:
            if getattr(self, "_chat_cancel", False):
                return  # ⏹ зупинили до перших токенів — тихо, без фейків
            full = ("Джерела мовчать (ліміт або нема мережі) — спробуй ще раз "
                    "чи перемкни джерело в картці Асистента.")
        src = self._chat_source()
        try:  # 📡 v48: «Авто»/драбина — показую, ЯКИЙ шлюз фактично відповів
            a = (LAST_STREAM_SOURCE.get("src") or "")
            if a in self.CHAT_PRETTY and \
                    time.time() - (LAST_STREAM_SOURCE.get("t") or 0) < 30:
                src = "📡 " + self.CHAT_PRETTY[a]
        except Exception:
            pass  # невідомо хто — лишається обране джерело (fail-open)
        self.chat_messages.append({"role": "assistant", "text": full,
                                   "src": src})
        self._chat_save()
        self._chat_render_assistant(full, src)
        try:  # ⚡ v48: мітку повертаю — там під час стріму жила швидкість
            self.chat_src_lbl.configure(text="Джерело думання: "
                                       + self._chat_source())
        except Exception:
            pass

    def _chat_stop(self):
        """⏹ v42: Стоп — обриваю стрім, ЗБЕРІГАЮЧИ те, що встигло (як у
        Claude: зупинка не їсть часткову відповідь)."""
        self._chat_cancel = True
        self._chat_busy = False
        self._chat_typing(False)
        try:  # ⚡ v48: мітку повертаю і при зупинці стріму
            self.chat_src_lbl.configure(text="Джерело думання: "
                                       + self._chat_source())
        except Exception:
            pass
        self.say("💬 Чат: зупинив")

    def _chat_copy(self, text):
        """📋 v42: Копіювати — відповідь або артефакт у буфер обміну."""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.say("💬 Чат: скопійовано")
        except Exception:
            self.say("💬 Чат: не вийшло скопіювати")

    def _chat_regen(self):
        """🔁 v42: Ще раз — перепитати останній запит (як у Claude: стара
        відповідь прибирається, генерується заново)."""
        if getattr(self, "_chat_busy", False):
            return
        msgs = getattr(self, "chat_messages", None) or []
        last_user = None
        for m in reversed(msgs):
            if m["role"] == "user":
                last_user = m["text"]
                break
        while msgs and msgs[-1]["role"] == "assistant":
            msgs.pop()
        if not last_user:
            self.say("💬 Чат: нема запиту, який перепитати")
            return
        self._chat_rerender()
        self._chat_send_now(last_user, add_user=False, no_cache=True)  # 💾 v48: оминати кеш

    def _chat_edit(self, idx):
        """✏️ v42: редагувати своє повідомлення — розмова відкочується до
        нього (все після — прибирається), текст чекає у полі (як у Claude)."""
        msgs = getattr(self, "chat_messages", None) or []
        if idx is None or not (0 <= idx < len(msgs)):
            return
        text = msgs[idx]["text"]
        del msgs[idx:]
        self._chat_save()
        self._chat_rerender()
        self.chat_input.delete("1.0", "end")
        self.chat_input.insert("1.0", text)
        self.chat_input.focus_set()
        self.say("💬 Чат: редагуй повідомлення і надішли знову (Enter)")

    def _chat_attach(self):
        """📎 v42: вкладення — файл (txt/md/srt/vtt/json/py/csv ≤200 КБ)
        дописується у контекст повідомлення, як вкладення у Claude."""
        try:
            path = filedialog.askopenfilename(filetypes=[
                ("Текст і код", "*.txt *.md *.srt *.vtt *.json *.py *.csv"),
                ("Усі файли", "*.*")])
            if not path:
                return
            with open(path, encoding="utf-8", errors="ignore") as f:
                content = f.read(200000)
            if not content.strip():
                self.say("📎 Файл порожній")
                return
            self.chat_input.insert("end", "\n\n📎 Файл «" + os.path.basename(path)
                                   + "»:\n" + content)
            self.say("📎 Додав " + os.path.basename(path) + " у контекст "
                     "повідомлення")
        except Exception as e:
            self.say("📎 Не вийшло прочитати файл: " + str(e)[:120])

    def _chat_new(self):
        """💬 v42: ＋ Нова розмова (Ctrl+K) — чистий аркуш: історія і chat.json
        прибираються, з'являються підказки (як «New chat» у Claude)."""
        self.chat_messages = []
        self._chat_cancel = True  # старий запит не цікавить
        self._chat_busy = False
        self._chat_stream_box = None
        self._chat_stream_frame = None
        self._chat_save()
        try:
            for w in self.chat_scroll.winfo_children():
                w.destroy()
        except Exception:
            pass
        self._chat_chips()
        self.say("💬 Чат: нова розмова")

    def _chat_to_fields(self):
        """💬 v42: ⚙️ у поля генератора — фраза з поля чату стає командою
        головного вікна (мостина між розмовою і генерацією відео)."""
        text = self.chat_input.get("1.0", "end").strip()
        if not text:
            self.say("💬 Чат: поле порожнє — напиши фразу для генератора")
            return
        self.agent_entry.delete("1.0", "end")
        self.agent_entry.insert("1.0", text)
        self._agent_send()

    def _chat_export(self):
        """📄 v51: розмова чату → читабельний txt (шапка з датою; хто,
        [джерело], текст). Порожній чат — підказка (fail-open)."""
        try:
            msgs = list(getattr(self, "chat_messages", None) or [])
            if not msgs:
                self.say("📄 Розмова порожня — нема що експортувати 🙂")
                return
            path = filedialog.asksaveasfilename(
                title="Куди зберегти розмову", defaultextension=".txt",
                initialfile="розмова_чата_" + datetime.now().strftime("%Y%m%d") + ".txt",
                filetypes=[("Текст", "*.txt")])
            if not path:
                return
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("Розмова з Асистентом «Генератора відео» — "
                         + datetime.now().strftime("%d.%m.%Y %H:%M") + "\n")
                fh.write("=" * 60 + "\n\n")
                for m in msgs:
                    who = "ТИ" if m.get("role") == "user" else "АСИСТЕНТ"
                    src = str(m.get("src") or "").strip()
                    head = "[" + who + ("]" if not src else " | " + src + "]")
                    fh.write(head + "\n" + str(m.get("text") or "") + "\n\n")
            self.say("📄 Розмову збережено: " + os.path.basename(path))
            try:
                os.startfile(os.path.dirname(path) or ".")
            except Exception:
                pass
        except Exception as e:
            self.say("📄 Не вийшло зберегти розмову: " + str(e)[:120])

    def _chat_voice_toggle(self):
        """🎤 v51: продиктуй питання — СТАРТ/СТОП запису: мікрофон (dshow)
        → wav 16 кГц моно → Whisper на Groq → текст у полі чату. Нема
        groq-ключа/ffmpeg/мікрофона — чесна підказка (fail-open)."""
        if getattr(self, "_voice_rec", False):
            self._voice_stop()
            return
        key = str(load_freekeys().get("groq") or "").strip()
        if len(key) < 20:
            messagebox.showwarning(
                "Стоп", "🎤 Для диктовки потрібен безкоштовний ключ Groq\n"
                        "(console.groq.com → API Keys, без картки) —\n"
                        "кнопка «🔑 Ключі» у картці Асистента 🙂")
            return
        ensure_ffmpeg(self.say)
        if not ffmpeg_available():
            self.say("🎤 Нема ffmpeg — диктовка недоступна (див. журнал)")
            return
        mic = _dshow_mic_name()
        if not mic:
            self.say("🎤 Не знайшов мікрофона Windows — перевір підключення")
            return
        self._voice_rec = True
        self._voice_wav = os.path.join(TOOLS_DIR, "_chat_voice.wav")
        try:
            os.makedirs(TOOLS_DIR, exist_ok=True)
            self._voice_proc = subprocess.Popen(
                [ffmpeg_path(), "-y", "-hide_banner", "-nostdin",
                 "-f", "dshow", "-i", "audio=" + mic,
                 "-ar", "16000", "-ac", "1", self._voice_wav])
        except Exception as e:
            self._voice_rec = False
            self.say("🎤 Запис не стартнув: " + str(e)[:120])
            return
        try:
            self._voice_btn.configure(text="⏹️")
        except Exception:
            pass
        self.say("🎤 Слухаю… натисни ⏹️ (до 45 с) — розпізнаю Whisper на Groq")

        def _watch():
            waited = 0.0
            while getattr(self, "_voice_rec", False) and waited < 45.0:
                time.sleep(0.5)
                waited += 0.5
            try:  # авто-стоп на 45 с — щоб не писав у пустоту
                if getattr(self, "_voice_rec", False):
                    self._voice_stop()
            except Exception:
                pass
        threading.Thread(target=_watch, daemon=True).start()

    def _voice_stop(self):
        """🎤 v51: стоп запису → Groq Whisper → текст у поле чату."""
        self._voice_rec = False
        try:
            self._voice_btn.configure(text="🎤")
        except Exception:
            pass
        proc = getattr(self, "_voice_proc", None)
        try:
            if proc is not None:
                proc.terminate()
                try:
                    proc.wait(timeout=60)
                except Exception:
                    proc.kill()
        except Exception:
            pass
        wav = getattr(self, "_voice_wav", "")
        if not wav or not os.path.isfile(wav) or os.path.getsize(wav) < 2048:
            self.say("🎤 Запис порожній — скажи щось довше 🙂")
            try:
                if wav and os.path.isfile(wav):
                    os.remove(wav)
            except OSError:
                pass
            return
        self.say("🎤 Розпізнаю (Whisper на Groq)…")

        def _job():
            try:
                txt = groq_stt_text(wav)
            finally:
                try:
                    os.remove(wav)
                except OSError:
                    pass
            if txt:
                self.q.put(("voice_text", txt))
            else:
                self.q.put(("chat_stream", "🎤 Не розпізнав — спробуй ще раз\n"))
        threading.Thread(target=_job, daemon=True).start()

    def _voice_text_done(self, txt):
        """🎤 v51: розпізнаний текст — у поле чату (курор на місці)."""
        try:
            self.chat_input.insert("end", txt)
            self.chat_input.focus()
            self.say("🎤 Продиктував: додано у поле чату")
        except Exception:
            pass

    def _llm_provider(self):
        """🌐 v31/v35/v36/v40: що обрано в картці Асистента: 'ollama', '9router',
        'pollinations', 'kilo', 'freekey' або 'auto' (драбина всіх джерел)."""
        try:
            val = self.llm_provider.get() or ""
            if val == "🌐 Онлайн":
                return "pollinations"
            if val == "⚡ Kilo":
                return "kilo"
            if val == "🔑 Ключ":
                return "freekey"
            if val == "🔄 Авто":
                return "auto"
            return "9router" if val == "9Router" else "ollama"
        except Exception:
            return "ollama"

    def _key_window(self):
        """🔑 v44: вікно безкоштовних ключів — обери шлюз → «🌐 Отримати ключ»
        (потрібна сторінка відкриється у Chrome) → встав ключ → «💾 Запам'ятати
        назавжди» (запишеться у tools/freekeys.json — папка програми, живе
        назавжди; у код і GitHub не потрапляє). «🔑 Авторизуватись через
        Google» — сторінка Google AI Studio у Chrome: увійди акаунтом
        Google → Create API key → встав тут."""
        try:  # не відкривати двічі — просто підняти існуюче
            if getattr(self, "_key_win", None) is not None:
                if self._key_win.winfo_exists():
                    self._key_win.focus_set()
                    return
        except Exception:
            pass
        win = ctk.CTkToplevel(self.root)
        win.title("🔑 Безкоштовні ключі AI-мозку")
        win.geometry("660x660")
        win.attributes("-topmost", True)
        win.after(400, lambda: win.attributes("-topmost", False))
        win.configure(fg_color=self.CLAUDE_BG)
        self._key_win = win
        ctk.CTkLabel(win, text="🔑 Безкоштовні ключі — обери шлюз",
                     font=self._f(15, "bold"),
                     text_color=self.CLAUDE_TEXT).pack(fill="x", padx=16,
                                                      pady=(14, 2))
        ctk.CTkLabel(win, text="Ключ — це «пароль» від безкоштовного фрітіру шлюзу. "
                     "Живе ЛИШЕ на цьому комп'ютері у tools/freekeys.json "
                     "(як ключ Pixabay) — у код і GitHub не потрапляє.",
                     font=self._f(11), text_color=self.CLAUDE_MUTED, anchor="w",
                     wraplength=620, justify="left").pack(fill="x", padx=16)
        names = [self.CHAT_PRETTY.get(n, n) for n in FREEKEY_ORDER]
        self._key_eng = ctk.CTkOptionMenu(
            win, values=names, width=320, height=34, corner_radius=10,
            fg_color=self.CLAUDE_CARD, text_color=self.CLAUDE_TEXT,
            button_color="#E8E5D9", font=self._f(12), command=lambda _v: self._key_pick())
        self._key_eng.set(self.CHAT_PRETTY.get(freekey_engine() or FREEKEY_ORDER[0],
                                               FREEKEY_ORDER[0]))
        self._key_eng.pack(padx=16, anchor="w", pady=(10, 2))
        self._key_hint = ctk.CTkLabel(win, text="", font=self._f(11),
                                      text_color=self.CLAUDE_MUTED, anchor="w",
                                      wraplength=620, justify="left")
        self._key_hint.pack(fill="x", padx=16, pady=(4, 2))
        row1 = ctk.CTkFrame(win, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(6, 2))
        ctk.CTkButton(row1, text="🌐 Отримати ключ (Chrome)", height=34, corner_radius=17,
                      fg_color=self.CLAUDE_ACCENT, hover_color=self.CLAUDE_ACCENT_H,
                      text_color="#FFFFFF", font=self._f(12),
                      command=self._key_open_signup).pack(side="left")
        ctk.CTkButton(row1, text="🔑 Авторизуватись через Google", height=34,
                      corner_radius=17, fg_color=self.CLAUDE_CARD,
                      hover_color="#E8E5D9", text_color=self.CLAUDE_TEXT,
                      font=self._f(12), command=self._key_google).pack(
                          side="left", padx=(8, 0))
        self._key_entry = ctk.CTkEntry(win, height=36, corner_radius=10,
                                       placeholder_text="Встав ключ сюди (Ctrl+V)",
                                       fg_color=self.CLAUDE_CARD, font=self._f(12))
        self._key_entry.pack(fill="x", padx=16, pady=(10, 2))
        self.attach_paste_menu(self._key_entry)  # 🖱 v44: ПКМ «Вставити» і тут
        row2 = ctk.CTkFrame(win, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(4, 2))
        ctk.CTkButton(row2, text="💾 Запам'ятати назавжди", height=34, corner_radius=17,
                      fg_color=self.CLAUDE_ACCENT, hover_color=self.CLAUDE_ACCENT_H,
                      text_color="#FFFFFF", font=self._f(12),
                      command=self._key_save).pack(side="left")
        ctk.CTkButton(row2, text="🗑 Прибрати ключ", height=34, corner_radius=17,
                      fg_color=self.CLAUDE_CARD, hover_color="#E8E5D9",
                      text_color=self.CLAUDE_TEXT, font=self._f(12),
                      command=self._key_remove).pack(side="left", padx=(8, 0))
        self._key_state = ctk.CTkLabel(win, text="", font=self._f(11),
                                       text_color=self.CLAUDE_MUTED, anchor="w",
                                       wraplength=620, justify="left")
        self._key_state.pack(fill="x", padx=16, pady=(8, 2))
        ctk.CTkLabel(win, text="🔄 Драбина «Авто» сама підхопить усе, що збережеш: "
                     "Puter → Anthropic → Cerebras → Groq → Mistral → GitHub → "
                     "Google AI Studio → OpenRouter → NVIDIA → SambaNova → HF → "
                     "GLM (Zhipu) → GLM (Z.AI) → SiliconFlow → ModelScope → Kilo → "
                     "LLM7 → Pollinations. GLM — дві платформи (glm-4.7-flash "
                     "безкоштовна!) і GLM:free у OpenRouter; ChatGPT-подібні — "
                     "Groq (gpt-oss) і Kilo/LLM7; Claude — Puter/Anthropic.",
                     font=self._f(10), text_color=self.CLAUDE_MUTED, anchor="w",
                     wraplength=620, justify="left").pack(fill="x", padx=16,
                                                          pady=(6, 8))
        self._key_pick()

    def _key_name(self):
        """🔑 v44: внутрішнє ім'я обраного у вікні шлюзу (pretty → ключ)."""
        try:
            pretty = self._key_eng.get()
            for n in FREEKEY_ORDER:
                if self.CHAT_PRETTY.get(n, n) == pretty:
                    return n
        except Exception:
            pass
        return freekey_engine() or FREEKEY_ORDER[0]

    def _key_pick(self):
        """🔑 v44: обрав шлюз — показую підказку і стан ключа."""
        name = self._key_name()
        try:
            self._key_hint.configure(text=KEY_HINTS.get(name, ""))
        except Exception:
            pass
        self._key_refresh()

    def _key_refresh(self):
        """🔑 v44: стан ключа обраного шлюзу (є/нема, без повного ключа)."""
        try:
            name = self._key_name()
            k = str(load_freekeys().get(name) or "").strip()
            if k:
                self._key_state.configure(
                    text="✅ Ключ " + name + " збережений (" + k[:6] + "…" +
                         ") — живе у папці назавжди.")
            else:
                self._key_state.configure(
                    text="— ключа " + name + " ще нема: «🌐 Отримати ключ» → "
                         "встав → «💾 Запам'ятати назавжди».")
        except Exception:
            pass

    def _key_open_signup(self):
        """🌐 v44: сторінка отримання ключа обраного шлюзу — у Chrome."""
        name = self._key_name()
        open_in_chrome(KEY_SIGNUP.get(name) or "https://aistudio.google.com/apikey")
        self.say("🌐 Відкрив Chrome: отримай ключ " + name + " і встав у вікно")

    def _key_google(self):
        """🔑 v44/v49: авторизація через Google — ОДРАЗУ віко входу Google
        (Chrome), після входу — сторінка ключа Gemini: Create API key →
        встав ключ у вікно → «Запам'ятати назавжди» — і «🤖 Gemini онлайн»
        у чаті заговорить. (Вхід Google вимагає справжнього браузера —
        reader-режим свого браузера не проводить логін.)"""
        try:
            self._key_eng.set(self.CHAT_PRETTY.get("gemini", "🤖 Google AI Studio"))
        except Exception:
            pass
        try:
            if getattr(self, "_key_win", None) is not None \
                    and self._key_win.winfo_exists():
                self._key_win.lift()
        except Exception:
            pass
        open_in_chrome("https://accounts.google.com/ServiceLogin?continue="
                       "https%3A%2F%2Faistudio.google.com%2Fapikey")
        self.say("🔑 Google: увійди → Create API key → встав у вікно ключів → 💾 Запам'ятати")

    def _key_save(self):
        """💾 v44: записати ключ у tools/freekeys.json — папка програми,
        запам'ятовується назавжди (у код і GitHub не потрапляє)."""
        name = self._key_name()
        k = (self._key_entry.get() or "").strip()
        if len(k) < 20:
            self.say("⚠️ Ключ надто короткий — схоже, це не він. Встав ВЕСЬ ключ.")
            return
        keys = load_freekeys()
        keys[name] = k
        try:
            os.makedirs(TOOLS_DIR, exist_ok=True)
            with open(FREEKEYS_FILE, "w", encoding="utf-8") as f:
                json.dump(keys, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.say("⚠️ Не вийшло зберегти ключ: " + str(e)[:80])
            return
        try:
            self._key_entry.delete(0, "end")
        except Exception:
            pass
        self.say("💾 Запам'ятав ключ " + name + " НАЗАВЖДИ — tools/freekeys.json "
                 "(лише локально, як ключ Pixabay)")
        self._key_refresh()
        self._freekey_model_menu(freekey_engine())
        try:  # чат відкритий — оновити мітку джерела
            self.chat_src_lbl.configure(text="Джерело думання: " + self._chat_source())
        except Exception:
            pass

    def _key_remove(self):
        """🗑 v44: прибрати ключ шлюзу з freekeys.json (fail-open)."""
        name = self._key_name()
        keys = load_freekeys()
        if name in keys:
            del keys[name]
            try:
                with open(FREEKEYS_FILE, "w", encoding="utf-8") as f:
                    json.dump(keys, f, ensure_ascii=False, indent=2)
                self.say("🗑 Прибрав ключ " + name + " — шлюз випав з драбини")
            except Exception as e:
                self.say("⚠️ Не вийшло прибрати: " + str(e)[:80])
        self._key_refresh()

    def _freekey_model_menu(self, eng):
        """🧠 v44: меню моделей шлюзу у картці Асистента: Claude — трійка
        Sonnet/Haiku/Opus (puter — з префіксом anthropic/), GLM — уся
        безкоштовна серія, Mistral — лінійка, інші — свої. Fail-open."""
        try:
            conf = FREEKEY_ENGINES.get(eng or "", {})
            models = list(FREEKEY_MODELS.get(eng) or
                          ([conf["model"]] if conf.get("model") else
                           [FREEKEY_ENGINES["groq"]["model"]]))
            cur = (self.ollama_model.get() or "").strip()
            self.ollama_model.configure(values=models)
            if cur not in models:
                self.ollama_model.set(models[0])
        except Exception:
            pass

    def _switch_llm_provider(self, val):
        """🌐 v31/v35/v36: перемикання Ollama ↔ 9Router ↔ Онлайн ↔ Kilo ↔ Ключ —
        дефолтний URL міняється слідом."""
        defs = {"Ollama": "http://localhost:11434", "9Router": "http://localhost:20128",
                "🌐 Онлайн": POLLINATIONS_URL, "⚡ Kilo": KILO_URL,
                "🔑 Ключ": (FREEKEY_ENGINES.get(freekey_engine() or "groq", {})
                            .get("url") or FREEKEY_ENGINES["groq"]["url"]),
                "🔄 Авто": ""}
        others = {v for k, v in defs.items() if k != val}
        cur = (self.ollama_url.get() or "").strip()
        if not cur or cur in others:
            self.ollama_url.delete(0, "end")
            self.ollama_url.insert(0, defs.get(val, "http://localhost:11434"))
        if val == "🔑 Ключ":  # 🔑 v44: вікно ключів; нема ключа — Chrome на сторінці отримання
            eng = freekey_engine()
            self._freekey_model_menu(eng)
            if not eng:
                open_in_chrome(KEY_SIGNUP.get(FREEKEY_ORDER[0], "https://puter.com"))
                self.ollama_status.configure(
                    text="🔑 Немає ключа — відкрив Chrome на сторінці отримання "
                         "(Puter, без картки). Отримай ключ → встав у вікно → "
                         "«💾 Запам'ятати назавжди».")
                self._key_window()
            else:
                self.ollama_status.configure(
                    text="🔑 Джерело: {} — ключ збережений. «🔑 Ключі» — поміняти, "
                         "«Перевірити» — підписати модель.".format(
                             self.CHAT_PRETTY.get(eng, eng)))
            return
        if val == "🔄 Авто":
            self.ollama_status.configure(
                text="🔄 Авто — драбина: 🤖 Claude (Puter) → Claude (Anthropic) → ⚡ Cerebras → "
                     "Groq → 🇪🇺 Mistral → GitHub → 🤖 Google AI Studio → 🧭 OpenRouter → 🟩 NVIDIA → "
                     "🟧 SambaNova → 🤗 HF → 🟣 GLM (Zhipu) → 🟣 GLM (Z.AI) → 🌊 SiliconFlow → "
                     "🟠 ModelScope → ⚡ Kilo → 🌐 LLM7 → 🌐 Pollinations. "
                     "Вичерпався — сам перескакує: Асистент не впирається в ліміти.")
        else:
            self.ollama_status.configure(
                text="Джерело: {} — за замовчуванням {}. Перевір — підпишу модель.".format(
                    val, defs.get(val, "")))

    def ollama_check_now(self):
        """🧠 v29 / 🌐 v31/v36: «Перевірити» — список моделей провайдера у фоні, Tk не зависає."""
        prov = self._llm_provider()
        if prov == "auto":
            keys = load_freekeys()
            have = [self.CHAT_PRETTY.get(n, n) for n in FREEKEY_ORDER
                    if len(str(keys.get(n) or "").strip()) >= 20]
            chain = have + ["⚡ Kilo", "🌐 LLM7", "🌐 Pollinations"]
            self.ollama_status.configure(
                text="🔄 Авто: " + " → ".join(chain) + " — вичерпався, сам іде далі")
            self.say("🔄 Авто: драбина з {} джерел — перший живий відповідає, "
                     "Асистент не впирається в ліміти".format(len(chain)))
            return
        if prov == "freekey" and not freekey_engine():
            self.ollama_status.configure(
                text="🔑 Немає ключа — натисни кнопку «🔑 Ключі»: обери шлюз → "
                     "«🌐 Отримати ключ» (сторінка відкриється у Chrome, без картки) → "
                     "встав ключ → «💾 Запам'ятати назавжди». Google AI Studio — кнопка "
                     "«Авторизуватись через Google». 2 хвилини — і драбина повна.")
            return
        if not prov:
            prov = "ollama"
        defs = {"pollinations": POLLINATIONS_URL, "kilo": KILO_URL,
                "9router": "http://localhost:20128"}
        url = (self.ollama_url.get().strip() or defs.get(prov) or
               (FREEKEY_ENGINES.get(freekey_engine() or "groq", {}).get("url")
                if prov == "freekey" else "http://localhost:11434"))
        name = {"9router": "🌐 9Router", "pollinations": "🌐 Pollinations (онлайн)",
                "kilo": "⚡ Kilo Code (онлайн)", "freekey": "🔑 Безкошт. ключ"}.get(prov, "🧠 Ollama")
        self.ollama_status.configure(text="🔄 Шукаю {} на {}…".format(name, url))
        threading.Thread(target=lambda: self.q.put(
            ("ollama_check", (prov, url, llm_list_models(prov, url)))), daemon=True).start()

    def _ollama_check_done(self, payload):
        """🧠 v29 / 🌐 v31/v36: перевірку зроблено — меню моделей, збереження, статус."""
        prov, url, models = payload
        name = {"9router": "🌐 9Router", "pollinations": "🌐 Pollinations (онлайн)",
                "kilo": "⚡ Kilo Code (онлайн)", "freekey": "🔑 Безкошт. ключ"}.get(prov, "🧠 Ollama")
        if not models:
            self.ollama_status.configure(
                text="ℹ️ {} на {} не піднято — Асистент працює як раніше (парсер)".format(name, url))
            return
        cur = self.ollama_model.get()
        self.ollama_model.configure(values=models)
        if cur not in models:
            self.ollama_model.set(models[0])
        try:
            save_ollama_conf(url, self.ollama_model.get(), models, prov)
        except Exception:
            pass
        self.ollama_status.configure(text="{} живий: {}. Модель «{}» збережено.".format(
            name, ", ".join(models[:4]) + (" …" if len(models) > 4 else ""),
            self.ollama_model.get()))
        self.say("{} готовий — Асистент тепер уміє більше".format(name))


    def _agent_apply(self, p):
        """🤖 v26: застосувати параметри до полів UI. Fail-open:
        чого немає або не читається — тихо пропускаю."""
        try:
            self._set_mode(p["mode"])
            if p["mode"] == "script" and p.get("script"):
                self.script.delete("1.0", "end")
                self.script.insert("1.0", p["script"])
            elif p.get("query"):
                self.query.delete("1.0", "end")
                self.query.insert("1.0", p["query"])
            if p["size"] and hasattr(self, "size"):
                try:
                    self.size.set(p["size"])
                except Exception:
                    pass
            if p["voice"] and hasattr(self, "voice"):
                try:
                    self.voice.set(p["voice"])
                except Exception:
                    pass
            if p["sub_style"] and hasattr(self, "sub_style"):
                try:
                    self.sub_style.set(p["sub_style"])
                except Exception:
                    pass
            if p["no_music"]:
                self.music_path = ""
            if p["trim"] is not None and hasattr(self, "trim_sil"):
                self.trim_sil.set(bool(p["trim"]))
            if p["cover"] is not None and hasattr(self, "cover_on"):
                self.cover_on.set(bool(p["cover"]))
            if p["seo"] is not None and hasattr(self, "seo"):
                self.seo.set(bool(p["seo"]))
        except Exception as e:
            self.say("ℹ️ Асистент: щось не налаштував ({}), поля лишаються як були".format(str(e)[:80]))

    def start(self):
        query = self.query.get("1.0", "end").strip()
        mode = getattr(self, "mode", "video")
        if mode == "mix":  # 🎧 мікс: тема = назва, треки в папці
            if not query:
                query = "Night Chill Mix"
            if not os.path.isdir(MIX_TRACKS_DIR) or not any(
                    n.lower().endswith((".mp3", ".wav", ".m4a"))
                    for n in os.listdir(MIX_TRACKS_DIR)):
                messagebox.showwarning("Стоп", "У папці MixTracks нема треків 🙂 Знайди їх через «🎵» у режимі 🎧 Мікс або поклади свої mp3 у папку.")
                return
        elif mode == "script":  # 📜 сценарій
            script = self.script.get("1.0", "end").strip()
            if len(script) < 10:
                messagebox.showwarning("Стоп", "Напиши сценарій у режимі «📜 Сценарій» 🙂 Частини — через порожній рядок.")
                return
        else:  # 🎬 відео
            if len(query) < 3:
                messagebox.showwarning("Стоп", "Спершу напиши тему відео 🙂")
                return
        if not hasattr(self, "music_path"):
            self.music_path = ""
        self.btn.configure(state="disabled")
        self.bar.start()
        self._gen_running = True
        self._reset_steps()
        self.status_lbl.configure(text="● Генерується…", text_color="#F59E0B")
        target = self.pipeline_mix if mode == "mix" else self.pipeline
        threading.Thread(target=target, args=(query,), daemon=True).start()
    def preflight_notes(self):
        """🧪 v24: передпольотні перевірки — попереджуємо ДО старту генерації,
        щоб не падати на 90-й хвилині. Тільки повідомлення у журнал."""
        try:
            free = shutil.disk_usage(os.path.expanduser("~")).free
            if free < 2 * 1024 ** 3:
                self.say("⚠️ Вільно лише {:.1f} ГБ — на рендер треба ~2 ГБ+, "
                         "може не влізти.".format(free / 1024 ** 3))
        except Exception:
            pass
        try:
            m = (getattr(self, "music_path", "") or "").strip()
            if m and not os.path.isfile(m):
                self.say("⚠️ Файл музики зник: «{}» — згенерую без музики.".format(
                    os.path.basename(m)[:60]))
                self.music_path = ""
            elif m:
                try:
                    audio_duration(m)
                except Exception:
                    self.say("⚠️ Файл музики не читається: «{}» — згенерую без музики.".format(
                        os.path.basename(m)[:60]))
                    self.music_path = ""
        except Exception:
            pass
        try:
            if getattr(self, "no_faces", None) is not None and self.no_faces.get() and cv2 is None:
                self.say("ℹ️ OpenCV не встановлено — фільтр «без обличчя» буде пропущений.")
        except Exception:
            pass
    def pipeline(self, query):
        ok = False
        try:
            self.preflight_notes()  # 🧪 v24: місце на диску / музика / cv2 — до старту
            many = []
            if getattr(self, "yt_many_bg", None) and self.yt_many_bg.get():
                many = self.parse_yt_links(self.yt_many.get("1.0", "end"))
                if not many:
                    self.say("⚠️ Перемикач посилань увімкнено, але посилань нема — шукаю фон сам")
                else:
                    self.say("🔗 У фон піде {} відео з твоїх посилань".format(len(many)))
            files = None
            if getattr(self, "merge_bg", None) and self.merge_bg.get() and self.merge_files:
                files = list(self.merge_files)
            sel = [u for u, v in getattr(self, "yt_checked", {}).items() if v.get()]
            if sel:
                self.say("🎬 У фон піде {} обраних відео з пошуку".format(len(sel)))
            # v14: налаштування стилів/пауз/обкладинки з сайдбара
            pins = [u for u, v in getattr(self, "pins_checked", {}).items() if v.get()]  # 🖼 v18
            if pins:
                self.say("🖼 Завантажую {} обраних зображень…".format(len(pins)))
                dl = []
                for u in pins:
                    try:
                        p = pinterest_download(u, self.say)
                        dl.append(p)
                        cr = getattr(self, "pins_info", {}).get(u)
                        if cr:
                            append_credit(os.path.dirname(p), cr)
                    except Exception as e:
                        self.say("⚠️ Зображення не завантажилось: " + str(e)[:120])
                pins = dl if dl else None
            else:
                pins = None
            sub = self.sub_style.get() if hasattr(self, "sub_style") else "Класичні"
            vid = self.vid_style.get() if hasattr(self, "vid_style") else "Без стилю"
            trans = self.transition.get() if hasattr(self, "transition") else "Різко"
            trim = bool(self.trim_sil.get()) if hasattr(self, "trim_sil") else False
            cov = bool(self.cover_on.get()) if hasattr(self, "cover_on") else False
            nf = bool(self.no_faces.get()) if hasattr(self, "no_faces") else False  # 🚫 v15
            se = bool(self.seo.get()) if hasattr(self, "seo") else False             # 📈 v15
            ln = bool(self.loudnorm.get()) if hasattr(self, "loudnorm") else False  # 🔊 v27
            pk = None  # 📦 v27: цільовий розмір копії
            if hasattr(self, "pack_size"):
                digits = "".join(c for c in str(self.pack_size.get()) if c.isdigit())
                pk = int(digits) if digits else None
            rt = int(self.tts_rate.get()) if hasattr(self, "tts_rate") else 0  # 🎚 v28: темп озвучки
            pv = (self.pub_platform.get() if getattr(self, "pub_platform", None)
                  and self.pub_platform.get() != "Не" else None)  # 📺 v32: платформа публікації
            up4 = bool(self.upscale4k.get()) if hasattr(self, "upscale4k") else False  # 📈 v34: 4К
            asc = bool(self.autoscrape.get()) if hasattr(self, "autoscrape") else False  # 🧹 v34: авоскраб
            ov = bool(self.overlays_on.get()) if hasattr(self, "overlays_on") else False  # 🏷️ 2.0: оверлеї
            if getattr(self, "mode", "video") == "script":
                generate_script_video(self.script.get("1.0", "end").strip(),
                                      self.voice.get(), SIZES[self.size.get()],
                                      getattr(self, "music_path", "").strip(), self.say,
                                      on_workdir=lambda wd: setattr(self, "workdir", wd),
                                      sub_style=sub, vid_style=vid, trim_sil=trim, cover=cov,
                                      no_faces=nf, seo=se, master=ln, pack_mb=pk, rate_pct=rt, platform=pv,
                                      upscale4k=up4, autoscrape=asc, overlays=ov)
                ok = True
                if self.workdir and os.path.isdir(self.workdir):
                    f = os.path.join(self.workdir, "final.mp4")
                    if os.path.isfile(f):
                        self.final_path = f
                        self.q.put(("poster", f))
            else:
                # 📚 v14: батч — кожен рядок поля «Тема» стає окремим відео
                themes = [query]
                if getattr(self, "batch", None) and self.batch.get():
                    themes = [t.strip() for t in query.splitlines() if len(t.strip()) >= 3] or [query]
                if len(themes) > 1:
                    self.say("📚 Батч: {} тем — генерую по черзі".format(len(themes)))
                done = 0
                for idx, th in enumerate(themes, 1):
                    if len(themes) > 1:
                        self.say("▶️ Батч {}/{}: «{}»".format(idx, len(themes), th[:60]))
                        self.q.put(("batch_reset", None))
                    try:
                        generate_video(th, self.voice.get(), SIZES[self.size.get()],
                                       getattr(self, "music_path", "").strip(), self.say,
                                       on_workdir=lambda wd: setattr(self, "workdir", wd),
                                       bg_files=files, yt_search_urls=sel, yt_many=many,
                                       pin_images=pins,
                                       sub_style=sub, vid_style=vid, transition=trans,
                                       trim_sil=trim, cover=cov, no_faces=nf, seo=se, master=ln, pack_mb=pk, rate_pct=rt, platform=pv,
                                       upscale4k=up4, autoscrape=asc, overlays=ov)
                        done += 1
                        if self.workdir and os.path.isdir(self.workdir):
                            f = os.path.join(self.workdir, "final.mp4")
                            if os.path.isfile(f):
                                self.final_path = f
                                self.q.put(("poster", f))
                    except Exception as e:
                        self.say("❌ Тема «{}» не вийшла: {}".format(th[:40], str(e)[:150]))
                ok = done > 0
            if ok and self.workdir and os.path.isdir(self.workdir):
                try:
                    os.startfile(self.workdir)  # Windows: одразу показати результат
                    self.say("📂 Відкрив папку з готовим відео")
                except Exception:
                    pass
        except Exception as e:
            self.say(f"❌ Помилка: {e}")
        finally:
            self.q.put(("gen_end", ok))


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        # Режим самоперевірки (для CI): генерує тестове відео без вікна.
        def _log(msg):
            with open("smoke-log.txt", "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        ok = True
        try:
            generate_video("Перевірка збірки генератора", "Остап",
                           "1280x720", "", _log, on_workdir=lambda wd: None,
                           auto_yt=False)
        except Exception as e:
            ok = False
            _log("SMOKE FAILED: " + str(e))
        sys.exit(0 if ok else 1)
    App().root.mainloop()
