def adjust_window_geometry(root):
    root.update_idletasks()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Keeps height strictly under screen bounds for 768p displays
    target_width = min(840, screen_width - 40)
    target_height = min(640, screen_height - 80)

    center_x = int((screen_width / 2) - (target_width / 2))
    center_y = int((screen_height / 2) - (target_height / 2))

    root.geometry(f"{target_width}x{target_height}+{center_x}+{center_y}")
    root.minsize(780, 520)
    root.resizable(True, True)
