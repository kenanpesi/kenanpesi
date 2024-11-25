# Installer script for Remote Access Service

!include "MUI2.nsh"
!include "FileFunc.nsh"

Name "Remote Access Service"
OutFile "RemoteAccessSetup.exe"
InstallDir "$PROGRAMFILES\RemoteAccess"

!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "Turkish"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    
    # Tüm dosyaları kopyala
    File /r "build\exe.win-amd64-3.11\*.*"
    
    # Windows servisi olarak kur
    ExecWait '"$INSTDIR\service_handler.exe" --startup auto install'
    ExecWait 'net start RemoteAccessService'
    
    # Kaldırma bilgilerini kaydet
    WriteUninstaller "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RemoteAccess" \
                     "DisplayName" "Remote Access Service"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RemoteAccess" \
                     "UninstallString" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    # Servisi durdur ve kaldır
    ExecWait 'net stop RemoteAccessService'
    ExecWait '"$INSTDIR\service_handler.exe" remove'
    
    # Dosyaları sil
    RMDir /r "$INSTDIR"
    
    # Registry kayıtlarını temizle
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RemoteAccess"
SectionEnd
