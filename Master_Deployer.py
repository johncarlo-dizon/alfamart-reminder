#Master_Deployer.py
import sys
import os
import json
import base64
import socket
import time
import concurrent.futures
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
import paramiko

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
SCHEDULES_FILE = os.path.join(BASE_DIR, "schedules.json")
STORES_FILE = os.path.join(BASE_DIR, "stores.txt")

DEFAULT_TEMPLATES = [
    {
        "time": "03:00",
        "title": "03:00 am Reminder (v2)",
        "lines": "1. Proceed sa Cash Pick-Up! | 2. Laging isara ang storage door | 3. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "06:00",
        "title": "6:00am Reminder (v2)",
        "lines": "1. I-secure ang benta ng graveyard at pending sales. | 2. Proceed sa Cash Pick-Up! | 3. Laging isara ang storage door | 4. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "12:00",
        "title": "12:00nn Reminder (v2)",
        "lines": "1. Proceed sa Cash Pick-Up! | 2. Laging isara ang storage door | 3. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "15:00",
        "title": "3:00pm Reminder (v2)",
        "lines": "1. I-secure ang benta ng Opening shift at pending sales sa vault. | 2. Proceed sa Cash Pick-Up! | 3. Laging isara ang storage door | 4. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "18:00",
        "title": "6:00pm Reminder (v2)",
        "lines": "1. Proceed sa Cash Pick-Up! | 2. Laging isara ang storage door | 3. Siguraduhing naka-combination mode ang vault."
    },
    {
        "time": "22:00",
        "title": "10:00pm Reminder (v2)",
        "lines": "1. I-secure ang benta ng closing shift at pending sales sa vault. | 2. Proceed sa Cash Pick-Up! | 3. Laging isara ang storage door | 4. Siguraduhing naka-combination mode ang vault."
    }
]


