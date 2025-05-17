"""
Theme configuration for the Pharmacy Management System.
This file defines colors and styles used throughout the application.
"""
import tkinter as tk
from tkinter import ttk

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

def apply_theme(root):
    """Apply the theme to the root window and configure ttk styles."""
    style = ttk.Style()

    # Configure the root window
    root.configure(background=BACKGROUND_COLOR)

    # Configure ttk styles - basic styles
    style.configure('TFrame', background=BACKGROUND_COLOR)
    style.configure('TLabel', background=BACKGROUND_COLOR, foreground=TEXT_COLOR)

    # Custom button style that works with ttk
    style.configure('Custom.TButton',
                   background=PRIMARY_COLOR,
                   foreground=TEXT_COLOR_LIGHT,
                   borderwidth=1,
                   relief="raised")
    style.map('Custom.TButton',
             background=[('active', SECONDARY_COLOR), ('pressed', SECONDARY_COLOR)])

    # Header style
    style.configure('Header.TFrame', background=PRIMARY_COLOR)
    style.configure('Header.TLabel', background=PRIMARY_COLOR, foreground=TEXT_COLOR_LIGHT, font=('Arial', 14, 'bold'))

    # Sidebar style
    style.configure('Sidebar.TFrame', background=PRIMARY_COLOR)
    style.configure('Sidebar.TLabel', background=PRIMARY_COLOR, foreground=TEXT_COLOR_LIGHT)
    style.configure('Sidebar.TButton',
                   background=PRIMARY_COLOR,
                   foreground=TEXT_COLOR_LIGHT,
                   borderwidth=0)
    style.map('Sidebar.TButton',
             background=[('active', SECONDARY_COLOR), ('pressed', SECONDARY_COLOR)])

    # Dashboard stat box styles
    for i, color in enumerate(STAT_BOX_COLORS):
        style.configure(f'StatBox{i}.TFrame', background=color)
        style.configure(f'StatBox{i}.TLabel', background=color, foreground=TEXT_COLOR_LIGHT)

    # Configure Treeview
    style.configure('Treeview',
                   background=BACKGROUND_COLOR,
                   foreground=TEXT_COLOR,
                   fieldbackground=BACKGROUND_COLOR)
    style.map('Treeview',
             background=[('selected', PRIMARY_COLOR)],
             foreground=[('selected', TEXT_COLOR_LIGHT)])

    # Configure Notebook (tabs)
    style.configure('TNotebook', background=BACKGROUND_COLOR)
    style.configure('TNotebook.Tab', background=BACKGROUND_COLOR, foreground=TEXT_COLOR)
    style.map('TNotebook.Tab',
             background=[('selected', PRIMARY_COLOR)],
             foreground=[('selected', TEXT_COLOR_LIGHT)])

    # Configure Entry
    style.configure('TEntry', foreground=TEXT_COLOR)

    # RTL styles for Arabic
    style.configure('RTL.TLabel', justify='right')
    style.configure('RTL.TEntry', justify='right')

    # Login button style
    style.configure('Login.TButton',
                   background=PRIMARY_COLOR,
                   foreground=TEXT_COLOR_LIGHT,
                   borderwidth=1,
                   relief="raised")
    style.map('Login.TButton',
             background=[('active', SECONDARY_COLOR), ('pressed', SECONDARY_COLOR)])

def create_sidebar(parent, buttons_config):
    """
    Create a styled sidebar with the given buttons configuration.

    Args:
        parent: The parent widget
        buttons_config: List of dictionaries with 'text' and 'command' keys

    Returns:
        The sidebar frame
    """
    sidebar = ttk.Frame(parent, style='Sidebar.TFrame', width=200)
    sidebar.pack(side=tk.RIGHT, fill=tk.Y)
    sidebar.pack_propagate(False)  # Prevent the frame from shrinking

    # Add logo or system name at the top
    logo_frame = ttk.Frame(sidebar, style='Sidebar.TFrame')
    logo_frame.pack(fill=tk.X, pady=20)

    # System name
    ttk.Label(logo_frame, text="نظام إدارة\nالصيدلية",
              style='Sidebar.TLabel', font=('Arial', 16, 'bold'),
              justify='center').pack(pady=10)

    # Add buttons
    for btn_config in buttons_config:
        btn = ttk.Button(sidebar, text=btn_config['text'],
                        command=btn_config['command'],
                        style='Sidebar.TButton')
        btn.pack(fill=tk.X, padx=10, pady=5)

    return sidebar

def create_stat_box(parent, title, value, index):
    """
    Create a styled stat box for the dashboard.

    Args:
        parent: The parent widget
        title: The title of the stat box
        value: The value to display
        index: The index for styling (0-3)

    Returns:
        The stat box frame
    """
    # Use modulo to cycle through colors if index > 3
    style_index = index % len(STAT_BOX_COLORS)

    frame = ttk.Frame(parent, style=f'StatBox{style_index}.TFrame')
    frame.grid(row=0, column=index, padx=10, pady=5, sticky="nsew")

    # Make the frame look like a card
    frame.configure(padding=(10, 10, 10, 10))

    # Add title and value
    ttk.Label(frame, text=title, style=f'StatBox{style_index}.TLabel').pack(anchor='e')
    ttk.Label(frame, text=str(value), style=f'StatBox{style_index}.TLabel',
             font=('Arial', 24, 'bold')).pack(pady=10)

    return frame

def create_header(parent, title, username=None, role=None):
    """
    Create a styled header for windows.

    Args:
        parent: The parent widget
        title: The title to display
        username: Optional username to display
        role: Optional role to display

    Returns:
        The header frame
    """
    header = ttk.Frame(parent, style='Header.TFrame')
    header.pack(fill=tk.X)

    # Add title
    ttk.Label(header, text=title, style='Header.TLabel').pack(side=tk.RIGHT, padx=20, pady=10)

    # Add user info if provided
    if username and role:
        user_info = f"{username} - {role}"
        ttk.Label(header, text=user_info, style='Header.TLabel').pack(side=tk.LEFT, padx=20, pady=10)

    return header
