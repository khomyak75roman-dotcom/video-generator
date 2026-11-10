# -*- coding: utf-8 -*-
"""Генератор відео 3.0 — ЯДРО (кардинальна переробка з нуля, Волна 15).

АРХІТЕКТУРА 3.0 — усе, чого навчився за 14 хвиль:
  1. FAIL-OPEN ДРАБИНА — головний принцип: кожен ступінь (мозок, озвучка,
     фон, даунлоадер) має запасні ступені; впав один — підхоплює наступний.
     Генератор НЕ ПАДАЄ, він деградує чесно.
  2. TRANSCRIPT-FIRST — текст сценарію є джерелом істини: озвучка,
     субтитри і запити фону ВИВЕДЕНІ зі сценарію, а не придумані окремо.
  3. JSON-ТАЙМЛАЙН — project.json описує все відео як дані (сцени, запити,
     фони, стани). Його можна відкрити, відредагувати, продовжити (Resume),
     і він же — чек (Video Receipts) для YouTube-апруву.
  4. ЦІНА ПЕРЕД СПЕНДОМ — перед стартом генератор ЧЕСНО показує оцінку
     часу (слова → озвучка → фон → рендер), а не мовчить у таймі.
  5. ОДНА ВСТАВКА — усе générється з одного текстового поля: тема АБО
     готовий сценарій. Режим перемикається однією кнопкою.
  6. НУЛЬ КЛЮЧІВ — жоден шлях не потребує API-ключа; ключі там, де без
     них фізично не можна (і то лише локальні файли користувача).
  7. ЧЕСНІСТЬ — кожен фолбек повідомляється у лог; «тихих» підмен нема.

Ланцюг фону частини (fail-open, зверху вниз):
  Кліп: посилання → YouTube-пошук за змістом (yt-dlp, ретраї 8) →
  cobalt (запасний даунлоадер) → фото Openverse → AI-кадр Pollinations →
  Кен-Бернс анімація → градієнт. Озвучка: edge-tts (шматками, з паузами)
  → системний голос Windows → тиша. Мозок (сценарій/SEO): Pollinations →
  LLM7 → Kilo — усі безключові.

Цеглини з Волин 1–14 (перевірені в бою): ffprobe у архіві ffmpeg (В13),
.retries 8 (В11), шматки .partNNN.mp3 + -f mp3 (В12), script_bg_query (В11),
cobalt-драбина (В14), обводка обкладинки (В14), +faststart всюди (В13).
"""

import os
import sys
import re
import json
import time
import math
import shutil
import zipfile
import queue
import threading
import subprocess
import asyncio
import datetime

import requests
from urllib.parse import quote, quote_plus

# --- залежності: кожна опційна, нема якої — генератор не вмирає ---
try:
    import customtkinter as ctk
except Exception:
    ctk = None
try:
    import edge_tts
except Exception:
    edge_tts = None
try:
    from PIL import Image as PILImage
except Exception:
    PILImage = None

VERSION = "3.0.0"
APP_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- КОНСТАНТИ
TOOLS_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local", "VideoGenerator")
GEN_BASE = os.path.join(os.path.expanduser("~"), "Videos", "Generated")
FFMPEG_EXE = os.path.join(TOOLS_DIR, "ffmpeg.exe")
FFPROBE_EXE = os.path.join(TOOLS_DIR, "ffprobe.exe")
YTDLP_EXE = os.path.join(TOOLS_DIR, "yt-dlp.exe")
YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_SOURCES = [
    "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip",
    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
]
UA_STRING = "VideoGenerator/3.0 (https://github.com/khomyak75roman-dotcom/video-generator)"
WEB_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

VOICES = {
    "Остап": "uk-UA-OstapNeural",
    "Поліна": "uk-UA-PolinaNeural",
    "Christopher (EN)": "en-US-ChristopherNeural",
    "Jenny (EN)": "en-US-JennyNeural",
    "Ryan (UK)": "en-GB-RyanNeural",
    "Sonia (UK)": "en-GB-SoniaNeural",
    "Marek (PL)": "pl-PL-MarekNeural",
    "Katja (DE)": "de-DE-KatjaNeural",
}
SIZES = {"1080p": (1920, 1080), "Shorts (9:16)": (1080, 1920), "720p": (1280, 720)}
SCRIPT_MAX_SCENES = 12

POLLINATIONS_URL = "https://text.pollinations.ai"      # мозок 1: без ключів
LLM7_URL = "https://api.llm7.io/v1"                    # мозок 2: Bearer "unused"
KILO_URL = "https://api.kilo.ai/api/gateway"           # мозок 3: ~200 зап/год

HF_SPACES = {  # публічні Gradio-API Spaces, БЕЗ ключа (fail-open на кожному)
    "img": "https://evalstate-flux1-schnell.hf.space",              # FLUX: текст → картинка
    "vid": "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space", # WAN 2.2: кадр → відео
}
AI_CACHE_DIR = os.path.join(TOOLS_DIR, "aicache")
AI_CACHE_MAX_FILES = 60

COBALT_INSTANCES = ("https://cobalt-api.kwiatekmiki.com",
                    "https://cobalt-api.meowing.de")
COBALT_FILE = os.path.join(TOOLS_DIR, "cobalt.json")   # своя інстанція: {"instance": "http://localhost:9000"}

LIBRE_INSTANCES = ("https://translate.cutie.dating",
                   "https://translate.fedilab.app",
                   "https://libretranslate.de",
                   "https://libretranslate.com")

STAGES = ("start", "script", "voice", "subtitles", "background", "render", "done")
SUB_STYLE = ("subtitles=sub.srt:force_style='FontName=Arial,FontSize=13,"
             "PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=1,"
             "Outline=2,Shadow=1,MarginV=36'")

# ------------------------------------------------------------- §1 ІНСТРУМЕНТИ

def run(cmd, cwd=None):
    """Виконати команду; не нуль — виняток з хвостом виводу (не ковтаю помилки)."""
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError("{} впав: {}".format(os.path.basename(cmd[0]), (p.stdout or "")[-280:]))
    return p.stdout or ""


def ffmpeg_available():
    try:
        return subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=10).returncode == 0
    except Exception:
        return False


def ffmpeg_path():
    if os.path.exists(FFMPEG_EXE):
        return FFMPEG_EXE
    if ffmpeg_available():
        return "ffmpeg"
    return FFMPEG_EXE


def ffprobe_path():
    fp = ffmpeg_path()
    if fp and fp != "ffmpeg":
        side = os.path.join(os.path.dirname(os.path.abspath(fp)), "ffprobe.exe")
        if os.path.exists(side):
            return side
    if os.path.exists(FFPROBE_EXE):
        return FFPROBE_EXE
    return "ffprobe"


def ensure_ffmpeg(say):
    """ffmpeg + ffprobe з ОДНОГО архіву (Волна 13: без ffprobe yt-dlp валить
    кожне завантаження). Один раз, офіційні збірки, нуль ключів."""
    if ffmpeg_available() or os.path.exists(FFMPEG_EXE):
        return
    os.makedirs(TOOLS_DIR, exist_ok=True)
    zip_path = os.path.join(TOOLS_DIR, "ffmpeg.zip")
    for url in FFMPEG_SOURCES:
        try:
            say("⬇️ Завантажую ffmpeg+ffprobe (офіційна збірка, ~100 МБ, тільки перший раз)…")
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
                pn = [n for n in z.namelist() if n.endswith("bin/ffprobe.exe")]
                if pn:
                    with z.open(pn[0]) as src, open(FFPROBE_EXE, "wb") as dst:
                        shutil.copyfileobj(src, dst)
        except Exception as e:
            say("ℹ️ Одне джерело не вийшло ({}), пробую інше…".format(str(e)[:120]))
            continue
        try:
            os.remove(zip_path)
        except OSError:
            pass
        if os.path.exists(FFMPEG_EXE) and os.path.getsize(FFMPEG_EXE) > 10_000_000:
            say("✅ ffmpeg + ffprobe встановлено — можна генерувати!")
            return
    raise RuntimeError("не вдалося встановити ffmpeg — перевір інтернет і спробуй ще раз")


