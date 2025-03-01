import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import os
import threading

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        speed = d.get('_speed_str', 'N/A')
        status_label.config(text=f"Descargando... {percent} a {speed}")
    elif d['status'] == 'finished':
        status_label.config(text="Descarga completada")

def download_content():
    threading.Thread(target=download_thread, daemon=True).start()

def download_thread():
    url = url_entry.get().split("&list=")[0]
    folder = folder_path.get()
    format_choice = format_var.get()
    
    if not url:
        messagebox.showerror("Error", "Por favor, ingresa un enlace de YouTube")
        return
    
    if not folder:
        messagebox.showerror("Error", "Selecciona una carpeta para guardar el archivo")
        return
    
    options = {
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'writethumbnail': True,
        'postprocessors': [
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'}
        ]
    }
    
    if format_choice == "Audio":
        options.update({
            'format': 'bestaudio/best',
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                {'key': 'FFmpegMetadata'},
                {'key': 'EmbedThumbnail'}
            ]
        })
    else:
        options['format'] = 'bestvideo+bestaudio/best'
    
    try:
        status_label.config(text="Descargando...", fg="blue")
        root.update()
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        messagebox.showinfo("Éxito", "Descarga completada con éxito")
    except Exception as e:
        messagebox.showerror("Error", f"Hubo un problema: {str(e)}")

# Carpeta donde se guardara
def choose_folder():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)

# UI UI UI UI 
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("500x350")
root.configure(bg="#f0f0f0")

label_font = ("Arial", 12)
button_font = ("Arial", 10, "bold")
button_bg = "#007BFF"
button_fg = "white"

# UCampo URL
tk.Label(root, text="Enlace de YouTube:", font=label_font, bg="#f0f0f0").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Selección de formato
tk.Label(root, text="Descargar como:", font=label_font, bg="#f0f0f0").pack()
format_var = tk.StringVar(value="Video")
tk.Radiobutton(root, text="Video", variable=format_var, value="Video", bg="#f0f0f0").pack()
tk.Radiobutton(root, text="Audio", variable=format_var, value="Audio", bg="#f0f0f0").pack()

folder_path = tk.StringVar()
tk.Button(root, text="Seleccionar carpeta", command=choose_folder, font=button_font, bg=button_bg, fg=button_fg).pack(pady=5)

# estado 
status_label = tk.Label(root, text="", font=label_font, bg="#f0f0f0")
status_label.pack(pady=5)

tk.Button(root, text="Descargar", command=download_content, font=button_font, bg="green", fg="white").pack(pady=10)

root.mainloop()
