import tkinter as tk
from tkinter import messagebox


def render_preview_modal(parent_root, sub_title, message, layout_type, s1_title, s1_sub, s1_body, s2_title, s2_sub, s2_body, warn_txt,
                          btn_name=None, btn_link=None):
    preview_win = tk.Toplevel(parent_root)
    preview_win.title("LIVE PREVIEW — Alfamart Reminder")
    preview_win.configure(bg="#FFFFFF")
    preview_win.attributes('-topmost', True)

    if layout_type in ["eservices_login", "eservices_eod"]:
        window_width = 460
        window_height = 360
        center_x = int((preview_win.winfo_screenwidth() / 2) - (window_width / 2))
        center_y = int((preview_win.winfo_screenheight() / 2) - (window_height / 2))
        preview_win.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        preview_win.resizable(False, False)


        header_frame = tk.Frame(preview_win, bg="#FFFFFF", pady=4)
        header_frame.pack(fill="x")

        title_container = tk.Frame(header_frame, bg="#FFFFFF")
        title_container.pack()

        tk.Label(title_container, text="🔔", font=("Segoe UI", 16), fg="#D93025", bg="#FFFFFF").pack(side="left", padx=(0, 4))
        tk.Label(title_container, text=(sub_title or "REMINDER!").upper(), font=("Impact", 18), fg="#001B3A", bg="#FFFFFF").pack(side="left")

        div_frame = tk.Frame(preview_win, bg="#FFFFFF")
        div_frame.pack(fill="x", padx=25)
        tk.Frame(div_frame, bg="#CCCCCC", height=1).pack(fill="x", pady=(0, 1))
        tk.Label(div_frame, text="HUWAG KALIMUTAN!", font=("Segoe UI", 8, "bold"), fg="#D93025", bg="#FFFFFF").pack()

        display_msg = message.strip() if message.strip() else ("MAG LOG IN SA E-SERVICES." if layout_type == "eservices_login" else "MAG EOD SA E-SERVICES.")
        tk.Label(preview_win, text=display_msg, font=("Segoe UI Black", 12, "bold"), fg="#001B3A", bg="#FFFFFF", justify="center", wraplength=420).pack(pady=(1, 4))

        step_badge = tk.Frame(preview_win, bg="#001B3A", padx=10, pady=1)
        step_badge.pack()
        tk.Label(step_badge, text="2-STEP CHECKLIST", font=("Segoe UI", 7, "bold"), fg="white", bg="#001B3A").pack()

        box_frame = tk.Frame(preview_win, bg="#FFFFFF", pady=4)
        box_frame.pack()

        # Step 1
        b1 = tk.Frame(box_frame, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#28A745")
        b1.config(highlightthickness=1, highlightcolor="#28A745")
        b1.grid(row=0, column=0, padx=6, ipadx=6, ipady=3)

        s1_hdr = tk.Frame(b1, bg="#FFFFFF")
        s1_hdr.pack(anchor="center", pady=(0, 2))
        tk.Label(s1_hdr, text="❶", font=("Segoe UI", 9, "bold"), fg="#28A745", bg="#FFFFFF").pack(side="left", padx=(0, 2))
        tk.Label(s1_hdr, text=(s1_title or "POS").upper(), font=("Segoe UI", 9, "bold"), fg="#28A745", bg="#FFFFFF").pack(side="left")

        tk.Label(b1, text=(s1_sub or "REGULAR POS LOGIN").upper(), font=("Segoe UI", 7, "bold"), fg="#000000", bg="#FFFFFF", wraplength=160).pack()
        tk.Label(b1, text=s1_body or "Mag log in sa POS tulad ng nakasanayan.", font=("Segoe UI", 6), fg="#555555", bg="#FFFFFF", justify="center", wraplength=160).pack()

        tk.Label(box_frame, text="➔", font=("Segoe UI", 12, "bold"), fg="#001B3A", bg="#FFFFFF").grid(row=0, column=1)

        # Step 2
        b2 = tk.Frame(box_frame, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#0056B3")
        b2.config(highlightthickness=1, highlightcolor="#0056B3")
        b2.grid(row=0, column=2, padx=6, ipadx=6, ipady=3)

        s2_hdr = tk.Frame(b2, bg="#FFFFFF")
        s2_hdr.pack(anchor="center", pady=(0, 2))
        tk.Label(s2_hdr, text="❷", font=("Segoe UI", 9, "bold"), fg="#0056B3", bg="#FFFFFF").pack(side="left", padx=(0, 2))
        tk.Label(s2_hdr, text=(s2_title or "E-SERVICES").upper(), font=("Segoe UI", 9, "bold"), fg="#0056B3", bg="#FFFFFF").pack(side="left")

        tk.Label(b2, text=(s2_sub or "E-SERVICES LOGIN").upper(), font=("Segoe UI", 7, "bold"), fg="#000000", bg="#FFFFFF", wraplength=160).pack()
        tk.Label(b2, text=s2_body or "Mag log in sa E-Services kada Cash-In.", font=("Segoe UI", 6), fg="#555555", bg="#FFFFFF", justify="center", wraplength=160).pack()

        # Warning
        warn_box = tk.Frame(preview_win, bg="#FFF3CD", bd=1, relief="solid", highlightbackground="#FFEEBA")
        warn_box.pack(fill="x", padx=20, pady=(4, 6), ipady=3)

        display_warn = warn_txt.strip() if warn_txt.strip() else ("UGALIIN MAG LOG IN AGAD SA E-SERVICES\nMATAPOS ANG POS REGULAR LOG IN\nPARA MAKAIWAS SA MGA TECHNICAL ERRORS")

        tk.Label(warn_box, text="⚠️", font=("Segoe UI", 10), bg="#FFF3CD").pack(side="left", padx=6)
        tk.Label(warn_box, text=display_warn, font=("Segoe UI", 6, "bold"), fg="#856404", bg="#FFF3CD", justify="left", wraplength=380).pack(side="left")

        tk.Button(
            preview_win, text="✔  OK, NAINTINDIHAN KO!", font=("Segoe UI", 8, "bold"),
            bg="#28A745", fg="white", padx=15, pady=3, bd=0, command=preview_win.destroy
        ).pack(pady=(0, 6))

    elif layout_type == "special":
        window_width = 480
        window_height = 340
        center_x = int((preview_win.winfo_screenwidth() / 2) - (window_width / 2))
        center_y = int((preview_win.winfo_screenheight() / 2) - (window_height / 2))
        preview_win.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        preview_win.resizable(False, False)

        header_frame = tk.Frame(preview_win, bg="#FFFFFF", pady=20)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame, text=(sub_title or "REMINDER").upper(), font=("Impact", 20),
            fg="#0A2540", bg="#FFFFFF"
        ).pack()

        div_frame = tk.Frame(preview_win, bg="#FFFFFF")
        div_frame.pack(fill="x", padx=35)
        tk.Frame(div_frame, bg="#666666", height=2).pack(fill="x", pady=(0, 12))

        body_frame = tk.Frame(preview_win, bg="#FFFFFF", padx=40, pady=6)
        body_frame.pack(fill="both", expand=True)

        display_msg = message.strip() if message.strip() else "SAMPLE MESSAGE"
        tk.Label(
            body_frame, text=display_msg, font=("Segoe UI", 12),
            fg="#1A1A1A", bg="#FFFFFF", justify="center", wraplength=400
        ).pack(anchor="center", fill="both", expand=True)

        display_btn_name = (btn_name or "").strip() or "LINK BUTTON"
        display_btn_link = (btn_link or "").strip() or "(no link set)"

        tk.Button(
            preview_win, text=f"🔗  {display_btn_name}", font=("Segoe UI", 9, "bold"),
            bg="#0056B3", fg="white", activebackground="#00408a", activeforeground="white",
            padx=20, pady=4, bd=0, cursor="hand2",
            # Preview-only: shows what will happen instead of actually opening
            # a browser, since this is just a WYSIWYG mockup for the operator.
            command=lambda: messagebox.showinfo(
                "Preview — Link Button", f"This button will open:\n{display_btn_link}",
                parent=preview_win
            )
        ).pack(pady=(4, 6))

        tk.Button(
            preview_win, text="✔  OK, NAINTINDIHAN KO!", font=("Segoe UI", 9, "bold"),
            bg="#28A745", fg="white", activebackground="#218838", activeforeground="white",
            padx=20, pady=4, bd=0, cursor="hand2", command=preview_win.destroy
        ).pack(pady=(0, 10))

    else:
        window_width = 580
        window_height = 460
        center_x = int((preview_win.winfo_screenwidth() / 2) - (window_width / 2))
        center_y = int((preview_win.winfo_screenheight() / 2) - (window_height / 2))
        preview_win.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        preview_win.resizable(False, False)

        header_frame = tk.Frame(preview_win, bg="#FFFFFF", pady=25)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame, text=(sub_title or "REMINDER").upper(), font=("Impact", 24),
            fg="#0A2540", bg="#FFFFFF"
        ).pack()

        div_frame = tk.Frame(preview_win, bg="#FFFFFF")
        div_frame.pack(fill="x", padx=35)
        tk.Frame(div_frame, bg="#666666", height=2).pack(fill="x", pady=(0, 15))

        body_frame = tk.Frame(preview_win, bg="#FFFFFF", padx=50, pady=10)
        body_frame.pack(fill="both", expand=True)

        tk.Label(
            body_frame, text=message, font=("Segoe UI", 13),
            fg="#1A1A1A", bg="#FFFFFF", justify="left", wraplength=480
        ).pack(anchor="w", fill="both", expand=True)

        btn_frame = tk.Frame(preview_win, bg="#FFFFFF", pady=25)
        btn_frame.pack(fill="x")

        tk.Button(
            btn_frame, text="✔  OK, NAINTINDIHAN KO!", font=("Segoe UI", 9, "bold"),
            bg="#28A745", fg="white", activebackground="#218838", activeforeground="white",
            padx=25, pady=5, bd=0, cursor="hand2", command=preview_win.destroy
        ).pack()