def ensure_ffprobe(say=None):
    """Волна 13: yt-dlp без ffprobe — «Unable to determine video duration».
    Нема поруч — докачую з того ж архіву ffmpeg."""
    try:
        r = subprocess.run([ffprobe_path(), "-version"], capture_output=True, timeout=15)
        if r.returncode == 0:
            return
    except Exception:
        pass
    os.makedirs(TOOLS_DIR, exist_ok=True)
    zip_path = os.path.join(TOOLS_DIR, "ffprobe.zip")
    for url in FFMPEG_SOURCES:
        try:
            if say:
                say("⬇️ Докачую ffprobe (без нього завантаження з YouTube падали)…")
            with requests.get(url, stream=True, timeout=300,
                              headers={"User-Agent": UA_STRING}) as r, \
                 open(zip_path, "wb") as f:
                r.raise_for_status()
                for chunk in r.iter_content(1 << 18):
                    f.write(chunk)
            with zipfile.ZipFile(zip_path) as z:
                pn = [n for n in z.namelist() if n.endswith("bin/ffprobe.exe")]
                if not pn:
                    raise RuntimeError("у архіві немає ffprobe.exe")
                with z.open(pn[0]) as src, open(FFPROBE_EXE, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        except Exception:
            continue
        try:
            os.remove(zip_path)
        except OSError:
            pass
        try:
            if subprocess.run([FFPROBE_EXE, "-version"], capture_output=True, timeout=15).returncode == 0:
                if say:
                    say("✅ ffprobe встановлено")
                return
        except Exception:
            pass
    raise RuntimeError("ffprobe не встановився — завантаження з YouTube нестабільні")


def ensure_ytdlp(say):
    """Один раз завантажує офіційний yt-dlp.exe з GitHub (нуль ключів)."""
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


def audio_duration(path):
    """Тривалість будь-якого медіа (розбір виводу ffmpeg -i, без ffprobe)."""
    r = subprocess.run([ffmpeg_path(), "-hide_banner", "-i", path],
                       capture_output=True, text=True, encoding="utf-8", errors="ignore")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", r.stderr)
    if not m:
        raise RuntimeError("Не вдалося визначити тривалість")
    h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mi * 60 + s


def has_audio(path):
    r = subprocess.run([ffmpeg_path(), "-hide_banner", "-i", path],
                       capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return "Audio: " in (r.stderr or "")


def open_folder(path):
    try:
        if os.name == "nt":
            os.startfile(path)  # noqa
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


def append_credit(workdir, line):
    """Credits — автори та ліцензії кожного матеріалу (Video Receipts)."""
    try:
        with open(os.path.join(workdir, "credits.txt"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass

# ----------------------------------------------------- §2 МОЗКИ БЕЗ КЛЮЧІВ

def pollinations_chat(prompt, system=None, timeout=60):
    """Мозок 1: Pollinations — POST /openai (OpenAI-формат, БЕЗ ключа);
    не вдався — GET-фолбек з промптом у URL. Порожньо = наступний ступінь."""
    base = POLLINATIONS_URL.rstrip("/")
    body = {"model": "gpt-oss-20b",
            "messages": ([{"role": "system", "content": system}] if system else [])
            + [{"role": "user", "content": prompt}]}
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
    try:
        q = base + "/" + quote_plus((prompt or "")[:1500]) + "?model=gpt-oss-20b"
        if system:
            q += "&system=" + quote_plus(system[:1500])
        r = requests.get(q, timeout=timeout, headers={"User-Agent": UA_STRING})
        if r.status_code == 200 and (r.text or "").strip():
            return r.text.strip()
    except Exception:
        pass
    return ""


def llm7_chat(prompt, system=None, timeout=60):
    """Мозок 2: LLM7 — анонімний OpenAI-сумісний шлюз, Bearer "unused"."""
    body = {"model": "gpt-5.5",
            "messages": ([{"role": "system", "content": system}] if system else [])
            + [{"role": "user", "content": prompt}]}
    try:
        r = requests.post(LLM7_URL.rstrip("/") + "/chat/completions",
                          json=body, timeout=timeout,
                          headers={"Authorization": "Bearer unused",
                                   "User-Agent": UA_STRING})
        if r.status_code != 200:
            return ""
        ch = (r.json().get("choices") or [{}])[0]
        return (((ch.get("message") or {}).get("content") or "")).strip()
    except Exception:
        return ""


def kilo_chat(prompt, system=None, timeout=60):
    """Мозок 3: Kilo Code — безкоштовний шлюз, ~200 зап/год, БЕЗ ключа."""
    body = {"model": "kilo-auto/free",
            "messages": ([{"role": "system", "content": system}] if system else [])
            + [{"role": "user", "content": prompt}]}
    try:
        r = requests.post(KILO_URL.rstrip("/") + "/chat/completions",
                          json=body, timeout=timeout,
                          headers={"User-Agent": UA_STRING})
        if r.status_code != 200:
            return ""
        ch = (r.json().get("choices") or [{}])[0]
        return (((ch.get("message") or {}).get("content") or "")).strip()
    except Exception:
        return ""


def llm_ask(prompt, system=None, say=None, timeout=60):
    """Драбина мозків: Pollinations → LLM7 → Kilo. Кожен мовчить — іду далі
    (fail-open). Всі мовчать — "" і викликач честно падає у свій фолбек."""
    for label, fn in (("Pollinations", pollinations_chat),
                      ("LLM7", llm7_chat),
                      ("Kilo", kilo_chat)):
        try:
            txt = fn(prompt, system=system, timeout=timeout)
        except Exception:
            txt = ""
        if txt and len(txt.strip()) >= 20:
            if say:
                say("🧠 Мозок {} відповів".format(label))
            return txt.strip()
        if say:
            say("🧠 {} мовчить — наступний ступінь…".format(label))
    return ""


# ------------------------------------------------- §3 ПОШУК І СКАЧУВАННЯ

def yt_search(query, limit, say):
    """Пошук на YouTube БЕЗ API-ключа (ytsearch у yt-dlp). (список, помилка)."""
    exe = ensure_ytdlp(say)
    try:
        proc = subprocess.run(
            [exe, "ytsearch{}:{}".format(limit, query), "--flat-playlist",
             "--dump-json", "--ignore-config", "--no-warnings"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=45)
        out = []
        for line in (proc.stdout or "").splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                j = json.loads(line)
            except Exception:
                continue
            if not j.get("id"):
                continue
            out.append({"id": j["id"],
                        "title": (j.get("title") or "")[:100],
                        "url": "https://www.youtube.com/watch?v=" + j["id"],
                        "dur": j.get("duration")})
        if out:
            return out, None
        return [], (proc.stderr or "порожньо")[:150]
    except Exception as e:
        return [], str(e)[:150]


def cobalt_instances():
    """Драбина cobalt-даунлоадерів: спершу СВІЯ (tools/cobalt.json), потім публічні."""
    out = []
    try:
        with open(COBALT_FILE, encoding="utf-8") as f:
            u = str((json.load(f) or {}).get("instance") or "").strip()
        if u:
            out.append(u.rstrip("/"))
    except Exception:
        pass
    return out + [u.rstrip("/") for u in COBALT_INSTANCES]


def cobalt_download(url, outdir, say, out_name="cobalt_clip"):
    """Волна 14: ЗАПАСНИЙ даунлоадер cobalt — рятівник, коли yt-dlp впав.
    Публічні інстанси часто за Turnstile — тоді чесно None (fail-open)."""
    name = (out_name or "cobalt_clip").replace(".mp4", "")
    for inst in cobalt_instances():
        try:
            say("🌊 Пробую запасний даунлоадер cobalt ({})…".format(inst.replace("https://", "")[:40]))
            r = requests.post(inst + "/",
                             json={"url": url, "videoQuality": "720", "filenameStyle": "basic"},
                             headers={"User-Agent": UA_STRING, "Accept": "application/json"},
                             timeout=45)
            if r.status_code != 200:
                continue
            j = r.json()
            if j.get("status") not in ("tunnel", "redirect") or not j.get("url"):
                continue
            out_path = os.path.join(outdir, name + ".mp4")
            with requests.get(j["url"], stream=True, timeout=300,
                              headers={"User-Agent": UA_STRING}) as resp:
                resp.raise_for_status()
                with open(out_path + ".part", "wb") as f:
                    for chunk in resp.iter_content(1 << 18):
                        f.write(chunk)
            if os.path.getsize(out_path + ".part") > 100000:
                os.replace(out_path + ".part", out_path)
                say("🌊 cobalt витягнув відео! (запасний канал спрацював)")
                return out_path
            try:
                os.remove(out_path + ".part")
            except OSError:
                pass
        except Exception:
            continue
    return None


def youtube_download(url, outdir, height, say, fixed_name=None, max_sec=0):
    """yt-dlp з бійцівським характером: ретраї 8 (В11), ffprobe обов'язково
    (В13), 5-хвилинний ліміт, прогрес у лог; впав — cobalt (В14)."""
    os.makedirs(outdir, exist_ok=True)
    exe = ensure_ytdlp(say)
    try:
        ensure_ffprobe(say)
    except Exception:
        pass
    out_tmpl = os.path.join(outdir, (fixed_name or "%(title).100B") + ".%(ext)s")
    cmd = [exe, "--no-playlist", "--no-warnings", "--newline",
           "--socket-timeout", "20", "--retries", "8",
           "--fragment-retries", "8",
           "-f", "bv*[ext=mp4][height<={0}]+ba[ext=m4a]/b[ext=mp4][height<={0}]/b[height<={0}]".format(height),
           "--merge-output-format", "mp4",
           "--ffmpeg-location", os.path.dirname(os.path.abspath(ffmpeg_path())),
           "-o", out_tmpl, "--no-simulate", "--print", "after_move:filepath", url]
    if max_sec:
        cmd += ["--download-sections", "*0:00-{}:00".format(int(max_sec) // 60)]
    say("▶️ Завантажую відео з YouTube…")
    proc = subprocess.Popen(cmd, cwd=outdir, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, universal_newlines=True,
                            encoding="utf-8", errors="replace")
    final_path, err, last_pct = None, None, -100.0
    deadline = time.time() + 300
    for line in proc.stdout:
        if time.time() > deadline:
            proc.terminate()
            raise RuntimeError("yt-dlp затягнув скачування (5 хв) — обриваю")
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
        try:
            proc.terminate()
        except Exception:
            pass
        cb = cobalt_download(url, outdir, say, fixed_name or "cobalt_clip")
        if cb:
            append_credit(outdir, "🎬 {} — фонове відео — cobalt — {}".format(os.path.basename(cb), url))
            return cb
        raise RuntimeError("yt-dlp: " + err)
    code = proc.wait()
    if code != 0 or not final_path:
        cb = cobalt_download(url, outdir, say, fixed_name or "cobalt_clip")
        if cb:
            append_credit(outdir, "🎬 {} — фонове відео — cobalt — {}".format(os.path.basename(cb), url))
            return cb
        raise RuntimeError("yt-dlp не зміг завантажити відео (код {})".format(code))
    append_credit(outdir, "🎬 {} — фонове відео (права належать автору) — YouTube — {}".format(
        os.path.basename(final_path), url))
    return final_path


def openverse_images_search(query, limit, say):
    """Відкриті фото Openverse — комерційні+модифікація, БЕЗ ключа."""
    try:
        r = requests.get("https://api.openverse.org/v1/images/",
                         params={"q": query, "page_size": min(limit, 20),
                                 "license_type": "commercial,modification"},
                         headers={"User-Agent": UA_STRING, "Api-User-Agent": UA_STRING},
                         timeout=25)
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
            return [], "Openverse: нічого підходящого"
        return out, None
    except Exception as e:
        return [], ("Openverse: {}".format(e))[:150]


def download_image(url, out_path, min_bytes=30000):
    """Качнути картинку у .part → на місце. Мала/битa — виняток (ступінь мовчить)."""
    with requests.get(url, stream=True, timeout=60,
                      headers={"User-Agent": UA_STRING}) as resp:
        resp.raise_for_status()
        with open(out_path + ".part", "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
    if os.path.getsize(out_path + ".part") < min_bytes:
        os.remove(out_path + ".part")
        raise RuntimeError("картинка порожня")
    os.replace(out_path + ".part", out_path)
    return out_path


# ------------------------------------------------ §4 ЗОБРАЖЕННЯ І AI-КЛІПИ

def pollinations_image(prompt, out_path, w=1280, h=720, seed=1, timeout=45):
    """AI-кадр БЕЗ ключів (image.pollinations.ai) + кеш Волни 6."""
    try:
        key = "{}|{}|{}|{}".format(prompt, w, h, seed)
        import hashlib
        key = hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]
        cpath = os.path.join(AI_CACHE_DIR, key + ".png")
        if os.path.isfile(cpath) and os.path.getsize(cpath) > 15000:
            shutil.copyfile(cpath, out_path)
            return out_path
    except Exception:
        pass
    url = ("https://image.pollinations.ai/prompt/" + quote((prompt or "")[:400])
           + "?width={}&height={}&nologo=true&seed={}".format(w, h, seed))
    with requests.get(url, stream=True, timeout=timeout,
                      headers={"User-Agent": UA_STRING}) as r:
        r.raise_for_status()
        with open(out_path + ".part", "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
    if os.path.getsize(out_path + ".part") < 15000:
        os.remove(out_path + ".part")
        raise RuntimeError("картинка порожня")
    os.replace(out_path + ".part", out_path)
    try:
        os.makedirs(AI_CACHE_DIR, exist_ok=True)
        shutil.copyfile(out_path, os.path.join(AI_CACHE_DIR, key + ".png"))
        files = [os.path.join(AI_CACHE_DIR, n) for n in os.listdir(AI_CACHE_DIR)
                 if n.lower().endswith(".png")]
        if len(files) > AI_CACHE_MAX_FILES:
            for f in sorted(files, key=os.path.getmtime)[:len(files) - AI_CACHE_MAX_FILES]:
                try:
                    os.remove(f)
                except OSError:
                    pass
    except Exception:
        pass
    return out_path


def hf_space_call(base, api, data, timeout=900):
    """Публічний Gradio-API HF Space БЕЗ ключа: POST → event_id → SSE."""
    r = requests.post(base.rstrip("/") + "/gradio_api/call" + api,
                      json={"data": data}, timeout=30,
                      headers={"User-Agent": UA_STRING})
    r.raise_for_status()
    ev = (r.json() or {}).get("event_id")
    if not ev:
        raise RuntimeError("Space не дав event_id (черга зайнята?)")
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
    raise RuntimeError("Space не відповів у час (ZeroGPU-черга)")


def hf_upload(base, path):
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


def hf_image(prompt, out_path):
    """FLUX.1-schnell (HF Space, БЕЗ ключа): текст → картинка."""
    if not (prompt or "").strip():
        raise RuntimeError("Опиши картинку")
    res = hf_space_call(HF_SPACES["img"], "/infer",
                        [prompt.strip(), 0, True, 1024, 1024, 4])
    img = res[0] if isinstance(res, list) and res else res
    return hf_download(HF_SPACES["img"], img, out_path)


def hf_image_to_video(image_path, prompt, out_path, say=None):
    """WAN 2.2 (HF Space, БЕЗ ключа): кадр → коротке AI-відео."""
    if not (image_path and os.path.isfile(image_path)):
        raise RuntimeError("Спершу картинка")
    base = HF_SPACES["vid"]
    img = hf_upload(base, image_path)
    res = hf_space_call(base, "/generate_video",
                        [img, (prompt or "").strip(), 6, "",
                         3.5, 1.0, 1.0, 42, True], timeout=1800)
    vid = res[0] if isinstance(res, list) and res else res
    return hf_download(base, vid, out_path)


def animate_images(images, out_path, w=1920, h=1080, per=3.0, fade=0.7, say=None):
    """Кен-Бернс у 4 напрямках + xfade-кросфейд (Волна 9, перевірено)."""
    if not images:
        raise RuntimeError("нема картинок")
    ff = ffmpeg_path()
    per = max(1.0, float(per or 3.0))
    fade = min(max(0.0, float(fade or 0.0)), per / 2.0)
    workdir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(workdir, exist_ok=True)
    segs = []
    try:
        for i, img in enumerate(images):
            if not (img and os.path.isfile(img)):
                continue
            seg = os.path.join(workdir, "_anim_{:03d}.mp4".format(i))
            frames = int(per * 25) + 1
            mode = i % 4
            if mode == 0:
                z = "min(zoom+0.0008,1.28)"
                x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
            elif mode == 1:
                z = "if(lte(zoom,1.0),1.30,max(zoom-0.0008,1.0))"
                x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
            elif mode == 2:
                z = "1.15"
                x, y = "(iw-iw/zoom)*(1-on/{})".format(frames), "ih/2-(ih/zoom/2)"
            else:
                z = "1.15"
                x, y = "(iw-iw/zoom)*on/{}".format(frames), "ih/2-(ih/zoom/2)"
            run([ff, "-y", "-hide_banner", "-nostdin", "-i", img,
                 "-vf", ("scale={}:{}:force_original_aspect_ratio=increase,crop={}:{},"
                         "zoompan=z='{}':x='{}':y='{}':d={}:s={}x{}:fps=25,"
                         "format=yuv420p").format(w, h, w, h, z, x, y, frames, w, h),
                 "-t", "{:.2f}".format(per),
                 "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", seg])
            segs.append(seg)
            if say:
                say("🎬 анімую кадр {}/{} (Кен-Бернс)…".format(i + 1, len(images)))
        if not segs:
            raise RuntimeError("Жодна картинка не анімувалась")
        if len(segs) == 1:
            shutil.copyfile(segs[0], out_path)
            return out_path
        if fade < 0.05:
            lst = os.path.join(workdir, "_anim_list.txt")
            with open(lst, "w", encoding="utf-8") as f:
                for s in segs:
                    f.write("file '{}'\n".format(s))
            run([ff, "-y", "-hide_banner", "-nostdin", "-f", "concat", "-safe", "0",
                 "-i", lst, "-c:v", "copy", out_path])
            try:
                os.remove(lst)
            except OSError:
                pass
            return out_path
        inputs = []
        for s in segs:
            inputs += ["-i", s]
        parts, off = [], per - fade
        for i in range(1, len(segs)):
            prev = "[0:v]" if i == 1 else "[x{}]".format(i - 1)
            parts.append("{}[{}:v]xfade=transition=fade:duration={:.2f}:offset={:.2f}[x{}]".format(
                prev, i, fade, off, i))
            off += per - fade
        parts.append("[x{}]format=yuv420p[v]".format(len(segs) - 1))
        run([ff, "-y", "-hide_banner", "-nostdin"] + inputs +
            ["-filter_complex", ";".join(parts), "-map", "[v]",
             "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", out_path])
        return out_path
    finally:
        for s in segs:
            try:
                os.remove(s)
            except OSError:
                pass


# --------------------------------------------- §5 ОЗВОЧКА (TTS)

_TTS_PAUSE = "\u2063\u2063\u2063"  # невидимий розділювач: пауза сценарію


def _expand_tts_pauses(lst):
    """«...»/«…» у сценарії — паузи автора → окремі шматки тиші по 700 мс."""
    out = []
    for ch in lst:
        for j, piece in enumerate(re.split(r"(\.{3,}|…+)", ch)):
            if j % 2:
                out.append(_TTS_PAUSE)
            elif piece.strip():
                out.append(piece.strip())
    while out and out[-1] == _TTS_PAUSE:
        out.pop()
    return out


def _tts_chunks(text, limit=500):
    """edge-tts обриває довгі тексти — ріжу по реченнях (наддовге — по словах)."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= limit:
        return _expand_tts_pauses([text])
    parts, cur = [], ""
    for sent in re.split(r"(?<=[.!?…])\s+", text):
        if len(sent) > limit:
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
    return _expand_tts_pauses([p.strip() for p in parts if p.strip()])


def _rm_parts(files):
    for q in files:
        try:
            os.remove(q)
        except OSError:
            pass


def sapi_tts(text, out_mp3, say):
    """План 1.5: системний голос Windows (PowerShell Speech) — без хмари.
    Голос системний (не Обраний edge), але відео генерується, а не падає."""
    wav = out_mp3 + ".wav"
    ps = ("Add-Type -AssemblyName System.Speech;"
          "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
          "$s.SetOutputToWaveFile('" + wav.replace("'", "''") + "');"
          "$s.Speak([Console]::In.ReadToEnd());"
          "$s.Dispose()")
    p = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       input=(text or "")[:3000], text=True,
                       encoding="utf-8", capture_output=True, timeout=300)
    if p.returncode != 0 or not os.path.isfile(wav) or os.path.getsize(wav) < 2000:
        raise RuntimeError("системний голос не озвучив")
    run([ffmpeg_path(), "-y", "-hide_banner", "-nostdin", "-i", wav,
         "-c:a", "libmp3lame", "-q:a", "4", out_mp3])
    try:
        os.remove(wav)
    except OSError:
        pass
    say("🖥 Озвучено системним голосом Windows (хмара мовчить)")
    return out_mp3


def silence_audio(out_mp3, seconds):
    """Останній ступінь драбини: тиша. Відео все одно збирається (sub працює)."""
    run([ffmpeg_path(), "-y", "-hide_banner", "-nostdin",
         "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", "{:.2f}".format(max(1.0, float(seconds))),
         "-c:a", "libmp3lame", "-q:a", "4", "-f", "mp3", out_mp3])
    return out_mp3


def tts_save(text, voice, out_mp3, say, rate_pct=0):
    """Озвучка-драбина: edge-tts шматками (паузи = 700 мс тиші, Волна 12) →
    системний голос Windows → тиша. Хмара 403 — генератор не вмирає."""
    ff = ffmpeg_path()
    chunks = _tts_chunks(text)
    for attempt in (1, 2):
        if edge_tts is None:
            break
        parts, ok = [], bool(chunks)
        for i, ch in enumerate(chunks):
            p = "{}.part{:03d}.mp3".format(out_mp3, i)  # Волна 12: .mp3 в кінці
            if ch == _TTS_PAUSE:
                run([ff, "-y", "-hide_banner", "-nostdin", "-f", "lavfi",
                     "-i", "anullsrc=r=24000:cl=mono", "-t", "0.7",
                     "-c:a", "libmp3lame", "-q:a", "4", "-f", "mp3", p])
                parts.append(p)
                continue
            try:
                asyncio.run(edge_tts.Communicate(
                    ch, voice, rate="{:+d}%".format(int(rate_pct or 0))).save(p))
                if os.path.exists(p) and os.path.getsize(p) > 500:
                    parts.append(p)
                else:
                    ok = False
                    break
            except Exception as e:
                say("ℹ️ edge-tts не відповів (спроба {}, шматок {} з {}): {}".format(
                    attempt, i + 1, len(chunks), str(e)[:120]))
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
                return out_mp3
            except Exception as e:
                say("ℹ️ Шматки не зшиваються ({}): ще спроба".format(str(e)[:100]))
        _rm_parts(parts)
    say("⚠️ Хмарна озвучка недоступна — пробую системний голос Windows…")
    try:
        return sapi_tts(text, out_mp3, say)
    except Exception as e:
        say("⚠️ Системний голос теж не вийшов ({}): кладу тишу — відео зберується".format(str(e)[:100]))
        words = len((text or "").split())
        return silence_audio(out_mp3, max(3.0, words / 2.4))


def concat_audio(mp3s, out_mp3):
    """Склеїти озвучки частин в один voice.mp3 (filter_complex concat)."""
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

# ------------------------------------------------------------ §6 СЦЕНАРІЙ

def script_bg_query(body):
    """Волна 11: РОЗУМНИЙ запит фону — стоп-слова укр/рос/анг геть, до 6
    змістових слів: фон влучає у ЗМІСТ частини, а не в зв'язки прози."""
    stop = set("""
    у і та й що як це не на з зі до по для є його їй її ним них він вона вони ми ви ти я
    нас нам цей ця це так там тут коли де чому потім також якщо але або чи від без
    за про при над під був була було були буде будуть мати має мають може можна
    треба тільки ще вже ось наприклад тобто свій свої свою вся всі дуже навіть щоб
    інше інший інших цьому цім
    это этот эта эти как что где когда зачем потом также если но или от без
    для про при под был была было будут может можно нужно только еще уже
    вот например свой свои все очень даже чтобы
    the a an of in on to and or is are was were be been being for with that this
    these those it its as at by from not you your we they he she his her their
    there here what which who whom how why when where will would can could should
    do does did have has had about into over under more most other some such only
    """.split())
    words, seen = [], set()
    for wd in re.sub(r"[^\w\s\-]", " ", (body or "")).split():
        wd = wd.strip("-_")
        lo = wd.lower()
        if len(wd) < 3 or lo in stop or lo in seen:
            continue
        seen.add(lo)
        words.append(wd)
        if len(words) >= 6:
            break
    return " ".join(words) if words else (body or "")[:40]


def parse_script(text):
    """Сценарій у частини: блоки розділені порожніми рядками. Керуючі рядки
    на початку частини: Пошук: (запит фону), Кліп: (твоє YouTube-відео),
    Тривалість: 12 (сек, озвучка підганяється темпом)."""
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
        if dur and not (2 <= dur <= 600):
            dur = None
        if not q:
            q = script_bg_query(body)
        scenes.append({"q": q, "text": body, "url": url, "dur": dur})
    return scenes


def script_from_theme(theme, say):
    """Режим Тема: безключовий мозок пише сценарій у керуючому форматі.
    Мозок мовчить — ЧЕСНИЙ шаблон (відео все одно генерується)."""
    theme = (theme or "").strip()
    if not theme:
        raise RuntimeError("Впиши тему або сценарій")
    say("🧠 Пишу сценарій за темою (безкоштовний онлайн-мозок)…")
    sysmsg = ("Ти — сценарист коротких захопливих YouTube-відео українською. "
              "Напиши сценарій з 3-5 частин. Частини розділи ПОРОЖНІМ РЯДКОМ. "
              "Перший рядок кожної частини — «Пошук: » + короткий запит англійською "
              "для пошуку фонового відео. Далі 2-4 речення живого енергійного тексту "
              "для озвучки. Без маркдауну, без нумерації, без зірок. Разом — до 90 секунд озвучки.")
    txt = llm_ask("Тема відео: " + theme, sysmsg, say, timeout=90)
    scenes = parse_script(txt)
    if scenes:
        say("🧠 Сценарій готовий: {} частин".format(len(scenes)))
        return scenes, "мозок"
    say("🧠 Мозок не відповів — збираю сценарій з простого шаблону (чесно: без НЛП)")
    q = script_bg_query(theme)
    tpl = [
        {"q": q + " closeup", "text": theme + ". Зараз покажу, чому це важливо і чому я звернув на це увагу.", "url": None, "dur": None},
        {"q": q, "text": "Розберімо детальніше. " + theme + " — тут є нюанси, про які майже ніхто не говорить, і саме вони вирішують все.", "url": None, "dur": None},
        {"q": q + " review", "text": "Якщо тобі було корисно — підпишись, і побачимось у наступному відео.", "url": None, "dur": None},
    ]
    return tpl, "шаблон"


# ------------------------------------------------------- §7 ФОН-ДРАБИНА

def scene_segment(clip, dur, w, h, workdir, idx, start=0.0):
    """Нормалізувати кліп під розмір і РІВНО dur секунд (зациклення/обрізка)."""
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
    """Останній ступінь драбини фону: живий градієнт — відео не без очок."""
    ff = ffmpeg_path()
    seg = os.path.join(workdir, "pseg{:02d}.mp4".format(idx))
    run([ff, "-y", "-hide_banner", "-nostdin",
         "-f", "lavfi", "-i", "gradients=s={0}x{1}:c0=0x0f2027:c1=0x2c5364:speed=0.03".format(int(w), int(h)),
         "-t", "{:.2f}".format(dur + 0.2),
         "-vf", "fps=25,setsar=1,format=yuv420p",
         "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", seg])
    return seg


def speed_fit(mp3, target, say):
    """Підігнати озвучку під цільову тривалість частини (Тривалість: N).
    Голос той самий, змінюється лише темп; поза 0.5–2.0 — не чіпаю."""
    target = max(2.0, float(target))
    d = audio_duration(mp3)
    ratio = d / target
    if abs(ratio - 1.0) < 0.04 or not (0.5 <= ratio <= 2.0):
        if say and abs(ratio - 1.0) >= 0.04:
            say("🎯 Ціль {:.0f} с надто далеко від озвучки ({:.1f} с) — лишаю як є".format(target, d))
        return mp3
    filters, r = [], ratio
    while r > 2.0:
        filters.append("atempo=2.0")
        r /= 2.0
    while r < 0.5:
        filters.append("atempo=0.5")
        r *= 2.0
    filters.append("atempo={:.4f}".format(r))
    out = mp3 + ".fit.mp3"
    run([ffmpeg_path(), "-y", "-hide_banner", "-nostdin", "-i", mp3,
         "-filter:a", ",".join(filters), "-c:a", "libmp3lame", "-q:a", "4", out])
    if say:
        say("🎯 Підігнав темп: {:.1f} с → {:.0f} с (голос природний)".format(d, target))
    return out


def script_photo_fallback(q, dur, w, h, workdir, i, say):
    """Ступінь «фото»: Openverse → до 3 фото → Кен-Бернс на тривалість частини.
    Стоки мовчать — AI-кадр Pollinations. Зовсім нічого — None (градієнт)."""
    imgs = []
    try:
        results, _err = openverse_images_search(q, 12, say)
    except Exception:
        results = []
    for r in (results or [])[:4]:
        if len(imgs) >= 3:
            break
        p = os.path.join(workdir, "scene{:02d}_p{}.jpg".format(i, len(imgs)))
        try:
            download_image(r["url"], p)
            imgs.append(p)
            append_credit(workdir, r.get("credit") or "🖼 фото Openverse")
        except Exception:
            pass
    if not imgs:
        say("🖼 Стоки мовчать — пробую AI-кадр (Pollinations, без ключа)…")
        p = os.path.join(workdir, "scene{:02d}_ai.jpg".format(i))
        try:
            pollinations_image(q + ", cinematic, photorealistic", p, w=w, h=h)
            imgs.append(p)
            append_credit(workdir, "🖼 AI-кадр — Pollinations (без ключа)")
        except Exception as e:
            say("ℹ️ AI-кадр не вийшов ({}): буде градієнт".format(str(e)[:100]))
    if not imgs:
        return None
    out = os.path.join(workdir, "scene{:02d}.mp4".format(i))
    animate_images(imgs, out, w=w, h=h, per=max(2.0, dur / max(len(imgs), 1)), fade=0.7, say=say)
    for p in imgs:
        try:
            os.remove(p)
        except OSError:
            pass
    return out


def script_ai_clip(q, dur, w, h, workdir, i, say):
    """Ступінь «AI-кліп» (перемикач 🎬 AI-кліпи): FLUX малює кадр → WAN 2.2
    оживляє. Публічні черги повільні — лише перші 4 частини; впав — драбина."""
    img = os.path.join(workdir, "scene{:02d}_flux.jpg".format(i))
    hf_image(q + ", cinematic, high detail", img)
    out = os.path.join(workdir, "scene{:02d}.mp4".format(i))
    hf_image_to_video(img, "slow cinematic camera movement, subtle natural motion, high quality", out, say)
    try:
        os.remove(img)
    except OSError:
        pass
    append_credit(workdir, "🎬 AI-кліп — FLUX.1-schnell + WAN 2.2 (HF Spaces, без ключа)")
    return out


def build_scene_bg(sc, dur, w, h, workdir, i, say, ai_clips=False):
    """Драбина фону ОДНІЄЇ частини — серце надійності 3.0:
    Кліп: → YouTube-пошук (до 3 проб) → фото → AI-кліп → градієнт.
    Кожен ступінь у credits.txt; повертає (файл, джерело)."""
    q = sc.get("q") or ""
    if ai_clips and i < 4:
        try:
            say("🎬 Частині {}: генерую AI-кліп (FLUX→WAN, без ключа)…".format(i + 1))
            out = script_ai_clip(q, dur, w, h, workdir, i, say)
            if out and os.path.isfile(out):
                return out, "ai-кліп"
        except Exception as e:
            say("ℹ️ AI-кліп не вийшов ({}): іду за звичайною драбиною".format(str(e)[:120]))
    if sc.get("url"):
        try:
            say("🎬 Частині {}: твоє відео з рядка Кліп:…".format(i + 1))
            clip = youtube_download(sc["url"], workdir, 1080, say, fixed_name="scene{:02d}_custom".format(i), max_sec=180)
            if clip and os.path.isfile(clip):
                return clip, "кліп автора"
        except Exception as e:
            say("ℹ️ Кліп: не завантажився ({}): шукаю за запитом".format(str(e)[:120]))
    if q:
        try:
            say("🔎 Шукаю на YouTube відео по темі частини: {}…".format(q))
            found, err = yt_search(q, 5, say)
        except Exception as e:
            found, err = [], str(e)[:120]
        for cand in (found or [])[:3]:
            dur_i = cand.get("dur") or 0
            if dur_i and (dur_i < 20 or dur_i > 7200):
                continue
            say("🎬 Беру у фон: {}".format(cand["title"][:70]))
            try:
                clip = youtube_download(cand["url"], workdir, 720, say,
                                        fixed_name="scene{:02d}_yt".format(i), max_sec=120)
                return clip, "YouTube: " + cand["title"][:60]
            except Exception as e:
                say("⚠️ Не завантажилось, пробую наступне: {}".format(str(e)[:120]))
        if err:
            say("ℹ️ YouTube пошук: {}".format(err))
    try:
        out = script_photo_fallback(q, dur, w, h, workdir, i, say)
        if out and os.path.isfile(out):
            return out, "фото/Кен-Бернс"
    except Exception as e:
        say("ℹ️ Фото-ступінь впав ({}): градієнт".format(str(e)[:120]))
    say("🖼 Частині {}: градієнтний фон (стоки і AI мовчали — чесно)".format(i + 1))
    return gradient_segment(dur, w, h, workdir, i), "градієнт"


# ------------------------------------------------------ §8 JSON-ТАЙМЛАЙН

def project_write(workdir, data):
    """project.json — таймлайн усього відео: сцени, запити, стани (Receipt)."""
    data = dict(data)
    data["version"] = VERSION
    data["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
    try:
        with open(os.path.join(workdir, "project.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def project_read(workdir):
    try:
        with open(os.path.join(workdir, "project.json"), encoding="utf-8") as f:
            j = json.load(f)
        return j if isinstance(j, dict) else {}
    except Exception:
        return {}


def find_resume_dir():
    """Найновіша незавершена генерація (project.json без done:true)."""
    try:
        dirs = [os.path.join(GEN_BASE, d) for d in os.listdir(GEN_BASE)
                if os.path.isdir(os.path.join(GEN_BASE, d))]
        for d in sorted(dirs, reverse=True):
            if os.path.isfile(os.path.join(d, "project.json")):
                p = project_read(d)
                if p and not p.get("done"):
                    return d
    except Exception:
        pass
    return None


# ------------------------------------------ §9 СУБТИТРИ, ОБКЛАДИНКА, РЕНДЕР

def make_srt_scenes(scenes, durs, workdir):
    """Субтитри: речення кожної частини розкладаються у її час (transcript-first)."""
    def fmt(t):
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        return "{:02d}:{:02d}:{:06.3f}".format(int(h), int(m), s).replace(".", ",")

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
            lines.append("{}\n{} --> {}\n{}\n".format(len(lines) + 1, fmt(t), fmt(end), s))
            t = end
        t0 += d
    with open(os.path.join(workdir, "sub.srt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _cover_draw(img, title):
    """Градієнт знизу + назва з обводкою (Волна 14: читається на будь-якому кадрі)."""
    from PIL import ImageDraw, ImageFont
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    gh = int(H * 0.45)
    for k in range(gh):
        d.line([(0, H - gh + k), (W, H - gh + k)],
               fill=(10, 10, 18, int(210 * (k + 1) / gh)))
    font, fs = None, max(24, int(W / 14))
    for fp in (r"C:\Windows\Fonts\segoeuib.ttf",
               r"C:\Windows\Fonts\arialbd.ttf",
               r"C:\Windows\Fonts\segoeui.ttf"):
        try:
            font = ImageFont.truetype(fp, fs)
            break
        except Exception:
            font = None
    if font is None:
        raise RuntimeError("системний шрифт не знайшовся")
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
        d.text(((W - tw) / 2, y), ln, font=font, fill=(255, 255, 255, 255),
               stroke_width=max(2, fs // 14), stroke_fill=(0, 0, 0, 200))
        y += lh
    return img


def make_cover(workdir, title, say):
    """Обкладинка з кадру готового відео + назва з обводкою. Pillow нема —
    просто кадр (fail-open)."""
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
        img = PILImage.open(tmp).convert("RGB")
        _cover_draw(img, title).save(cover, quality=90)
        say("📷 Обкладинка для YouTube: cover.jpg у робочій папці")
    except Exception as e:
        try:
            os.replace(tmp, cover)
            say("📷 Обкладинка без тексту (кадр) — " + str(e)[:80])
        except OSError:
            pass
    try:
        os.remove(tmp)
    except OSError:
        pass


def make_cover_from_image(src_img, title, out_path, say=None):
    """Обкладинка з AI-зображення (кнопка 🖼): FLUX малює фон — назва зверху."""
    try:
        if PILImage is None:
            raise RuntimeError("Pillow не знайшовся")
        img = PILImage.open(src_img).convert("RGB")
        _cover_draw(img, title).save(out_path, quality=90)
        if say:
            say("📷 Обкладинка: " + os.path.basename(out_path))
    except Exception as e:
        try:
            shutil.copyfile(src_img, out_path)
        except Exception:
            pass
        if say:
            say("⚠️ Обкладинка без тексту (копія) — " + str(e)[:80])
    return out_path


def cover_from_text(text, say):
    """Кнопка 🖼 «З цього — обкладинка»: FLUX малює → назва з обводкою.
    Вихід — у папці результатів (одна вставка: текст у полі — і все)."""
    text = (text or "").strip()
    if not text:
        raise RuntimeError("Впиши у поле тему або назву — з неї малюю обкладинку")
    os.makedirs(GEN_BASE, exist_ok=True)
    out = os.path.join(GEN_BASE, "cover_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg")
    tmp = os.path.join(GEN_BASE, "_cover_tmp.png")
    say("🖼 Малюю фон обкладинки (FLUX, без ключа)…")
    hf_image(text[:300] + ", vibrant, high detail, youtube thumbnail style", tmp)
    make_cover_from_image(tmp, text[:80], out, say)
    try:
        os.remove(tmp)
    except OSError:
        pass
    return out


def final_render(workdir, say, subs=True):
    """Фінал: фон-частини + voice.mp3 (+субтитри burned) → final.mp4 з
    +faststart (Волна 13) і нормалізацією гучності під YouTube (-16 LUFS)."""
    ff = ffmpeg_path()
    lst = os.path.join(workdir, "_segs.txt")
    with open(lst, "w", encoding="utf-8") as f:
        i = 0
        while True:
            seg = "pseg{:02d}.mp4".format(i)
            if not os.path.isfile(os.path.join(workdir, seg)):
                break
            f.write("file '{}'\n".format(seg))
            i += 1
    if i == 0:
        raise RuntimeError("жодної фон-частини — рендерити нічого")
    cmd = [ff, "-y", "-hide_banner", "-nostdin",
           "-f", "concat", "-safe", "0", "-i", lst,
           "-i", "voice.mp3",
           "-map", "0:v", "-map", "1:a"]
    if subs and os.path.isfile(os.path.join(workdir, "sub.srt")):
        cmd += ["-vf", SUB_STYLE]
    cmd += ["-c:v", "libx264", "-crf", "21", "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:a", "aac", "-b:a", "160k",
            "-shortest", "-movflags", "+faststart", "final.mp4"]
    say("🚀 Рендерю відео…")
    run(cmd, cwd=workdir)
    try:
        os.remove(lst)
    except OSError:
        pass
    return os.path.join(workdir, "final.mp4")


def qc_mini(workdir, say):
    """Міні-QC (Чесність): розмір, faststart, тривалість — звіт без прикрас."""
    p = os.path.join(workdir, "final.mp4")
    if not os.path.isfile(p):
        say("🛡 QC: final.mp4 нема — рендер не дійшов до кінця")
        return
    with open(p, "rb") as f:
        head = f.read(2 * 1024 * 1024)
    moov, mdat = head.find(b"moov"), head.find(b"mdat")
    if moov != -1 and (mdat == -1 or moov < mdat):
        say("🛡 QC: +faststart на місці — YouTube стартує швидко")
    else:
        say("🛡 QC: moov не на початку — варто перезібрати")
    try:
        d = audio_duration(p)
        if d < 5:
            say("🛡 QC: тривалість підозріло мала ({:.1f} с) — переглянь".format(d))
        else:
            say("🛡 QC: тривалість {:.1f} с, розмір {:.1f} МБ — ок".format(
                d, os.path.getsize(p) / 1048576))
    except Exception:
        pass


def seo_pack(workdir, theme, say):
    """SEO-пак для YouTube (назва/опис/теги) — мозок, а мовчить — простий
    чесний шаблон. Вихід: youtube-seo.txt."""
    txt = llm_ask(
        "Відео на тему: " + theme[:300] +
        "\nВидай ТІЛЬКИ JSON без маркдауну: {\"title\": ..., \"description\": ..., \"tags\": [\"...\"], \"comment\": ...}"
        + "\nВсе українською, теги — 12-15 штук, опис до 900 символів з закликом.",
        "Ти — YouTube-SEO-спеціаліст. Жодних пояснень, лише JSON.", say, timeout=90)
    title, desc, tags = theme[:90], "", []
    m = re.search(r"\{.*\}", txt, re.S)
    if m:
        try:
            j = json.loads(m.group(0))
            title = str(j.get("title") or title)[:95]
            desc = str(j.get("description") or "")[:900]
            tags = [str(t).strip() for t in (j.get("tags") or []) if str(t).strip()][:15]
        except Exception:
            pass
    if not desc:
        desc = theme + "\n\nПідпишись, щоб не пропустити наступне відео!"
        tags = [w for w in re.sub(r"[^\w\s]", " ", theme.lower()).split() if len(w) > 3][:12]
    with open(os.path.join(workdir, "youtube-seo.txt"), "w", encoding="utf-8") as f:
        f.write("НАЗВА:\n{}\n\nОПИС:\n{}\n\nТЕГИ:\n{}\n\nХЕШТЕГИ:\n{}\n\nПІДКАПРІВ:\n"
                "Розкажи у перших 2 годинах, як тобі відео — це підніме його в рекомендаціях.\n".format(
                    title, desc, ", ".join(tags),
                    " ".join("#" + re.sub(r"[^\w]", "", t) for t in tags[:5])))
    say("📈 SEO-пак: youtube-seo.txt у робочій папці")

# ------------------------------------------------- §10 ГОЛОВНИЙ ПАЙПЛАЙН

def stage_set(workdir, stage, say):
    """Прогрес-мапа: start ▸ script ▸ voice ▸ subtitles ▸ background ▸ render ▸ done."""
    try:
        with open(os.path.join(workdir, "stage.txt"), "w", encoding="utf-8") as f:
            f.write(stage)
    except OSError:
        pass
    say("🗺 " + " ▸ ".join("[" + s + "]" if s == stage else s for s in STAGES))


def generate_video(source_text, mode, voice_label, size_label, subs=True,
                   cover=True, ai_clips=False, say=None, resume_dir=None):
    """(тема | сценарій) → озвучка → субтитри → фон-драбина → рендер → чек.
    Кожен крок пишеться у project.json: впав запуск — Resume підхопить."""
    say = say or (lambda m: print(m))
    # 1) Сценарій — джерело істини (transcript-first).
    # Resume: частини читаю з project.json (таймлайн), а не з текстового поля.
    resume = bool(resume_dir and os.path.isdir(resume_dir))
    scenes, theme, src = None, "", ""
    if resume:
        saved = project_read(resume_dir).get("scenes") or []
        if saved:
            scenes = [{"q": s.get("q"), "text": s.get("text"),
                       "url": s.get("url"),
                       "dur": s.get("dur_target") or s.get("dur")}
                      for s in saved if (s or {}).get("text")]
            theme = project_read(resume_dir).get("theme") or (scenes[0]["text"] or "")[:80]
            src = "project.json (Resume)"
    if scenes is None:
        if mode == "theme":
            scenes, src = script_from_theme(source_text, say)
            theme = source_text.strip()[:80]
        else:
            scenes = parse_script(source_text)
            if not scenes:
                raise RuntimeError("Сценарій порожній — розділи частини порожнім рядком")
            theme = (scenes[0]["text"] or "")[:80]
            src = "твій сценарій"
    if len(scenes) > SCRIPT_MAX_SCENES:
        say("⚠️ Частин {} — беру перші {}".format(len(scenes), SCRIPT_MAX_SCENES))
        scenes = scenes[:SCRIPT_MAX_SCENES]

    # 2) Робоча папка
    if resume:
        workdir = resume_dir
        say("🔁 Resume: продовжую впалу генерацію у старій папці")
    else:
        workdir = os.path.join(GEN_BASE, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(workdir, exist_ok=True)
    w, h = SIZES.get(size_label, (1920, 1080))
    voice = VOICES.get(voice_label, "uk-UA-OstapNeural")

    # 3) ЦІНА ПЕРЕД СПЕНДОМ — чесна оцінка часу ДО старту
    words = sum(len(sc["text"].split()) for sc in scenes)
    est_voice = words / 2.3
    est_bg = len(scenes) * 30
    est_total = est_voice + est_bg + 60
    say("⏱ Ціна перед стартом: {} сл → озвучка ~{:.0f} с • фон ~{:.0f} с • "
        "рендер ~1 хв — разом ОРІЄНТОВНО {:.0f} хв".format(
            words, est_voice, est_bg, est_total / 60))
    say("📋 Джерело сценарію: {} • частин: {}".format(src, len(scenes)))

    project = project_read(workdir) if resume else {}
    project.update({"mode": mode, "theme": theme, "voice": voice_label,
                    "size": size_label, "subs": bool(subs), "cover": bool(cover),
                    "scenes": [{"q": sc["q"], "text": sc["text"],
                                "url": sc.get("url"), "dur_target": sc.get("dur")}
                               for sc in scenes]})
    project_write(workdir, project)

    say("🔍 Перевіряю ffmpeg (якщо немає — встановлю сам, один раз)…")
    ensure_ffmpeg(say)
    say("🎬 Частин у сценарії: {}".format(len(scenes)))
    stage_set(workdir, "script", say)
    stage_set(workdir, "voice", say)

    # 4) Озвучка частин (Resume: готові voice_XX.mp3 не переробовуються)
    say("🎙️ Озвучую частини голосом {}…".format(voice_label))
    mp3s, durs = [], []
    for i, sc in enumerate(scenes):
        m = os.path.join(workdir, "voice_{:02d}.mp3".format(i))
        if resume and os.path.isfile(m) and os.path.getsize(m) > 20000:
            say("🔁 Частину {} вже озвучено раніше — не переробляю".format(i + 1))
        else:
            tts_save(sc["text"], voice, m, say)
            if sc.get("dur"):
                try:
                    m = speed_fit(m, sc["dur"], say)
                except Exception as e:
                    say("ℹ️ Темп не підігнався ({}): лишаю природний".format(str(e)[:100]))
        mp3s.append(m)
        durs.append(audio_duration(m))
        say("ℹ️ Частина {}/{}: {:.1f} с".format(i + 1, len(scenes), durs[-1]))
    concat_audio(mp3s, os.path.join(workdir, "voice.mp3"))

    # 5) Субтитри — з тексту сценарію (не з повітря)
    stage_set(workdir, "subtitles", say)
    sub_path = os.path.join(workdir, "sub.srt")
    if not (resume and os.path.isfile(sub_path)):
        make_srt_scenes(scenes, durs, workdir)
    say("💬 Субтитри готові")

    # 6) Фон-драбина кожної частини (Resume: готові psegXX не переробовуються)
    stage_set(workdir, "background", say)
    bg_sources = []
    for i, sc in enumerate(scenes):
        seg = os.path.join(workdir, "pseg{:02d}.mp4".format(i))
        if resume and os.path.isfile(seg) and os.path.getsize(seg) > 100000:
            say("🔁 Фон частини {} вже готовий — не переробляю".format(i + 1))
            bg_sources.append("з минулого запуску")
            continue
        raw, source = build_scene_bg(sc, durs[i] + 0.05, w, h, workdir, i, say, ai_clips=ai_clips)
        if source != "градієнт":
            scene_segment(raw, durs[i], w, h, workdir, i)
            try:
                if raw != seg and os.path.isfile(raw) and "scene" in os.path.basename(raw):
                    os.remove(raw)
            except OSError:
                pass
        else:
            try:
                if os.path.isfile(raw) and raw != seg:
                    os.replace(raw, seg)
            except OSError:
                pass
        bg_sources.append(source)
        project["bg_{}".format(i)] = source
        project_write(workdir, project)

    # 7) Рендер: частини + голос + субтитри → final.mp4 (+faststart)
    stage_set(workdir, "render", say)
    final = final_render(workdir, say, subs=subs)

    # 8) Чек і обкладинка, SEO
    qc_mini(workdir, say)
    if cover:
        make_cover(workdir, theme, say)
    try:
        seo_pack(workdir, theme, say)
    except Exception as e:
        say("ℹ️ SEO-пак не зібрався ({}): не критично".format(str(e)[:100]))

    project["done"] = True
    project["final"] = final
    project["bg_sources"] = bg_sources
    project["durs"] = [round(d, 2) for d in durs]
    project["total"] = round(sum(durs), 2)
    project_write(workdir, project)
    say("📋 Маніфест генерації (project.json) — чек усього відео: джерела, тривалості, фони")

    stage_set(workdir, "done", say)
    open_folder(workdir)
    say("✅ ГОТОВО: {}".format(final))
    return final


# ------------------------------------------------------------- §11 ПЕРЕКЛАД

def libre_translate(text, target, timeout=25):
    """LibreTranslate — публічні дзеркала без ключів (драбина інстансів).
    Всі мовчать — ("", "") і викликач іде на драбину LLM (fail-open)."""
    for base in LIBRE_INSTANCES:
        try:
            r = requests.post(base.rstrip("/") + "/translate",
                              json={"q": str(text or "")[:4000],
                                    "source": "auto", "target": str(target or "en"),
                                    "format": "text"},
                              timeout=timeout, headers={"User-Agent": WEB_UA})
            if r.status_code == 200:
                j = r.json()
                if j.get("translatedText"):
                    return str(j["translatedText"]), base
        except Exception:
            continue
    return "", ""


def translate_srt_file(srt_path, lang, say):
    """Переклад .srt: LibreTranslate → LLM-драбина. Таймінги НЕ чіпаю,
    лише текст; вихід — <ім'я>_<мова>.srt поруч з оригіналом."""
    if not srt_path or not os.path.isfile(srt_path):
        say("🌐 Спершу обери файл .srt 🙂")
        return None
    lang = (lang or "en").strip().lower()[:5] or "en"
    with open(srt_path, "r", encoding="utf-8", errors="ignore") as fh:
        raw = fh.read()
    blocks = [b for b in re.split(r"\n\s*\n", raw.strip()) if b.strip()][:200]
    if not blocks:
        say("🌐 У файлі нема блоків субтитрів")
        return None
    say("🌐 Перекладаю {} блоків субтитрів на {}…".format(len(blocks), lang))
    out_blocks, via = [], ""
    for b in blocks:
        lines = b.split("\n")
        text_idx = 2 if len(lines) > 2 and "-->" in lines[1] else None
        if text_idx is None:
            out_blocks.append(b)
            continue
        txt = "\n".join(lines[2:])
        tr, inst = libre_translate(txt, lang)
        if tr:
            via = via or "LibreTranslate (" + inst.replace("https://", "") + ")"
        else:
            tr = llm_ask("Переклади на мову {}: {}".format(lang, txt), None, say, timeout=45)
            via = via or "LLM-драбина"
        out_blocks.append("\n".join(lines[:2] + [(tr or txt).strip()]))
    out_path = os.path.splitext(srt_path)[0] + "_" + lang + ".srt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(out_blocks) + "\n")
    say("🌐 Готово: {} (через {})".format(os.path.basename(out_path), via or "без перекладу"))
    return out_path


# ------------------------------------------------------------- §12 АВАТАР

def avatar_video(photo, audio, out_path, say=None):
    """Аватар-ведучий без ключів і GPU: фото оживляється Кен-Бернсом і звучить
    твоїм аудіо. Чесно: ліпсинку губ нема (це GPU-моделі DUIX/SadTalker)."""
    if not (photo and os.path.isfile(photo)):
        raise RuntimeError("Спершу обери фото ведучого")
    if not (audio and os.path.isfile(audio)):
        raise RuntimeError("Спершу обери аудіо з голосом")
    ensure_ffmpeg(say)
    workdir = os.path.dirname(os.path.abspath(out_path))
    dur = audio_duration(audio) or 5.0
    seg = os.path.join(workdir, "_avatar_seg.mp4")
    animate_images([photo], seg, per=max(dur, 1.0), fade=0.0, say=say)
    run([ffmpeg_path(), "-y", "-hide_banner", "-nostdin", "-i", seg, "-i", audio,
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20",
         "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-shortest",
         "-movflags", "+faststart", out_path], cwd=workdir)
    try:
        os.remove(seg)
    except OSError:
        pass
    return out_path


# ------------------------------------------------------------------ §13 GUI

def console_mode():
    """GUI нема (customtkinter не встановлено) — консольний режим, чесно."""
    print("customtkinter не знайдено — працюю в консольному режимі.")
    print("Режим (1 — тема, 2 — сценарій):")
    mode = "theme" if input().strip() != "2" else "scenario"
    print("Встав текст (кінець — порожній рядок):")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            break
        lines.append(line)
    text = "\n".join(lines)
    try:
        generate_video(text, mode, "Остап", "1080p", say=print)
    except Exception as e:
        print("❌ " + str(e))


def smoke_mode():
    """Смоук-тест (--smoke): перевірка збірки без GUI — для GitHub Actions.
    Генерує коротке відео безключовим шляхом, пише smoke-log.txt,
    виходить із кодом 0 (успіх) / 1 (невдача)."""
    log_path = os.path.join(APP_DIR, "smoke-log.txt")
    lf = open(log_path, "w", encoding="utf-8")

    def say(msg):
        line = str(msg)
        try:
            print(line)
        except Exception:
            pass
        try:
            lf.write(line + "\n")
            lf.flush()
        except Exception:
            pass

    code = 1
    try:
        say("🔍 Смоук-тест 3.0: генерація без GUI…")
        final = generate_video("Перевірка збірки генератора", "theme", "Остап", "720p",
                               subs=True, cover=False, ai_clips=False, say=say)
        if final and os.path.isfile(final):
            say("SMOKE OK: " + str(final))
            code = 0
        else:
            say("SMOKE FAILED: final.mp4 не створено")
    except SystemExit:
        lf.close()
        raise
    except Exception as e:
        say("SMOKE FAILED: " + str(e)[:2000])
    lf.close()
    sys.exit(code)


def app_main():
    if ctk is None:
        console_mode()
        return
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("Генератор відео 3.0")
    root.geometry("920x680")
    root.minsize(760, 560)
    sayq = queue.Queue()

    def say(msg):
        sayq.put(str(msg))

    def poll():
        try:
            while True:
                msg = sayq.get_nowait()
                log.insert("end", msg + "\n")
                log.see("end")
        except queue.Empty:
            pass
        root.after(150, poll)

    top = ctk.CTkFrame(root, fg_color="transparent")
    top.pack(fill="x", padx=16, pady=(12, 4))
    ctk.CTkLabel(top, text="Генератор відео 3.0", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
    mode_seg = ctk.CTkSegmentedButton(top, values=["💡 Тема", "🎬 Сценарій"])
    mode_seg.set("💡 Тема")
    mode_seg.pack(side="right")

    text_box = ctk.CTkTextbox(root, height=200)
    text_box.pack(fill="both", expand=True, padx=16, pady=8)

    opts = ctk.CTkFrame(root, fg_color="transparent")
    opts.pack(fill="x", padx=16)
    ctk.CTkLabel(opts, text="Голос:").pack(side="left", padx=(0, 4))
    voice_menu = ctk.CTkOptionMenu(opts, values=list(VOICES), width=150)
    voice_menu.set("Остап")
    voice_menu.pack(side="left", padx=(0, 12))
    ctk.CTkLabel(opts, text="Розмір:").pack(side="left", padx=(0, 4))
    size_menu = ctk.CTkOptionMenu(opts, values=list(SIZES), width=140)
    size_menu.set("1080p")
    size_menu.pack(side="left", padx=(0, 12))
    subs_var = ctk.BooleanVar(value=True)
    ctk.CTkCheckBox(opts, text="Субтитри", variable=subs_var, width=90).pack(side="left", padx=(0, 6))
    cover_var = ctk.BooleanVar(value=True)
    ctk.CTkCheckBox(opts, text="Обкладинка", variable=cover_var, width=110).pack(side="left", padx=(0, 6))
    ai_var = ctk.BooleanVar(value=False)
    ctk.CTkCheckBox(opts, text="🎬 AI-кліпи", variable=ai_var, width=110).pack(side="left")

    go_btn = ctk.CTkButton(root, text="🚀 ЗГЕНЕРУВАТИ", height=42,
                           font=ctk.CTkFont(size=16, weight="bold"),
                           command=lambda: on_generate(None))
    go_btn.pack(fill="x", padx=16, pady=(8, 4))

    tools = ctk.CTkFrame(root, fg_color="transparent")
    tools.pack(fill="x", padx=16, pady=2)
    ctk.CTkButton(tools, text="🔁 Resume", width=110, command=on_resume).pack(side="left", padx=(0, 6))
    ctk.CTkButton(tools, text="🖼 Обкладинка", width=120, command=on_cover).pack(side="left", padx=(0, 6))
    ctk.CTkButton(tools, text="🌐 Переклад SRT", width=130, command=on_translate).pack(side="left", padx=(0, 6))
    ctk.CTkButton(tools, text="🎭 Аватар", width=100, command=on_avatar).pack(side="left")

    log = ctk.CTkTextbox(root, height=220)
    log.pack(fill="both", expand=True, padx=16, pady=(6, 12))
    say("Вітаю! Впиши тему (або перемкни на Сценарій і встав свій) — і тисни ЗГЕНЕРУВАТИ.")
    say("Фон шукається за змістом кожної частини; все без ключів, з драбиною запасних ступенів.")

    busy = threading.Semaphore(1)

    def worker(fn):
        if not busy.acquire(blocking=False):
            say("⏳ Уже генерую — дочекайся завершення")
            return
        go_btn.configure(state="disabled")

        def run_and_unlock():
            try:
                fn()
            except Exception as e:
                say("❌ Помилка: " + str(e)[:400])
            finally:
                busy.release()
                try:
                    go_btn.configure(state="normal")
                except Exception:
                    pass
        threading.Thread(target=run_and_unlock, daemon=True).start()

    def on_generate(resume_dir):
        mode = "theme" if mode_seg.get().startswith("💡") else "scenario"
        text = text_box.get("1.0", "end").strip()
        if not text:
            say("⚠️ Поле порожнє — впиши тему або сценарій")
            return
        worker(lambda: generate_video(
            text, mode, voice_menu.get(), size_menu.get(),
            subs=subs_var.get(), cover=cover_var.get(), ai_clips=ai_var.get(),
            say=say, resume_dir=resume_dir))

    def on_resume():
        d = find_resume_dir()
        if not d:
            say("🔁 Нема впалих генерацій — усі завершені")
            return
        say("🔁 Знайшов незавершену генерацію: {}".format(os.path.basename(d)))
        worker(lambda: generate_video("", "scenario", voice_menu.get(), size_menu.get(),
                                      subs=subs_var.get(), cover=cover_var.get(),
                                      ai_clips=ai_var.get(), say=say, resume_dir=d))

    def on_cover():
        text = text_box.get("1.0", "end").strip()
        worker(lambda: cover_from_text(text, say) and open_folder(GEN_BASE))

    def on_translate():
        from tkinter import filedialog, simpledialog
        p = filedialog.askopenfilename(title="Обери .srt", filetypes=[("Субтитри", "*.srt")])
        if not p:
            return
        lang = simpledialog.askstring("Мова", "Код мови (en, ru, es, de…):", initialvalue="en")
        worker(lambda: translate_srt_file(p, lang, say))

    def on_avatar():
        from tkinter import filedialog
        photo = filedialog.askopenfilename(title="Фото ведучого",
                                           filetypes=[("Зображення", "*.jpg *.jpeg *.png")])
        if not photo:
            return
        audio = filedialog.askopenfilename(title="Аудіо з голосом",
                                           filetypes=[("Аудіо", "*.mp3 *.wav *.m4a")])
        if not audio:
            return
        os.makedirs(GEN_BASE, exist_ok=True)
        out = os.path.join(GEN_BASE, "avatar_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".mp4")

        def do():
            say("🎭 Оживляю фото і накладаю голос…")
            avatar_video(photo, audio, out, say)
            say("✅ Аватар: {}".format(os.path.basename(out)))
            open_folder(GEN_BASE)
        worker(do)

    poll()
    root.mainloop()


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        smoke_mode()
    else:
        app_main()
📋 КОПІЮВАТИ ВЕСЬ КОД (app.py)
✅ Якщо збірка після вставки впаде — у Issues зʼявиться звіт 💥 з логом смоук
