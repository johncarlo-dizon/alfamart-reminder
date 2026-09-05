import sys
import os
import subprocess
import argparse
import winsound
import ctypes
import tkinter as tk
from tkinter import ttk

# Default Configuration Parameters
DEFAULT_NTP_SERVER = "time1.google.com"
EXE_PATH = r"C:\Reminder_v2\Alfamart_Reminder.exe"
WINDOW_HEADER_TITLE = "Alfamart Reminder"

DEFAULT_SHIFTS = [
    {
        "time": "03:00",
        "title": "03:00 am Reminder (v2)",
        "msg": "1. Proceed sa Cash Pick-Up!\n2. Laging isara ang storage door\n3. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "06:00",
        "title": "6:00am Reminder (v2)",
        "msg": "1. I-secure ang benta ng graveyard at pending sales.\n2. Proceed sa Cash Pick-Up!\n3. Laging isara ang storage door\n4. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "12:00",
        "title": "12:00nn Reminder (v2)",
        "msg": "1. Proceed sa Cash Pick-Up!\n2. Laging isara ang storage door\n3. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "15:00",
        "title": "3:00pm Reminder (v2)",
        "msg": "1. I-secure ang benta ng Opening shift at pending sales sa vault.\n2. Proceed sa Cash Pick-Up!\n3. Laging isara ang storage door\n4. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "18:00",
        "title": "6:00pm Reminder (v2)",
        "msg": "1. Proceed sa Cash Pick-Up!\n2. Laging isara ang storage door\n3. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "22:00",
        "title": "10:00pm Reminder (v2)",
        "msg": "1. I-secure ang benta ng closing shift at pending sales sa vault.\n2. Proceed sa Cash Pick-Up!\n3. Laging isara ang storage door\n4. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "11:34",
        "title": "11:34am Reminder",
        "msg": "1. Proceed sa Cash Pick-Up!\n2. Laging isara ang storage door\n3. Siguraduhing naka-combination mode ang vault."
    },
]

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """Relaunches the executable as Administrator if privileges are missing."""
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
    sys.exit(0)


class InstallationWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window while configuring geometry to prevent flashing

        self.root.title(WINDOW_HEADER_TITLE)
        self.root.configure(bg="#FFFFFF")
        
        self.root.attributes('-topmost', True)

        window_width = 540
        window_height = 420
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.resizable(False, False)

        # Header Frame
        header_frame = tk.Frame(self.root, bg="#FFFFFF", pady=10)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame, text="SYSTEM INITIALIZATION & TIME UPDATER",
            font=("Segoe UI", 11, "bold"), fg="#000000", bg="#FFFFFF"
        ).pack()

        # Status & Progress Frame
        status_frame = tk.Frame(self.root, bg="#FFFFFF", padx=20)
        status_frame.pack(fill="x")

        self.status_label = tk.Label(
            status_frame, text="Starting installation...",
            font=("Segoe UI", 9, "italic"), fg="#555555", bg="#FFFFFF"
        )
        self.status_label.pack(anchor="w", pady=(0, 5))

        self.progress = ttk.Progressbar(status_frame, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(fill="x")

        # Logs Console Frame
        log_frame = tk.LabelFrame(self.root, text=" Installation Logs ", font=("Segoe UI", 8, "bold"), bg="#FFFFFF", padx=10, pady=5)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(10, 5))

        self.log_box = tk.Text(log_frame, height=10, font=("Consolas", 8), bg="#F8F9FA", fg="#1E1E1E", bd=1, relief="solid")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=log_scroll.set)

        self.log_box.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

        # Action Button Frame
        btn_frame = tk.Frame(self.root, bg="#FFFFFF", pady=12)
        btn_frame.pack(fill="x", side="bottom")

        self.ok_btn = tk.Button(
            btn_frame, text="OK", font=("Segoe UI", 9, "bold"),
            bg="#E1E1E1", fg="#000000", activebackground="#CCCCCC",
            padx=30, pady=4, bd=1, relief="solid", state="disabled", command=self.root.destroy
        )
        self.ok_btn.pack()

        # Unhide and force focus after initialization layout is built
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def log(self, text):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.config(state="disabled")
        self.log_box.see(tk.END)
        self.root.update()

    def update_progress(self, val, status):
        self.progress['value'] = val
        self.status_label.config(text=status)
        self.root.update()

    def run_setup(self):
        self.log("--- Starting Setup & Initialization ---")
        
        # Step 1: Configure Time Sync
        self.update_progress(10, "Configuring Google NTP Time Server...")
        self.log(f"Setting NTP Server to: {DEFAULT_NTP_SERVER}")
        
        try:
            cmd1 = f'w32tm /config /manualpeerlist:"{DEFAULT_NTP_SERVER}" /syncfromflags:manual /reliable:YES /update'
            subprocess.run(cmd1, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log(" [SUCCESS] NTP Server registered.")
        except Exception as e:
            self.log(f" [WARNING] NTP config warning: {str(e).strip()}")

        self.update_progress(30, "Resyncing Windows System Time...")
        try:
            subprocess.run('net stop w32time && net start w32time', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            res = subprocess.run('w32tm /resync /force', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0:
                self.log(" [SUCCESS] System time corrected successfully.")
            else:
                self.log(" [INFO] Time resync triggered.")
        except Exception as e:
            self.log(f" [ERROR] Time sync failed: {str(e).strip()}")

        # Step 2: Register Default Shift Tasks via PowerShell
        self.update_progress(50, "Registering Default Shift Tasks...")
        self.log("\n--- Registering Task Scheduler Jobs ---")

        installed_count = 0
        total_shifts = len(DEFAULT_SHIFTS)

        for idx, shift in enumerate(DEFAULT_SHIFTS):
            prog_val = 50 + int(((idx + 1) / total_shifts) * 40)
            formatted_time = shift["time"].zfill(5)
            task_id = formatted_time.replace(":", "")
            task_name = f"Alfamart_Reminder_Shift_{task_id}"

            safe_title = shift["title"].replace('"', '`"')
            safe_msg = shift["msg"].replace('\r', '').replace('\n', ' | ').replace('"', '`"')

            self.update_progress(prog_val, f"Adding Task: {task_name} ({formatted_time})...")

            ps_script = f'''
            $action = New-ScheduledTaskAction -Execute "{EXE_PATH}" -Argument '--custom "{safe_title}" "{safe_msg}"'
            $trigger = New-ScheduledTaskTrigger -Daily -At "{formatted_time}"
            $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
            Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -Settings $settings -User "$env:USERNAME" -RunLevel Highest -Force
            '''

            ps_cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]

            res = subprocess.run(
                ps_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if res.returncode == 0:
                installed_count += 1
                self.log(f" [SUCCESS] Task Installed: {task_name}")
            else:
                err_msg = res.stderr.strip() or res.stdout.strip()
                self.log(f" [FAILED] {task_name} -> {err_msg}")

        # Step 3: Complete
        self.update_progress(100, "Initialization Complete!")
        self.log(f"\nCompleted! {installed_count}/{total_shifts} tasks created in Task Scheduler.")
        
        # Save Flag
        try:
            with open(r"C:\Windows\Temp\alfamart_reminder_initialized.flag", "w") as f:
                f.write("initialized")
        except Exception:
            pass

        self.ok_btn.config(state="normal")
        try:
            winsound.MessageBeep(winsound.MB_ICONINFORMATION)
        except Exception:
            pass
        
        self.root.mainloop()


def show_reminder_gui(sub_title, message):
    """Displays the custom White Theme Reminder Dialog without screen flash."""
    root = tk.Tk()
    root.withdraw()  # Hide window while configuring geometry to prevent flashing

    root.title(WINDOW_HEADER_TITLE)
    root.configure(bg="#FFFFFF")
    
    root.attributes('-topmost', True)

    window_width = 500
    window_height = 250
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    root.resizable(False, False)

    def safe_exit():
        try:
            root.destroy()
        finally:
            sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", safe_exit)

    header_frame = tk.Frame(root, bg="#FFFFFF", pady=12)
    header_frame.pack(fill="x")

    header_label = tk.Label(
        header_frame, text=sub_title, font=("Segoe UI", 12, "bold"),
        fg="#000000", bg="#FFFFFF"
    )
    header_label.pack()

    body_frame = tk.Frame(root, bg="#FFFFFF", padx=25, pady=5)
    body_frame.pack(fill="both", expand=True)

    msg_label = tk.Label(
        body_frame, text=message, font=("Segoe UI", 10),
        fg="#333333", bg="#FFFFFF", justify="left", wraplength=440
    )
    msg_label.pack(anchor="w", fill="both", expand=True)

    btn_frame = tk.Frame(root, bg="#FFFFFF", pady=12)
    btn_frame.pack(fill="x")

    ack_button = tk.Button(
        btn_frame, text="OK", font=("Segoe UI", 9, "bold"),
        bg="#E1E1E1", fg="#000000", activebackground="#CCCCCC",
        padx=25, pady=4, bd=1, relief="solid", cursor="hand2", command=safe_exit
    )
    ack_button.pack()

    try:
        winsound.MessageBeep(winsound.MB_ICONINFORMATION)
    except Exception:
        pass

    # Unhide and focus window smoothly once centering and layouts are applied
    root.deiconify()
    root.lift()
    root.focus_force()

    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Alfamart Reminder Popup")
    parser.add_argument("--custom", nargs=2, metavar=('TITLE', 'MESSAGE'), help="Custom Title and Message")
    parser.add_argument("--init", action="store_true", help="Initialize Time Sync and Default Scheduler")
    args = parser.parse_args()

    flag_path = r"C:\Windows\Temp\alfamart_reminder_initialized.flag"

    # Self-Initialize setup on first execution or --init — but never for a plain reminder popup
    if not args.custom and (args.init or not os.path.exists(flag_path)):
        if not is_admin():
            run_as_admin()
        
        setup_win = InstallationWindow()
        setup_win.run_setup()

    # Window Body Sub-title and Messages when triggered by scheduler
    sub_title = "Scheduled Reminder"
    message = "1. Proceed to Cash Pick-Up!\n2. Secure vault and storage doors."

    if args.custom:
        sub_title = args.custom[0]
        message = args.custom[1].replace(" | ", "\n")

    show_reminder_gui(sub_title, message)


if __name__ == "__main__":
    main()