"""
Custom theme implementation for the Pharmacy Management System.
This file provides a more direct approach to styling the application.
"""
import tkinter as tk
from tkinter import ttk
import os

# Color Constants
PRIMARY_COLOR = "#0D6E6E"  # Dark teal/green for sidebar and headers
SECONDARY_COLOR = "#4ECDC4"  # Light teal for stat boxes
ACCENT_COLOR_1 = "#FF6B6B"  # Orange/red for some stat boxes
ACCENT_COLOR_2 = "#3498DB"  # Blue for some stat boxes
ACCENT_COLOR_3 = "#F7B731"  # Yellow for some elements
BACKGROUND_COLOR = "#F5F5F5"  # Light gray for backgrounds
TEXT_COLOR = "#333333"  # Dark gray for text
TEXT_COLOR_LIGHT = "#FFFFFF"  # White text for dark backgrounds
BORDER_COLOR = "#DDDDDD"  # Light gray for borders

# Stat Box Colors (for dashboard)
STAT_BOX_COLORS = [
    SECONDARY_COLOR,  # Light teal
    ACCENT_COLOR_1,   # Orange/red
    PRIMARY_COLOR,    # Dark teal
    ACCENT_COLOR_2    # Blue
]

def create_colored_button(parent, text, command, bg_color=PRIMARY_COLOR, fg_color=TEXT_COLOR_LIGHT,
                         hover_color=SECONDARY_COLOR, **kwargs):
    """Create a button with custom colors using tk.Button instead of ttk.Button"""
    button = tk.Button(parent, text=text, command=command,
                      bg=bg_color, fg=fg_color,
                      activebackground=hover_color, activeforeground=fg_color,
                      relief=tk.RAISED, bd=1, **kwargs)
    return button

def create_colored_frame(parent, bg_color=PRIMARY_COLOR, **kwargs):
    """Create a frame with custom background color using tk.Frame instead of ttk.Frame"""
    frame = tk.Frame(parent, bg=bg_color, **kwargs)
    return frame

def create_colored_label(parent, text, bg_color=BACKGROUND_COLOR, fg_color=TEXT_COLOR, **kwargs):
    """Create a label with custom colors using tk.Label instead of ttk.Label"""
    label = tk.Label(parent, text=text, bg=bg_color, fg=fg_color, **kwargs)
    return label

def create_sidebar(parent, buttons_config):
    """Create a styled sidebar with the given buttons configuration."""
    sidebar = create_colored_frame(parent, bg_color=PRIMARY_COLOR, width=200)
    sidebar.pack(side=tk.RIGHT, fill=tk.Y)
    sidebar.pack_propagate(False)  # Prevent the frame from shrinking

    # Add logo or system name at the top
    logo_frame = create_colored_frame(sidebar, bg_color=PRIMARY_COLOR)
    logo_frame.pack(fill=tk.X, pady=20)

    # System name
    create_colored_label(logo_frame, text="نظام إدارة\nالصيدلية",
                        bg_color=PRIMARY_COLOR, fg_color=TEXT_COLOR_LIGHT,
                        font=('Arial', 16, 'bold'), justify='center').pack(pady=10)

    # Add icon if available
    icon_path = os.path.join('assets', 'icon.png')
    if os.path.exists(icon_path):
        try:
            icon_image = tk.PhotoImage(file=icon_path)
            icon_label = tk.Label(logo_frame, image=icon_image, bg=PRIMARY_COLOR)
            icon_label.image = icon_image  # Keep a reference
            icon_label.pack(pady=10)
        except:
            pass

    # Add buttons
    for btn_config in buttons_config:
        btn = create_colored_button(sidebar, text=btn_config['text'],
                                  command=btn_config['command'],
                                  bg_color=PRIMARY_COLOR,
                                  fg_color=TEXT_COLOR_LIGHT,
                                  hover_color=SECONDARY_COLOR,
                                  width=15, height=1)
        btn.pack(fill=tk.X, padx=10, pady=5)

    return sidebar

def create_stat_box(parent, title, value, index):
    """Create a styled stat box for the dashboard."""
    # Use modulo to cycle through colors if index > 3
    color_index = index % len(STAT_BOX_COLORS)
    bg_color = STAT_BOX_COLORS[color_index]

    frame = create_colored_frame(parent, bg_color=bg_color, padx=10, pady=10)
    frame.grid(row=0, column=index, padx=10, pady=5, sticky="nsew")

    # Add title and value
    create_colored_label(frame, text=title,
                        bg_color=bg_color, fg_color=TEXT_COLOR_LIGHT,
                        anchor='e', justify='right').pack(anchor='e')

    create_colored_label(frame, text=str(value),
                        bg_color=bg_color, fg_color=TEXT_COLOR_LIGHT,
                        font=('Arial', 24, 'bold')).pack(pady=10)

    return frame

def create_header(parent, title, username=None, role=None):
    """Create a styled header for windows."""
    header = create_colored_frame(parent, bg_color=PRIMARY_COLOR)
    header.pack(fill=tk.X)

    # Add title
    create_colored_label(header, text=title,
                        bg_color=PRIMARY_COLOR, fg_color=TEXT_COLOR_LIGHT,
                        font=('Arial', 14, 'bold')).pack(side=tk.RIGHT, padx=20, pady=10)

    # Add user info if provided
    if username and role:
        user_info = f"{username} - {role}"
        create_colored_label(header, text=user_info,
                           bg_color=PRIMARY_COLOR, fg_color=TEXT_COLOR_LIGHT).pack(side=tk.LEFT, padx=20, pady=10)

    return header

def create_login_panel():
    """Create a styled login panel."""
    # This is a placeholder for future implementation
    pass
