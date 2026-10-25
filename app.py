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
"""
import array
import asyncio
import base64
import hashlib
import json
import os
import queue
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
from urllib.parse import quote_plus

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
UA_STRING = "VideoGenerator/1.32 (https://github.com/khomyak75roman-dotcom/video-generator)"
# v16 🎧: мікс-режим — папка треків і локальний ключ Pixabay (НЕ в коді/репозиторії)
MIX_TRACKS_DIR = os.path.join(os.path.expanduser("~"), "Videos", "MixTracks")
PIXABAY_KEY_FILE = os.path.join(TOOLS_DIR, "pixabay.key")
OLLAMA_CONF_FILE = os.path.join(TOOLS_DIR, "ollama.json")  # 🧠 v29/🌐 v31: URL+модель+провайдер, лише локально
LLM_TRACE_FILE = os.path.join(TOOLS_DIR, "llm_trace.jsonl")  # 📝 v32: журнал запитів Tier 2, лише локально
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
            d = {"app": "Генератор відео v32"}
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


def write_manifest(info, workdir, say):
    """📋 v28: manifest.json — план і результат генерації у робочій папці:
    режим, тема або частини сценарію (текст, запит, посилання, тривалість),
    голос, розмір, стилі. Артефакт-тека: видно, з чого зібрано відео, і легко
    повторити той самий запуск. Fail-open: не вийшло — не важливо."""
    try:
        data = {"generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "app": "Генератор відео v32"}
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


def ollama_chat(url, model, prompt, system=None, timeout=90):
    """🧠 v29: один запит до локального Ollama (/api/chat, stream=false).
    Повертає текст відповіді або "" — нема сервера/таймаут/помилка (fail-open)."""
    try:
        body = {"model": model, "stream": False,
                "messages": ([{"role": "system", "content": system}] if system else [])
                + [{"role": "user", "content": prompt}]}
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


def router_chat(url, model, prompt, system=None, timeout=90):
    """🌐 v31: 9Router — один запит /v1/chat/completions (OpenAI-формат).
    Повертає текст відповіді або "" — нема роутера/таймаут/помилка (fail-open)."""
    try:
        body = {"model": model,
                "messages": ([{"role": "system", "content": system}] if system else [])
                + [{"role": "user", "content": prompt}]}
        r = requests.post((url or "").rstrip("/") + "/v1/chat/completions",
                          json=body, timeout=timeout)
        if r.status_code != 200:
            return ""
        ch = (r.json().get("choices") or [{}])[0]
        return (((ch.get("message") or {}).get("content") or "")).strip()
    except Exception:
        return ""


def llm_list_models(provider, url, timeout=8):
    """🌐 v31: список моделей за провайдером: Ollama (/api/tags) або 9Router (/v1/models)."""
    if provider == "9router":
        return router_list_models(url, timeout)
    return ollama_list_models(url, timeout)


def llm_chat(provider, url, model, prompt, system=None, timeout=90):
    """🌐 v31: один запит за провайдером: Ollama (/api/chat) або 9Router (/v1/chat/completions)."""
    if provider == "9router":
        return router_chat(url, model, prompt, system=system, timeout=timeout)
    return ollama_chat(url, model, prompt, system=system, timeout=timeout)


def llm_trace(kind, provider, model, t0, ok, chars):
    """📝 v32: llm_trace.jsonl — журнал запитів Tier 2 (opik @track-патерн):
    провайдер/модель/вид/мс/успіх/символи. Ротація: >64 КБ — лишаю останні
    500 рядків. Fail-open: журнал — лише діагностика, ніколи не ламає запит."""
    try:
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
            s = re.sub(r"<[^>]*>", " ", s)  # теги , <00:00:01.000> тощо
            s = re.sub(r" ", " ", s)
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


def generate_video(query, voice_label, size_str, music, say, on_workdir=None, yt_url="", bg_files=None, yt_search_urls=None, auto_yt=True, yt_many=None, pin_images=None, sub_style="Класичні", vid_style="Без стилю", transition="Різко", trim_sil=False, cover=False, no_faces=False, seo=False, master=False, pack_mb=None, rate_pct=0, platform=None):
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


def generate_script_video(script_text, voice_label, size_str, music, say, on_workdir=None, sub_style="Класичні", vid_style="Без стилю", trim_sil=False, cover=False, no_faces=False, seo=False, master=False, pack_mb=None, rate_pct=0, platform=None):
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
        return {"url": "http://localhost:11434", "model": "", "models": [], "provider": "ollama"}}


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
            head, values=["🎬 Генерація", "🗂 Історія", "⚙️ Налаштування"],
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

        # === ТРИ ТАБИ ===
        self.tab_gen = ctk.CTkFrame(self.root, fg_color="transparent")
        self.tab_hist = ctk.CTkFrame(self.root, fg_color="transparent")
        self.tab_set = ctk.CTkFrame(self.root, fg_color="transparent")
        self._build_gen_tab()
        self._build_hist_tab()
        self._build_set_tab()
        self._show_tab("🎬 Генерація")
        # v13: меню правого кліку («📋 Вставити») для всіх текстових полів
        for w in (self.query, self.script, self.yt_many, self.yt_search_entry, self.pins_entry, self.tr_entry, self.px_key, self.px_query, self.suno_cookie, self.suno_desc, self.suno_tags):
            self.attach_paste_menu(w)

    def _show_tab(self, val):
        for t in (self.tab_gen, self.tab_hist, self.tab_set):
            t.pack_forget()
        if "Історія" in val:
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
        for seq in ("", "", ""):
            self._bind_safe(self.query, seq, self._paste_event)
        self._bind_safe(self.query, "", self._ctrl_enter)
        qrow = ctk.CTkFrame(qc, fg_color="transparent")
        qrow.pack(fill="x", padx=16, pady=(2, 2))
        ctk.CTkButton(qrow, text="📥 Вставити", width=100, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.paste_query).pack(side="left")
        ctk.CTkButton(qrow, text="🧲 Оцінити", width=100, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.score_now).pack(side="left", padx=(8, 0))
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
        self._bind_safe(self.agent_entry, "", _agent_enter)
        ctk.CTkLabel(ac, text="📥 Вставити — скопійований текст з буфера • 🤖 Виконати фразу або Enter — налаштувати поля",
                     font=self._f(10), text_color=self.MUTED).pack(anchor="w",
                                                                   padx=16, pady=(0, 2))
        abtn = ctk.CTkFrame(ac, fg_color="transparent")
        abtn.pack(fill="x", padx=16, pady=(2, 4))
        ctk.CTkButton(abtn, text="📥 Вставити", height=36, corner_radius=18,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13, "bold"),
                      command=lambda: self.paste_into(self.agent_entry)).pack(
                          side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkButton(abtn, text="🤖  Виконати фразу", height=36, corner_radius=18,
                      font=self._f(13, "bold"), command=self._agent_send).pack(
                          side="left", fill="x", expand=True, padx=(4, 0))

        # 🧠 v29: Tier 2 — опційний локальний Ollama: сильніший розбір фраз і сценарії
        ctk.CTkLabel(ac, text="🧠 Локальний AI (опційно): Ollama або 🌐 9Router (api-free) — краще розбирає фрази, вміє писати сценарій",
                     font=self._f(11), text_color=self.MUTED, anchor="w",
                     wraplength=560).pack(fill="x", padx=16, pady=(8, 2))
        _oc = load_ollama_conf()
        prow = ctk.CTkFrame(ac, fg_color="transparent")
        prow.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(prow, text="Джерело:", font=self._f(11),
                     text_color=self.MUTED).pack(side="left", padx=(0, 6))
        self.llm_provider = ctk.CTkSegmentedButton(
            prow, values=["Ollama", "9Router"], font=self._f(11), height=28,
            fg_color=self.INSET, selected_color=self.ACCENT,
            selected_hover_color=self.ACCENT_H, unselected_color=self.HOVER,
            command=self._switch_llm_provider)
        self.llm_provider.set("9Router" if (_oc.get("provider") or "ollama") == "9router" else "Ollama")
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
        ctk.CTkButton(orow, text="🔄 Перевірити", height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.ollama_check_now).pack(side="left", padx=(8, 0))
        self.ollama_status = ctk.CTkLabel(
            ac, text="Перевір — підпишу модель. Зберігається лише локально; без локального AI — Асистент як раніше.",
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
        for seq in ("", "", ""):
            self._bind_safe(self.script, seq, self._paste_script_event)
        self._bind_safe(self.script, "", self._ctrl_enter)
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
        for seq in ("", "", ""):
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
        ctk.CTkLabel(ac, text="Генератор відео v32 — простий інтерфейс: обери режим (🎬 Відео / 📜 Сценарій / 🎧 Мікс) і натисни кнопку.\nТема → озвучка → субтитри → фон (YouTube / фото: Openverse, Pixabay, Pinterest) → рендер. Додатково: 🎼 музика Suno AI, стилі, пресети, транскрипція, SEO-пак.\nКлюч Pixabay і cookie Suno — лише локально на комп'ютері. Дизайн надихався MoneyPrinterTurbo. Репозиторій: khomyak75roman-dotcom/video-generator",
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

    def attach_paste_menu(self, widget):
        """🖱 ПКМ у полі — меню «📋 Вставити» / «🧹 Очистити» (текст з буфера обміну)."""
        menu = tkinter.Menu(widget, tearoff=0, bg="#1C1C1E", fg="#F5F5F7",
                            activebackground="#3A3A3C", activeforeground="#FFFFFF",
                            font=("Segoe UI", 11))
        menu.add_command(label="📋 Вставити", command=lambda: self.paste_into(widget))
        menu.add_command(label="🧹 Очистити", command=lambda: self.clear_field(widget))
        widget._paste_menu = menu

        def _popup(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
        self._bind_safe(widget, "", _popup, add="+")

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
                        "🌐 9Router" if _prov == "9router" else "Ollama", _om))
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
        self.say("🧠 Ollama підказала{} — перевір поля й пиши «давай»".format(
            " і написала сценарій" if sc else ""))

    def _llm_provider(self):
        """🌐 v31: що обрано в картці Асистента: 'ollama' або '9router'."""
        try:
            return "9router" if (self.llm_provider.get() or "") == "9Router" else "ollama"
        except Exception:
            return "ollama"

    def _switch_llm_provider(self, val):
        """🌐 v31: перемикання Ollama ↔ 9Router — дефолтний URL міняється слідом."""
        defs = {"Ollama": "http://localhost:11434", "9Router": "http://localhost:20128"}
        others = {v for k, v in defs.items() if k != val}
        cur = (self.ollama_url.get() or "").strip()
        if not cur or cur in others:
            self.ollama_url.delete(0, "end")
            self.ollama_url.insert(0, defs.get(val, "http://localhost:11434"))
        self.ollama_status.configure(
            text="Джерело: {} — за замовчуванням {}. Перевір — підпишу модель.".format(
                val, defs.get(val, "")))

    def ollama_check_now(self):
        """🧠 v29 / 🌐 v31: «Перевірити» — список моделей провайдера у фоні, Tk не зависає."""
        prov = self._llm_provider()
        url = (self.ollama_url.get().strip()
               or ("http://localhost:20128" if prov == "9router" else "http://localhost:11434"))
        name = "🌐 9Router" if prov == "9router" else "🧠 Ollama"
        self.ollama_status.configure(text="🔄 Шукаю {} на {}…".format(name, url))
        threading.Thread(target=lambda: self.q.put(
            ("ollama_check", (prov, url, llm_list_models(prov, url)))), daemon=True).start()

    def _ollama_check_done(self, payload):
        """🧠 v29 / 🌐 v31: перевірку зроблено — меню моделей, збереження, статус."""
        prov, url, models = payload
        name = "🌐 9Router" if prov == "9router" else "🧠 Ollama"
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
            if getattr(self, "mode", "video") == "script":
                generate_script_video(self.script.get("1.0", "end").strip(),
                                      self.voice.get(), SIZES[self.size.get()],
                                      getattr(self, "music_path", "").strip(), self.say,
                                      on_workdir=lambda wd: setattr(self, "workdir", wd),
                                      sub_style=sub, vid_style=vid, trim_sil=trim, cover=cov,
                                      no_faces=nf, seo=se, master=ln, pack_mb=pk, rate_pct=rt, platform=pv)
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
                                       trim_sil=trim, cover=cov, no_faces=nf, seo=se, master=ln, pack_mb=pk, rate_pct=rt, platform=pv)
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