def load_stores():
    stores = []
    if os.path.exists(STORES_FILE):
        with open(STORES_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split(",")
                    if len(parts) >= 3:
                        stores.append({
                            "ip": parts[0].strip(),
                            "user": parts[1].strip(),
                            "pwd": parts[2].strip()
                        })
    return stores


def load_schedules():
    if os.path.exists(SCHEDULES_FILE):
        try:
            with open(SCHEDULES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    save_schedules(DEFAULT_TEMPLATES)
    return DEFAULT_TEMPLATES


def save_schedules(schedules):
    with open(SCHEDULES_FILE, "w") as f:
        json.dump(schedules, f, indent=2)


def run_ssh_command(ip, user, pwd, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=user, password=pwd, timeout=5)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='ignore')
        err = stderr.read().decode('utf-8', errors='ignore')
        ssh.close()
        return True, out, err
    except Exception as e:
        return False, "", str(e)


def test_connection(ip, user, pwd):
    """Bare SSH connect attempt, used purely to classify *why* a store is unreachable
    before we go any further (auth vs network vs something else)."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=user, password=pwd, timeout=6)
        ssh.close()
        return True, None
    except paramiko.AuthenticationException:
        return False, "AUTH_FAILED"
    except (paramiko.SSHException, socket.timeout, socket.error, OSError) as e:
        return False, f"CONNECTION_ERROR: {e}"
    except Exception as e:
        return False, f"UNKNOWN_ERROR: {e}"


class MasterITDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Alfamart IT Master Task Deployer")
        self.root.configure(bg="#f4f4f4")

        window_width = 820
        window_height = 590
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.resizable(False, False)

        self.stores = load_stores()
        self.schedules = load_schedules()
        self.selected_schedule_index = None
        self.log_queue = queue.Queue()

        main_container = tk.Frame(self.root, bg="#f4f4f4")
        main_container.pack(fill="both", expand=True, padx=12, pady=12)

        master_frame = tk.LabelFrame(main_container, text=" IT Master Schedule Library ", font=("Segoe UI", 9, "bold"), bg="#f4f4f4", padx=10, pady=3)
        master_frame.pack(fill="x", pady=(0, 6))

        table_frame = tk.Frame(master_frame, bg="#f4f4f4")
        table_frame.pack(side="left", fill="y", padx=(0, 10))

        columns = ("Time", "Title")
        self.sched_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=4)
        self.sched_tree.heading("Time", text="Time")
        self.sched_tree.heading("Title", text="Popup Title")
        self.sched_tree.column("Time", width=65)
        self.sched_tree.column("Title", width=220)
        self.sched_tree.pack(side="left", fill="y")
        self.sched_tree.bind("<<TreeviewSelect>>", self.on_schedule_select)

        sched_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.sched_tree.yview)
        self.sched_tree.configure(yscrollcommand=sched_scroll.set)
        sched_scroll.pack(side="right", fill="y")

        form_frame = tk.Frame(master_frame, bg="#f4f4f4")
        form_frame.pack(side="right", fill="both", expand=True)

        tk.Label(form_frame, text="Time (HH:MM):", bg="#f4f4f4", font=("Segoe UI", 8, "bold")).grid(row=0, column=0, sticky="w")
        self.time_entry = tk.Entry(form_frame, width=12, font=("Segoe UI", 9))
        self.time_entry.grid(row=0, column=1, sticky="w", pady=1)

        tk.Label(form_frame, text="Title:", bg="#f4f4f4", font=("Segoe UI", 8, "bold")).grid(row=1, column=0, sticky="w")
        self.title_entry = tk.Entry(form_frame, width=38, font=("Segoe UI", 9))
        self.title_entry.grid(row=1, column=1, sticky="w", pady=1)

        tk.Label(form_frame, text="Message Lines:", bg="#f4f4f4", font=("Segoe UI", 8, "bold")).grid(row=2, column=0, sticky="nw")
        self.msg_entry = tk.Text(form_frame, width=38, height=3, font=("Segoe UI", 8))
        self.msg_entry.grid(row=2, column=1, sticky="w", pady=1)

        edit_btn_frame = tk.Frame(form_frame, bg="#f4f4f4")
        edit_btn_frame.grid(row=3, column=0, columnspan=2, pady=(3, 0), sticky="ew")

        tk.Button(edit_btn_frame, text="➕ Add New", font=("Segoe UI", 8), bg="#28A745", fg="white", command=self.add_schedule).pack(side="left", padx=2)
        tk.Button(edit_btn_frame, text="💾 Update", font=("Segoe UI", 8), bg="#007ACC", fg="white", command=self.update_schedule).pack(side="left", padx=2)
        tk.Button(edit_btn_frame, text="🗑️ Delete", font=("Segoe UI", 8), bg="#D9534F", fg="white", command=self.delete_schedule).pack(side="left", padx=2)
        tk.Button(edit_btn_frame, text="Clear", font=("Segoe UI", 8), command=self.clear_form).pack(side="right", padx=2)

        store_frame = tk.LabelFrame(main_container, text=" Target Stores Selection ", font=("Segoe UI", 9, "bold"), bg="#f4f4f4", padx=10, pady=3)
        store_frame.pack(fill="x", pady=(0, 6))

        ctrl_btn_frame = tk.Frame(store_frame, bg="#f4f4f4")
        ctrl_btn_frame.pack(fill="x", pady=(0, 2))

        tk.Button(ctrl_btn_frame, text="Select All", font=("Segoe UI", 8), command=self.select_all_stores).pack(side="left", padx=2)
        tk.Button(ctrl_btn_frame, text="Deselect All", font=("Segoe UI", 8), command=self.deselect_all_stores).pack(side="left", padx=2)
        tk.Button(ctrl_btn_frame, text="🔄 Reload stores.txt", font=("Segoe UI", 8), command=self.reload_stores_list).pack(side="right", padx=2)

        list_container = tk.Frame(store_frame, bg="#f4f4f4")
        list_container.pack(fill="x")

        self.store_vars = {}
        canvas = tk.Canvas(list_container, height=65, bg="#ffffff", highlightthickness=1, highlightbackground="#ccc")
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.scrollable_frame = scrollable_frame

        deploy_btn_frame = tk.Frame(main_container, bg="#f4f4f4")
        deploy_btn_frame.pack(fill="x", pady=(0, 6))

        self.deploy_btn = tk.Button(
            deploy_btn_frame, text="🚀 CLEAN UPDATE ALL & PUSH TASKS TO STORES", font=("Segoe UI", 10, "bold"),
            bg="#28A745", fg="white", pady=5, command=self.clean_update_and_push
        )
        self.deploy_btn.pack(fill="x")

        # --- Live progress status ---
        progress_frame = tk.Frame(main_container, bg="#f4f4f4")
        progress_frame.pack(fill="x", pady=(0, 4))

        self.status_label = tk.Label(
            progress_frame, text="Idle — ready to deploy",
            font=("Segoe UI", 8, "italic"), fg="#555555", bg="#f4f4f4"
        )
        self.status_label.pack(anchor="w")

        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(2, 0))

        log_frame = tk.LabelFrame(main_container, text=" Deployment Execution Results ", font=("Segoe UI", 9, "bold"), bg="#f4f4f4", padx=10, pady=3)
        log_frame.pack(fill="both", expand=True)

        log_container = tk.Frame(log_frame, bg="#f4f4f4")
        log_container.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_container, font=("Consolas", 8), wrap="word", state="disabled")
        log_scroll = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

        self.refresh_schedule_table()
        self.populate_store_checkboxes()

    def refresh_schedule_table(self):
        for item in self.sched_tree.get_children():
            self.sched_tree.delete(item)
        self.schedules.sort(key=lambda x: x["time"])
        for idx, s in enumerate(self.schedules):
            self.sched_tree.insert("", tk.END, iid=idx, values=(s["time"], s["title"]))
        save_schedules(self.schedules)

    def on_schedule_select(self, event):
        selected = self.sched_tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        self.selected_schedule_index = idx
        s = self.schedules[idx]

        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, s["time"])
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, s["title"])
        self.msg_entry.delete("1.0", tk.END)
        self.msg_entry.insert("1.0", s["lines"])

    def clear_form(self):
        self.selected_schedule_index = None
        self.sched_tree.selection_remove(self.sched_tree.selection())
        self.time_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.msg_entry.delete("1.0", tk.END)

    def add_schedule(self):
        t = self.time_entry.get().strip()
        title = self.title_entry.get().strip()
        lines = self.msg_entry.get("1.0", tk.END).strip()

        if not t or not title or not lines:
            messagebox.showwarning("Input Error", "Time, Title, and Message Lines are required.")
            return

        self.schedules.append({"time": t, "title": title, "lines": lines})
        self.refresh_schedule_table()
        self.clear_form()

    def update_schedule(self):
        if self.selected_schedule_index is None:
            messagebox.showwarning("Selection Error", "Please select a schedule from the list to update.")
            return

        t = self.time_entry.get().strip()
        title = self.title_entry.get().strip()
        lines = self.msg_entry.get("1.0", tk.END).strip()

        self.schedules[self.selected_schedule_index] = {"time": t, "title": title, "lines": lines}
        self.refresh_schedule_table()
        self.clear_form()

    def delete_schedule(self):
        if self.selected_schedule_index is None:
            messagebox.showwarning("Selection Error", "Please select a schedule from the list to delete.")
            return

        del self.schedules[self.selected_schedule_index]
        self.refresh_schedule_table()
        self.clear_form()

    def populate_store_checkboxes(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.store_vars.clear()

        if not self.stores:
            tk.Label(self.scrollable_frame, text="No stores found in stores.txt", bg="#ffffff", fg="red").pack(anchor="w", padx=5, pady=2)
            return

        for idx, s in enumerate(self.stores):
            var = tk.BooleanVar(value=True)
            ip = s["ip"]
            self.store_vars[ip] = var
            chk = tk.Checkbutton(
                self.scrollable_frame, text=f"Store #{idx+1} — {ip} ({s['user']})",
                variable=var, bg="#ffffff", activebackground="#ffffff", anchor="w"
            )
            chk.pack(fill="x", anchor="w", padx=5, pady=1)

    def select_all_stores(self):
        for var in self.store_vars.values():
            var.set(True)

    def deselect_all_stores(self):
        for var in self.store_vars.values():
            var.set(False)

    def reload_stores_list(self):
        self.stores = load_stores()
        self.populate_store_checkboxes()
        self.append_log("System: Reloaded stores.txt successfully.")

    def append_log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)

    def get_selected_stores(self):
        return [s for s in self.stores if self.store_vars.get(s["ip"], tk.BooleanVar()).get()]

    def clean_update_and_push(self):
        selected_stores = self.get_selected_stores()
        if not selected_stores:
            messagebox.showwarning("Selection Error", "Please select at least one store PC to push schedules.")
            return

        if not self.schedules:
            messagebox.showwarning("Schedule Error", "Your Master Schedule Library is empty. Add tasks first.")
            return

        if not messagebox.askyesno("Confirm Clean Update", f"This will CLEAR ALL existing reminder tasks on {len(selected_stores)} store PC(s) and install the {len(self.schedules)} master tasks.\n\nProceed?"):
            return

        self.deploy_btn.config(state="disabled", text="⏳ Deploying...")
        self.progress.config(mode="determinate", maximum=len(selected_stores), value=0)
        self.status_label.config(text=f"Starting deployment to {len(selected_stores)} store(s)...")

        self.append_log(f"\n==================================================")
        self.append_log(f"--- STARTING CLEAN UPDATE TO {len(selected_stores)} STORE(S) ---")
        self.append_log(f"==================================================")

        app_path = r"C:\Reminder_v2\Alfamart_Reminder.exe"

        def deploy_worker(store):
            ip, user, pwd = store["ip"], store["user"], store["pwd"]

            def log(text):
                self.log_queue.put(("log", f"[STORE: {ip}] {text}"))

            log("Connecting...")
            self.log_queue.put(("status", f"Connecting to {ip}..."))

            # 0. Verify we can actually authenticate before doing anything else.
            # This separates "bad credentials / account locked" from "no user logged in"
            # instead of letting a connection failure masquerade as a user-detection issue.
            conn_ok, conn_err = test_connection(ip, user, pwd)
            if not conn_ok:
                if conn_err == "AUTH_FAILED":
                    log("FAILED — SSH authentication rejected.")
                    log("Likely cause: wrong username/password for this store in stores.txt, "
                        "or the Windows account is locked out after repeated bad attempts.")
                else:
                    log(f"FAILED — could not connect: {conn_err}")
                    log("Likely cause: store PC is offline, SSH service isn't running, "
                        "or a firewall/VPN is blocking the connection.")
                log("SKIPPED — fix connectivity/credentials for this store and re-run.")
                self.log_queue.put(("progress", 1))
                return

            log("Connected and authenticated successfully.")

            # 0b. Kill lingering hung instances and rename old executable if present
            run_ssh_command(ip, user, pwd, 'taskkill /F /IM Alfamart_Reminder.exe')


            # 1. Detect the interactive desktop user via explorer.exe, with a query-session fallback
            self.log_queue.put(("status", f"Detecting logged-in user on {ip}..."))
            detect_cmd = (
                'powershell -NoProfile -Command '
                '"(Get-Process -Name explorer -IncludeUserName -ErrorAction SilentlyContinue | '
                'Select-Object -First 1 -ExpandProperty UserName)"'
            )
            ok_u, out_u, err_u = run_ssh_command(ip, user, pwd, detect_cmd)
            raw_user = out_u.strip() if ok_u else ""

            if not raw_user and err_u.strip():
                log(f"explorer.exe lookup returned an error: {err_u.strip()}")

            if not raw_user:
                # Fallback: parse 'query user' — doesn't need IncludeUserName's elevated rights
                ok_q, out_q, err_q = run_ssh_command(ip, user, pwd, 'query user')
                if ok_q and out_q.strip():
                    for line in out_q.splitlines():
                        if ">" in line or "Active" in line or "Disc" in line:
                            parts_u = line.split()
                            if parts_u:
                                u = parts_u[0].replace(">", "").strip()
                                if u and u.lower() != "username":
                                    raw_user = u
                                    break
                if raw_user:
                    log(f"Fallback 'query user' found: '{raw_user}'")
                elif err_q and err_q.strip():
                    log(f"'query user' also failed: {err_q.strip()}")

            if not raw_user:
                log("WARNING: no interactive desktop user detected (nobody logged in, or the SSH account lacks rights to see the session)")
                log("SKIPPED — installing as SYSTEM would make the popup invisible.")
                self.log_queue.put(("progress", 1))
                return

            logged_user = raw_user.split("\\")[-1] if "\\" in raw_user else raw_user
            log(f"Detected interactive user: '{logged_user}'")

            # 2. Clean up existing tasks via PowerShell
            self.log_queue.put(("status", f"Wiping old tasks on {ip}..."))
            clean_cmd = 'powershell -Command "Get-ScheduledTask -TaskName \'Reminder_v2*\' -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false"'
            run_ssh_command(ip, user, pwd, clean_cmd)
            log("Wiped old Reminder_v2 tasks")

            # 3. Create fresh tasks via Base64 PowerShell EncodedCommand over SSH
            success_count = 0
            total = len(self.schedules)
            for i, item in enumerate(self.schedules):
                t_str = item["time"]
                title = item["title"]

                raw_lines = str(item.get("lines", ""))
                clean_lines = " | ".join(raw_lines.splitlines())

                safe_title = title.replace("'", "''").replace('"', '')
                safe_msg = clean_lines.replace("'", "''").replace('"', '')

                formatted_time = t_str.zfill(5)
                task_id = formatted_time.replace(":", "")
                task_name = f"Reminder_v2_Shift_{task_id}"

                self.log_queue.put(("status", f"Installing {task_name} on {ip} ({i + 1}/{total})..."))

                # Native PowerShell script block, forced to Interactive logon so the popup can actually paint on screen
                ps_script = (
                    f"$Action = New-ScheduledTaskAction -Execute '{app_path}' -Argument '--custom \"{safe_title}\" \"{safe_msg}\"'; "
                    f"$Trigger = New-ScheduledTaskTrigger -Daily -At '{formatted_time}'; "
                    f"$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable; "
                    f"$Principal = New-ScheduledTaskPrincipal -UserId '{logged_user}' -LogonType Interactive -RunLevel Limited; "
                    f"Register-ScheduledTask -TaskName '{task_name}' -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force"
                )

                # Base64 encode to UTF-16LE to safely bypass cmd.exe parsing
                encoded_script = base64.b64encode(ps_script.encode('utf-16le')).decode('utf-8')
                full_cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {encoded_script}'

                # Register-ScheduledTask occasionally hits a transient lock on the Task
                # Scheduler's internal store right after a previous registration
                # ("used by another process" / HRESULT 0x80070020). Retry a couple of
                # times with a short pause before giving up on that task.
                max_attempts = 3
                ok_c, out_c, err_c = False, "", ""
                for attempt in range(1, max_attempts + 1):
                    ok_c, out_c, err_c = run_ssh_command(ip, user, pwd, full_cmd)
                    if ok_c and "TaskName" in out_c:
                        break
                    transient = "being used by another process" in err_c or "0x80070020" in err_c
                    if transient and attempt < max_attempts:
                        log(f"Task {task_name} hit a busy Task Scheduler lock, retrying ({attempt}/{max_attempts})...")
                        time.sleep(1.5)
                        continue
                    break

                if ok_c and "TaskName" in out_c:
                    success_count += 1
                    log(f"Installed task: {task_name} ({formatted_time})")
                else:
                    log(f"FAILED task: {task_name} -> {err_c.strip() or out_c.strip()}")

            log(f"Completed: {success_count}/{total} tasks installed.")
            self.log_queue.put(("progress", 1))

        def run_all():
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                list(executor.map(deploy_worker, selected_stores))
            self.log_queue.put(("done", None))

        threading.Thread(target=run_all, daemon=True).start()
        self.root.after(100, self.poll_log_queue)

    def poll_log_queue(self):
        try:
            while True:
                kind, payload = self.log_queue.get_nowait()
                if kind == "log":
                    self.append_log(payload)
                elif kind == "status":
                    self.status_label.config(text=payload)
                elif kind == "progress":
                    self.progress.step(payload)
                elif kind == "done":
                    self.append_log("\n==================================================")
                    self.append_log("--- DEPLOYMENT FINISHED ---")
                    self.append_log("==================================================\n")
                    self.status_label.config(text="Deployment finished.")
                    self.deploy_btn.config(state="normal", text="🚀 CLEAN UPDATE ALL & PUSH TASKS TO STORES")
                    messagebox.showinfo("Clean Push Finished", "Clean update completed! Check results log below.")
                    return
        except queue.Empty:
            pass
        self.root.after(100, self.poll_log_queue)


if __name__ == "__main__":
    root = tk.Tk()
    app = MasterITDashboard(root)
    root.mainloop()