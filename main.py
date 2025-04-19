import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import re
import threading
import traceback
import yt_dlp
from PIL import Image, ImageTk
import webbrowser

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

def download_media(url, format_type, quality, output_dir, log_callback):
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            if video_title:
                video_title = clean_filename(video_title)
            else:
                video_title = "untitled_media"
        
        options = {
            'outtmpl': os.path.join(output_dir, f"{video_title}.%(ext)s"),
            'progress_hooks': [log_callback],
        }
        
        if format_type == "mp3":
            options.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }]
            })
            file_extension = "mp3"
        else:  # mp4
            if quality == "high":
                options['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            elif quality == "medium":
                options['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
            else:  # low
                options['format'] = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'
            file_extension = "mp4"

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        return video_title, f"{video_title}.{file_extension}"

    except Exception as e:
        save_crash_log(e)
        return None, None

class HoverButton(tk.Canvas):
    def __init__(self, master=None, text='', command=None, width=120, height=35, 
                 bg_color="#FF0000", text_color="white", hover_color="#D10000",
                 corner_radius=18, font=("Segoe UI", 12, "bold"), **kw):
        # Usa il colore di sfondo del parent frame o un colore predefinito se non disponibile
        parent_bg = "#121212"  # Colore di sfondo predefinito
        super().__init__(master, width=width, height=height, bg=parent_bg,
                        highlightthickness=0, **kw)
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.command = command
        
        # Create rounded rectangle
        self.normal_bg = self._create_rounded_rect(0, 0, width, height, corner_radius, bg_color)
        # Create text
        self.text_id = self.create_text(width/2, height/2, text=text, fill=text_color, font=font)
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
    
    def _create_rounded_rect(self, x1, y1, x2, y2, radius, color):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, fill=color, smooth=True, outline=color)
    
    def _on_enter(self, event):
        self.itemconfig(self.normal_bg, fill=self.hover_color, outline=self.hover_color)
        self.config(cursor="hand2")
    
    def _on_leave(self, event):
        self.itemconfig(self.normal_bg, fill=self.bg_color, outline=self.bg_color)
        self.config(cursor="")
    
    def _on_click(self, event):
        self.itemconfig(self.normal_bg, fill="#900000", outline="#900000")
    
    def _on_release(self, event):
        self.itemconfig(self.normal_bg, fill=self.hover_color, outline=self.hover_color)
        if self.command:
            self.command()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("YTDLPY")
        self.root.geometry("700x500")
        self.root.configure(bg="#121212")
        self.root.resizable(True, True)
        
        # Set min size
        self.root.minsize(700, 500)
        
        # Set application icon if available
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "YTDLPY.png")
            if os.path.exists(icon_path):
                icon = ImageTk.PhotoImage(Image.open(icon_path))
                self.root.iconphoto(True, icon)
        except:
            pass

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#121212", foreground="white", font=("Segoe UI", 11))
        self.style.configure("TEntry", font=("Segoe UI", 12), padding=10, relief="flat", fieldbackground="#1E1E1E", foreground="white")
        self.style.configure("TButton", font=("Segoe UI", 12), padding=10, background="#FF0000")
        self.style.configure("TFrame", background="#121212")
        self.style.configure("TCombobox", fieldbackground="#1E1E1E", background="#1E1E1E", foreground="white", selectbackground="#121212", selectforeground="white")
        self.style.map('TCombobox', fieldbackground=[('readonly', '#1E1E1E')], selectbackground=[('readonly', '#121212')])
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        
        # Main frames
        self.header_frame = ttk.Frame(root)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        self.header_frame.columnconfigure(0, weight=1)
        
        self.content_frame = ttk.Frame(root)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=0)
        self.content_frame.rowconfigure(1, weight=1)
        
        self.footer_frame = ttk.Frame(root)
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.create_header()
        self.create_content()
        self.create_footer()
        
        # Set Default values
        self.format_var.set("mp4")
        self.quality_var.set("high")
        
        # Initial directory for saving files
        self.output_dir = os.path.dirname(os.path.abspath(__file__))
        
    def create_header(self):
        # Title and logo
        title_label = ttk.Label(self.header_frame, text="YTDLPY", font=("Segoe UI", 24, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        subtitle_label = ttk.Label(self.header_frame, text="Advanced YouTube Downloader", font=("Segoe UI", 12))
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Instructions button
        instructions_button = ttk.Button(self.header_frame, text="Instructions", command=self.show_instructions)
        instructions_button.grid(row=0, column=1, rowspan=2, sticky="e")
        
    def create_content(self):
        # URL input frame
        url_frame = ttk.Frame(self.content_frame)
        url_frame.grid(row=0, column=0, sticky="ew", pady=(10, 0))
        url_frame.columnconfigure(1, weight=1)
        
        url_label = ttk.Label(url_frame, text="Enter Video URL:")
        url_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=10)
        
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.grid(row=0, column=1, sticky="ew", pady=10)
        self.url_entry.bind("<Button-3>", self.paste)
        
        paste_button = ttk.Button(url_frame, text="Paste", command=lambda: self.url_entry.event_generate("<<Paste>>"))
        paste_button.grid(row=0, column=2, sticky="e", padx=(10, 0), pady=10)
        
        # Options frame
        options_frame = ttk.Frame(self.content_frame)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(2, weight=1)
        
        # Format selection
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        
        format_label = ttk.Label(format_frame, text="Format:", font=("Segoe UI", 12, "bold"))
        format_label.pack(pady=(0, 10))
        
        self.format_var = tk.StringVar()
        mp4_radio = ttk.Radiobutton(format_frame, text="MP4 (Video)", value="mp4", variable=self.format_var)
        mp4_radio.pack(anchor="w", pady=2)
        
        mp3_radio = ttk.Radiobutton(format_frame, text="MP3 (Audio)", value="mp3", variable=self.format_var)
        mp3_radio.pack(anchor="w", pady=2)
        
        # Quality selection
        quality_frame = ttk.Frame(options_frame)
        quality_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        quality_label = ttk.Label(quality_frame, text="Quality:", font=("Segoe UI", 12, "bold"))
        quality_label.pack(pady=(0, 10))
        
        self.quality_var = tk.StringVar()
        high_radio = ttk.Radiobutton(quality_frame, text="High", value="high", variable=self.quality_var)
        high_radio.pack(anchor="w", pady=2)
        
        medium_radio = ttk.Radiobutton(quality_frame, text="Medium (720p)", value="medium", variable=self.quality_var)
        medium_radio.pack(anchor="w", pady=2)
        
        low_radio = ttk.Radiobutton(quality_frame, text="Low (480p)", value="low", variable=self.quality_var)
        low_radio.pack(anchor="w", pady=2)
        
        # Output directory
        output_frame = ttk.Frame(options_frame)
        output_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=10)
        
        output_label = ttk.Label(output_frame, text="Output:", font=("Segoe UI", 12, "bold"))
        output_label.pack(pady=(0, 10))
        
        browse_button = ttk.Button(output_frame, text="Select Folder", command=self.select_output_directory)
        browse_button.pack(anchor="w", pady=2)
        
        self.output_path_label = ttk.Label(output_frame, text="Default folder", font=("Segoe UI", 9), wraplength=200)
        self.output_path_label.pack(anchor="w", pady=2)
        
        # Result display
        self.result_frame = ttk.Frame(self.content_frame)
        self.result_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        self.result_frame.columnconfigure(0, weight=1)
        
        self.result_label = ttk.Label(self.result_frame, text="Ready to download", font=("Segoe UI", 11))
        self.result_label.grid(row=0, column=0, sticky="w")
        
    def create_footer(self):
        # Download button with custom rounded style
        self.download_button = HoverButton(
            self.footer_frame, 
            text="DOWNLOAD", 
            command=self.start_download,
            width=200, 
            height=40,
            bg_color="#FF0000",
            hover_color="#D10000",
            corner_radius=20
        )
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Version info and GitHub link
        version_frame = ttk.Frame(self.footer_frame)
        version_frame.pack(side=tk.RIGHT)
        
        version_label = ttk.Label(version_frame, text="Version 2.0", font=("Segoe UI", 9))
        version_label.grid(row=0, column=0, sticky="e")
        
        github_link = ttk.Label(version_frame, text="Visit GitHub", font=("Segoe UI", 9), foreground="#3498db", cursor="hand2")
        github_link.grid(row=1, column=0, sticky="e")
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/dddevid/YTDLPY"))
        
    def select_output_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir)
        if directory:
            self.output_dir = directory
            # Truncate path for display if too long
            display_path = directory
            if len(display_path) > 30:
                display_path = "..." + display_path[-27:]
            self.output_path_label.config(text=display_path)

    def paste(self, event):
        self.url_entry.event_generate("<<Paste>>")
        
    def show_instructions(self):
        instructions = (
            "YTDLPY - How to use:\n\n"
            "1. Enter the YouTube video URL in the input field.\n"
            "2. Choose your format preference (MP4 video or MP3 audio).\n"
            "3. Select the desired quality:\n"
            "   - High: Best available quality\n"
            "   - Medium: 720p for videos, 192kbps for audio\n"
            "   - Low: 480p for videos, 128kbps for audio\n"
            "4. Select an output folder (optional).\n"
            "5. Click the DOWNLOAD button to start downloading.\n"
            "6. Monitor the download progress in the log window.\n\n"
            "Note: You can paste the URL using the right-click or the Paste button."
        )
        messagebox.showinfo("Instructions", instructions)
        
    def start_download(self):
        url = self.url_entry.get().strip()
        format_type = self.format_var.get()
        quality = self.quality_var.get()
        
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a valid URL.")
            return
            
        self.result_label.config(text="Starting download...")
        
        # Create log window
        log_window = tk.Toplevel(self.root)
        log_window.title("Download Progress")
        log_window.geometry("700x300")
        log_window.configure(bg="#121212")
        
        # Configure log window grid
        log_window.grid_columnconfigure(0, weight=1)
        log_window.grid_rowconfigure(0, weight=0)
        log_window.grid_rowconfigure(1, weight=1)
        
        status_label = ttk.Label(log_window, text="Downloading...", font=("Segoe UI", 12, "bold"))
        status_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, font=("Consolas", 10), bg="#1E1E1E", fg="#CCCCCC")
        log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        def log_callback(d):
            if d['status'] == 'downloading':
                _bytes = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                
                if total > 0:
                    percent = _bytes / total * 100
                    speed = d.get('speed', 0) or 0
                    eta = d.get('eta', 0) or 0
                    
                    speed_str = f"{speed/1024/1024:.2f} MB/s" if speed else "unknown speed"
                    eta_str = f"{eta//60}:{eta%60:02d}" if eta else "unknown"
                    
                    log_message = f"Downloading: {d.get('filename', 'Unknown')}\n"
                    log_message += f"Progress: {_bytes/1024/1024:.2f} MB / {total/1024/1024:.2f} MB ({percent:.1f}%)\n"
                    log_message += f"Speed: {speed_str}, ETA: {eta_str}\n"
                else:
                    log_message = f"Downloading: {d.get('filename', 'Unknown')} - {_bytes/1024/1024:.2f} MB downloaded\n"
                
                log_text.delete(1.0, tk.END)
                log_text.insert(tk.END, log_message)
                log_text.see(tk.END)
                self.root.update_idletasks()
            elif d['status'] == 'finished':
                log_text.insert(tk.END, f"\nDownload finished! Post-processing...\n")
                status_label.config(text="Processing...")
                log_text.see(tk.END)
                self.root.update_idletasks()
        
        def download_thread():
            try:
                # Convert quality value for MP3
                mp3_quality = "0"  # High
                if quality == "medium":
                    mp3_quality = "5"
                elif quality == "low":
                    mp3_quality = "7"
                
                video_title, output_file = download_media(
                    url, 
                    format_type, 
                    mp3_quality if format_type == "mp3" else quality,
                    self.output_dir, 
                    log_callback
                )
                
                if video_title and output_file:
                    status_label.config(text="Download Complete!")
                    log_text.insert(tk.END, f"\nSuccess! File saved as: {output_file}\n")
                    log_text.see(tk.END)
                    
                    self.result_label.config(text=f"Successfully downloaded: {video_title}")
                    messagebox.showinfo("Download Complete", f"The file was successfully downloaded!\nSaved as: {output_file}")
                else:
                    status_label.config(text="Download Failed")
                    self.result_label.config(text="Download failed. See error log for details.")
            except Exception as e:
                save_crash_log(e)
                status_label.config(text="Error Occurred")
                self.result_label.config(text="An error occurred. Check logs for details.")
        
        threading.Thread(target=download_thread, daemon=True).start()
        
# Main application execution
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except Exception as e:
        save_crash_log(e)
        messagebox.showerror("Critical Error", "The application failed to start.")
        sys.exit(1)
