import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import os

# Sabit değerler
API_KEY = "Ayin2iyul"  # app.py'deki API_KEY ile aynı olmalı
SERVER_URL = "https://kenanpeyser.up.railway.app"  # Railway'deki uygulama URL'niz

class FileUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dosya Yükleyici")
        self.root.geometry("400x150")
        
        # Ana frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Dosya seçme butonu
        self.select_button = tk.Button(main_frame, text="Dosya Seç ve Yükle", command=self.upload_file)
        self.select_button.pack(pady=20)
        
        # Durum etiketi
        self.status_label = tk.Label(main_frame, text="", wraplength=350)
        self.status_label.pack(pady=10)

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        
        try:
            # Dosyayı yükle
            with open(file_path, 'rb') as file:
                files = {'file': file}
                headers = {'X-API-Key': API_KEY}
                response = requests.post(f"{SERVER_URL}/upload", files=files, headers=headers)
            
            if response.status_code == 200:
                messagebox.showinfo("Başarılı", "Dosya başarıyla yüklendi!")
                self.status_label.config(text=f"Son yüklenen dosya: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Hata", f"Yükleme başarısız: {response.text}")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")

def main():
    root = tk.Tk()
    app = FileUploaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
