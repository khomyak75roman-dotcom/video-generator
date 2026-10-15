# -*- coding: utf-8 -*-
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
"""
import asyncio
import base64
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import tkinter
import webbrowser
import zipfile
from datetime import datetime
from tkinter import messagebox, filedialog, simpledialog
from urllib.parse import quote_plus

import customtkinter as ctk
import edge_tts
import requests

try:
    from PIL import Image as PILImage  # кадр-прев'ю готового відео (Pillow іде в комплекті з CustomTkinter)
except Exception:
    PILImage = None

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
UA_STRING = "VideoGenerator/1.14 (https://github.com/khomyak75roman-dotcom/video-generator)"


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


def audio_duration(path):
    r = subprocess.run([ffmpeg_path(), "-hide_banner", "-i", path], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", r.stderr)
    if not m:
        raise RuntimeError("Не вдалося визначити тривалість озвучки")
    h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mi * 60 + s


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
        paths, total = [], 0.0
        for i, it in enumerate(good):
            if len(paths) >= max_clips or total >= need:
                break
            ext = os.path.splitext(it["url"].split("?")[0])[1].lstrip(".") or "mp4"
            p = os.path.join(workdir, "clip{}.{}".format(i, ext))
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
                append_credit(workdir, "🎬 {} — {} — {} — {}".format(
                    (it.get("title") or "?")[:60], it.get("license") or "?",
                    it.get("creator") or "?", it.get("foreign_landing_url") or ""))
            except Exception:
                try:
                    os.remove(p)
                except OSError:
                    pass
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


def build_bg_from_clips(clips, dur, w, h, workdir, transition=""):
    """Справжній відеоряд: кожен кліп обрізається до свого слота, нормалізується
    і склеюється. Якщо матеріалу менше за озвучку — кліпи йдуть по колу.
    v14: transition ≠ «» — між фрагментами плавний перехід (xfade)."""
    ff = ffmpeg_path()
    w, h = int(w), int(h)
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
    cmd = [exe, "--no-playlist", "--no-warnings", "--newline",
           "-f", "bv*[ext=mp4][height<={0}]+ba[ext=m4a]/b[ext=mp4][height<={0}]/b[height<={0}]".format(height),
           "--merge-output-format", "mp4",
           "--ffmpeg-location", os.path.dirname(os.path.abspath(ffmpeg_path())),
           "-o", out_tmpl, "--no-simulate", "--print", "after_move:filepath", url]
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


def tts_save(text, voice, out_mp3, say):
    """Озвучка з запасними планами: edge-tts → системний голос Windows → тиха пауза.

    Хмара edge-tts часом відповідає 403 (Microsoft обмежує доступ) —
    додаток усе одно генерує відео, а не падає.
    """
    ff = ffmpeg_path()

    # План 1: edge-tts — найкращі голоси
    for attempt in (1, 2):
        try:
            asyncio.run(edge_tts.Communicate(text, voice).save(out_mp3))
            if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
                return
        except Exception as e:
            say(f"ℹ️ edge-tts не відповів (спроба {attempt}): {e}")
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


def generate_video(query, voice_label, size_str, music, say, on_workdir=None, yt_url="", bg_files=None, yt_search_urls=None, auto_yt=True, yt_many=None, sub_style="Класичні", vid_style="Без стилю", transition="Різко", trim_sil=False, cover=False):
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
    tts_save(text, voice, os.path.join(workdir, "voice.mp3"), say)
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
                bg = build_bg_from_clips(got, dur, w, h, workdir, transition=transition)
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
            bg = build_bg_from_clips(list(bg_files), dur, w, h, workdir, transition=transition)
            say("🎬 Фон: твоя компіляція з кількох відео")
        except Exception as e:
            say("⚠️ Твої відео не зібралися ({}), шукаю фон сам…".format(str(e)[:200]))
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
                bg = build_bg_from_clips(got, dur, w, h, workdir, transition=transition)
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
                bg = build_bg_from_clips(clips, dur, w, h, workdir)
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
    vf_base = f"scale={w}:{h}:force_original_aspect_ratio=cover"
    if vfx:
        vf_base += "," + vfx

    cmd = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", "voice.mp3"]
    if music:
        cmd += ["-i", music]

    if music:
        cmd += ["-filter_complex",
                f"[0:v]{vf_base},"
                f"subtitles=sub.srt:force_style='{stl}'[v];"
                f"[1:a][2:a]amix=inputs=2:duration=first:weights='1 0.15'[a]",
                "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a", "-shortest", "-vf",
                f"{vf_base},"
                f"subtitles=sub.srt:force_style='{stl}'"]

    cmd += ["-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "final.mp4"]

    say("🚀 Рендерю відео…")
    try:
        run(cmd, cwd=workdir)
    except Exception as err:
        say("⚠️ Рендер із субтитрами не вдався — спробую простіший, без субтитрів…")
        say("📝 Причина: " + str(err)[:400])
        cmd2 = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", "voice.mp3",
                "-map", "0:v", "-map", "1:a", "-shortest"]
        if vfx:
            cmd2 += ["-vf", vf_base]
        cmd2 += ["-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "final.mp4"]
        run(cmd2, cwd=workdir)
        say("ℹ️ Відео готове без субтитрів; повний лог: ffmpeg-error.txt у робочій папці")
    if cover:  # 📷 v14: обкладинка для YouTube
        try:
            make_cover(workdir, query, say)
        except Exception as e:
            say("⚠️ Обкладинка не вийшла: " + str(e)[:120])
    say(f"✅ ГОТОВО: {os.path.join(workdir, 'final.mp4')}")
    return workdir


def parse_script(text):
    """Сценарій у частини: блоки розділені порожніми рядками.
    Керуючі рядки на початку частини (будь-яким порядком, далі — текст озвучки):
      «Пошук: запит» (або «Знайти:», «Search:») — запит для YouTube-пошуку фону частини;
      «Кліп: посилання» (або «Відео:», «Clip:») — ТВОЄ конкретне YouTube-відео у фон
      частини (якщо не завантажиться — шукаю автоматично за запитом)."""
    scenes = []
    for block in re.split(r"\n[ \t]*\n+", (text or "").strip()):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        q, url = None, None
        while lines:
            m = re.match(r"(?i)^(?:пошук|знайти|search)\s*[:\-—]\s*(.+)$", lines[0])
            u = re.match(r"(?i)^(?:кліп|відео|clip)\s*[:\-—]\s*(\S+)$", lines[0])
            if m and not q:
                q = m.group(1).strip()
                lines = lines[1:]
            elif u and not url:
                url = u.group(1).strip()
                lines = lines[1:]
            else:
                break
        body = " ".join(lines).strip()
        if not body:
            continue
        if url and not re.match(r"(?i)^https?://", url):
            url = None
        if not q:
            words = [w for w in re.sub(r"[^\w\s\-]", " ", body).split() if len(w) > 2]
            q = " ".join(words[:6]) if words else body[:40]
        scenes.append({"q": q, "text": body, "url": url})
    return scenes


def scene_segment(clip, dur, w, h, workdir, idx):
    """Фон однієї частини: нормалізується під розмір і триває рівно dur секунд
    (короткий кліп зациклюється, довгий обрізається)."""
    ff = ffmpeg_path()
    seg = os.path.join(workdir, "pseg{:02d}.mp4".format(idx))
    vf = ("scale={}:{}:force_original_aspect_ratio=increase,crop={}:{},"
          "fps=25,setsar=1,format=yuv420p").format(int(w), int(h), int(w), int(h))
    run([ff, "-y", "-hide_banner", "-nostdin", "-stream_loop", "-1", "-i", clip,
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


def generate_script_video(script_text, voice_label, size_str, music, say, on_workdir=None, sub_style="Класичні", vid_style="Без стилю", trim_sil=False, cover=False):
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
    mp3s, durs = [], []
    for i, sc in enumerate(scenes):
        m = os.path.join(workdir, "voice_{:02d}.mp3".format(i))
        tts_save(sc["text"], voice, m, say)
        if trim_sil:  # ✂️ v14: прибираємо паузи в кожній частині окремо
            t_out = os.path.join(workdir, "vtrim_{:02d}.mp3".format(i))
            p, _ = remove_pauses(m, t_out, say)
            if os.path.abspath(p) == os.path.abspath(t_out):
                try:
                    os.replace(t_out, m)
                except OSError:
                    pass
        d = audio_duration(m)
        mp3s.append(m)
        durs.append(max(d, 1.0))
        say("🎙️ Частина {}/{} готова: {:.1f} с".format(i + 1, len(scenes), d))
    concat_audio(mp3s, os.path.join(workdir, "voice.mp3"))
    total = sum(durs)
    say("⏱️ Загальна тривалість: {:.1f} с".format(total))

    # 2) Субтитри по частинах
    make_srt_scenes(scenes, durs, workdir)
    say("💬 Субтитри готові")

    # 3) Фон кожної частини: своє відео («Кліп: …») або авто-пошук YouTube
    segs = []
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
            try:
                segs.append(scene_segment(clip, durs[i], w, h, workdir, i))
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
    vf_base = f"scale={w}:{h}:force_original_aspect_ratio=cover"
    if vfx:
        vf_base += "," + vfx
    cmd = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", "voice.mp3"]
    if music:
        cmd += ["-i", music]
    if music:
        cmd += ["-filter_complex",
                f"[0:v]{vf_base},"
                f"subtitles=sub.srt:force_style='{stl}'[v];"
                f"[1:a][2:a]amix=inputs=2:duration=first:weights='1 0.15'[a]",
                "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a", "-shortest", "-vf",
                f"{vf_base},"
                f"subtitles=sub.srt:force_style='{stl}'"]
    cmd += ["-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "final.mp4"]
    say("🚀 Рендерю відео…")
    try:
        run(cmd, cwd=workdir)
    except Exception as err:
        say("⚠️ Рендер із субтитрами не вдався — рендерю без субтитрів…")
        say("📝 Причина: " + str(err)[:400])
        cmd2 = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", "voice.mp3",
                "-map", "0:v", "-map", "1:a", "-shortest"]
        if vfx:
            cmd2 += ["-vf", vf_base]
        cmd2 += ["-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "final.mp4"]
        run(cmd2, cwd=workdir)
        say("ℹ️ Відео готове без субтитрів; повний лог: ffmpeg-error.txt у робочій папці")
    if cover:  # 📷 v14: обкладинка — назва з першої частини сценарію
        try:
            first_line = scenes[0]["text"].splitlines()[0].strip() if scenes else ""
            make_cover(workdir, first_line or "Моє відео", say)
        except Exception as e:
            say("⚠️ Обкладинка не вийшла: " + str(e)[:120])
    say(f"✅ ГОТОВО: {os.path.join(workdir, 'final.mp4')}")
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
        ("Запит:", "Сценар", "Робоча папка", "Перевіряю ffmpeg"),
        ("Озвуч", "озвуч", "Голосів немає", "системним голосом", "Тривалість", "Прибрав пауз"),
        ("убтитр",),
        ("Фон", "фон", "кліп", "Openverse", "Wikimedia", "градієнт",
         "відеоряд", "YouTube", "Посилання", "пошуку", "Шукаю", "зображення"),
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
        for w in (self.query, self.script, self.yt_many, self.yt_search_entry):
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

        # === ЦЕНТР: прев'ю → кнопка → пайплайн → пошук YouTube ===
        center = ctk.CTkScrollableFrame(self.tab_gen, fg_color="transparent")
        center.pack(side="right", fill="both", expand=True, padx=(8, 0), pady=(8, 8))

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

        sc = self._card(center, fill="x", pady=(0, 8))
        ctk.CTkLabel(sc, text="🔍 Пошук на YouTube (без ключів)", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        srow = ctk.CTkFrame(sc, fg_color="transparent")
        srow.pack(fill="x", padx=16, pady=(0, 6))
        self.yt_search_entry = ctk.CTkEntry(
            srow, placeholder_text="Що шукати? (наприклад: космос 4k короткі)",
            height=38, corner_radius=10, fg_color=self.INSET, font=self._f(13))
        self.yt_search_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(srow, text="📋", width=48, height=38, corner_radius=10,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(15),
                      command=lambda: self.paste_into(self.yt_search_entry)).pack(side="left", padx=(8, 0))
        ctk.CTkButton(srow, text="🔎 Шукати", width=110, height=38, corner_radius=10,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=self.yt_search_now).pack(side="left", padx=(8, 0))
        ctk.CTkButton(srow, text="🌐", width=48, height=38, corner_radius=10,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(15),
                      command=lambda: self.open_youtube_search(self.yt_search_entry)).pack(side="left", padx=(8, 0))
        self.yt_results_frame = ctk.CTkScrollableFrame(sc, height=170, fg_color=self.INSET,
                                                       corner_radius=12)
        self.yt_results_frame.pack(fill="x", padx=16, pady=(0, 6))
        ctk.CTkLabel(self.yt_results_frame, text="Тут з'являться результати пошуку",
                     font=self._f(11), text_color=self.MUTED).pack(anchor="w")
        ctk.CTkLabel(sc, text="обрані відео підуть кліпами у фон • нічого не обрав — я сам знайду на YouTube по словах теми",
                     font=self._f(10), text_color=self.MUTED).pack(anchor="w", padx=16, pady=(0, 12))

        # === САЙДБАР НАЛАШТУВАНЬ (лівий, скролінг) ===
        side = ctk.CTkScrollableFrame(self.tab_gen, width=310, fg_color="transparent")
        side.pack(side="left", fill="y", padx=(8, 0), pady=(8, 0))

        qc = self._card(side, fill="x", pady=(0, 8))
        ctk.CTkLabel(qc, text="Тема відео", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        self.query = ctk.CTkTextbox(qc, height=64, font=self._f(13), wrap="word",
                                    fg_color=self.INSET, corner_radius=10)
        self.query.pack(fill="x", padx=14, pady=(0, 4))
        for seq in ("<Control-v>", "<Control-V>", "<Shift-Insert>"):
            self.query.bind(seq, self._paste_event)
        self.query.bind("<Control-Return>", self._ctrl_enter)
        qrow = ctk.CTkFrame(qc, fg_color="transparent")
        qrow.pack(fill="x", padx=14, pady=(2, 2))
        ctk.CTkButton(qrow, text="🧲 Оцінити", width=100, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.score_now).pack(side="left")
        ctk.CTkButton(qrow, text="🌐 YouTube", width=100, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.open_youtube_search).pack(side="left", padx=(8, 0))
        self.batch = ctk.BooleanVar(value=False)  # 📚 v14: батч-генерація
        ctk.CTkSwitch(qc, text="📚 Батч: кожна тема з нового рядка", variable=self.batch,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 0))
        ctk.CTkLabel(qc, text="Ctrl+V вставити • Ctrl+Enter згенерувати",
                     font=self._f(10), text_color=self.MUTED).pack(anchor="w", padx=14, pady=(2, 12))

        tc = self._card(side, fill="x", pady=(0, 8))
        ctk.CTkLabel(tc, text="🎬 Сценарій (по частинах)", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(tc, text="Частини через порожній рядок. «Пошук: запит» задає пошук фону, «Кліп: посилання» — твоє конкретне відео.",
                     font=self._f(10), text_color=self.MUTED, justify="left",
                     wraplength=250).pack(fill="x", padx=14, pady=(0, 4))
        self.script = ctk.CTkTextbox(tc, height=96, font=self._f(13), wrap="word",
                                     fg_color=self.INSET, corner_radius=10)
        self.script.pack(fill="x", padx=14, pady=(0, 4))
        for seq in ("<Control-v>", "<Control-V>", "<Shift-Insert>"):
            self.script.bind(seq, self._paste_script_event)
        self.script.bind("<Control-Return>", self._ctrl_enter)
        trow = ctk.CTkFrame(tc, fg_color="transparent")
        trow.pack(fill="x", padx=14, pady=(2, 2))
        ctk.CTkButton(trow, text="📋", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=lambda: self.paste_into(self.script)).pack(side="left")
        ctk.CTkButton(trow, text="📂", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=self.load_script_file).pack(side="left", padx=(6, 0))
        ctk.CTkButton(trow, text="💾", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=self.save_script_file).pack(side="left", padx=(6, 0))
        self.use_script = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(tc, text="🎬 Генерувати за сценарієм", variable=self.use_script,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 12))

        yb = self._card(side, fill="x", pady=(0, 8))
        ctk.CTkLabel(yb, text="🔗 Відео з YouTube (кілька посилань)",
                     font=self._f(13, "bold"), anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(yb, text="Кожне посилання з нового рядка — з них наріжу фрагменти і змонтую компіляцію у фон.",
                     font=self._f(10), text_color=self.MUTED, justify="left",
                     wraplength=250).pack(fill="x", padx=14, pady=(0, 4))
        self.yt_many = ctk.CTkTextbox(yb, height=72, font=self._f(12), wrap="word",
                                     fg_color=self.INSET, corner_radius=10)
        self.yt_many.pack(fill="x", padx=14, pady=(0, 4))
        for seq in ("<Control-v>", "<Control-V>", "<Shift-Insert>"):
            self.yt_many.bind(seq, self._paste_many_event)
        yrow = ctk.CTkFrame(yb, fg_color="transparent")
        yrow.pack(fill="x", padx=14, pady=(2, 2))
        ctk.CTkButton(yrow, text="📋", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=lambda: self.paste_into(self.yt_many)).pack(side="left")
        ctk.CTkButton(yrow, text="⬇️", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=self.download_yt_many).pack(side="left", padx=(6, 0))
        ctk.CTkButton(yrow, text="🧹", width=48, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(13),
                      command=lambda: self.clear_field(self.yt_many)).pack(side="left", padx=(6, 0))
        yqrow = ctk.CTkFrame(yb, fg_color="transparent")
        yqrow.pack(fill="x", padx=14, pady=(2, 2))
        ctk.CTkLabel(yqrow, text="Якість", font=self._f(11), text_color=self.MUTED).pack(side="left")
        self.yt_q = ctk.CTkOptionMenu(yqrow, values=list(YT_QUALITY), width=130, height=32,
                                      fg_color=self.INSET, button_color=self.HOVER,
                                      button_hover_color=self.HOVER, font=self._f(12))
        self.yt_q.set("720p")
        self.yt_q.pack(side="left", padx=(8, 0))
        self.yt_many_bg = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(yb, text="✂️ Нарізати фрагменти у фон", variable=self.yt_many_bg,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 12))

        vc = self._card(side, fill="x", pady=(0, 8))
        ctk.CTkLabel(vc, text="🎙 Голос озвучення", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        self.voice = ctk.CTkOptionMenu(vc, values=list(VOICES), height=36,
                                       fg_color=self.INSET, button_color=self.HOVER,
                                       button_hover_color=self.HOVER, font=self._f(12))
        self.voice.set("Остап")
        self.voice.pack(fill="x", padx=14, pady=(0, 12))

        stc = self._card(side, fill="x", pady=(0, 8))  # 🎨 v14: стилі відео
        ctk.CTkLabel(stc, text="🎨 Стиль відео", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(stc, text="💬 Стиль субтитрів", font=self._f(11),
                     text_color=self.MUTED, anchor="w").pack(fill="x", padx=14, pady=(4, 0))
        self.sub_style = ctk.CTkOptionMenu(stc, values=list(SUBTITLE_STYLES), height=32,
                                          fg_color=self.INSET, button_color=self.HOVER,
                                          button_hover_color=self.HOVER, font=self._f(12))
        self.sub_style.set("Класичні")
        self.sub_style.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(stc, text="🎨 Стилістика картинки", font=self._f(11),
                     text_color=self.MUTED, anchor="w").pack(fill="x", padx=14, pady=(4, 0))
        self.vid_style = ctk.CTkOptionMenu(stc, values=list(VIDEO_STYLES), height=32,
                                           fg_color=self.INSET, button_color=self.HOVER,
                                           button_hover_color=self.HOVER, font=self._f(12))
        self.vid_style.set("Без стилю")
        self.vid_style.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(stc, text="🎞 Переходи між фрагментами", font=self._f(11),
                     text_color=self.MUTED, anchor="w").pack(fill="x", padx=14, pady=(4, 0))
        self.transition = ctk.CTkOptionMenu(stc, values=list(TRANSITIONS), height=32,
                                            fg_color=self.INSET, button_color=self.HOVER,
                                            button_hover_color=self.HOVER, font=self._f(12))
        self.transition.set("Різко")
        self.transition.pack(fill="x", padx=14, pady=(0, 6))
        self.trim_sil = ctk.BooleanVar(value=False)  # ✂️ v14: паузи з озвучки
        ctk.CTkSwitch(stc, text="✂️ Прибирати паузи з озвучки", variable=self.trim_sil,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 0))
        self.cover_on = ctk.BooleanVar(value=True)  # 📷 v14: обкладинка YouTube
        ctk.CTkSwitch(stc, text="📷 Обкладинка YouTube (cover.jpg)", variable=self.cover_on,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 12))

        zc = self._card(side, fill="x", pady=(0, 8))
        ctk.CTkLabel(zc, text="📐 Розмір відео", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        self.size = ctk.CTkOptionMenu(zc, values=list(SIZES), height=36,
                                      fg_color=self.INSET, button_color=self.HOVER,
                                      button_hover_color=self.HOVER, font=self._f(12))
        self.size.set("720p")
        self.size.pack(fill="x", padx=14, pady=(0, 12))

        mc = self._card(side, fill="x", pady=(0, 8))
        ctk.CTkLabel(mc, text="🎵 Фонова музика (не обов'язково)", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        mrow = ctk.CTkFrame(mc, fg_color="transparent")
        mrow.pack(fill="x", padx=14, pady=(0, 12))
        self.music_lbl = ctk.CTkLabel(mrow, text="Не обрано — буде лише голос",
                                      font=self._f(11), text_color=self.MUTED, anchor="w")
        self.music_lbl.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(mrow, text="Обрати файл…", width=110, height=34, corner_radius=17,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_music).pack(side="left")

        prc = self._card(side, fill="x", pady=(0, 8))  # 💾 v14: пресети налаштувань
        ctk.CTkLabel(prc, text="💾 Пресети налаштувань", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(prc, text="Зберігають голос, розмір, стилі субтитрів, стилістику, переходи і перемикачі — щоб не налаштовувати щоразу.",
                     font=self._f(10), text_color=self.MUTED, justify="left",
                     wraplength=250).pack(fill="x", padx=14, pady=(0, 4))
        self.preset_menu = ctk.CTkOptionMenu(prc, values=["(порожньо)"], height=32,
                                             fg_color=self.INSET, button_color=self.HOVER,
                                             button_hover_color=self.HOVER, font=self._f(12))
        self.preset_menu.pack(fill="x", padx=14, pady=(0, 4))
        prow2 = ctk.CTkFrame(prc, fg_color="transparent")
        prow2.pack(fill="x", padx=14, pady=(0, 2))
        ctk.CTkButton(prow2, text="💾 Зберегти", width=92, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.save_preset).pack(side="left")
        ctk.CTkButton(prow2, text="📂 Застосувати", width=104, height=32, corner_radius=16,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.apply_preset).pack(side="left", padx=(6, 0))
        ctk.CTkButton(prow2, text="🗑", width=44, height=32, corner_radius=16,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.delete_preset).pack(side="left", padx=(6, 0))
        self._refresh_presets()

        gc = self._card(side, fill="x", pady=(0, 8))
        ctk.CTkLabel(gc, text="🎞 Компіляція з кількох відео", font=self._f(13, "bold"),
                     anchor="w").pack(fill="x", padx=14, pady=(12, 2))
        self.merge_lbl = ctk.CTkLabel(gc, text="Не обрано жодного відео",
                                      font=self._f(11), text_color=self.MUTED, anchor="w")
        self.merge_lbl.pack(fill="x", padx=14, pady=(0, 4))
        grow = ctk.CTkFrame(gc, fg_color="transparent")
        grow.pack(fill="x", padx=14, pady=(0, 2))
        ctk.CTkButton(grow, text="➕ Додати", width=90, height=34, corner_radius=17,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.pick_merge_files).pack(side="left")
        ctk.CTkButton(grow, text="✖️", width=44, height=34, corner_radius=17,
                      fg_color=self.INSET, hover_color=self.HOVER, font=self._f(12),
                      command=self.clear_merge_files).pack(side="left", padx=(6, 0))
        ctk.CTkButton(grow, text="🎞 Зшити", width=90, height=34, corner_radius=17,
                      fg_color=self.ACCENT, hover_color=self.ACCENT_H, font=self._f(12),
                      command=self.merge_now).pack(side="right")
        self.merge_bg = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(gc, text="🎬 Ці відео у фон генерації", variable=self.merge_bg,
                      font=self._f(12), progress_color=self.ACCENT).pack(anchor="w", padx=14, pady=(2, 12))

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
        ctk.CTkLabel(hc, text="Жодних API-ключів не потрібно — усе працює з відкритими джерелами.",
                     font=self._f(11), text_color=self.MUTED, anchor="w").pack(fill="x", padx=16, pady=(2, 12))

        ac = self._card(scroll, fill="x", padx=24, pady=(8, 16))
        ctk.CTkLabel(ac, text="Про застосунок", font=self._f(14, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(ac, text="Генератор відео v14 — тема → озвучка (edge-tts) → субтитри → фон → рендер (ffmpeg).\nПресети, стилі субтитрів, стилістика, переходи, обкладинка, прибрання пауз, батч — усе без API-ключів.\nДизайн інтерфейсу надихався MoneyPrinterTurbo (harry0703). Репозиторій: khomyak75roman-dotcom/video-generator",
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
        widget.bind("<Button-3>", _popup, add="+")

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
        self.use_script.set(True)
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

    def start(self):
        query = self.query.get("1.0", "end").strip()
        if getattr(self, "use_script", None) and self.use_script.get():
            script = self.script.get("1.0", "end").strip()
            if len(script) < 10:
                messagebox.showwarning("Стоп", "Режим сценарію увімкнений — напиши сценарій у картці «🎬 Сценарій» 🙂")
                return
        elif len(query) < 3:
            messagebox.showwarning("Стоп", "Спершу встав запит 🙂")
            return
        if not hasattr(self, "music_path"):
            self.music_path = ""
        self.btn.configure(state="disabled")
        self.bar.start()
        self._gen_running = True
        self._reset_steps()
        self.status_lbl.configure(text="● Генерується…", text_color="#F59E0B")
        threading.Thread(target=self.pipeline, args=(query,), daemon=True).start()

    def pipeline(self, query):
        ok = False
        try:
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
            sub = self.sub_style.get() if hasattr(self, "sub_style") else "Класичні"
            vid = self.vid_style.get() if hasattr(self, "vid_style") else "Без стилю"
            trans = self.transition.get() if hasattr(self, "transition") else "Різко"
            trim = bool(self.trim_sil.get()) if hasattr(self, "trim_sil") else False
            cov = bool(self.cover_on.get()) if hasattr(self, "cover_on") else False
            if getattr(self, "use_script", None) and self.use_script.get():
                generate_script_video(self.script.get("1.0", "end").strip(),
                                      self.voice.get(), SIZES[self.size.get()],
                                      getattr(self, "music_path", "").strip(), self.say,
                                      on_workdir=lambda wd: setattr(self, "workdir", wd),
                                      sub_style=sub, vid_style=vid, trim_sil=trim, cover=cov)
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
                                       sub_style=sub, vid_style=vid, transition=trans,
                                       trim_sil=trim, cover=cov)
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
