# -*- coding: utf-8 -*-
"""Генератор відео з запиту: озвучка edge-tts + фон + субтитри (ffmpeg)."""
import asyncio
import os
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

import edge_tts
import requests

VOICES = {
    "Остап (укр, чоловічий)": "uk-UA-OstapNeural",
    "Поліна (укр, жіночий)": "uk-UA-PolinaNeural",
    "Christopher (англ)": "en-US-ChristopherNeural",
    "Jenny (англ)": "en-US-JennyNeural",
}
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
APP_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))


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


def fetch_pexels_background(query, workdir):
    """Стокове відео з Pexels, якщо заданий PEXELS_API_KEY. Інакше — Openverse/градієнт."""
    if PEXELS_KEY:
        try:
            r = requests.get(
                "https://api.pexels.com/videos/search",
                params={"query": query, "per_page": 5},
                headers={"Authorization": PEXELS_KEY}, timeout=20)
            files = [f for v in r.json().get("videos", []) for f in v.get("video_files", [])]
            files = [f for f in files if f.get("width", 0) >= 1280] or files
            if files:
                best = max(files, key=lambda f: f.get("width", 0))
                with requests.get(best["link"], stream=True, timeout=60) as d, \
                     open(os.path.join(workdir, "bg.mp4"), "wb") as out:
                    for chunk in d.iter_content(1 << 16):
                        out.write(chunk)
                return os.path.join(workdir, "bg.mp4")
        except Exception:
            pass
    return None  # fallback: Openverse або градієнт


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
        urls = [it.get("url") for it in r.json().get("results", []) if it.get("url")][:count]
        if not urls:
            return None, "Openverse: нічого не знайшов за запитом"
        paths = []
        for i, u in enumerate(urls):
            p = os.path.join(workdir, "img{}.jpg".format(i))
            with requests.get(u, timeout=30, headers={"User-Agent": "VideoGenerator/1.0"}) as d:
                d.raise_for_status()
                with open(p, "wb") as out:
                    for chunk in d.iter_content(65536):
                        out.write(chunk)
            paths.append(p)
        return (paths, None) if paths else (None, "Openverse: зображення не завантажились")
    except Exception as e:
        return None, "Openverse: {}".format(e)


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


def generate_video(query, voice_label, size_str, music, say, on_workdir=None):
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

    bg = fetch_pexels_background(query, workdir)
    if not bg:
        say("Шукаю зображення в Openverse (без API-ключа)...")
        imgs, reason = fetch_openverse_images(query, workdir)
        if imgs:
            say("🖼️ Знайдено зображень: " + str(len(imgs)) + " (Openverse)")
            bg = build_bg_from_images(imgs, dur, w, h, workdir)
        else:
            say("⚠️ " + (reason or "Openverse недоступній") + " — буде градієнтний фон")
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
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎬 Генератор відео")
        self.root.geometry("640x560")
        self.q = queue.Queue()
        self.workdir = None
        self._build()
        self.root.after(150, self._poll)

    def _build(self):
        frm = ttk.Frame(self.root, padding=12); frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Твій запит (тема відео):").pack(anchor="w")
        qrow = ttk.Frame(frm); qrow.pack(fill="x", pady=(2, 8))
        self.query = tk.Text(qrow, height=4, font=("Segoe UI", 12), wrap="word")
        self.query.pack(side="left", fill="x", expand=True)
        qscroll = ttk.Scrollbar(qrow, orient="vertical", command=self.query.yview)
        self.query.configure(yscrollcommand=qscroll.set)
        qscroll.pack(side="left", fill="y")
        ttk.Button(qrow, text="📋 Вставити", command=self.paste_query).pack(side="left", padx=(6, 0))

        # Вставка скопійованого тексту: Ctrl+V, Shift+Insert, правий клік
        for seq in ("<Control-v>", "<Control-V>", "<Shift-Insert>"):
            self.query.bind(seq, self._paste_event)
        self.query.bind("<Button-3>", self._query_menu)

        row = ttk.Frame(frm); row.pack(fill="x", pady=2)
        ttk.Label(row, text="Голос:").pack(side="left")
        self.voice = ttk.Combobox(row, values=list(VOICES), state="readonly", width=28)
        self.voice.current(0); self.voice.pack(side="left", padx=6)
        ttk.Label(row, text="Розмір:").pack(side="left", padx=(12, 2))
        self.size = ttk.Combobox(row, values=["1280x720", "1920x1080", "1080x1920 (Shorts)"], width=18, state="readonly")
        self.size.current(0); self.size.pack(side="left")

        self.music_path = tk.StringVar(value="")
        mrow = ttk.Frame(frm); mrow.pack(fill="x", pady=2)
        ttk.Label(mrow, text="Фонова музика:").pack(side="left")
        ttk.Entry(mrow, textvariable=self.music_path).pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(mrow, text="…", width=3, command=self.pick_music).pack(side="left")

        self.btn = ttk.Button(frm, text="🎬  ЗГЕНЕРУВАТИ ВІДЕО", command=self.start)
        self.btn.pack(fill="x", pady=8)
        self.bar = ttk.Progressbar(frm, mode="indeterminate"); self.bar.pack(fill="x")
        ttk.Button(frm, text="📂 Відкрити папку з результатом",
                   command=self.open_folder).pack(anchor="e", pady=4)
        ttk.Label(frm, text="Журнал:").pack(anchor="w", pady=(6, 0))
        lrow = ttk.Frame(frm); lrow.pack(fill="both", expand=True)
        self.log = tk.Text(lrow, height=9, state="disabled", font=("Consolas", 9), wrap="word")
        self.log.pack(side="left", fill="both", expand=True)
        lscroll = ttk.Scrollbar(lrow, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=lscroll.set)
        lscroll.pack(side="right", fill="y")

    def paste_query(self):
        """Вставляє текст із буфера обміну в поле запиту."""
        try:
            clip = self.root.clipboard_get()
        except tk.TclError:
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

    def _query_menu(self, event):
        """Меню правого кліку: вставити / копіювати / очистити."""
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="📋 Вставити", command=self.paste_query)
        m.add_command(label="✂️ Вирізати", command=lambda: self.query.event_generate("<<Cut>>"))
        m.add_command(label="📄 Копіювати", command=lambda: self.query.event_generate("<<Copy>>"))
        m.add_separator()
        m.add_command(label="🗑️ Очистити поле", command=lambda: self.query.delete("1.0", "end"))
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    def pick_music(self):
        p = filedialog.askopenfilename(filetypes=[("Аудіо", "*.mp3 *.wav *.m4a *.ogg")])
        if p: self.music_path.set(p)

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
                self.btn.state(["!disabled"])
                continue
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n"); self.log.see("end")
            self.log.configure(state="disabled")
        self.root.after(150, self._poll)

    def start(self):
        query = self.query.get("1.0", "end").strip()
        if len(query) < 3:
            messagebox.showwarning("Стоп", "Спершу встав запит 🙂")
            return
        self.btn.state(["disabled"]); self.bar.start(12)
        threading.Thread(target=self.pipeline, args=(query,), daemon=True).start()

    def pipeline(self, query):
        try:
            generate_video(query, self.voice.get(), self.size.get(),
                           self.music_path.get().strip(), self.say,
                           on_workdir=lambda wd: setattr(self, "workdir", wd))
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
            generate_video("Перевірка збірки генератора", "Остап (укр, чоловічий)",
                           "1280x720", "", _log, on_workdir=lambda wd: None)
        except Exception as e:
            ok = False
            _log("SMOKE FAILED: " + str(e))
        sys.exit(0 if ok else 1)
    App().root.mainloop()
