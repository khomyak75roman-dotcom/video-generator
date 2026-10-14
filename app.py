# -*- coding: utf-8 -*-
"""Генератор відео з запиту: озвучка edge-tts + відеокліпи Openverse + субтитри (ffmpeg).
UI у стилі iPhone (CustomTkinter, dark mode iOS). v3: скролінг, авто-ffmpeg, YouTube-фон.
v4: пошук YouTube без ключів — обрані знайдені відео йдуть кліпами у фон.
v5: фронтенд у стилі iPhone — вікно з пропорціями екрана ноутбука (16:10),
центрована колонка контенту, статус-бар з годинником, home-індикатор."""
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
import zipfile
from datetime import datetime
from tkinter import messagebox, filedialog

import customtkinter as ctk
import edge_tts
import requests

ctk.set_appearance_mode("dark")  # iOS: темна тема за замовчуванням
ctk.set_default_color_theme("blue")

# Шрифт Segoe UI — системний шрифт Windows (Roboto, що в CustomTkinter за замовчуванням, у Windows відсутній і виглядає дивно)

VOICES = {
    "Остап": "uk-UA-OstapNeural",
    "Поліна": "uk-UA-PolinaNeural",
    "Christopher": "en-US-ChristopherNeural",
    "Jenny": "en-US-JennyNeural",
}
SIZES = {
    "720p": "1280x720",
    "1080p": "1920x1080",
    "Shorts": "1080x1920 (Shorts)",
}
YT_QUALITY = {"720p": 720, "1080p": 1080, "Максимальна": 2160}
YT_SEARCH_LIMIT = 12   # скільки результатів пошуку показувати
YT_CLIP_MAX_SEC = 120  # кожне обране відео — максимум стільки секунд у фоні
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
UA_STRING = "VideoGenerator/1.5 (https://github.com/khomyak75roman-dotcom/video-generator)"


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


def build_bg_from_clips(clips, dur, w, h, workdir):
    """Справжній відеоряд: кожен кліп обрізається до свого слота, нормалізується
    і склеюється. Якщо матеріалу менше за озвучку — кліпи йдуть по колу."""
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
    segs = []
    for j, (c, take) in enumerate(slots):
        seg = os.path.join(workdir, "vseg{}.mp4".format(j))
        run([ff, "-y", "-hide_banner", "-nostdin", "-i", c, "-t", "{:.2f}".format(take),
             "-an", "-vf",
             ("scale={}:{}:force_original_aspect_ratio=increase,crop={}:{},"
              "fps=25,setsar=1,format=yuv420p").format(w, h, w, h),
             "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", seg])
        segs.append(seg)
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


