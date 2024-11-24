import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import os

class UploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dosya Yükleme Uygulaması")
        self.root.geometry("400x200")
        
        # API Anahtarı girişi
        self.api_key_label = tk.Label(root, text="API Anahtarı:")
        self.api_key_label.pack(pady=5)
        
        self.api_key_entry = tk.Entry(root, width=50)
        self.api_key_entry.pack(pady=5)
        
        # Sunucu URL'si girişi
        self.server_label = tk.Label(root, text="Sunucu URL'si:")
        self.server_label.pack(pady=5)
        
        self.server_entry = tk.Entry(root, width=50)
        self.server_entry.insert(0, "http://localhost:5000")  # Varsayılan değer
        self.server_entry.pack(pady=5)
        
        # Dosya seçme butonu
        self.select_button = tk.Button(root, text="Dosya Seç ve Yükle", command=self.upload_file)
        self.select_button.pack(pady=20)
        
        # Durum etiketi
        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=10)

    def upload_file(self):
        # Dosya seç
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
            
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("Hata", "API anahtarı gerekli!")
            return
            
        server_url = self.server_entry.get().strip()
        if not server_url:
            messagebox.showerror("Hata", "Sunucu URL'si gerekli!")
            return
        
        try:
            # Dosyayı yükle
            files = {'file': open(file_path, 'rb')}
            headers = {'X-API-Key': api_key}
            
            self.status_label.config(text="Dosya yükleniyor...")
            self.root.update()
            
            response = requests.post(f"{server_url}/upload", files=files, headers=headers)
            
            if response.status_code == 200:
                messagebox.showinfo("Başarılı", "Dosya başarıyla yüklendi!")
                self.status_label.config(text="Son yükleme: Başarılı")
            else:
                error_msg = response.json().get('error', 'Bilinmeyen bir hata oluştu')
                messagebox.showerror("Hata", f"Yükleme başarısız: {error_msg}")
                self.status_label.config(text="Son yükleme: Başarısız")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")
            self.status_label.config(text="Son yükleme: Hata")
        
        finally:
            if 'files' in locals():
                files['file'].close()

if __name__ == "__main__":
    root = tk.Tk()
    app = UploaderApp(root)
    root.mainloop()
