import os
import sys
from dotenv import load_dotenv
import tkinter as tk
import subprocess
from tkinter import messagebox

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# .env 파일에서 환경 변수 로드
dotenv_path = get_resource_path(".env")
load_dotenv(dotenv_path)
global_password = os.getenv("PASSWORD", "default_password")

def run_command_with_sudo(command, password):
    try:
        process = subprocess.Popen(
            f'echo {password} | sudo -S {command}',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, error = process.communicate()
        return output.decode().strip(), error.decode().strip(), process.returncode
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")
        return "", str(e), 1

def get_current_status():
    command = "networksetup -getinfo Wi-Fi"
    output, error, returncode = run_command_with_sudo(command, global_password)
    if returncode == 0:
        if "DHCP Configuration" in output:
            return "[현재 상태]: 일반 Wi-Fi 사용 중"
        elif "IP address" in output and "DHCP Configuration" not in output:
            return "[현재 상태]: 아이폰 핫스팟 수동 IP 설정 중"
        else:
            return "[현재 상태]: 미설정"
    else:
        return "[현재 상태]: 오류 발생"

def set_manual_ip():
    ip_address  = "192.168.100.10" # 회사에서 요구하는 ip로 변경
    subnet_mask = "255.255.255.0"  # 회사에서 요구하는 서브넷 마스크로 변경
    gateway     = "192.168.100.1"  # 회사에서 요구하는 게이트웨이로 변경

    command = f"networksetup -setmanual Wi-Fi {ip_address} {subnet_mask} {gateway}"
    run_command_with_sudo(command, global_password)
    update_status_button()

def set_dhcp():
    command = "networksetup -setdhcp Wi-Fi"
    run_command_with_sudo(command, global_password)
    update_status_button()

def update_status_button():
    global status_button
    status = get_current_status()
    status_button.config(text=status)

def run_gui():
    global status_button

    root = tk.Tk()
    root.title("Network Setup Tool")

    width, height = 300, 150
    screen_width = root.winfo_screenwidth()
    x, y = screen_width - width * 2, 0
    root.geometry(f'{width}x{height}+{x}+{y}')

    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    manual_button = tk.Button(
        frame, text="아이폰 핫스팟 세팅",
        command=set_manual_ip, bg='lightgrey',
        activebackground='lightgrey'
    )
    manual_button.pack(pady=10)

    dhcp_button = tk.Button(
        frame, text="일반 Wi-Fi 세팅",
        command=set_dhcp, bg='lightgrey',
        activebackground='lightgrey'
    )
    dhcp_button.pack(pady=10)

    status_button = tk.Button(
        root,
        text="상태 확인 중...",
        bg='lightgrey',
        anchor='center',
        justify='center'
    )
    status_button.pack(side=tk.BOTTOM, fill=tk.X)

    # 상태 초기화
    update_status_button()

    root.mainloop()

if __name__ == "__main__":
    run_gui()
