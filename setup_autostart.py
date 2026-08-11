"""Spusť jednou jako správce nebo bez – zapíše autostart do registru."""
import winreg
import sys
import os

def setup_autostart():
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    run_pyw = os.path.abspath(os.path.join(os.path.dirname(__file__), "run.pyw"))
    
    command = f'"{pythonw}" "{run_pyw}"'
    
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "MedBox", 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        print(f"✅ Autostart nastaven: {command}")
    except Exception as e:
        print(f"❌ Chyba: {e}")

if __name__ == "__main__":
    setup_autostart()
