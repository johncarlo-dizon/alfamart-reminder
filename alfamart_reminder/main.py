import sys
import os
import subprocess
import argparse
import winsound
import ctypes
import webbrowser
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Default Configuration Parameters
DEFAULT_NTP_SERVER = "time1.google.com"
EXE_PATH = r"C:\Reminder_v2\Alfamart_Reminder.exe"
WINDOW_HEADER_TITLE = "Alfamart Reminder"
ACK_LOG_PATH = r"C:\Reminder_v2\ack_logs.txt"

# Default Shifts including both Cash Pick-Up & E-Services Tasks
DEFAULT_SHIFTS = [
    {
        "time": "03:00",
        "title": "03:00 am Reminder",
        "msg": "1. Proceed sa Cash Pick-Up!\n2. Laging isara ang storage door\n3. Siguraduhing naka-combination mode ang vault.",
        "type": "standard"
    },
    {
        "time": "06:00",
        "title": "6:00 AM REMINDER!",
        "msg": "MAG LOG IN SA E-SERVICES.",
        "type": "eservices_login"
    },
    {
        "time": "21:26",
        "title": "9:26 PM Reminder",
        "msg": "1. Proceed sa Cash Pick-Up!\n2. Laging isara ang storage door\n3. Siguraduhing naka-combination mode ang vault.",
        "type": "standard"
    },
    {
        "time": "15:00",
        "title": "3:00pm Reminder",
        "msg": "1. I-secure ang benta ng Opening shift at pending sales sa vault.\n2. Proceed sa Cash Pick-Up!\n3. Laging isara ang storage door\n4. Siguraduhing naka-combination mode ang vault.",
        "type": "standard"
    },
    {
        "time": "00:37",
        "title": "12:37 AM Reminder",
        "msg": "1. Proceed sa Cash Pick-Up!\n2. Laging isara ang storage door\n3. Siguraduhing naka-combination mode ang vault.",
        "type": "standard"
    },
    {
        "time": "00:36",
        "title": "12:36 AM REMINDER!",
        "msg": "MAG EOD SA E-SERVICES.",
        "type": "eservices_eod"
    }
]

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
    sys.exit(0)


class InstallationWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

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

        header_frame = tk.Frame(self.root, bg="#FFFFFF", pady=10)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame, text="SYSTEM INITIALIZATION & TIME UPDATER",
            font=("Segoe UI", 11, "bold"), fg="#000000", bg="#FFFFFF"
        ).pack()

        status_frame = tk.Frame(self.root, bg="#FFFFFF", padx=20)
        status_frame.pack(fill="x")

        self.status_label = tk.Label(
            status_frame, text="Starting installation...",
            font=("Segoe UI", 9, "italic"), fg="#555555", bg="#FFFFFF"
        )
        self.status_label.pack(anchor="w", pady=(0, 5))

        self.progress = ttk.Progressbar(status_frame, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(fill="x")

        log_frame = tk.LabelFrame(self.root, text=" Installation Logs ", font=("Segoe UI", 8, "bold"), bg="#FFFFFF", padx=10, pady=5)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(10, 5))

        self.log_box = tk.Text(log_frame, height=10, font=("Consolas", 8), bg="#F8F9FA", fg="#1E1E1E", bd=1, relief="solid")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=log_scroll.set)

        self.log_box.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

        btn_frame = tk.Frame(self.root, bg="#FFFFFF", pady=12)
        btn_frame.pack(fill="x", side="bottom")

        self.ok_btn = tk.Button(
            btn_frame, text="OK", font=("Segoe UI", 9, "bold"),
            bg="#E1E1E1", fg="#000000", activebackground="#CCCCCC",
            padx=30, pady=4, bd=1, relief="solid", state="disabled", command=self.finish_setup
        )
        self.ok_btn.pack()

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

        # Step 1: NTP Time Sync
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

        # Step 2: Task Scheduler Registration
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
            layout_type = shift.get("type", "standard")

            self.update_progress(prog_val, f"Adding Task: {task_name} ({formatted_time})...")

            ps_script = f'''
            $action = New-ScheduledTaskAction -Execute "{EXE_PATH}" -Argument '--custom "{safe_title}" "{safe_msg}" --type "{layout_type}"'
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

        self.update_progress(100, "Initialization Complete!")
        self.log(f"\nCompleted! {installed_count}/{total_shifts} tasks created in Task Scheduler.")

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

    def finish_setup(self):
        self.root.destroy()
        # Sequence Preview Dialogs after setup button click
        show_reminder_gui("Sample Reminder", "1. Proceed sa Cash Pick-Up!\n2. Laging isara ang storage door\n3. Siguraduhing naka-combination mode ang vault.", layout_type="standard")
        show_reminder_gui("Sample REMINDER!", "MAG LOG IN SA E-SERVICES.", layout_type="eservices_login")
        show_reminder_gui(
            "Sample Announcement", "This is a sample special reminder with a link button.",
            layout_type="special", btn_name="VIEW DETAILS", btn_link="https://apps.atp.ph/"
        )


LAYOUT_TYPE_LABELS = {
    "standard": "CASH PICKUP",
    "eservices_login": "E-SERVICES LOGIN",
    "eservices_eod": "E-SERVICES EOD",
    "special": "SPECIAL",
}


def log_ack_click(store_code="", store_name="", layout_type=""):
    """Append one line to the local ack log next to the exe.
    Local file write only — deliberately no network code here.
    Best-effort: a logging hiccup should never block the popup closing."""
    try:
        os.makedirs(os.path.dirname(ACK_LOG_PATH), exist_ok=True)
        now = datetime.now()
        timestamp = f"{now.strftime('%Y-%m-%d')} {now.strftime('%H%M')}"
        type_label = LAYOUT_TYPE_LABELS.get(layout_type, (layout_type or "UNKNOWN").upper())
        line = f"User clicked OK button {timestamp} [{type_label}] {store_code or ''} {store_name or ''}".rstrip()
        with open(ACK_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def show_reminder_gui(sub_title, message, layout_type="standard",
                       s1_title=None, s1_sub=None, s1_body=None,
                       s2_title=None, s2_sub=None, s2_body=None,
                       warning=None, btn_name=None, btn_link=None,
                       store_code=None, store_name=None):
    """Renders the Standard Cash Pick-Up, Rich E-Services, and Special
    (link-button) UI Layouts dynamically.

    s1_*/s2_*/warning let the deployer override the step-checklist text per
    schedule entry. Any left as None fall back to the original hardcoded
    login/EOD copy so old-style --custom/--type calls still work unchanged.

    btn_name/btn_link are only used by layout_type == "special": they label
    a button that opens btn_link in the default browser when clicked.
    """
    root = tk.Tk()
    root.withdraw()

    root.title(WINDOW_HEADER_TITLE)
    root.configure(bg="#FFFFFF")
    root.attributes('-topmost', True)

    def safe_exit():
        try:
            root.destroy()
        finally:
            pass

    def ack_and_exit():
        # Only fires on an explicit OK click, not on window-close (X).
        log_ack_click(store_code, store_name, layout_type)
        safe_exit()

    root.protocol("WM_DELETE_WINDOW", safe_exit)

    # ---------------------------------------------------------------------
    # RICH E-SERVICES POPUP LAYOUT
    # ---------------------------------------------------------------------
    if layout_type in ["eservices_login", "eservices_eod"]:
        window_width = 560
        window_height = 420
        center_x = int((root.winfo_screenwidth() / 2) - (window_width / 2))
        center_y = int((root.winfo_screenheight() / 2) - (window_height / 2))
        root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        root.resizable(False, False)


        # Bell Header Banner
        header_frame = tk.Frame(root, bg="#FFFFFF", pady=8)
        header_frame.pack(fill="x")

        title_container = tk.Frame(header_frame, bg="#FFFFFF")
        title_container.pack()

        tk.Label(title_container, text="🔔", font=("Segoe UI", 24), fg="#D93025", bg="#FFFFFF").pack(side="left", padx=(0, 8))
        tk.Label(title_container, text=sub_title.upper(), font=("Impact", 22), fg="#0A2540", bg="#FFFFFF").pack(side="left")

        # Divider & Subheader
        div_frame = tk.Frame(root, bg="#FFFFFF")
        div_frame.pack(fill="x", padx=40)
        tk.Frame(div_frame, bg="#A0A0A0", height=1).pack(fill="x", pady=(0, 2))
        tk.Label(div_frame, text="HUWAG KALIMUTAN!", font=("Segoe UI", 9, "bold"), fg="#D93025", bg="#FFFFFF").pack()

        # Action Instruction
        action_text = message.strip() if message and message.strip() else (
            "MAG LOG IN SA E-SERVICES." if layout_type == "eservices_login" else "MAG EOD SA E-SERVICES."
        )
        tk.Label(root, text=action_text, font=("Segoe UI Black", 16, "bold"), fg="#0A2540", bg="#FFFFFF").pack(pady=(2, 6))

        # 2-Step Checklist Banner
        step_badge = tk.Frame(root, bg="#002060", padx=12, pady=2)
        step_badge.pack()
        tk.Label(step_badge, text="2-STEP CHECKLIST", font=("Segoe UI", 8, "bold"), fg="white", bg="#002060").pack()

        box_frame = tk.Frame(root, bg="#FFFFFF", pady=10)
        box_frame.pack()

        # Resolve step 1 (POS) text: use what was passed in, else the old hardcoded default
        s1_title_final = (s1_title or "POS").upper()
        s1_sub_final = (s1_sub or ("REGULAR POS LOGIN" if layout_type == "eservices_login" else "REGULAR POS EOD"))
        s1_body_final = (s1_body or ("Mag log in sa POS tulad ng\nnakasanayan." if layout_type == "eservices_login" else "Mag EOD sa POS\ntulad ng nakasanayan."))

        # Box 1 (POS)
        b1 = tk.Frame(box_frame, bg="#FFFFFF", bd=2, relief="solid", highlightbackground="#28A745")
        b1.config(highlightthickness=1, highlightcolor="#28A745")
        b1.grid(row=0, column=0, padx=10, ipadx=10, ipady=5)

        tk.Label(b1, text=f"❶ {s1_title_final}", font=("Segoe UI", 10, "bold"), fg="#28A745", bg="#FFFFFF").pack()
        tk.Label(b1, text=s1_sub_final, font=("Segoe UI", 8, "bold"), fg="#000000", bg="#FFFFFF").pack()
        tk.Label(b1, text=s1_body_final, font=("Segoe UI", 7), fg="#555555", bg="#FFFFFF", justify="center").pack()

        # Arrow Indicator
        tk.Label(box_frame, text="➔", font=("Segoe UI", 18, "bold"), fg="#002060", bg="#FFFFFF").grid(row=0, column=1)

        # Resolve step 2 (E-Services) text: use what was passed in, else the old hardcoded default
        s2_title_final = (s2_title or "E-SERVICES").upper()
        s2_sub_final = (s2_sub or ("E-SERVICES LOGIN" if layout_type == "eservices_login" else "E-SERVICES EOD"))
        s2_body_final = (s2_body or ("Mag log in sa E-Services\nkada Cash-In." if layout_type == "eservices_login" else "Mag EOD sa E-Services."))

        # Box 2 (E-Services)
        b2 = tk.Frame(box_frame, bg="#FFFFFF", bd=2, relief="solid", highlightbackground="#0056B3")
        b2.config(highlightthickness=1, highlightcolor="#0056B3")
        b2.grid(row=0, column=2, padx=10, ipadx=10, ipady=5)

        tk.Label(b2, text=f"❷ {s2_title_final}", font=("Segoe UI", 10, "bold"), fg="#0056B3", bg="#FFFFFF").pack()
        tk.Label(b2, text=s2_sub_final, font=("Segoe UI", 8, "bold"), fg="#000000", bg="#FFFFFF").pack()
        tk.Label(b2, text=s2_body_final, font=("Segoe UI", 7), fg="#555555", bg="#FFFFFF", justify="center").pack()

        # Warning Callout Box
        warn_box = tk.Frame(root, bg="#FFF3CD", bd=1, relief="solid", highlightbackground="#FFEEBA")
        warn_box.pack(fill="x", padx=35, pady=(0, 10), ipady=4)

        w_text = warning.strip() if warning and warning.strip() else (
            "UGALIIN MAG LOG IN AGAD SA E-SERVICES\nMATAPOS ANG POS REGULAR LOG IN\nPARA MAKAIWAS SA MGA TECHNICAL ERRORS"
            if layout_type == "eservices_login" else
            "UGALIIN MAG EOD SA E-SERVICES\nMATAPOS ANG POS REGULAR EOD\nPARA MAKAIWAS SA MGA TECHNICAL ERRORS"
        )

        tk.Label(warn_box, text="⚠️", font=("Segoe UI", 12), bg="#FFF3CD").pack(side="left", padx=8)
        tk.Label(warn_box, text=w_text, font=("Segoe UI", 7, "bold"), fg="#856404", bg="#FFF3CD", justify="left").pack(side="left")

        # Action Button
        ack_button = tk.Button(
            root, text="✔  OK, NAINTINDIHAN KO!", font=("Segoe UI", 9, "bold"),
            bg="#28A745", fg="white", activebackground="#218838", activeforeground="white",
            padx=25, pady=5, bd=0, cursor="hand2", command=ack_and_exit
        )
        ack_button.pack(pady=(0, 10))

    # ---------------------------------------------------------------------
    # SPECIAL POPUP LAYOUT (TITLE + MESSAGE + LINK BUTTON + OK)
    # ---------------------------------------------------------------------
    elif layout_type == "special":
        window_width = 560
        window_height = 380
        center_x = int((root.winfo_screenwidth() / 2) - (window_width / 2))
        center_y = int((root.winfo_screenheight() / 2) - (window_height / 2))
        root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        root.resizable(False, False)

        header_frame = tk.Frame(root, bg="#FFFFFF", pady=20)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame, text=sub_title.upper(), font=("Impact", 22),
            fg="#0A2540", bg="#FFFFFF"
        ).pack()

        div_frame = tk.Frame(root, bg="#FFFFFF")
        div_frame.pack(fill="x", padx=35)
        tk.Frame(div_frame, bg="#666666", height=2).pack(fill="x", pady=(0, 15))

        body_frame = tk.Frame(root, bg="#FFFFFF", padx=45, pady=6)
        body_frame.pack(fill="both", expand=True)

        tk.Label(
            body_frame, text=message, font=("Segoe UI", 13),
            fg="#1A1A1A", bg="#FFFFFF", justify="center", wraplength=460
        ).pack(anchor="center", fill="both", expand=True)

        # Link Button — opens btn_link in the default browser. It does NOT
        # close the popup or count as an acknowledgement by itself; the
        # operator still has to click "OK, NAINTINDIHAN KO!" below to close
        # the reminder (and to record the ack log entry).
        display_btn_name = (btn_name or "").strip() or "OPEN LINK"

        def open_link():
            link = (btn_link or "").strip()
            if link:
                try:
                    webbrowser.open(link)
                except Exception:
                    pass

        tk.Button(
            root, text=f"🔗  {display_btn_name}", font=("Segoe UI", 9, "bold"),
            bg="#0056B3", fg="white", activebackground="#00408a", activeforeground="white",
            padx=25, pady=5, bd=0, cursor="hand2", command=open_link
        ).pack(pady=(0, 8))

        # Bottom Button Section
        btn_frame = tk.Frame(root, bg="#FFFFFF", pady=10)
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame, text="✔  OK, NAINTINDIHAN KO!", font=("Segoe UI", 9, "bold"),
            bg="#28A745", fg="white", activebackground="#218838", activeforeground="white",
            padx=25, pady=5, bd=0, cursor="hand2", command=ack_and_exit
        ).pack()

    # ---------------------------------------------------------------------
    # STANDARD POPUP LAYOUT (CASH PICK-UP)
    # ---------------------------------------------------------------------
    else:
        window_width = 560
        window_height = 420
        center_x = int((root.winfo_screenwidth() / 2) - (window_width / 2))
        center_y = int((root.winfo_screenheight() / 2) - (window_height / 2))
        root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        root.resizable(False, False)

        # Header Section
        header_frame = tk.Frame(root, bg="#FFFFFF", pady=25)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame, text=sub_title.upper(), font=("Impact", 24),
            fg="#0A2540", bg="#FFFFFF"
        ).pack()

        # Divider
        div_frame = tk.Frame(root, bg="#FFFFFF")
        div_frame.pack(fill="x", padx=35)
        tk.Frame(div_frame, bg="#666666", height=2).pack(fill="x", pady=(0, 15))

        # Main Text Body Area
        body_frame = tk.Frame(root, bg="#FFFFFF", padx=50, pady=10)
        body_frame.pack(fill="both", expand=True)

        tk.Label(
            body_frame, text=message, font=("Segoe UI", 13),
            fg="#1A1A1A", bg="#FFFFFF", justify="left", wraplength=480
        ).pack(anchor="w", fill="both", expand=True)

        # Bottom Button Section (Kept intact)
        btn_frame = tk.Frame(root, bg="#FFFFFF", pady=25)
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame, text="✔  OK, NAINTINDIHAN KO!", font=("Segoe UI", 9, "bold"),
            bg="#28A745", fg="white", activebackground="#218838", activeforeground="white",
            padx=25, pady=5, bd=0, cursor="hand2", command=ack_and_exit
        ).pack()

    try:
        winsound.MessageBeep(winsound.MB_ICONINFORMATION)
    except Exception:
        pass

    root.deiconify()
    root.lift()
    root.focus_force()
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Alfamart Reminder Popup")
    parser.add_argument("--custom", nargs=2, metavar=('TITLE', 'MESSAGE'), help="Custom Title and Message")
    parser.add_argument("--type", default="standard", help="Layout type (standard, eservices_login, eservices_eod)")
    parser.add_argument("--s1_title", default=None, help="Step 1 header override")
    parser.add_argument("--s1_sub", default=None, help="Step 1 subtitle override")
    parser.add_argument("--s1_body", default=None, help="Step 1 body text override")
    parser.add_argument("--s2_title", default=None, help="Step 2 header override")
    parser.add_argument("--s2_sub", default=None, help="Step 2 subtitle override")
    parser.add_argument("--s2_body", default=None, help="Step 2 body text override")
    parser.add_argument("--warning", default=None, help="Bottom warning callout override")
    parser.add_argument("--btn_name", default=None, help="Link button label (layout type 'special')")
    parser.add_argument("--btn_link", default=None, help="Link button URL (layout type 'special')")
    parser.add_argument("--store_code", default=None, help="Store code, embedded in ack log lines")
    parser.add_argument("--store_name", default=None, help="Store name, embedded in ack log lines")
    parser.add_argument("--init", action="store_true", help="Initialize Time Sync and Default Scheduler")
    args = parser.parse_args()

    flag_path = r"C:\Windows\Temp\alfamart_reminder_initialized.flag"

    if not args.custom and (args.init or not os.path.exists(flag_path)):
        if not is_admin():
            run_as_admin()

        setup_win = InstallationWindow()
        setup_win.run_setup()
        return

    sub_title = "Scheduled Reminder"
    message = "1. Proceed to Cash Pick-Up!\n2. Secure vault and storage doors."

    if args.custom:
        sub_title = args.custom[0]
        message = args.custom[1].replace(" | ", "\n")

    def restore_pipes(text):
        return text.replace(" | ", "\n") if text else text

    show_reminder_gui(
        sub_title, message, layout_type=args.type,
        s1_title=args.s1_title,
        s1_sub=args.s1_sub,
        s1_body=restore_pipes(args.s1_body),
        s2_title=args.s2_title,
        s2_sub=args.s2_sub,
        s2_body=restore_pipes(args.s2_body),
        warning=restore_pipes(args.warning),
        btn_name=args.btn_name,
        btn_link=args.btn_link,
        store_code=args.store_code,
        store_name=args.store_name,
    )


if __name__ == "__main__":
    main()