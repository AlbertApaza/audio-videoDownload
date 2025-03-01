import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import os
import threading
import time
import json
from datetime import datetime
class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("680x650")
        self.root.configure(bg="#f0f0f0")
        self.url_var = tk.StringVar()
        self.folder_path = tk.StringVar()
        self.format_var = tk.StringVar(value="Video")
        self.filename_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Listo para descargar")
        self.save_metadata_var = tk.BooleanVar(value=True)
        self.formats_cache = {}
        self.metadata_cache = {}
        self.is_downloading = False
        self.create_widgets()
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        download_tab = ttk.Frame(self.notebook)
        self.notebook.add(download_tab, text="Descargar")
        metadata_tab = ttk.Frame(self.notebook)
        self.notebook.add(metadata_tab, text="Metadatos")
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("TRadiobutton", background="#f0f0f0", font=("Arial", 10))
        style.configure("TEntry", font=("Arial", 10))
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("Header.TLabel", background="#f0f0f0", font=("Arial", 12, "bold"))
        style.configure("Status.TLabel", background="#f0f0f0", font=("Arial", 10, "italic"))
        self.create_download_tab(download_tab)
        self.create_metadata_tab(metadata_tab)
    def create_download_tab(self, parent):
        ttk.Label(parent, text="Enlace de YouTube:", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        url_frame = ttk.Frame(parent)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Entry(url_frame, textvariable=self.url_var, width=50).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(url_frame, text="Obtener formatos", command=self.update_formats).pack(side=tk.RIGHT)
        format_frame = ttk.Frame(parent)
        format_frame.pack(fill=tk.X, pady=10)
        ttk.Label(format_frame, text="Descargar como:", style="Header.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="Video", variable=self.format_var, value="Video", 
                        command=self.update_formats).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="Audio", variable=self.format_var, value="Audio", 
                       command=self.update_formats).pack(side=tk.LEFT)
        ttk.Label(parent, text="Selecciona un formato:", style="Header.TLabel").pack(anchor=tk.W, pady=(5, 5))
        formats_frame = ttk.Frame(parent)
        formats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        columns = ("id", "quality", "size")
        self.format_tree = ttk.Treeview(formats_frame, columns=columns, show="headings", height=8)
        self.format_tree.heading("id", text="ID")
        self.format_tree.heading("quality", text="Calidad")
        self.format_tree.heading("size", text="Tamaño")
        self.format_tree.column("id", width=50)
        self.format_tree.column("quality", width=300)
        self.format_tree.column("size", width=100)
        scrollbar = ttk.Scrollbar(formats_frame, orient=tk.VERTICAL, command=self.format_tree.yview)
        self.format_tree.configure(yscroll=scrollbar.set)
        self.format_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        filename_frame = ttk.Frame(parent)
        filename_frame.pack(fill=tk.X, pady=10)
        ttk.Label(filename_frame, text="Nombre del archivo:", style="Header.TLabel").pack(anchor=tk.W, pady=(5, 5))
        ttk.Entry(filename_frame, textvariable=self.filename_var, width=50).pack(fill=tk.X, pady=5)
        folder_frame = ttk.Frame(parent)
        folder_frame.pack(fill=tk.X, pady=10)
        ttk.Label(folder_frame, text="Carpeta de destino:", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=40)
        folder_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Examinar", command=self.choose_folder).pack(side=tk.RIGHT)
        metadata_frame = ttk.Frame(parent)
        metadata_frame.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(metadata_frame, text="Guardar metadatos en archivo JSON", 
                       variable=self.save_metadata_var).pack(anchor=tk.W)
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=10)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, length=100, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.loading_indicator = tk.Canvas(progress_frame, width=30, height=30, bg="#f0f0f0", highlightthickness=0)
        self.loading_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.draw_loading_indicator(0)
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(parent, text="DESCARGAR", command=self.download_video, 
                  style="TButton").pack(pady=10, fill=tk.X)
        self.format_tree.bind("<<TreeviewSelect>>", self.on_format_select)
    def create_metadata_tab(self, parent):
        ttk.Label(parent, text="Metadatos del video:", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        metadata_frame = ttk.Frame(parent)
        metadata_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        columns = ("field", "value")
        self.metadata_tree = ttk.Treeview(metadata_frame, columns=columns, show="headings", height=20)
        self.metadata_tree.heading("field", text="Campo")
        self.metadata_tree.heading("value", text="Valor")
        self.metadata_tree.column("field", width=150)
        self.metadata_tree.column("value", width=400)
        scrollbar = ttk.Scrollbar(metadata_frame, orient=tk.VERTICAL, command=self.metadata_tree.yview)
        self.metadata_tree.configure(yscroll=scrollbar.set)
        self.metadata_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Actualizar Metadatos", 
                 command=self.fetch_metadata).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Exportar Metadatos", 
                 command=self.export_metadata).pack(side=tk.LEFT)
    def draw_loading_indicator(self, angle):
        """Draws a rotating loading indicator"""
        self.loading_indicator.delete("all")
        if not self.is_downloading:
            return
        self.loading_indicator.create_arc(5, 5, 25, 25, start=angle, extent=60, 
                                         outline="#4CAF50", width=3, style=tk.ARC)
        self.loading_indicator.create_arc(5, 5, 25, 25, start=angle+180, extent=60, 
                                         outline="#4CAF50", width=3, style=tk.ARC)
        self.root.after(50, lambda: self.draw_loading_indicator((angle + 10) % 360))
    def on_format_select(self, event):
        """Handle format selection to update filename"""
        selected = self.format_tree.selection()
        if selected:
            item = self.format_tree.item(selected[0])
            format_id = item['values'][0]
            if self.url_var.get() in self.formats_cache:
                video_info = self.formats_cache[self.url_var.get()]['info']
                if 'title' in video_info:
                    self.filename_var.set(video_info['title'])

    def progress_hook(self, d):
        
        print("progress_hook fue llamada")
        print("Debug data:", d)
        """Update progress bar and status based on download progress"""
        
        print("Debug data:", d)
        
        if d['status'] == 'downloading':
            percent_value = d.get('_percent_str', None)

            if percent_value is None:
                print("Advertencia: '_percent_str' es None, estableciendo a '0%'")
                percent_value = "0%"
            elif isinstance(percent_value, (int, float)):
                percent_value = f"{percent_value}%"
            
            try:
                percent = float(percent_value.replace('%', '').strip())
            except Exception as e:
                print(f"Error al convertir porcentaje: {e}")
                percent = 0.0

            self.progress_var.set(percent)

            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', '')

            self.status_var.set(f"Descargando... {percent_value} a {speed} (ETA: {eta})")
            self.root.update_idletasks()

        elif d['status'] == 'finished':
            self.status_var.set("Procesando archivo...")
            self.progress_var.set(100)
            self.root.update_idletasks()


    def format_size(self, size):
        """Format file size for display"""
        if not size:
            return "Desconocido"
        if size >= 1e9:
            return f"{size / 1e9:.2f} GB"
        elif size >= 1e6:
            return f"{size / 1e6:.2f} MB"
        elif size >= 1e3:
            return f"{size / 1e3:.2f} KB"
        else:
            return f"{size} bytes"
    def get_available_formats(self, url):
        """Fetch and cache available formats for the URL"""
        try:
            if url in self.formats_cache:
                return self.formats_cache[url]['formats']
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                self.formats_cache[url] = {
                    'info': info,
                    'formats': []
                }
                if 'title' in info:
                    self.filename_var.set(info['title'])
                self.metadata_cache[url] = self.extract_metadata(info)
                self.fill_metadata_tree(url)
                format_type = self.format_var.get().lower()
                formats_list = []
                for f in info.get('formats', []):
                    if f.get('vcodec', '') == 'none' and format_type == 'video':
                        continue
                    if f.get('acodec', '') == 'none' and format_type == 'audio':
                        continue
                    if format_type == 'audio' and f.get('acodec', '') != 'none':
                        quality = f.get('format_note', 'N/A')
                        size = f.get('filesize') or f.get('filesize_approx', 0)
                        formats_list.append((f['format_id'], f"{quality} - {f.get('acodec', 'N/A')}", self.format_size(size), size))
                    elif format_type == 'video' and f.get('vcodec', '') != 'none':
                        quality = f.get('format_note', 'N/A')
                        resolution = f"{f.get('width', '?')}x{f.get('height', '?')}"
                        size = f.get('filesize') or f.get('filesize_approx', 0)
                        formats_list.append((f['format_id'], f"{quality} - {resolution}", self.format_size(size), size))
                formats_list.sort(key=lambda x: x[3] if x[3] else 0, reverse=True)
                self.formats_cache[url]['formats'] = formats_list
                return formats_list
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron obtener formatos: {str(e)}")
            return []
    def extract_metadata(self, info):
        """Extract all possible metadata fields from the video info"""
        metadata = {}
        metadata_fields = [
            'title', 'track', 'date', 'upload_date', 'description', 'synopsis',
            'purl', 'comment', 'webpage_url', 'track_number', 'artist', 'artists',
            'creator', 'creators', 'uploader', 'uploader_id', 'composer', 'composers',
            'genre', 'genres', 'album', 'album_artist', 'album_artists', 'disc',
            'disc_number', 'show', 'series', 'season_number', 'episode_id', 'episode',
            'episode_sort', 'episode_number', 'language'
        ]
        for field in metadata_fields:
            if field in info:
                metadata[field] = info[field]
        if 'formats' in info:
            metadata['available_formats'] = []
            for fmt in info['formats']:
                format_info = {
                    'format_id': fmt.get('format_id', 'unknown'),
                    'format_note': fmt.get('format_note', 'N/A'),
                    'width': fmt.get('width', 'N/A'),
                    'height': fmt.get('height', 'N/A'),
                    'resolution': f"{fmt.get('width', '?')}x{fmt.get('height', '?')}",
                    'fps': fmt.get('fps', 'N/A'),
                    'vcodec': fmt.get('vcodec', 'N/A'),
                    'acodec': fmt.get('acodec', 'N/A'),
                    'abr': fmt.get('abr', 'N/A'),
                    'vbr': fmt.get('vbr', 'N/A'),
                    'filesize': fmt.get('filesize', 'N/A'),
                    'format': fmt.get('format', 'N/A'),
                    'language': fmt.get('language', 'N/A')
                }
                metadata['available_formats'].append(format_info)
        if 'thumbnails' in info:
            metadata['thumbnails'] = []
            for thumb in info.get('thumbnails', []):
                metadata['thumbnails'].append({
                    'url': thumb.get('url', ''),
                    'width': thumb.get('width', 'N/A'),
                    'height': thumb.get('height', 'N/A')
                })
        metadata['extraction_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return metadata
    def fill_metadata_tree(self, url):
        """Fill the metadata treeview with data from cache"""
        for item in self.metadata_tree.get_children():
            self.metadata_tree.delete(item)
        if url not in self.metadata_cache:
            return
        metadata = self.metadata_cache[url]
        for field, value in metadata.items():
            if field in ['available_formats', 'thumbnails']:
                continue
            if isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False)
            if isinstance(value, str) and len(value) > 500:
                value = value[:497] + "..."
            self.metadata_tree.insert("", tk.END, values=(field, value))
        formats_parent = self.metadata_tree.insert("", tk.END, values=("Formatos disponibles", f"{len(metadata.get('available_formats', []))} formatos"))
        for i, fmt in enumerate(metadata.get('available_formats', [])):
            fmt_desc = f"#{i+1}: {fmt.get('format_id')} - {fmt.get('resolution')} - {fmt.get('vcodec')}/{fmt.get('acodec')}"
            format_item = self.metadata_tree.insert(formats_parent, tk.END, values=("Formato", fmt_desc))
            for k, v in fmt.items():
                if k not in ['format_id']:
                    self.metadata_tree.insert(format_item, tk.END, values=(k, v))
        if 'thumbnails' in metadata and metadata['thumbnails']:
            thumb_parent = self.metadata_tree.insert("", tk.END, values=("Miniaturas", f"{len(metadata['thumbnails'])} miniaturas"))
            
            # Add thumbnails as children
            for i, thumb in enumerate(metadata['thumbnails']):
                thumb_desc = f"#{i+1}: {thumb.get('width')}x{thumb.get('height')}"
                self.metadata_tree.insert(thumb_parent, tk.END, values=("Miniatura", thumb_desc))
    
    def update_formats(self):
        """Update the format list based on the URL"""
        threading.Thread(target=self.update_formats_thread, daemon=True).start()

    def update_formats_thread(self):
        """Background thread for fetching formats"""
        url = self.url_var.get()
        if not url:
            messagebox.showinfo("Información", "Por favor, ingresa un enlace de YouTube válido")
            return
        for item in self.format_tree.get_children():
            self.format_tree.delete(item)
        self.status_var.set("Obteniendo formatos disponibles...")
        self.root.update_idletasks()
        formats = self.get_available_formats(url)
        for i, (format_id, quality, size, _) in enumerate(formats):
            self.format_tree.insert("", tk.END, values=(format_id, quality, size))
        if formats:
            first_item = self.format_tree.get_children()[0]
            self.format_tree.selection_set(first_item)
            self.format_tree.focus(first_item)
            self.on_format_select(None)
        self.status_var.set(f"{len(formats)} formatos disponibles")
        self.notebook.select(1)
        self.root.after(2000, lambda: self.notebook.select(0))
    def fetch_metadata(self):
        """Fetch metadata for the current URL"""
        url = self.url_var.get()
        if not url:
            messagebox.showinfo("Información", "Por favor, ingresa un enlace de YouTube válido")
            return
        threading.Thread(target=lambda: self.update_formats_thread(), daemon=True).start()
    def export_metadata(self):
        """Export metadata to a JSON file"""
        url = self.url_var.get()
        if url not in self.metadata_cache:
            messagebox.showinfo("Información", "No hay metadatos disponibles para exportar")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"metadata_{self.filename_var.get()}.json"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata_cache[url], f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Éxito", f"Metadatos exportados exitosamente a:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar metadatos: {str(e)}")
    def choose_folder(self):
        """Open folder selection dialog"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
    def download_video(self):
        """Start download in background thread"""
        threading.Thread(target=self.download_video_thread, daemon=True).start()
    def download_video_thread(self):
        """Background thread for downloading"""
        url = self.url_var.get()
        folder = self.folder_path.get()
        custom_filename = self.filename_var.get()
        if not url:
            messagebox.showerror("Error", "Por favor, ingresa un enlace de YouTube")
            return
        if not folder:
            messagebox.showerror("Error", "Selecciona una carpeta para guardar el archivo")
            return
        selected = self.format_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Selecciona un formato para descargar")
            return
        item = self.format_tree.item(selected[0])
        format_id = item['values'][0]
        if not custom_filename:
            custom_filename = "video"
        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            custom_filename = custom_filename.replace(char, '_')
        file_ext = ".mp4" if self.format_var.get() == "Video" else ".mp3"
        full_filename = f"{custom_filename}{file_ext}"
        full_path = os.path.join(folder, full_filename)
        if self.save_metadata_var.get() and url in self.metadata_cache:
            metadata_path = os.path.join(folder, f"{custom_filename}_metadata.json")
            try:
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(self.metadata_cache[url], f, ensure_ascii=False, indent=4)
            except Exception as e:
                self.status_var.set(f"Error al guardar metadatos: {str(e)}")
        self.is_downloading = True
        self.draw_loading_indicator(0)
        options = {
            'outtmpl': full_path,
            'progress_hooks': [self.progress_hook],
            'format': format_id,
            'writethumbnail': True,
            'writeinfojson': False,
            'addmetadata': True,
            'embed_metadata': True,
            'embedthumbnail': True,
        }
        if self.format_var.get() == "Audio":
            options['postprocessors'] = [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'EmbedThumbnail',
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                }
            ]

        try:
            self.status_var.set("Inicializando descarga...")
            self.progress_var.set(0)
            self.root.update_idletasks()
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            self.is_downloading = False
            self.status_var.set("¡Descarga completada con éxito!")
            messagebox.showinfo("Éxito", f"¡Descarga completada!\nArchivo guardado en:\n{full_path}")
            
        except Exception as e:
            self.is_downloading = False
            self.status_var.set("Error en la descarga")
            messagebox.showerror("Error", f"Hubo un problema: {str(e)}")
        finally:
            self.is_downloading = False
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()