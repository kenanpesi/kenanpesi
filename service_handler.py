import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import platform
import psutil
import requests
import json
import time
from threading import Thread

class RemoteAccessService(win32serviceutil.ServiceFramework):
    _svc_name_ = "RemoteAccessService"
    _svc_display_name_ = "Remote Access Service"
    _svc_description_ = "Uzaktan erişim için Windows servisi"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    def SvcDoRun(self):
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            self.main()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Servis çalışırken hata: {str(e)}")

    def get_system_info(self):
        try:
            info = {
                'hostname': socket.gethostname(),
                'os': platform.system() + ' ' + platform.release(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'ip_address': socket.gethostbyname(socket.gethostname()),
                'last_update': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            return info
        except Exception as e:
            servicemanager.LogErrorMsg(f"Sistem bilgisi alınırken hata: {str(e)}")
            return {}

    def send_system_info(self):
        try:
            # Railway URL'inizi buraya ekleyin
            api_url = os.environ.get('RAILWAY_URL', 'https://your-railway-url.up.railway.app')
            system_info = self.get_system_info()
            
            # Admin kullanıcı bilgileri
            auth_data = {
                'username': os.environ.get('ADMIN_USERNAME', 'muradsayagi'),
                'password': os.environ.get('ADMIN_PASSWORD', 'eldos')
            }

            # Önce login olup token alalım
            login_response = requests.post(f"{api_url}/login", data=auth_data)
            if login_response.status_code == 200:
                # Sistem bilgilerini gönder
                response = requests.post(
                    f"{api_url}/update_system_info",
                    json=system_info,
                    cookies=login_response.cookies
                )
                if response.status_code == 200:
                    servicemanager.LogInfoMsg("Sistem bilgileri başarıyla gönderildi")
                else:
                    servicemanager.LogErrorMsg(f"Sistem bilgileri gönderilirken hata: {response.status_code}")
            else:
                servicemanager.LogErrorMsg("Login başarısız")
        except Exception as e:
            servicemanager.LogErrorMsg(f"Bilgi gönderilirken hata: {str(e)}")

    def update_thread(self):
        while self.running:
            self.send_system_info()
            # Her 30 saniyede bir güncelle
            time.sleep(30)

    def main(self):
        # Güncelleme thread'ini başlat
        update_thread = Thread(target=self.update_thread)
        update_thread.daemon = True
        update_thread.start()

        # Ana servis döngüsü
        while self.running:
            # 1 saniye bekle ve durma sinyalini kontrol et
            rc = win32event.WaitForSingleObject(self.stop_event, 1000)
            if rc == win32event.WAIT_OBJECT_0:
                break

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(RemoteAccessService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(RemoteAccessService)
