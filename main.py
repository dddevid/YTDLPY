import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import re
import threading
import traceback

def create_log_folder():
    user_dir = Path.home()
    log_dir = user_dir / "YTDLPY"
    if not log_dir.exists():
        log_dir.mkdir()
    return log_dir

def save_crash_log(e):
    log_dir = create_log_folder()
    crash_log_file = log_dir / f"crash_log_{datetime.now().strftime('%Y-%m-%d')}.log"
    with open(crash_log_file, 'w') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Error: {str(e)}\n")
        f.write(traceback.format_exc())
    messagebox.showerror("Critical Error", f"An unexpected error occurred. More details are available in the log file:\n{crash_log_file}")

def clean_filename(name):
    return re.sub(r'[\\/:*?"<>|]', ' ', name)

def download_video(url, log_callback):
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            if video_title:
                video_title = clean_filename(video_title)
            else:
                video_title = "untitled_video"

        video_file = f"{video_title}.mp4"

        video_options = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': video_file,
            'progress_hooks': [log_callback]
        }
        with yt_dlp.YoutubeDL(video_options) as ydl:
            ydl.download([url])

        return video_title, video_file

    except Exception as e:
        save_crash_log(e)
        return None, None

def start_download():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Missing URL", "Please enter a valid URL.")
        return

    def log_callback(d, log_text):
        if d['status'] == 'downloading':
            log_message = f"Downloading: {d.get('filename', 'Unknown')} - {d.get('downloaded_bytes', 0)} bytes downloaded\n"
            log_text.insert(tk.END, log_message)
            log_text.yview(tk.END)
            root.update_idletasks()

    def download_with_log():
        try:
            log_window = tk.Toplevel(root)
            log_window.title("Download Log")
            log_window.geometry("600x200")
            log_window.configure(bg="#0f0f0f")

            log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, font=("Segoe UI", 10), bg="#181818", fg="white")
            log_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

            def internal_log_callback(d):
                log_callback(d, log_text)

            video_title, video_file = download_video(url, internal_log_callback)
            if video_title and video_file:
                messagebox.showinfo("Download Complete", f"The video was successfully downloaded! Saved as {video_title}.mp4.")
        except Exception as e:
            save_crash_log(e)
        finally:
            log_window.destroy()

    threading.Thread(target=download_with_log, daemon=True).start()

def paste(event):
    url_entry.event_generate("<<Paste>>")

def show_instructions():
    instructions = (
        "1. Enter the YouTube video URL you want to download in the designated field.\n"
        "2. Press the 'Download' button to start the video download.\n"
        "3. The video will be downloaded in the highest available quality and saved as an MP4 file.\n"
        "4. You can paste the URL directly from the clipboard by right-clicking in the URL field.\n"
        "5. Monitor the download progress in the log window that appears after the download starts.\n"
        "6. Once the download is complete, the video will be available in the folder where this program is located."
    )
    messagebox.showinfo("Instructions", instructions)

root = tk.Tk()
root.title("YTDLPY")
root.geometry("400x250")
root.configure(bg="#0f0f0f")

root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("TEntry", font=("Segoe UI", 12), padding=10, relief="flat", fieldbackground="#181818", foreground="white")

canvas = tk.Canvas(root, bg="#0f0f0f", bd=0, highlightthickness=0)
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

welcome_label = tk.Label(root, text="Download YouTube Videos", font=("Segoe UI", 16), bg="#0f0f0f", fg="white")
welcome_label.place(relx=0.5, y=50, anchor="center")

url_entry = ttk.Entry(root, width=50, style="TEntry")
url_entry.place(relx=0.5, y=100, anchor="center", width=300, height=35)

url_entry.bind("<Button-3>", paste)

instructions_button = tk.Button(root, text="Instructions", font=("Segoe UI", 10), bg="#0f0f0f", fg="white", command=show_instructions)
instructions_button.place(relx=0.95, rely=0.05, anchor="ne")

def create_rounded_button(canvas, x, y, width, height, radius, bg_color, text_color, text, command):
    canvas.create_oval(x, y, x+radius*2, y+radius*2, fill=bg_color, outline=bg_color)
    canvas.create_oval(x+width-radius*2, y, x+width, y+radius*2, fill=bg_color, outline=bg_color)
    canvas.create_oval(x, y+height-radius*2, x+radius*2, y+height, fill=bg_color, outline=bg_color)
    canvas.create_oval(x+width-radius*2, y+height-radius*2, x+width, y+height, fill=bg_color, outline=bg_color)
    canvas.create_rectangle(x+radius, y, x+width-radius, y+height, fill=bg_color, outline=bg_color)
    canvas.create_rectangle(x, y+radius, x+width, y+height-radius, fill=bg_color, outline=bg_color)

    button = canvas.create_text(x+width/2, y+height/2, text=text, fill=text_color, font=("Segoe UI", 12))

    def on_click(event):
        command()
    
    def on_enter(event):
        canvas.config(cursor="hand2")
    
    def on_leave(event):
        canvas.config(cursor="")

    canvas.tag_bind(button, "<Button-1>", on_click)
    canvas.tag_bind(button, "<Enter>", on_enter)
    canvas.tag_bind(button, "<Leave>", on_leave)

create_rounded_button(canvas, x=140, y=160, width=120, height=35, radius=18, bg_color="#FF0000", text_color="white", text="Download", command=start_download)

info_label = tk.Label(root, text="ⓘ Right-click to paste from your clipboard", font=("Segoe UI", 10), bg="#0f0f0f", fg="red")
info_label.pack(side=tk.BOTTOM, pady=10)

root.mainloop()
