import tkinter as tk
from tkinter import ttk


def show_ack_log_window(parent_root, results):
    """Displays pulled ack_logs.txt content for one or more stores.

    results: list of dicts, each with keys:
        ip (str), name (str), code (str), and either
        content (str, may be empty) or error (str)
    """
    win = tk.Toplevel(parent_root)
    win.title("Pulled Ack Logs")
    win.configure(bg="#f4f4f4")

    window_width = 760
    window_height = 560
    center_x = int((win.winfo_screenwidth() / 2) - (window_width / 2))
    center_y = int((win.winfo_screenheight() / 2) - (window_height / 2))
    win.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    top_frame = tk.Frame(win, bg="#f4f4f4")
    top_frame.pack(fill="x", padx=8, pady=6)
    tk.Label(
        top_frame, text=f"Ack Logs — {len(results)} store(s)",
        font=("Segoe UI", 9, "bold"), bg="#f4f4f4"
    ).pack(side="left")

    text_frame = tk.Frame(win, bg="#f4f4f4")
    text_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    log_text = tk.Text(text_frame, font=("Consolas", 8), wrap="word")
    scroll = ttk.Scrollbar(text_frame, orient="vertical", command=log_text.yview)
    log_text.configure(yscrollcommand=scroll.set)
    log_text.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    log_text.tag_configure("header", font=("Consolas", 8, "bold"), foreground="#0056B3")
    log_text.tag_configure("error", foreground="#D9534F")

    for r in results:
        code_part = r.get("code") or "N/A"
        header = f"=== {r['name']}  [{code_part}]  ({r['ip']}) ===\n"
        log_text.insert(tk.END, header, "header")

        if r.get("error"):
            log_text.insert(tk.END, r["error"] + "\n", "error")
        else:
            content = r.get("content") or ""
            log_text.insert(tk.END, (content if content else "(No ack logs recorded yet.)") + "\n")

        log_text.insert(tk.END, "\n")

    log_text.config(state="disabled")