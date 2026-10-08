# -*- coding: utf-8 -*-
"""Генератор відео з запиту: озвучка edge-tts + відеокліпи Openverse + субтитри (ffmpeg). UI в стилі iOS (CustomTkinter)."""
import asyncio
import os
import queue
import re
import subprocess
import sys
import threading
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
TOOLS_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local", "VideoGenerator")
YTDLP_EXE = os.path.join(TOOLS_DIR, "yt-dlp.exe")
YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
YT_OUT_DIR = os.path.join(os.path.expanduser("~"), "Videos", "YouTube")
MERGE_OUT_DIR = os.path.join(os.path.expanduser("~"), "Videos", "Compiled")
APP_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
UA_STRING = "VideoGenerator/1.1 (https://github.com/khomyak75roman-dotcom/video-generator)"


def ffmpeg_path():
    local = os.path.join(APP_DIR, "ffmpeg.exe")
    return local if os.path.exists(local) else "ffmpeg"


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


def youtube_download(url, outdir, height, say, fixed_name=None):
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


def generate_video(query, voice_label, size_str, music, say, on_workdir=None, yt_url="", bg_files=None):
    """Повний цикл генерації. say — колбек журналу. Повертає робочу папку."""
    base = os.path.join(os.path.expanduser("~"), "Videos", "Generated")
    workdir = os.path.join(base, datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + re.sub(r'[^\w-]', '_', query[:30]))
    os.makedirs(workdir, exist_ok=True)
    if on_workdir:
        on_workdir(workdir)
    ff = ffmpeg_path()
    w, h = size_str.split(" ")[0].split("x")
    say(f"▶️ Запит: {query}")
    say("📁 Робоча папка створена")

    text = narration_for(query)
    voice = VOICES[voice_label]
    say(f"🎙️ Озвучую голосом {voice_label}…")
    asyncio.run(edge_tts.Communicate(text, voice).save(os.path.join(workdir, "voice.mp3")))

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
    """Інтерфейс у стилі iOS: темний фон, заокруглені картки, синій акцент."""

    BG = "#1C1C1E"      # iOS: основний темний фон
    CARD = "#2C2C2E"    # iOS: картка
    ACCENT = "#0A84FF"  # iOS: синій акцент
    MUTED = "#8E8E93"   # iOS: приглушений текст

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Генератор відео")
        self.root.geometry("760x1010")
        self.root.configure(fg_color=self.BG)
        self.q = queue.Queue()
        self.workdir = None
        self.merge_files = []
        self._build()
        self.root.after(150, self._poll)

    def _card(self, master, **pack):
        card = ctk.CTkFrame(master, fg_color=self.CARD, corner_radius=18)
        card.pack(**pack)
        return card

    def _build(self):
        # Великий заголовок як в iOS
        ctk.CTkLabel(self.root, text="🎬  Відео",
                     font=ctk.CTkFont(family="Segoe UI", size=34, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", padx=20, pady=(18, 0))
        ctk.CTkLabel(self.root, text="Опиши тему — зроблю відео з озвучкою та субтитрами",
                     font=ctk.CTkFont(family="Segoe UI", size=14),
                     text_color=self.MUTED).pack(anchor="w", padx=20, pady=(0, 4))

        # — Картка: запит —
        qc = self._card(self.root, fill="x", padx=20, pady=(12, 4))
        ctk.CTkLabel(qc, text="Твій запит",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        qrow = ctk.CTkFrame(qc, fg_color="transparent")
        qrow.pack(fill="x", padx=16, pady=(0, 4))
        self.query = ctk.CTkTextbox(qrow, height=110,
                                    font=ctk.CTkFont(family="Segoe UI", size=14),
                                    wrap="word", fg_color=self.BG)
        self.query.pack(side="left", fill="both", expand=True)
        ctk.CTkButton(qrow, text="📋 Вставити", width=100, height=34,
                      corner_radius=17, fg_color=self.ACCENT,
                      font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.paste_query).pack(side="left", padx=(8, 0))
        # Вставка скопійованого тексту: Ctrl+V, Shift+Insert
        for seq in ("<Control-v>", "<Control-V>", "<Shift-Insert>"):
            self.query.bind(seq, self._paste_event)
        ctk.CTkLabel(qc, text="Ctrl+V теж працює",
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=self.MUTED).pack(anchor="e", padx=16, pady=(0, 10))

        # — Картка: голос —
        vc = self._card(self.root, fill="x", padx=20, pady=4)
        ctk.CTkLabel(vc, text="🎙 Голос озвучення",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        self.voice = ctk.CTkSegmentedButton(vc, values=list(VOICES),
                                            font=ctk.CTkFont(family="Segoe UI", size=13),
                                            selected_color=self.ACCENT,
                                            selected_hover_color=self.ACCENT)
        self.voice.set("Остап")
        self.voice.pack(fill="x", padx=16, pady=(0, 14))

        # — Картка: розмір —
        zc = self._card(self.root, fill="x", padx=20, pady=4)
        ctk.CTkLabel(zc, text="📐 Розмір відео",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        self.size = ctk.CTkSegmentedButton(zc, values=list(SIZES),
                                           font=ctk.CTkFont(family="Segoe UI", size=13),
                                           selected_color=self.ACCENT,
                                           selected_hover_color=self.ACCENT)
        self.size.set("720p")
        self.size.pack(fill="x", padx=16, pady=(0, 14))

        # — Картка: музика —
        mc = self._card(self.root, fill="x", padx=20, pady=4)
        ctk.CTkLabel(mc, text="🎵 Фонова музика (не обов'язково)",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        mrow = ctk.CTkFrame(mc, fg_color="transparent")
        mrow.pack(fill="x", padx=16, pady=(0, 12))
        self.music_lbl = ctk.CTkLabel(mrow, text="Не обрано — буде лише голос",
                                      font=ctk.CTkFont(family="Segoe UI", size=13),
                                      text_color=self.MUTED, anchor="w")
        self.music_lbl.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(mrow, text="Обрати файл…", width=120, height=34,
                      corner_radius=17, fg_color="#3A3A3C",
                      hover_color="#48484A", font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.pick_music).pack(side="left")

        # — Картка: YouTube —
        yc = self._card(self.root, fill="x", padx=20, pady=4)
        ctk.CTkLabel(yc, text="▶️ Завантажити з YouTube",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        yrow = ctk.CTkFrame(yc, fg_color="transparent")
        yrow.pack(fill="x", padx=16, pady=(0, 6))
        self.yt_url = ctk.CTkEntry(yrow, placeholder_text="Посилання на відео (https://youtube.com/…)",
                                   height=36, font=ctk.CTkFont(family="Segoe UI", size=13))
        self.yt_url.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(yrow, text="⬇️ Завантажити", width=120, height=34,
                      corner_radius=17, fg_color="#3A3A3C",
                      hover_color="#48484A", font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.download_yt).pack(side="left", padx=(8, 0))
        self.yt_q = ctk.CTkSegmentedButton(yc, values=list(YT_QUALITY),
                                           font=ctk.CTkFont(family="Segoe UI", size=13),
                                           selected_color=self.ACCENT,
                                           selected_hover_color=self.ACCENT)
        self.yt_q.set("720p")
        self.yt_q.pack(fill="x", padx=16, pady=(0, 4))
        self.yt_bg = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(yc, text="Використати це відео як фон мого ролика",
                      variable=self.yt_bg,
                      font=ctk.CTkFont(family="Segoe UI", size=12),
                      progress_color=self.ACCENT).pack(anchor="w", padx=16, pady=(0, 12))

        # — Картка: компіляція з кількох відео —
        gc = self._card(self.root, fill="x", padx=20, pady=4)
        ctk.CTkLabel(gc, text="🎞 Компіляція з кількох відео",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        self.merge_lbl = ctk.CTkLabel(gc, text="Не обрано жодного відео",
                                      font=ctk.CTkFont(family="Segoe UI", size=12),
                                      text_color=self.MUTED, anchor="w")
        self.merge_lbl.pack(fill="x", padx=16, pady=(0, 4))
        grow = ctk.CTkFrame(gc, fg_color="transparent")
        grow.pack(fill="x", padx=16, pady=(0, 6))
        ctk.CTkButton(grow, text="➕ Додати відео…", height=34,
                      corner_radius=17, fg_color="#3A3A3C", hover_color="#48484A",
                      font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.pick_merge_files).pack(side="left")
        ctk.CTkButton(grow, text="✖️ Очистити", width=100, height=34,
                      corner_radius=17, fg_color="transparent", border_width=1,
                      border_color="#48484A", hover_color=self.CARD,
                      font=ctk.CTkFont(family="Segoe UI", size=12),
                      command=self.clear_merge_files).pack(side="left", padx=(8, 0))
        ctk.CTkButton(grow, text="🎞 Зшити в одне", height=34,
                      corner_radius=17, fg_color=self.ACCENT, hover_color="#3395FF",
                      font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.merge_now).pack(side="right")
        self.merge_bg = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(gc, text="Використати ці відео як фон мого ролика",
                      variable=self.merge_bg,
                      font=ctk.CTkFont(family="Segoe UI", size=12),
                      progress_color=self.ACCENT).pack(anchor="w", padx=16, pady=(0, 12))

        # — Головна кнопка-пігулка —
        self.btn = ctk.CTkButton(self.root, text="🎬  ЗГЕНЕРУВАТИ ВІДЕО",
                                 height=52, corner_radius=26,
                                 font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                 fg_color=self.ACCENT,
                                 hover_color="#3395FF",
                                 command=self.start)
        self.btn.pack(fill="x", padx=20, pady=(12, 4))

        self.bar = ctk.CTkProgressBar(self.root, mode="indeterminate",
                                      progress_color=self.ACCENT)
        self.bar.pack(fill="x", padx=20)
        self.bar.set(0)

        ctk.CTkButton(self.root, text="📂 Відкрити папку з результатом",
                      height=34, corner_radius=17, fg_color="transparent",
                      border_width=1, border_color="#48484A",
                      hover_color=self.CARD,
                      font=ctk.CTkFont(family="Segoe UI", size=13),
                      command=self.open_folder).pack(anchor="e", padx=20, pady=6)

        # — Картка: журнал —
        lc = self._card(self.root, fill="both", expand=True, padx=20, pady=(2, 16))
        ctk.CTkLabel(lc, text="Журнал",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(12, 2))
        self.log = ctk.CTkTextbox(lc, state="disabled",
                                   font=ctk.CTkFont(family="Segoe UI", size=12),
                                   wrap="word", fg_color=self.BG)
        self.log.pack(fill="both", expand=True, padx=16, pady=(0, 16))

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
            p = youtube_download(url, YT_OUT_DIR, YT_QUALITY[self.yt_q.get()], self.say)
            self.say("✅ Готово: " + p)
            self.say("📂 Файл у папці Відео\\YouTube")
        except Exception as e:
            self.say("❌ " + str(e)[:300])
        finally:
            self.q.put(None)

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
            if getattr(self, "yt_bg", None) and self.yt_bg.get() and self.yt_url.get().strip():
                yt = self.yt_url.get().strip()
            files = None
            if getattr(self, "merge_bg", None) and self.merge_bg.get() and self.merge_files:
                files = list(self.merge_files)
            generate_video(query, self.voice.get(), SIZES[self.size.get()],
                           getattr(self, "music_path", "").strip(), self.say,
                           on_workdir=lambda wd: setattr(self, "workdir", wd),
                           yt_url=yt, bg_files=files)
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