def generate_video(query, voice_label, size_str, music, say, on_workdir=None, yt_url="", bg_files=None, yt_search_urls=None):
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
            bg = build_bg_from_clips(list(bg_files), dur, w, h, workdir)
            say("🎬 Фон: твоя компіляція з кількох відео")
        except Exception as e:
            say("⚠️ Твої відео не зібралися ({}), шукаю фон сам…".format(str(e)[:200]))
            bg = None
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

    cmd = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", "voice.mp3"]
    if music:
        cmd += ["-i", music]

    if music:
        cmd += ["-filter_complex",
                f"[0:v]scale={w}:{h}:force_original_aspect_ratio=cover,"
                f"subtitles=sub.srt:force_style='FontSize=16'[v];"
                f"[1:a][2:a]amix=inputs=2:duration=first:weights='1 0.15'[a]",
                "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a", "-shortest", "-vf",
                f"scale={w}:{h}:force_original_aspect_ratio=cover,"
                f"subtitles=sub.srt:force_style='FontSize=16'"]

    cmd += ["-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "final.mp4"]

    say("🚀 Рендерю відео…")
    try:
        run(cmd, cwd=workdir)
    except Exception as err:
        say("⚠️ Рендер із субтитрами не вдався — спробую простіший, без субтитрів…")
        say("📝 Причина: " + str(err)[:400])
        cmd2 = [ff, "-y", "-hide_banner", "-nostdin", *vf_in, "-i", "voice.mp3",
                "-map", "0:v", "-map", "1:a", "-shortest",
                "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "final.mp4"]
        run(cmd2, cwd=workdir)
        say("ℹ️ Відео готове без субтитрів; повний лог: ffmpeg-error.txt у робочій папці")
    say(f"✅ ГОТОВО: {os.path.join(workdir, 'final.mp4')}")
    return workdir


class App:
    """Інтерфейс у стилі iPhone: чорний фон dark mode iOS, картки-групи, синій акцент.
    v5: вікно з пропорціями екрана ноутбука (16:10), центрована колонка контенту,
    статус-бар з годинником зверху і home-індикатор знизу — як в iPhone."""

    BG = "#000000"       # iPhone: справжній чорний фон (systemBackground, dark)
    CARD = "#1C1C1E"     # iPhone: картка-група (secondarySystemBackground)
    INSET = "#2C2C2E"    # iPhone: вкладені поля і кнопки (tertiarySystemBackground)
    HOVER = "#3A3A3C"    # iPhone: наведення на вкладені елементи
    ACCENT = "#0A84FF"   # iPhone: системний синій (systemBlue)
    ACCENT_H = "#3395FF" # iPhone: синій при наведенні
    MUTED = "#8E8E93"    # iPhone: приглушений текст (secondaryLabel)
    SEP = "#38383A"      # iPhone: розділювач/рамка (separator)

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Генератор відео")
        # Розміри: пропорції екрана ноутбука (16:10), з полями до країв екрана
        try:
            dpi = self.root.winfo_fpixels("1i")
        except Exception:
            dpi = 96.0
        scale = max(1.0, dpi / 96.0)
        scr_w = self.root.winfo_screenwidth() / scale
        scr_h = self.root.winfo_screenheight() / scale
        h = int(max(600, min(800, scr_h - 60)))
        w = int(max(900, min(1280, scr_w - 120)))
        if w > h * 16 / 10:  # тримаємо пропорцію 16:10, як екран ноутбука
            w = int(h * 16 / 10)
        self.pad = max(24, (w - 840) // 2)  # центрована колонка контенту
        # Вікно по центру екрана
        try:
            px_w = self.root.winfo_screenwidth()
            px_h = self.root.winfo_screenheight()
            x = max(0, int((px_w - w * scale) / 2))
            y = max(0, int((px_h - h * scale) / 2))
            self.root.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            self.root.geometry(f"{w}x{h}")
        self.root.minsize(860, 520)
        self.root.configure(fg_color=self.BG)
        self.q = queue.Queue()
        self.workdir = None
        self.yt_checked = {}   # url -> BooleanVar (обране в пошуку YouTube)
        self.merge_files = []
        self._build()
        self.root.after(150, self._poll)
        self.root.after(1000, self._tick_clock)
        threading.Thread(target=self._startup_check, daemon=True).start()

    def _card(self, master, **pack):
        card = ctk.CTkFrame(master, fg_color=self.CARD, corner_radius=24)
        card.pack(**pack)
        return card

    def _tick_clock(self):
        """Годинник у статус-барі, як на iPhone."""
        try:
            self.clock.configure(text=datetime.now().strftime("%H:%M"))
        except Exception:
            pass
        self.root.after(20000, self._tick_clock)

    def _startup_check(self):
        """Одразу показує в журналі, чи готовий ffmpeg до роботи."""
        if ffmpeg_available():
            self.say("✅ ffmpeg знайдено — усе готове до генерації")
        else:
            self.say("ℹ️ ffmpeg ще не встановлено — при першій генерації завантажу його сам (один раз, ~100 МБ)")

    def _build(self):
        # === СТАТУС-БАР, як в iPhone: час зліва, іконки справа ===
        sb = ctk.CTkFrame(self.root, fg_color="transparent", height=30)
        sb.pack(side="top", fill="x")
        self.clock = ctk.CTkLabel(sb, text="",
                                 font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                                 text_color="#FFFFFF", anchor="w")
        self.clock.pack(side="left", padx=(self.pad, 0), pady=(8, 0))
        ctk.CTkLabel(sb, text="📶  🔋  100%",
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color=self.MUTED).pack(side="right", padx=(0, self.pad), pady=(8, 0))

        # === НИЖНЯ ЗАКРІПЛЕНА ЗОНА: кнопка, прогрес, журнал — ЗАВЖДИ на екрані ===
        bottom = ctk.CTkFrame(self.root, fg_color="transparent")
        bottom.pack(side="bottom", fill="x")

        # Головна кнопка-пігулка, як у iOS
        self.btn = ctk.CTkButton(bottom, text="🎬  ЗГЕНЕРУВАТИ ВІДЕО",
                                 height=56, corner_radius=28,
                                 font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
                                 fg_color=self.ACCENT, hover_color=self.ACCENT_H,
                                 command=self.start)
        self.btn.pack(fill="x", padx=self.pad, pady=(12, 0))

        self.bar = ctk.CTkProgressBar(bottom, mode="indeterminate", height=6,
                                      corner_radius=3, progress_color=self.ACCENT)
        self.bar.pack(fill="x", padx=self.pad, pady=(6, 0))
        self.bar.set(0)

        ctk.CTkButton(bottom, text="📂 Відкрити папку з результатом",
                      height=34, corner_radius=17, fg_color="transparent",
                      border_width=1, border_color=self.SEP,
                      hover_color=self.CARD,
                      font=ctk.CTkFont(family="Segoe UI", size=12),
                      command=self.open_folder).pack(anchor="e", padx=self.pad, pady=4)

        # Картка журналу (фіксована висота, завжди видима)
        lc = ctk.CTkFrame(bottom, fg_color=self.CARD, corner_radius=24)
        lc.pack(fill="x", padx=self.pad, pady=(0, 6))
        ctk.CTkLabel(lc, text="Журнал",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(12, 2))
        self.log = ctk.CTkTextbox(lc, state="disabled", height=150,
                                  font=ctk.CTkFont(family="Segoe UI", size=12),
                                  wrap="word", fg_color=self.BG, corner_radius=14)
        self.log.pack(fill="x", padx=20, pady=(0, 12))

        # Home-індикатор — пігулка знизу вікна, як в iPhone
        ctk.CTkFrame(bottom, width=150, height=5, corner_radius=3,
                     fg_color="#48484A").pack(pady=(0, 10))

        # === ВЕРХНЯ ЗОНА ЗІ СКРОЛІНГОМ: усі картки налаштувань ===
        scroll = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        scroll.pack(side="top", fill="both", expand=True)

        # Великий заголовок, як в iOS (large title)
        ctk.CTkLabel(scroll, text="🎬  Відео",
                     font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", padx=self.pad, pady=(10, 0))
        ctk.CTkLabel(scroll, text="Опиши тему — зроблю відео з озвучкою та субтитрами",
                     font=ctk.CTkFont(family="Segoe UI", size=14),
                     text_color=self.MUTED).pack(anchor="w", padx=self.pad, pady=(0, 2))
        ctk.CTkLabel(scroll, text="⬇️ Картки нижче крутяться коліщатком мишки",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.MUTED).pack(anchor="w", padx=self.pad, pady=(0, 4))

        # — Картка: запит —
        qc = self._card(scroll, fill="x", padx=self.pad, pady=(8, 4))
        ctk.CTkLabel(qc, text="Твій запит",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(14, 2))
        qrow = ctk.CTkFrame(qc, fg_color="transparent")
        qrow.pack(fill="x", padx=20, pady=(0, 4))
        self.query = ctk.CTkTextbox(qrow, height=110,
                                    font=ctk.CTkFont(family="Segoe UI", size=14),
                                    wrap="word", fg_color=self.BG, corner_radius=14)
        self.query.pack(side="left", fill="both", expand=True)
        ctk.CTkButton(qrow, text="📋 Вставити", width=110, height=40,
                      corner_radius=20, fg_color=self.INSET, hover_color=self.HOVER,
                      font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.paste_query).pack(side="left", padx=(8, 0))
        # Вставка скопійованого тексту: Ctrl+V, Shift+Insert
        for seq in ("<Control-v>", "<Control-V>", "<Shift-Insert>"):
            self.query.bind(seq, self._paste_event)
        # Ctrl+Enter = згенерувати
        self.query.bind("<Control-Return>", self._ctrl_enter)
        srow = ctk.CTkFrame(qc, fg_color="transparent")
        srow.pack(fill="x", padx=20, pady=(2, 0))
        ctk.CTkLabel(srow, text="Перевір, чи заголовок «чепляє» глядача",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.MUTED).pack(side="left")
        ctk.CTkButton(srow, text="🧲 Оцінити заголовок", width=160, height=32,
                      corner_radius=16, fg_color=self.INSET, hover_color=self.HOVER,
                      font=ctk.CTkFont(family="Segoe UI", size=12),
                      command=self.score_now).pack(side="right")
        ctk.CTkLabel(qc, text="Ctrl+V вставити • Ctrl+Enter згенерувати",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.MUTED).pack(anchor="e", padx=20, pady=(2, 12))

        # — Картка: голос —
        vc = self._card(scroll, fill="x", padx=self.pad, pady=4)
        ctk.CTkLabel(vc, text="🎙 Голос озвучення",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(14, 2))
        self.voice = ctk.CTkSegmentedButton(vc, values=list(VOICES),
                                            font=ctk.CTkFont(family="Segoe UI", size=13),
                                            selected_color=self.ACCENT,
                                            selected_hover_color=self.ACCENT)
        self.voice.set("Остап")
        self.voice.pack(fill="x", padx=20, pady=(0, 14))

        # — Картка: розмір —
        zc = self._card(scroll, fill="x", padx=self.pad, pady=4)
        ctk.CTkLabel(zc, text="📐 Розмір відео",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(14, 2))
        self.size = ctk.CTkSegmentedButton(zc, values=list(SIZES),
                                           font=ctk.CTkFont(family="Segoe UI", size=13),
                                           selected_color=self.ACCENT,
                                           selected_hover_color=self.ACCENT)
        self.size.set("720p")
        self.size.pack(fill="x", padx=20, pady=(0, 14))

        # — Картка: музика —
        mc = self._card(scroll, fill="x", padx=self.pad, pady=4)
        ctk.CTkLabel(mc, text="🎵 Фонова музика (не обов'язково)",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(14, 2))
        mrow = ctk.CTkFrame(mc, fg_color="transparent")
        mrow.pack(fill="x", padx=20, pady=(0, 12))
        self.music_lbl = ctk.CTkLabel(mrow, text="Не обрано — буде лише голос",
                                      font=ctk.CTkFont(family="Segoe UI", size=13),
                                      text_color=self.MUTED, anchor="w")
        self.music_lbl.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(mrow, text="Обрати файл…", width=130, height=40,
                      corner_radius=20, fg_color=self.INSET,
                      hover_color=self.HOVER, font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.pick_music).pack(side="left")

        # — Картка: YouTube —
        yc = self._card(scroll, fill="x", padx=self.pad, pady=4)
        ctk.CTkLabel(yc, text="▶️ YouTube: завантажити і/або взяти у генерацію",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(14, 2))
        yrow = ctk.CTkFrame(yc, fg_color="transparent")
        yrow.pack(fill="x", padx=20, pady=(0, 6))
        self.yt_url = ctk.CTkEntry(yrow, placeholder_text="Посилання на відео (https://youtube.com/…)",
                                   height=40, corner_radius=12, fg_color=self.INSET,
                                   font=ctk.CTkFont(family="Segoe UI", size=13))
        self.yt_url.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(yrow, text="⬇️ Завантажити", width=130, height=40,
                      corner_radius=20, fg_color=self.INSET,
                      hover_color=self.HOVER, font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.download_yt).pack(side="left", padx=(8, 0))
        self.yt_q = ctk.CTkSegmentedButton(yc, values=list(YT_QUALITY),
                                           font=ctk.CTkFont(family="Segoe UI", size=13),
                                           selected_color=self.ACCENT,
                                           selected_hover_color=self.ACCENT)
        self.yt_q.set("720p")
        self.yt_q.pack(fill="x", padx=20, pady=(0, 4))
        self.yt_bg = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(yc, text="🎬 Використати це відео у моїй генерації (як фон)",
                      variable=self.yt_bg,
                      font=ctk.CTkFont(family="Segoe UI", size=12),
                      progress_color=self.ACCENT).pack(anchor="w", padx=20, pady=(0, 4))
        ctk.CTkLabel(yc, text="Кнопка ⬇️ просто зберігає відео у папку Відео\\YouTube",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.MUTED).pack(anchor="w", padx=20, pady=(0, 14))

        # — Картка: пошук YouTube —
        sc = self._card(scroll, fill="x", padx=self.pad, pady=4)
        ctk.CTkLabel(sc, text="🔍 Пошук на YouTube (без ключів)",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(14, 2))
        srow = ctk.CTkFrame(sc, fg_color="transparent")
        srow.pack(fill="x", padx=20, pady=(0, 6))
        self.yt_search_entry = ctk.CTkEntry(srow, placeholder_text="Що шукати? (наприклад: космос 4k короткі)",
                                           height=40, corner_radius=12, fg_color=self.INSET,
                                           font=ctk.CTkFont(family="Segoe UI", size=13))
        self.yt_search_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(srow, text="🔎 Шукати", width=120, height=40,
                      corner_radius=20, fg_color=self.INSET,
                      hover_color=self.HOVER, font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.yt_search_now).pack(side="left", padx=(8, 0))
        self.yt_results_frame = ctk.CTkScrollableFrame(sc, height=180, fg_color=self.INSET,
                                                       corner_radius=14)
        self.yt_results_frame.pack(fill="x", padx=20, pady=(0, 6))
        ctk.CTkLabel(self.yt_results_frame, text="Тут з'являться результати пошуку",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.MUTED).pack(anchor="w")
        ctk.CTkLabel(sc, text="Обрані відео підуть кліпами у фон генерації (кожне — перші 2 хв)",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.MUTED).pack(anchor="w", padx=20, pady=(0, 14))

        # — Картка: компіляція з кількох відео —
        gc = self._card(scroll, fill="x", padx=self.pad, pady=4)
        ctk.CTkLabel(gc, text="🎞 Компіляція з кількох відео",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(14, 2))
        self.merge_lbl = ctk.CTkLabel(gc, text="Не обрано жодного відео",
                                      font=ctk.CTkFont(family="Segoe UI", size=12),
                                      text_color=self.MUTED, anchor="w")
        self.merge_lbl.pack(fill="x", padx=20, pady=(0, 4))
        grow = ctk.CTkFrame(gc, fg_color="transparent")
        grow.pack(fill="x", padx=20, pady=(0, 6))
        ctk.CTkButton(grow, text="➕ Додати відео…", height=40,
                      corner_radius=20, fg_color=self.INSET, hover_color=self.HOVER,
                      font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.pick_merge_files).pack(side="left")
        ctk.CTkButton(grow, text="✖️ Очистити", width=110, height=40,
                      corner_radius=20, fg_color="transparent", border_width=1,
                      border_color=self.SEP, hover_color=self.CARD,
                      font=ctk.CTkFont(family="Segoe UI", size=12),
                      command=self.clear_merge_files).pack(side="left", padx=(8, 0))
        ctk.CTkButton(grow, text="🎞 Зшити в одне", height=40,
                      corner_radius=20, fg_color=self.ACCENT, hover_color=self.ACCENT_H,
                      font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.merge_now).pack(side="right")
        self.merge_bg = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(gc, text="🎬 Використати ці відео у моїй генерації (як фон)",
                      variable=self.merge_bg,
                      font=ctk.CTkFont(family="Segoe UI", size=12),
                      progress_color=self.ACCENT).pack(anchor="w", padx=20, pady=(0, 14))

    def paste_query(self):
        """Вставляє текст із буфера обміну в поле запиту."""
        try:
            clip = self.root.clipboard_get()
        except Exception:
            self.say("⚠️ Буфер обміну порожній")
            return
        clip = clip.strip()
        if clip:
            self.query.insert("insert", clip)
            self.query.see("insert")
            self.say("📋 Текст вставлено в поле запиту")

    def _paste_event(self, event):
        self.paste_query()
        return "break"

    def _ctrl_enter(self, event):
        self.start()
        return "break"

    def score_now(self):
        """🧲 Оцінка заголовка з поля запиту (поради — у журнал)."""
        score_hook(self.query.get("1.0", "end").strip(), self.say)

    def pick_music(self):
        p = filedialog.askopenfilename(filetypes=[("Аудіо", "*.mp3 *.wav *.m4a *.ogg")])
        if p:
            self.music_lbl.configure(text=os.path.basename(p), text_color="#FFFFFF")
            self.music_path = p

    def download_yt(self):
        """Завантаження відео з YouTube окремим потоковим процесом."""
        url = self.yt_url.get().strip()
        if not url.startswith("http"):
            messagebox.showwarning("Стоп", "Встав посилання на відео 🙂")
            return
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self._yt_thread, args=(url,), daemon=True).start()

    def _yt_thread(self, url):
        try:
            ensure_ffmpeg(self.say)
            p = youtube_download(url, YT_OUT_DIR, YT_QUALITY[self.yt_q.get()], self.say)
            self.say("✅ Готово: " + p)
            self.say("📂 Файл у папці Відео\\YouTube")
        except Exception as e:
            self.say("❌ " + str(e)[:300])
        finally:
            self.q.put(None)

    def yt_search_now(self):
        """Пошук YouTube у фоновому потоці (без жодних API-ключів)."""
        q = self.yt_search_entry.get().strip()
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
                if msg[0] == "yt_search_results":
                    self._show_yt_results(msg[1], msg[2])
                continue
            if msg is None:  # пайплайн завершено
                self.bar.stop()
                self.bar.set(0)
                self.btn.configure(state="normal")
                continue
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.root.after(150, self._poll)

    def start(self):
        query = self.query.get("1.0", "end").strip()
        if len(query) < 3:
            messagebox.showwarning("Стоп", "Спершу встав запит 🙂")
            return
        if not hasattr(self, "music_path"):
            self.music_path = ""
        self.btn.configure(state="disabled")
        self.bar.start()
        threading.Thread(target=self.pipeline, args=(query,), daemon=True).start()

    def pipeline(self, query):
        try:
            yt = ""
            if getattr(self, "yt_bg", None) and self.yt_bg.get():
                yt = self.yt_url.get().strip()
                if not yt:
                    self.say("⚠️ Перемикач YouTube увімкнено, але посилання порожнє — шукаю фон сам")
            files = None
            if getattr(self, "merge_bg", None) and self.merge_bg.get() and self.merge_files:
                files = list(self.merge_files)
            sel = [u for u, v in getattr(self, "yt_checked", {}).items() if v.get()]
            if sel:
                self.say("🎬 У фон піде {} обраних відео з пошуку".format(len(sel)))
            generate_video(query, self.voice.get(), SIZES[self.size.get()],
                           getattr(self, "music_path", "").strip(), self.say,
                           on_workdir=lambda wd: setattr(self, "workdir", wd),
                           yt_url=yt, bg_files=files, yt_search_urls=sel)
            if self.workdir and os.path.isdir(self.workdir):
                try:
                    os.startfile(self.workdir)  # Windows: одразу показати результат
                    self.say("📂 Відкрив папку з готовим відео")
                except Exception:
                    pass
        except Exception as e:
            self.say(f"❌ Помилка: {e}")
        finally:
            self.q.put(None)


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        # Режим самоперевірки (для CI): генерує тестове відео без вікна.
        def _log(msg):
            with open("smoke-log.txt", "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        ok = True
        try:
            generate_video("Перевірка збірки генератора", "Остап",
                           "1280x720", "", _log, on_workdir=lambda wd: None)
        except Exception as e:
            ok = False
            _log("SMOKE FAILED: " + str(e))
        sys.exit(0 if ok else 1)
    App().root.mainloop()
