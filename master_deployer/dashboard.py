import base64
import time
import concurrent.futures
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

from config import PRESETS
from data_store import load_stores, load_schedules, save_schedules
from ssh_utils import run_ssh_command, test_connection
from ui_utils import adjust_window_geometry
from preview_window import render_preview_modal
from log_manager import append_full_log
from log_history_window import show_log_history_window
from store_editor_window import show_store_editor_window

class MasterITDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Alfamart IT Master Task Deployer")
        adjust_window_geometry(self.root)
        self.root.configure(bg="#f4f4f4")

        self.stores = load_stores()
        self.schedules = load_schedules()
        self.selected_schedule_index = None
        self.log_queue = queue.Queue()
        self.failed_stores = []
        self.success_stores = []

        main_container = tk.Frame(self.root, bg="#f4f4f4")
        main_container.pack(fill="both", expand=True, padx=10, pady=8)

        master_frame = tk.LabelFrame(main_container, text=" IT Master Schedule Library & WYSIWYG Editor ", font=("Segoe UI", 9, "bold"), bg="#f4f4f4", padx=8, pady=4)
        master_frame.pack(fill="x", pady=(0, 4))

        table_frame = tk.Frame(master_frame, bg="#f4f4f4")
        table_frame.pack(side="left", fill="y", padx=(0, 8))

        columns = ("Time", "Title", "Type")
        self.sched_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.sched_tree.heading("Time", text="Time")
        self.sched_tree.heading("Title", text="Popup Title")
        self.sched_tree.heading("Type", text="Layout")
        self.sched_tree.column("Time", width=50)
        self.sched_tree.column("Title", width=150)
        self.sched_tree.column("Type", width=100)
        self.sched_tree.pack(side="left", fill="y")
        self.sched_tree.bind("<<TreeviewSelect>>", self.on_schedule_select)

        sched_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.sched_tree.yview)
        self.sched_tree.configure(yscrollcommand=sched_scroll.set)
        sched_scroll.pack(side="right", fill="y")

        self.form_frame = tk.Frame(master_frame, bg="#f4f4f4")
        self.form_frame.pack(side="right", fill="both", expand=True)

        row0 = tk.Frame(self.form_frame, bg="#f4f4f4")
        row0.pack(fill="x", pady=1)
        tk.Label(row0, text="Time (HH:MM):", bg="#f4f4f4", font=("Segoe UI", 8, "bold")).pack(side="left")
        self.time_entry = tk.Entry(row0, width=8, font=("Segoe UI", 9))
        self.time_entry.pack(side="left", padx=(5, 12))

        tk.Label(row0, text="Layout Type:", bg="#f4f4f4", font=("Segoe UI", 8, "bold")).pack(side="left")
        self.type_combo = ttk.Combobox(row0, values=["standard", "eservices_login", "eservices_eod"], width=15, state="readonly")
        self.type_combo.pack(side="left", padx=5)
        self.type_combo.set("standard")
        self.type_combo.bind("<<ComboboxSelected>>", self.on_layout_change)

        row1 = tk.Frame(self.form_frame, bg="#f4f4f4")
        row1.pack(fill="x", pady=1)
        tk.Label(row1, text="Title:", bg="#f4f4f4", font=("Segoe UI", 8, "bold"), width=12, anchor="w").pack(side="left")
        self.title_entry = tk.Entry(row1, font=("Segoe UI", 9))
        self.title_entry.pack(side="left", fill="x", expand=True)

        row2 = tk.Frame(self.form_frame, bg="#f4f4f4")
        row2.pack(fill="x", pady=1)
        tk.Label(row2, text="Main Content:", bg="#f4f4f4", font=("Segoe UI", 8, "bold"), width=12, anchor="nw").pack(side="left")
        self.msg_entry = tk.Text(row2, height=2, font=("Segoe UI", 8))
        self.msg_entry.pack(side="left", fill="x", expand=True)

        # Dynamic Box Inputs
        self.eservices_frame = tk.LabelFrame(self.form_frame, text=" Dynamic E-Services Custom Fields ", font=("Segoe UI", 8, "bold"), bg="#f4f4f4", padx=5, pady=2)

        s1_frame = tk.Frame(self.eservices_frame, bg="#f4f4f4")
        s1_frame.pack(fill="x", pady=1)
        tk.Label(s1_frame, text="Step 1 Header/Sub:", bg="#f4f4f4", font=("Segoe UI", 7, "bold"), width=20, anchor="w").pack(side="left")
        self.s1_title_entry = tk.Entry(s1_frame, font=("Segoe UI", 8), width=10)
        self.s1_title_entry.pack(side="left", padx=(0, 4))
        self.s1_sub_entry = tk.Entry(s1_frame, font=("Segoe UI", 8))
        self.s1_sub_entry.pack(side="left", fill="x", expand=True)

        s1_body_frame = tk.Frame(self.eservices_frame, bg="#f4f4f4")
        s1_body_frame.pack(fill="x", pady=1)
        tk.Label(s1_body_frame, text="Step 1 Body Text:", bg="#f4f4f4", font=("Segoe UI", 7, "bold"), width=20, anchor="nw").pack(side="left")
        self.s1_body_text = tk.Text(s1_body_frame, height=2, font=("Segoe UI", 8))
        self.s1_body_text.pack(side="left", fill="x", expand=True)

        s2_frame = tk.Frame(self.eservices_frame, bg="#f4f4f4")
        s2_frame.pack(fill="x", pady=1)
        tk.Label(s2_frame, text="Step 2 Header/Sub:", bg="#f4f4f4", font=("Segoe UI", 7, "bold"), width=20, anchor="w").pack(side="left")
        self.s2_title_entry = tk.Entry(s2_frame, font=("Segoe UI", 8), width=10)
        self.s2_title_entry.pack(side="left", padx=(0, 4))
        self.s2_sub_entry = tk.Entry(s2_frame, font=("Segoe UI", 8))
        self.s2_sub_entry.pack(side="left", fill="x", expand=True)

        s2_body_frame = tk.Frame(self.eservices_frame, bg="#f4f4f4")
        s2_body_frame.pack(fill="x", pady=1)
        tk.Label(s2_body_frame, text="Step 2 Body Text:", bg="#f4f4f4", font=("Segoe UI", 7, "bold"), width=20, anchor="nw").pack(side="left")
        self.s2_body_text = tk.Text(s2_body_frame, height=2, font=("Segoe UI", 8))
        self.s2_body_text.pack(side="left", fill="x", expand=True)

        warn_frame = tk.Frame(self.eservices_frame, bg="#f4f4f4")
        warn_frame.pack(fill="x", pady=1)
        tk.Label(warn_frame, text="Bottom Warning Note:", bg="#f4f4f4", font=("Segoe UI", 7, "bold"), width=20, anchor="nw").pack(side="left")
        self.warning_text = tk.Text(warn_frame, height=2, font=("Segoe UI", 8))
        self.warning_text.pack(side="left", fill="x", expand=True)

        edit_btn_frame = tk.Frame(self.form_frame, bg="#f4f4f4")
        edit_btn_frame.pack(fill="x", pady=(4, 0))

        tk.Button(edit_btn_frame, text="➕ Add New", font=("Segoe UI", 8), bg="#28A745", fg="white", command=self.add_schedule).pack(side="left", padx=2)
        tk.Button(edit_btn_frame, text="💾 Update", font=("Segoe UI", 8), bg="#007ACC", fg="white", command=self.update_schedule).pack(side="left", padx=2)
        tk.Button(edit_btn_frame, text="🗑️ Delete", font=("Segoe UI", 8), bg="#D9534F", fg="white", command=self.delete_schedule).pack(side="left", padx=2)
        tk.Button(edit_btn_frame, text="👁️ Live Preview Modal", font=("Segoe UI", 8, "bold"), bg="#17A2B8", fg="white", command=self.show_live_preview).pack(side="left", padx=6)
        tk.Button(edit_btn_frame, text="Clear", font=("Segoe UI", 8), command=self.clear_form).pack(side="right", padx=2)

                # Two-column row: stores on the left, live results on the right
        columns_frame = tk.Frame(main_container, bg="#f4f4f4")
        columns_frame.pack(fill="both", expand=True, pady=(0, 4))
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1)
        columns_frame.grid_rowconfigure(0, weight=1)

        store_frame = tk.LabelFrame(columns_frame, text=" Target Stores Selection ", font=("Segoe UI", 9, "bold"), bg="#f4f4f4", padx=8, pady=2)
        store_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        ctrl_btn_frame = tk.Frame(store_frame, bg="#f4f4f4")
        ctrl_btn_frame.pack(fill="x", pady=(0, 2))

        tk.Button(ctrl_btn_frame, text="Select All", font=("Segoe UI", 8), command=self.select_all_stores).pack(side="left", padx=2)
        tk.Button(ctrl_btn_frame, text="Deselect All", font=("Segoe UI", 8), command=self.deselect_all_stores).pack(side="left", padx=2)
        tk.Button(ctrl_btn_frame, text="🔄 Reload stores.txt", font=("Segoe UI", 8), command=self.reload_stores_list).pack(side="right", padx=2)
        tk.Button(ctrl_btn_frame, text="📜 Logs History", font=("Segoe UI", 8), command=self.open_logs_history).pack(side="right", padx=2)
        tk.Button(ctrl_btn_frame, text="✏️ Edit stores.txt", font=("Segoe UI", 8), command=self.open_store_editor).pack(side="right", padx=2)

        list_container = tk.Frame(store_frame, bg="#f4f4f4")
        list_container.pack(fill="both", expand=True)

        self.store_vars = {}
        canvas = tk.Canvas(list_container, bg="#ffffff", highlightthickness=1, highlightbackground="#ccc")
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.scrollable_frame = scrollable_frame
        deploy_btn_frame = tk.Frame(store_frame, bg="#f4f4f4")
        deploy_btn_frame.pack(fill="x", pady=(4, 0))

        self.deploy_btn = tk.Button(
            deploy_btn_frame, text="🚀 CLEAN UPDATE ALL & PUSH TASKS TO STORES", font=("Segoe UI", 9, "bold"),
            bg="#28A745", fg="white", pady=4, command=self.clean_update_and_push
        )
        self.deploy_btn.pack(fill="x")
        log_frame = tk.LabelFrame(columns_frame, text=" Deployment Execution Results ", font=("Segoe UI", 9, "bold"), bg="#f4f4f4", padx=8, pady=2)
        log_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        log_container = tk.Frame(log_frame, bg="#f4f4f4")
        log_container.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_container, font=("Consolas", 8), wrap="word", state="disabled")
        log_scroll = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")
        self.log_text.tag_configure("failed", foreground="#D9534F")

        progress_frame = tk.Frame(main_container, bg="#f4f4f4")
        progress_frame.pack(fill="x", pady=(0, 2))

        self.status_label = tk.Label(
            progress_frame, text="Idle — ready to deploy",
            font=("Segoe UI", 8, "italic"), fg="#555555", bg="#f4f4f4"
        )
        self.status_label.pack(anchor="w")

        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x")

        self.refresh_schedule_table()
        self.populate_store_checkboxes()
        self.on_layout_change()

    # --- AUTO-POPULATE TEMPLATE ON DROPDOWN CHANGE ---
    def on_layout_change(self, event=None):
        l_type = self.type_combo.get()
        if l_type in ["eservices_login", "eservices_eod"]:
            self.eservices_frame.pack(fill="x", pady=(2, 0))

            # If selecting from dropdown manually (and not via clicking table row)
            if event is not None and l_type in PRESETS:
                p = PRESETS[l_type]
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, p["title"])

                self.msg_entry.delete("1.0", tk.END)
                self.msg_entry.insert("1.0", p["lines"])

                self.s1_title_entry.delete(0, tk.END)
                self.s1_title_entry.insert(0, p["step1_title"])

                self.s1_sub_entry.delete(0, tk.END)
                self.s1_sub_entry.insert(0, p["step1_sub"])

                self.s1_body_text.delete("1.0", tk.END)
                self.s1_body_text.insert("1.0", p["step1_body"])

                self.s2_title_entry.delete(0, tk.END)
                self.s2_title_entry.insert(0, p["step2_title"])

                self.s2_sub_entry.delete(0, tk.END)
                self.s2_sub_entry.insert(0, p["step2_sub"])

                self.s2_body_text.delete("1.0", tk.END)
                self.s2_body_text.insert("1.0", p["step2_body"])

                self.warning_text.delete("1.0", tk.END)
                self.warning_text.insert("1.0", p["warning"])
        else:
            self.eservices_frame.pack_forget()

    def show_live_preview(self):
        t = self.title_entry.get().strip() or "SAMPLE TITLE"
        msg = self.msg_entry.get("1.0", tk.END).strip() or "SAMPLE MESSAGE"
        l_type = self.type_combo.get()

        s1_t = self.s1_title_entry.get().strip()
        s1_s = self.s1_sub_entry.get().strip()
        s1_b = self.s1_body_text.get("1.0", tk.END).strip()

        s2_t = self.s2_title_entry.get().strip()
        s2_s = self.s2_sub_entry.get().strip()
        s2_b = self.s2_body_text.get("1.0", tk.END).strip()

        warn = self.warning_text.get("1.0", tk.END).strip()

        render_preview_modal(self.root, t, msg, l_type, s1_t, s1_s, s1_b, s2_t, s2_s, s2_b, warn)

    def refresh_schedule_table(self):
        for item in self.sched_tree.get_children():
            self.sched_tree.delete(item)
        self.schedules.sort(key=lambda x: x["time"])
        for idx, s in enumerate(self.schedules):
            self.sched_tree.insert("", tk.END, iid=idx, values=(s["time"], s["title"], s.get("type", "standard")))
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
        self.type_combo.set(s.get("type", "standard"))

        self.msg_entry.delete("1.0", tk.END)
        self.msg_entry.insert("1.0", s.get("lines", ""))

        self.s1_title_entry.delete(0, tk.END)
        self.s1_title_entry.insert(0, s.get("step1_title", "POS"))

        self.s1_sub_entry.delete(0, tk.END)
        self.s1_sub_entry.insert(0, s.get("step1_sub", "REGULAR POS LOGIN"))

        self.s1_body_text.delete("1.0", tk.END)
        self.s1_body_text.insert("1.0", s.get("step1_body", ""))

        self.s2_title_entry.delete(0, tk.END)
        self.s2_title_entry.insert(0, s.get("step2_title", "E-SERVICES"))

        self.s2_sub_entry.delete(0, tk.END)
        self.s2_sub_entry.insert(0, s.get("step2_sub", "E-SERVICES LOGIN"))

        self.s2_body_text.delete("1.0", tk.END)
        self.s2_body_text.insert("1.0", s.get("step2_body", ""))

        self.warning_text.delete("1.0", tk.END)
        self.warning_text.insert("1.0", s.get("warning", ""))

        self.on_layout_change(event=None)

    def clear_form(self):
        self.selected_schedule_index = None
        self.sched_tree.selection_remove(self.sched_tree.selection())
        self.time_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.type_combo.set("standard")
        self.msg_entry.delete("1.0", tk.END)

        self.s1_title_entry.delete(0, tk.END)
        self.s1_sub_entry.delete(0, tk.END)
        self.s1_body_text.delete("1.0", tk.END)

        self.s2_title_entry.delete(0, tk.END)
        self.s2_sub_entry.delete(0, tk.END)
        self.s2_body_text.delete("1.0", tk.END)

        self.warning_text.delete("1.0", tk.END)
        self.on_layout_change(event=None)

    def add_schedule(self):
        t = self.time_entry.get().strip()
        title = self.title_entry.get().strip()
        l_type = self.type_combo.get()
        lines = self.msg_entry.get("1.0", tk.END).strip()

        s1_t = self.s1_title_entry.get().strip()
        s1_s = self.s1_sub_entry.get().strip()
        s1_b = self.s1_body_text.get("1.0", tk.END).strip()

        s2_t = self.s2_title_entry.get().strip()
        s2_s = self.s2_sub_entry.get().strip()
        s2_b = self.s2_body_text.get("1.0", tk.END).strip()

        warn = self.warning_text.get("1.0", tk.END).strip()

        if not t or not title or not lines:
            messagebox.showwarning("Input Error", "Time, Title, and Main Content are required.")
            return

        self.schedules.append({
            "time": t, "title": title, "type": l_type, "lines": lines,
            "step1_title": s1_t, "step1_sub": s1_s, "step1_body": s1_b,
            "step2_title": s2_t, "step2_sub": s2_s, "step2_body": s2_b,
            "warning": warn
        })
        self.refresh_schedule_table()
        self.clear_form()

    def update_schedule(self):
        if self.selected_schedule_index is None:
            messagebox.showwarning("Selection Error", "Please select a schedule from the list to update.")
            return

        t = self.time_entry.get().strip()
        title = self.title_entry.get().strip()
        l_type = self.type_combo.get()
        lines = self.msg_entry.get("1.0", tk.END).strip()

        s1_t = self.s1_title_entry.get().strip()
        s1_s = self.s1_sub_entry.get().strip()
        s1_b = self.s1_body_text.get("1.0", tk.END).strip()

        s2_t = self.s2_title_entry.get().strip()
        s2_s = self.s2_sub_entry.get().strip()
        s2_b = self.s2_body_text.get("1.0", tk.END).strip()

        warn = self.warning_text.get("1.0", tk.END).strip()

        self.schedules[self.selected_schedule_index] = {
            "time": t, "title": title, "type": l_type, "lines": lines,
            "step1_title": s1_t, "step1_sub": s1_s, "step1_body": s1_b,
            "step2_title": s2_t, "step2_sub": s2_s, "step2_body": s2_b,
            "warning": warn
        }
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

        grouped = {}
        for s in self.stores:
            grouped.setdefault(s.get("dc", "Ungrouped"), []).append(s)

        for dc_name in sorted(grouped.keys()):
            dc_stores = grouped[dc_name]

            dc_header = tk.Frame(self.scrollable_frame, bg="#e9ecef")
            dc_header.pack(fill="x", pady=(6, 2))

            dc_var = tk.BooleanVar(value=True)

            def make_toggle_dc(dc_stores=dc_stores, dc_var=dc_var):
                def toggle_dc():
                    new_val = dc_var.get()
                    for s in dc_stores:
                        self.store_vars[s["ip"]].set(new_val)
                return toggle_dc

            tk.Checkbutton(
                dc_header, text=f"  {dc_name}  ({len(dc_stores)} store{'s' if len(dc_stores) != 1 else ''})",
                variable=dc_var, bg="#e9ecef", activebackground="#e9ecef",
                font=("Segoe UI", 8, "bold"), anchor="w",
                command=make_toggle_dc()
            ).pack(fill="x", padx=2)

            for s in dc_stores:
                var = tk.BooleanVar(value=True)
                ip = s["ip"]
                self.store_vars[ip] = var

                label_bits = [s.get("name") or ip]
                if s.get("code"):
                    label_bits.append(f"[{s['code']}]")
                if s.get("pos"):
                    label_bits.append(f"- {s['pos']}")
                label_bits.append(f"({ip})")

                tk.Checkbutton(
                    self.scrollable_frame, text=" ".join(label_bits),
                    variable=var, bg="#ffffff", activebackground="#ffffff", anchor="w"
                ).pack(fill="x", anchor="w", padx=20, pady=1)

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

    def append_log(self, text, tag=None):
        self.log_text.config(state="normal")
        if tag:
            self.log_text.insert(tk.END, text + "\n", tag)
        else:
            self.log_text.insert(tk.END, text + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)

    def log_both(self, text, tag=None):
        self.append_log(text, tag)
        append_full_log(text)

    def open_logs_history(self):
        show_log_history_window(self.root)

    def open_store_editor(self):
        show_store_editor_window(self.root, on_save=self.reload_stores_list)

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

        self.failed_stores = []
        self.success_stores = []
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")
        self.deploy_btn.config(state="disabled", text="⏳ Deploying...")
        self.progress.config(mode="determinate", maximum=len(selected_stores), value=0)
        self.status_label.config(text=f"Starting deployment to {len(selected_stores)} store(s)...")

        self.log_both(f"\n==================================================")
        self.log_both(f"--- STARTING CLEAN UPDATE TO {len(selected_stores)} STORE(S) ---")
        self.log_both(f"==================================================")
        app_path = r"C:\Reminder_v2\Alfamart_Reminder.exe"

        def deploy_worker(store):
            ip, user, pwd = store["ip"], store["user"], store["pwd"]
            store_code = store.get("code", "")
            store_pos = store.get("pos", "")
            label_parts = [p for p in [store_code, store_pos] if p]
            store_label = f"{' - '.join(label_parts)} ({ip})" if label_parts else ip

            def log(text, tag=None):
                self.log_queue.put(("log", f"[STORE: {ip}] {text}", tag))

            def detail(text):
                self.log_queue.put(("detail", f"[STORE: {ip}] {text}", None))

            log("Connecting...")
            self.log_queue.put(("status", f"Connecting to {ip}...", None))

            conn_ok, conn_err = test_connection(ip, user, pwd)
            if not conn_ok:
                if conn_err == "AUTH_FAILED":
                    log("FAILED — SSH authentication rejected.", tag="failed")
                else:
                    log(f"FAILED — could not connect: {conn_err}", tag="failed")
                log("SKIPPED — fix connectivity/credentials for this store and re-run.", tag="failed")
                self.log_queue.put(("failed_store", store_label, None))
                self.log_queue.put(("progress", 1, None))
                return

            log("Connected and authenticated successfully.")
            run_ssh_command(ip, user, pwd, 'taskkill /F /IM Alfamart_Reminder.exe')

            self.log_queue.put(("status", f"Detecting logged-in user on {ip}...", None))
            detect_cmd = (
                'powershell -NoProfile -Command '
                '"(Get-Process -Name explorer -IncludeUserName -ErrorAction SilentlyContinue | '
                'Select-Object -First 1 -ExpandProperty UserName)"'
            )
            ok_u, out_u, err_u = run_ssh_command(ip, user, pwd, detect_cmd)
            raw_user = out_u.strip() if ok_u else ""

            if not raw_user:
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

            if not raw_user:
                log("WARNING: no interactive desktop user detected.", tag="failed")
                log("SKIPPED — installing as SYSTEM would make the popup invisible.", tag="failed")
                self.log_queue.put(("failed_store", store_label, None))
                self.log_queue.put(("progress", 1, None))
                return

            logged_user = raw_user.split("\\")[-1] if "\\" in raw_user else raw_user
            detail(f"Detected interactive user: '{logged_user}'")

            self.log_queue.put(("status", f"Wiping old tasks on {ip}...", None))
            clean_cmd = 'powershell -Command "Get-ScheduledTask | Where-Object {$_.TaskName -like \'Reminder_v2*\' -or $_.TaskName -like \'Alfamart_Reminder*\'} | Unregister-ScheduledTask -Confirm:$false"'
            run_ssh_command(ip, user, pwd, clean_cmd)
            detail("Wiped old scheduled tasks.")

            success_count = 0
            total = len(self.schedules)
            for i, item in enumerate(self.schedules):
                t_str = item["time"]
                title = item["title"]
                l_type = item.get("type", "standard")

                raw_lines = str(item.get("lines", ""))
                clean_lines = " | ".join([line.strip() for line in raw_lines.splitlines() if line.strip()])

                raw_warn = str(item.get("warning", ""))
                clean_warn = " | ".join([line.strip() for line in raw_warn.splitlines() if line.strip()])

                safe_title = title.replace("'", "''").replace('"', '')
                safe_msg = clean_lines.replace("'", "''").replace('"', '')

                safe_s1_t = item.get("step1_title", "POS").replace("'", "''").replace('"', '')
                safe_s1_s = item.get("step1_sub", "REGULAR POS LOGIN").replace("'", "''").replace('"', '')
                safe_s1_b = " | ".join([line.strip() for line in str(item.get("step1_body", "")).splitlines() if line.strip()]).replace("'", "''").replace('"', '')

                safe_s2_t = item.get("step2_title", "E-SERVICES").replace("'", "''").replace('"', '')
                safe_s2_s = item.get("step2_sub", "E-SERVICES LOGIN").replace("'", "''").replace('"', '')
                safe_s2_b = " | ".join([line.strip() for line in str(item.get("step2_body", "")).splitlines() if line.strip()]).replace("'", "''").replace('"', '')

                safe_warn = clean_warn.replace("'", "''").replace('"', '')

                formatted_time = t_str.zfill(5)
                task_id = formatted_time.replace(":", "")
                task_name = f"Alfamart_Reminder_Shift_{task_id}"

                self.log_queue.put(("status", f"Installing {task_name} on {ip} ({i + 1}/{total})...", None))

                arg_str = (
                    f'--custom "{safe_title}" "{safe_msg}" --type "{l_type}" '
                    f'--s1_title "{safe_s1_t}" --s1_sub "{safe_s1_s}" --s1_body "{safe_s1_b}" '
                    f'--s2_title "{safe_s2_t}" --s2_sub "{safe_s2_s}" --s2_body "{safe_s2_b}" '
                    f'--warning "{safe_warn}"'
                )

                ps_script = (
                    f"$Action = New-ScheduledTaskAction -Execute '{app_path}' -Argument '{arg_str}'; "
                    f"$Trigger = New-ScheduledTaskTrigger -Daily -At '{formatted_time}'; "
                    f"$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable; "
                    f"$Principal = New-ScheduledTaskPrincipal -UserId '{logged_user}' -LogonType Interactive -RunLevel Limited; "
                    f"Register-ScheduledTask -TaskName '{task_name}' -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force"
                )

                encoded_script = base64.b64encode(ps_script.encode('utf-16le')).decode('utf-8')
                full_cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {encoded_script}'

                max_attempts = 3
                ok_c, out_c, err_c = False, "", ""
                for attempt in range(1, max_attempts + 1):
                    ok_c, out_c, err_c = run_ssh_command(ip, user, pwd, full_cmd)
                    if ok_c and "TaskName" in out_c:
                        break
                    transient = "being used by another process" in err_c or "0x80070020" in err_c
                    if transient and attempt < max_attempts:
                        time.sleep(1.5)
                        continue
                    break

                if ok_c and "TaskName" in out_c:
                    success_count += 1
                    detail(f"Installed task: {task_name} ({formatted_time}) [{l_type}]")
                else:
                    log(f"FAILED task: {task_name} -> {err_c.strip() or out_c.strip()}", tag="failed")

            done_tag = None if success_count == total else "failed"
            log(f"Completed: {success_count}/{total} tasks installed.", tag=done_tag)
            if success_count < total:
                self.log_queue.put(("failed_store", store_label, None))
            else:
                self.log_queue.put(("success_store", store_label, None))
            self.log_queue.put(("progress", 1, None))

        def run_all():
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                list(executor.map(deploy_worker, selected_stores))
            self.log_queue.put(("done", None, None))

        threading.Thread(target=run_all, daemon=True).start()
        self.root.after(100, self.poll_log_queue)

    def poll_log_queue(self):
        try:
            while True:
                kind, payload, tag = self.log_queue.get_nowait()
                if kind == "log":
                    self.log_both(payload, tag)
                elif kind == "detail":
                    append_full_log(payload)
                elif kind == "status":
                    self.status_label.config(text=payload)
                elif kind == "progress":
                    self.progress.step(payload)
                elif kind == "failed_store":
                    if payload not in self.failed_stores:
                        self.failed_stores.append(payload)
                elif kind == "success_store":
                    if payload not in self.success_stores:
                        self.success_stores.append(payload)
                elif kind == "done":
                    self.log_both("\n==================================================")
                    self.log_both("--- DEPLOYMENT FINISHED ---")
                    if self.success_stores:
                        self.log_both(f"Stores completed successfully ({len(self.success_stores)}):")
                        for s in self.success_stores:
                            self.log_both(f"  ✓ {s}")
                    if self.failed_stores:
                        self.log_both(f"Stores with errors ({len(self.failed_stores)}):", tag="failed")
                        for s in self.failed_stores:
                            self.log_both(f"  ✗ {s}", tag="failed")
                    if not self.success_stores and not self.failed_stores:
                        self.log_both("No stores were processed.")
                    self.log_both("==================================================\n")
                    self.status_label.config(text="Deployment finished.")
                    self.deploy_btn.config(state="normal", text="🚀 CLEAN UPDATE ALL & PUSH TASKS TO STORES")
                    messagebox.showinfo("Clean Push Finished", "Clean update completed! Check results log below.")
                    return
        except queue.Empty:
            pass
        self.root.after(100, self.poll_log_queue)
