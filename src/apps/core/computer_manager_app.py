#!/usr/bin/env python3
"""
JAMF Dashboard App Launcher - Persistent Browser Window with Auto-Reload
"""
import dash
from dash import dcc, html, Input, Output, State, callback_context as ctx, ALL
import random
from datetime import datetime
import subprocess
import webbrowser
import time
import threading
import psutil
import os
import signal
import sys
from pathlib import Path
import requests
import json

# Global variables for process management
browser_process = None
server_process = None
backend_process = None
launcher_running = True

# Backend configuration
BACKEND_URL = "http://localhost:8900"

# Import unified backend client
from lib.utils.connect_backend import BackendClient

# Initialize backend client
backend_client = BackendClient()


def create_real_object_stats(obj_detail: dict, object_type: str):
    """Create real statistics display based on object type and data"""
    stats = []

    if object_type == "policies":
        # Policy-specific stats
        if obj_detail.get("enabled") is not None:
            status_color = "#34C759" if obj_detail["enabled"] else "#FF3B30"
            status_text = "Enabled" if obj_detail["enabled"] else "Disabled"
            stats.append(create_stat_row("Status:", status_text, status_color))

        if obj_detail.get("category"):
            stats.append(
                create_stat_row("Category:", obj_detail["category"], "#FFFFFF")
            )

        if obj_detail.get("frequency"):
            stats.append(
                create_stat_row("Frequency:", obj_detail["frequency"], "#FFFFFF")
            )

        if obj_detail.get("trigger"):
            stats.append(create_stat_row("Trigger:", obj_detail["trigger"], "#FFFFFF"))

        if obj_detail.get("scope"):
            scope = obj_detail["scope"]
            stats.append(
                create_stat_row(
                    "Scoped Computers:", f"{scope.get('computers', 0)}", "#007AFF"
                )
            )
            stats.append(
                create_stat_row(
                    "Scoped Groups:", f"{scope.get('computer_groups', 0)}", "#AF52DE"
                )
            )

        if obj_detail.get("packages") is not None:
            stats.append(
                create_stat_row("Packages:", f"{obj_detail['packages']}", "#FF3B30")
            )

        if obj_detail.get("scripts") is not None:
            stats.append(
                create_stat_row("Scripts:", f"{obj_detail['scripts']}", "#34C759")
            )

    elif object_type == "profiles":
        # Configuration Profile stats
        if obj_detail.get("distribution_method"):
            stats.append(
                create_stat_row(
                    "Distribution:", obj_detail["distribution_method"], "#FFFFFF"
                )
            )

        if obj_detail.get("level"):
            stats.append(create_stat_row("Level:", obj_detail["level"], "#FFFFFF"))

        if obj_detail.get("user_removable") is not None:
            removable_color = "#FF9F0A" if obj_detail["user_removable"] else "#34C759"
            removable_text = "Yes" if obj_detail["user_removable"] else "No"
            stats.append(
                create_stat_row("User Removable:", removable_text, removable_color)
            )

        if obj_detail.get("payloads") is not None:
            stats.append(
                create_stat_row("Payloads:", f"{obj_detail['payloads']}", "#007AFF")
            )

        if obj_detail.get("scope"):
            scope = obj_detail["scope"]
            stats.append(
                create_stat_row(
                    "Scoped Computers:", f"{scope.get('computers', 0)}", "#007AFF"
                )
            )
            stats.append(
                create_stat_row(
                    "Scoped Groups:", f"{scope.get('computer_groups', 0)}", "#AF52DE"
                )
            )

    elif object_type == "groups":
        # Computer Group stats
        if obj_detail.get("is_smart") is not None:
            group_type = "Smart Group" if obj_detail["is_smart"] else "Static Group"
            group_color = "#34C759" if obj_detail["is_smart"] else "#007AFF"
            stats.append(create_stat_row("Type:", group_type, group_color))

        if obj_detail.get("computers") is not None:
            stats.append(
                create_stat_row("Computers:", f"{obj_detail['computers']}", "#007AFF")
            )

        if obj_detail.get("criteria") is not None and obj_detail.get("is_smart"):
            stats.append(
                create_stat_row("Criteria:", f"{obj_detail['criteria']}", "#34C759")
            )

        if obj_detail.get("site"):
            stats.append(create_stat_row("Site:", obj_detail["site"], "#FFFFFF"))

    elif object_type == "scripts":
        # Script stats
        if obj_detail.get("filename"):
            stats.append(
                create_stat_row("Filename:", obj_detail["filename"], "#FFFFFF")
            )

        if obj_detail.get("priority"):
            stats.append(
                create_stat_row("Priority:", obj_detail["priority"], "#FF9F0A")
            )

        if obj_detail.get("parameters") is not None:
            stats.append(
                create_stat_row("Parameters:", f"{obj_detail['parameters']}", "#34C759")
            )

        if obj_detail.get("os_requirements"):
            stats.append(
                create_stat_row(
                    "OS Requirements:", obj_detail["os_requirements"], "#FFFFFF"
                )
            )

    elif object_type == "packages":
        # Package stats
        if obj_detail.get("filename"):
            stats.append(
                create_stat_row("Filename:", obj_detail["filename"], "#FFFFFF")
            )

        if obj_detail.get("reboot_required") is not None:
            reboot_color = "#FF3B30" if obj_detail["reboot_required"] else "#34C759"
            reboot_text = "Yes" if obj_detail["reboot_required"] else "No"
            stats.append(create_stat_row("Reboot Required:", reboot_text, reboot_color))

        if obj_detail.get("priority"):
            stats.append(
                create_stat_row("Priority:", obj_detail["priority"], "#FF9F0A")
            )

    elif object_type == "categories":
        # Category stats
        if obj_detail.get("priority") is not None:
            stats.append(
                create_stat_row("Priority:", f"{obj_detail['priority']}", "#FF9F0A")
            )

    # Add timestamps if available
    if obj_detail.get("created"):
        stats.append(create_stat_row("Created:", obj_detail["created"][:10], "#8E8E93"))

    if obj_detail.get("modified"):
        stats.append(
            create_stat_row("Modified:", obj_detail["modified"][:10], "#8E8E93")
        )

    return html.Div(stats)


def create_stat_row(label: str, value: str, color: str = "#FFFFFF"):
    """Create a statistics row"""
    return html.Div(
        [
            html.Span(label, style={"color": "#8E8E93", "font-weight": "600"}),
            html.Span(
                value,
                style={
                    "color": color,
                    "margin-left": "8px",
                    "font-size": "16px",
                    "font-weight": "600",
                },
            ),
        ],
        style={"margin-bottom": "8px"},
    )


def kill_existing_processes():
    """Kill any existing processes on our ports and close existing browser windows"""
    # First, close any existing Chrome windows with our dashboard
    try:
        print("🔍 Closing any existing dashboard browser windows...")
        result = subprocess.run(
            ["pkill", "-f", "Chrome.*--app=http://127.0.0.1:8060"], capture_output=True
        )
        if result.returncode == 0:
            print("🔪 Closed existing dashboard browser windows")
        time.sleep(1)
    except Exception as e:
        print(f"⚠️  Error closing browser windows: {e}")

    ports_to_check = [8060, 8061, 8062]

    for port in ports_to_check:
        try:
            for proc in psutil.process_iter(["pid", "name", "connections"]):
                try:
                    for conn in proc.info["connections"] or []:
                        if conn.laddr.port == port:
                            print(
                                f"🔪 Killing existing process on port {port}: PID {proc.info['pid']}"
                            )
                            proc.kill()
                            time.sleep(1)
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    pass
        except Exception as e:
            print(f"⚠️  Error checking port {port}: {e}")


def launch_browser_window():
    """Launch a persistent browser window"""
    global browser_process

    try:
        # Kill any existing Chrome processes for our app (double-check)
        subprocess.run(
            ["pkill", "-f", "Chrome.*--app=http://127.0.0.1:8060"], capture_output=True
        )
        time.sleep(1)

        # Also try to close any Chrome windows with our URL in the title/URL
        subprocess.run(["pkill", "-f", "127.0.0.1:8060"], capture_output=True)
        time.sleep(1)

        # Launch Chrome in app mode (no address bar, looks like native app)
        browser_process = subprocess.Popen(
            [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "--app=http://127.0.0.1:8060",
                "--window-size=1400,900",
                "--window-position=100,100",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-translate",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--disable-ipc-flooding-protection",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print("🌐 Launched persistent browser window (app mode)")
        return True

    except Exception as e:
        print(f"❌ Error launching browser: {e}")
        return False


def monitor_server_health():
    """Monitor server health and restart if needed"""
    global launcher_running, server_process

    while launcher_running:
        try:
            # Check if server is responding
            import requests

            response = requests.get("http://127.0.0.1:8060", timeout=5)
            if response.status_code == 200:
                print("✅ Server health check passed")
            else:
                print("⚠️  Server responding but status not OK")
        except:
            print("❌ Server not responding, restarting...")
            restart_server()

        time.sleep(10)  # Check every 10 seconds


def restart_server():
    """Restart the server process"""
    global server_process

    try:
        if server_process:
            print("🔄 Restarting server...")
            server_process.terminate()
            time.sleep(2)
            server_process.kill()
            time.sleep(1)

        # Start new server process
        start_server_process()

    except Exception as e:
        print(f"❌ Error restarting server: {e}")


def start_server_process():
    """Start the server process"""
    global server_process

    try:
        server_process = subprocess.Popen(
            [sys.executable, __file__], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("🚀 Server process started")

    except Exception as e:
        print(f"❌ Error starting server: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global launcher_running, browser_process, server_process, backend_process

    print("\n🛑 Shutting down launcher...")
    launcher_running = False

    if browser_process:
        browser_process.terminate()

    if server_process:
        server_process.terminate()

    if backend_process:
        backend_process.terminate()
        print("🛑 Enhanced backend stopped")

    sys.exit(0)


# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "JPAPI Computer Dash - App"

# CSS Styles (identical to live Dash)
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #000000;
                color: #FFFFFF;
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }
            
            .nav-header {
                background: linear-gradient(135deg, #1C1C1E 0%, #2C2C2E 100%);
                padding: clamp(12px, 2vw, 24px);
                border-bottom: 1px solid #38383A;
                margin-bottom: clamp(12px, 3vh, 24px);
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: clamp(8px, 2vw, 16px);
            }
            
            .nav-title {
                font-size: clamp(20px, 4vw, 28px);
                font-weight: 700;
                color: #FFFFFF;
                margin: 0;
                line-height: 1.2;
            }
            
            .nav-subtitle {
                font-size: clamp(12px, 2vw, 14px);
                color: #8E8E93;
                margin: 0;
            }
            
            .stat-card {
                background: #1C1C1E;
                border: 1px solid #38383A;
                border-radius: 8px;
                padding: clamp(12px, 2vw, 20px);
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
                cursor: pointer;
                color: #FFFFFF;
                min-height: clamp(80px, 15vh, 120px);
                display: flex;
                flex-direction: column;
                justify-content: center;
                aspect-ratio: 1.2;
            }
            
            .stat-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.6);
                border-color: #48484A;
            }
            
            .stat-number {
                font-size: clamp(24px, 4vw, 32px);
                font-weight: 700;
                color: #FFFFFF;
                margin-bottom: clamp(4px, 1vh, 8px);
                line-height: 1.1;
            }
            
            .stat-label {
                font-size: clamp(12px, 2vw, 14px);
                color: #8E8E93;
                font-weight: 500;
            }
            
            .object-card {
                background: #1C1C1E;
                border: 1px solid #38383A;
                border-radius: 8px;
                padding: clamp(6px, 1.5vw, 12px);
                margin-bottom: clamp(4px, 1vh, 8px);
                transition: all 0.2s ease;
                cursor: pointer;
                color: #FFFFFF;
                position: relative;
                min-height: clamp(50px, 8vh, 70px);
                overflow: hidden;
            }
            
            .object-card:hover {
                background: linear-gradient(135deg, #2C2C2E, #3C3C3E);
                border-color: #48484A;
                transform: translateY(-1px);
                box-shadow: 0 4px 16px rgba(0,0,0,0.4);
            }
            
            .relationship-bubbles {
                margin-top: 6px;
                text-align: right;
                line-height: 1.0;
                display: flex;
                flex-wrap: wrap;
                justify-content: flex-end;
                gap: 1px;
            }
            
            .usage-bubble {
                display: inline-block;
                padding: clamp(1px, 0.2vw, 2px) clamp(2px, 0.5vw, 3px);
                border-radius: clamp(3px, 0.8vw, 4px);
                font-size: clamp(6px, 1.2vw, 8px);
                font-weight: 500;
                margin: clamp(0.3px, 0.1vw, 0.5px);
                text-align: center;
                line-height: 1.0;
                opacity: 0.8;
                transition: opacity 0.3s ease;
                min-width: clamp(10px, 2vw, 12px);
                max-width: clamp(18px, 3vw, 22px);
            }
            
            .usage-bubble:nth-child(1) { opacity: 1.0; }
            .usage-bubble:nth-child(2) { opacity: 0.9; }
            .usage-bubble:nth-child(3) { opacity: 0.8; }
            .usage-bubble:nth-child(4) { opacity: 0.7; }
            .usage-bubble:nth-child(5) { opacity: 0.6; }
            
            /* Relationship bubble hover effects */
            .relationship-bubble:hover .bubble-circle {
                transform: scale(1.1);
                box-shadow: 0 4px 16px rgba(0,0,0,0.4);
                border: 2px solid rgba(255,255,255,0.3) !important;
            }
            
            .relationship-bubble {
                transition: all 0.2s ease;
            }
            
            .bubble-circle {
                transition: all 0.2s ease;
            }
            .usage-bubble:nth-child(6) { opacity: 0.5; }
            .usage-bubble:nth-child(7) { opacity: 0.4; }
            .usage-bubble:nth-child(8) { opacity: 0.3; }
            .usage-bubble:nth-child(9) { opacity: 0.2; }
            .usage-bubble:nth-child(10) { opacity: 0.1; }
            
            .bubble-policies { background: rgba(0, 122, 255, 0.2); color: #007AFF; }
            .bubble-profiles { background: rgba(255, 159, 10, 0.2); color: #FF9F0A; }
            .bubble-scripts { background: rgba(52, 199, 89, 0.2); color: #34C759; }
            .bubble-packages { background: rgba(255, 59, 48, 0.2); color: #FF3B30; }
            .bubble-groups { background: rgba(175, 82, 222, 0.2); color: #AF52DE; }
            .bubble-categories { background: rgba(142, 142, 147, 0.2); color: #8E8E93; }
            .bubble-total { background: rgba(255, 255, 255, 0.1); color: #FFFFFF; }
            
            .status-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 500;
                background: #1C1C1E;
                border: 1px solid #38383A;
            }
            
            .status-connected {
                color: #34C759;
            }
            
            .status-disconnected {
                color: #FF3B30;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .dash-button {
                background: #007AFF;
                color: white;
                border: none;
                padding: clamp(6px, 1.5vw, 8px) clamp(12px, 2.5vw, 16px);
                border-radius: clamp(4px, 1vw, 6px);
                cursor: pointer;
                font-size: clamp(12px, 2.5vw, 14px);
                font-weight: 500;
                transition: background 0.2s ease;
                margin-bottom: clamp(12px, 3vh, 20px);
            }
            
            .dash-button:hover {
                background: #0056CC;
            }
            
            .app-status {
                position: fixed;
                top: 10px;
                right: 10px;
                background: rgba(0,0,0,0.8);
                color: #34C759;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                z-index: 1000;
                border: 1px solid #34C759;
            }
            
            /* Responsive containers */
            .main-container {
                padding: clamp(12px, 3vw, 24px);
                max-width: 100%;
                margin: 0 auto;
            }
            
            .grid-container {
                display: grid;
                gap: clamp(8px, 2vw, 16px);
                width: 100%;
            }
            
            .stat-grid {
                grid-template-columns: repeat(auto-fit, minmax(clamp(120px, 20vw, 200px), 1fr));
                grid-auto-rows: minmax(clamp(80px, 15vh, 120px), auto);
            }
            
            .object-grid {
                grid-template-columns: repeat(auto-fill, minmax(clamp(280px, 40vw, 400px), 1fr));
            }
            
            /* Header card responsive */
            .header-card {
                width: 100% !important;
                max-width: none !important;
                margin-bottom: clamp(8px, 2vh, 16px);
                padding: clamp(12px, 2vw, 20px) !important;
            }
            
            /* Media queries for specific breakpoints */
            @media (max-width: 768px) {
                .nav-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 8px;
                }
                
                .stat-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .object-grid {
                    grid-template-columns: 1fr;
                }
                
                .object-card {
                    margin-bottom: 6px;
                }
                
                .nav-title {
                    font-size: 20px;
                }
                
                .nav-subtitle {
                    font-size: 12px;
                }
            }
            
            @media (max-width: 480px) {
                .stat-grid {
                    grid-template-columns: 1fr 1fr;
                    gap: 8px;
                }
                
                .stat-card {
                    min-height: 70px;
                    padding: 8px;
                }
                
                .stat-number {
                    font-size: 20px;
                }
                
                .stat-label {
                    font-size: 11px;
                }
                
                .object-card {
                    padding: 8px;
                    min-height: 45px;
                }
                
                .main-container {
                    padding: 8px;
                }
            }
            
            @media (min-width: 1200px) {
                .stat-grid {
                    grid-template-columns: repeat(6, 1fr);
                }
                
                .object-grid {
                    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                }
            }
            
            @media (min-width: 1600px) {
                .object-grid {
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                }
                
                .main-container {
                    max-width: 1400px;
                }
            }
            
            /* Progress and task components */
            .progress-container {
                background: #1C1C1E;
                border: 1px solid #38383A;
                border-radius: 8px;
                padding: clamp(12px, 2vw, 16px);
                margin: clamp(8px, 2vh, 12px) 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            }
            
            /* Loading spinner animation */
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .progress-bar {
                width: 100%;
                height: clamp(6px, 1vh, 8px);
                background: #38383A;
                border-radius: 4px;
                overflow: hidden;
                margin: clamp(6px, 1vh, 8px) 0;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #007AFF, #34C759);
                transition: width 0.3s ease;
                border-radius: 4px;
            }
            
            .task-button {
                background: #FF9500;
                color: white;
                border: none;
                padding: clamp(6px, 1.5vw, 8px) clamp(12px, 2.5vw, 16px);
                border-radius: clamp(4px, 1vw, 6px);
                cursor: pointer;
                font-size: clamp(11px, 2vw, 13px);
                font-weight: 500;
                transition: background 0.2s ease;
                margin: clamp(2px, 0.5vw, 4px);
            }
            
            .task-button:hover {
                background: #FF8C00;
            }
            
            .task-button:disabled {
                background: #38383A;
                cursor: not-allowed;
            }
            
            .task-status {
                font-size: clamp(11px, 2vw, 12px);
                color: #8E8E93;
                margin-top: clamp(4px, 1vh, 6px);
            }
            
            .spinner {
                border: 2px solid #38383A;
                border-top: 2px solid #007AFF;
                border-radius: 50%;
                width: clamp(12px, 2vw, 16px);
                height: clamp(12px, 2vw, 16px);
                animation: spin 1s linear infinite;
                display: inline-block;
                margin-right: clamp(4px, 1vw, 8px);
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="app-status">🟢 App Running</div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


def create_stat_card(label: str, value: int, card_type: str) -> html.Div:
    """Create a stat card with colored left border"""
    colors = {
        "policies": "#007AFF",
        "profiles": "#FF9F0A",
        "scripts": "#34C759",
        "packages": "#FF3B30",
        "groups": "#AF52DE",
        "categories": "#8E8E93",
    }

    border_color = colors.get(card_type, "#8E8E93")

    return html.Div(
        [
            html.Div(str(value), className="stat-number"),
            html.Div(label, className="stat-label"),
        ],
        className="stat-card",
        id={"type": "stat-card", "object_type": card_type},
        style={"cursor": "pointer", "border-left": f"4px solid {border_color}"},
    )


def create_header_card(title: str, count: int, object_type: str) -> html.Div:
    """Create a header card with Apple-style design and fade effect"""
    colors = {
        "policies": "#007AFF",
        "profiles": "#FF9F0A",
        "scripts": "#34C759",
        "packages": "#FF3B30",
        "groups": "#AF52DE",
        "categories": "#8E8E93",
    }

    border_color = colors.get(object_type, "#8E8E93")
    accent_color = border_color + "20"

    return html.Div(
        [
            html.Div(
                [
                    html.Button(
                        "← Back to Dashboard",
                        id="back-to-dashboard",
                        style={
                            "background": "#007AFF",
                            "color": "#FFFFFF",
                            "border": "none",
                            "padding": "8px 16px",
                            "border-radius": "6px",
                            "font-size": "12px",
                            "cursor": "pointer",
                            "margin-right": "16px",
                            "transition": "all 0.2s ease",
                        },
                    ),
                    html.Span(
                        f"📋 {title}",
                        style={
                            "font-size": "20px",
                            "font-weight": "700",
                            "color": "#FFFFFF",
                        },
                    ),
                    html.Span(
                        f"({count})",
                        style={
                            "font-size": "18px",
                            "font-weight": "600",
                            "color": border_color,
                            "margin-left": "8px",
                        },
                    ),
                ],
                style={"display": "flex", "align-items": "center"},
            ),
            html.Div(
                style={
                    "height": "3px",
                    "background": f"linear-gradient(90deg, {border_color} 0%, {accent_color} 50%, #8E8E93 100%)",
                    "border-radius": "0 0 12px 12px",
                    "margin": "12px -20px -16px -20px",
                }
            ),
            html.Div(
                style={
                    "position": "absolute",
                    "top": "0",
                    "right": "0",
                    "bottom": "0",
                    "width": "50px",
                    "background": "linear-gradient(90deg, transparent 0%, rgba(0,0,0,0.1) 30%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0.6) 100%)",
                    "pointer-events": "none",
                    "border-radius": "0 12px 12px 0",
                }
            ),
        ],
        className="header-card",
        style={
            "background": "linear-gradient(135deg, #1C1C1E 0%, #2C2C2E 100%)",
            "border-left": f"6px solid {border_color}",
            "border-radius": "clamp(8px, 2vw, 12px)",
            "box-shadow": f"0 4px 16px rgba(0,0,0,0.4), inset 0 0 0 1px {accent_color}",
            "border": "1px solid #38383A",
            "position": "relative",
            "overflow": "hidden",
        },
    )


def create_object_card(obj: dict, object_type: str) -> html.Div:
    """Create a smaller object card with right-colored border, text truncation, and relationship bubbles"""
    colors = {
        "policies": "#007AFF",
        "profiles": "#FF9F0A",
        "scripts": "#34C759",
        "packages": "#FF3B30",
        "groups": "#AF52DE",
        "categories": "#8E8E93",
    }

    border_color = colors.get(object_type, "#8E8E93")
    obj_id = obj.get("id", "Unknown") or f"unknown_{random.randint(1000,9999)}"
    obj_name = obj.get("name", "Unknown") or "Unknown"

    # Truncate long names
    display_name = obj_name[:25] + "..." if len(obj_name) > 25 else obj_name

    card_content = [
        html.Div(
            [
                html.Span(
                    f"📋 {display_name}",
                    style={
                        "font-size": "clamp(12px, 2.5vw, 14px)",
                        "font-weight": "500",
                        "white-space": "nowrap",
                        "overflow": "hidden",
                        "text-overflow": "ellipsis",
                        "max-width": "clamp(150px, 30vw, 200px)",
                        "display": "inline-block",
                    },
                ),
                html.Span(
                    f"ID: {obj_id}",
                    style={
                        "color": "#8E8E93",
                        "font-size": "clamp(9px, 1.5vw, 10px)",
                        "float": "right",
                    },
                ),
            ],
            style={
                "margin-bottom": "clamp(3px, 1vh, 6px)",
                "display": "flex",
                "justify-content": "space-between",
                "align-items": "center",
            },
        ),
        html.Div(
            [
                html.Span(
                    f"Mock {object_type} description for testing purposes",
                    style={
                        "color": "#8E8E93",
                        "font-size": "clamp(9px, 1.5vw, 10px)",
                        "white-space": "nowrap",
                        "overflow": "hidden",
                        "text-overflow": "ellipsis",
                        "max-width": "clamp(200px, 40vw, 250px)",
                        "display": "inline-block",
                    },
                )
            ],
            style={"margin-bottom": "clamp(3px, 1vh, 6px)"},
        ),
        html.Div(
            [
                html.Span(
                    "→",
                    style={
                        "color": "#8E8E93",
                        "font-size": "clamp(12px, 2.5vw, 14px)",
                        "float": "right",
                        "margin-top": "clamp(1px, 0.5vh, 2px)",
                    },
                )
            ]
        ),
    ]

    # Show object type instead of relationship bubbles (for performance)
    card_content.append(
        html.Div(
            [
                html.Span(
                    f"Type: {object_type}",
                    style={"color": "#8E8E93", "font-size": "clamp(11px, 2vw, 12px)"},
                )
            ],
            style={"margin-top": "clamp(6px, 1.5vh, 8px)"},
        )
    )

    return html.Div(
        card_content,
        className="object-card",
        id={"type": "object-card", "object_type": object_type, "object_id": obj_id},
        style={"cursor": "pointer", "border-right": f"3px solid {border_color}"},
    )


def render_dashboard():
    """Render the main dashboard with real data from enhanced backend"""
    # Try to get real data from enhanced backend
    stats_response = backend_client.get_stats()

    if stats_response and stats_response.get("success") and stats_response.get("data"):
        # Extract data from new backend format
        stats_data = stats_response["data"]
        print(f"✅ Loaded real JAMF stats: {stats_data}")
    else:
        # Fallback to mock data if backend unavailable
        stats_data = {
            "policies": random.randint(1200, 1500),
            "profiles": random.randint(800, 1000),
            "scripts": random.randint(500, 700),
            "packages": random.randint(1100, 1300),
            "groups": random.randint(600, 800),
            "categories": random.randint(2500, 3000),
            "source": "mock_fallback",
        }
        print(f"⚠️ Using fallback stats: {stats_data}")

    stat_cards = html.Div(
        [
            create_stat_card("Policies", stats_data["policies"], "policies"),
            create_stat_card("Profiles", stats_data["profiles"], "profiles"),
            create_stat_card("Scripts", stats_data["scripts"], "scripts"),
            create_stat_card("Packages", stats_data["packages"], "packages"),
            create_stat_card("Groups", stats_data["groups"], "groups"),
            create_stat_card("Categories", stats_data["categories"], "categories"),
        ],
        className="grid-container stat-grid",
        style={"margin-bottom": "clamp(16px, 4vh, 32px)"},
    )

    return html.Div(
        [
            html.H2(
                "📊 JPAPI Computer Dash Environment",
                style={
                    "font-size": "clamp(20px, 4vw, 28px)",
                    "margin-bottom": "clamp(8px, 2vh, 16px)",
                },
            ),
            html.P(
                "Backend API serving real-time data • Click stat cards to explore objects",
                style={
                    "color": "#8E8E93",
                    "margin-bottom": "clamp(12px, 3vh, 24px)",
                    "font-size": "clamp(14px, 2.5vw, 16px)",
                },
            ),
            create_simple_controls(),
            stat_cards,
        ],
        className="main-container",
    )


def create_progress_component(
    task_name: str, progress: int = 0, message: str = "", task_id: str = ""
):
    """Create a progress indicator component"""
    return html.Div(
        [
            html.H4(
                f"🔄 {task_name}",
                style={"margin": "0 0 8px 0", "font-size": "clamp(14px, 2.5vw, 16px)"},
            ),
            html.Div(
                [
                    html.Div(
                        style={
                            "width": f"{progress}%",
                            "height": "100%",
                            "background": "linear-gradient(90deg, #007AFF, #34C759)",
                            "border-radius": "4px",
                            "transition": "width 0.3s ease",
                        }
                    )
                ],
                className="progress-bar",
            ),
            html.Div(
                [
                    html.Span(f"{progress}% ", style={"font-weight": "500"}),
                    html.Span(message, style={"color": "#8E8E93"}),
                ],
                className="task-status",
            ),
            html.Div(id=f"task-result-{task_id}", style={"margin-top": "8px"}),
        ],
        className="progress-container",
    )


def create_task_button(object_type: str, object_id: str):
    """Create a button to start relationship analysis"""
    return html.Button(
        f"🔍 Analyze Relationships",
        id=f"analyze-btn-{object_type}-{object_id}",
        className="task-button",
        style={"margin-top": "8px"},
    )


def create_simple_controls():
    """Create simple control panel"""
    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        "🔄 Quick Actions:",
                        style={
                            "color": "#8E8E93",
                            "font-size": "clamp(14px, 2.5vw, 16px)",
                            "margin-right": "12px",
                        },
                    ),
                    html.Button(
                        "Refresh Stats",
                        id="simple-refresh-btn",
                        style={
                            "background": "#34C759",
                            "color": "white",
                            "border": "none",
                            "padding": "6px 12px",
                            "border-radius": "6px",
                            "font-size": "12px",
                            "cursor": "pointer",
                            "margin-right": "8px",
                        },
                    ),
                    html.Span(
                        "",
                        id="refresh-status",
                        style={
                            "color": "#8E8E93",
                            "font-size": "12px",
                            "margin-left": "8px",
                        },
                    ),
                ],
                style={"margin-bottom": "16px"},
            ),
            html.Div(
                id="loading-indicator", children=[], style={"margin-bottom": "12px"}
            ),
        ]
    )


def create_loading_spinner(message="Loading..."):
    """Create a simple loading indicator"""
    return html.Div(
        [
            html.Div(
                "⏳",
                style={
                    "display": "inline-block",
                    "animation": "spin 1s linear infinite",
                    "margin-right": "8px",
                    "font-size": "14px",
                },
            ),
            html.Span(
                message,
                style={"color": "#FF9500", "font-size": "12px", "font-weight": "500"},
            ),
        ],
        style={
            "background": "rgba(255, 149, 0, 0.1)",
            "border": "1px solid rgba(255, 149, 0, 0.3)",
            "border-radius": "6px",
            "padding": "8px 12px",
            "display": "inline-block",
        },
    )


def render_object_list(object_type: str):
    """Render object list view with real data from enhanced backend"""
    # Try to get real data from enhanced backend
    objects_response = backend_client.get_objects(object_type, limit=50)

    if (
        objects_response
        and objects_response.get("success")
        and objects_response.get("data")
    ):
        # Extract data from new backend format
        objects = objects_response["data"]
        count = objects_response.get("count", len(objects))
        print(f"✅ Loaded {len(objects)} {object_type} objects")
    else:
        # Fallback to mock data if backend unavailable
        objects = []
        for i in range(20):
            objects.append(
                {
                    "id": random.randint(1000, 9999),
                    "name": f"{object_type.title()} {i+1}",
                    "description": f"Mock {object_type} description for testing purposes",
                }
            )
        count = len(objects)

    object_cards = [create_object_card(obj, object_type) for obj in objects]
    header_card = create_header_card(object_type.title(), count, object_type)

    return (
        html.Div(
            [
                header_card,
                html.Div(object_cards, className="grid-container object-grid"),
            ],
            className="main-container",
        ),
        objects,
    )


def render_object_detail(obj: dict, object_type: str):
    """Render object detail view with real JAMF data"""
    # Get detailed object data from backend
    detail_data = backend_client.get_object_detail(object_type, str(obj["id"]))

    if detail_data and detail_data.get("object"):
        obj_detail = detail_data["object"]
        source = detail_data.get("source", "unknown")
    else:
        # Fallback to basic object data
        obj_detail = obj
        source = "fallback"

    return html.Div(
        [
            html.Button("← Back to List", id="back-to-list", className="dash-button"),
            html.H2(f"📋 {obj_detail.get('name', obj['name'])}"),
            html.P(
                f"ID: {obj_detail.get('id', obj['id'])} • Type: {object_type.title()} • Source: {source}",
                style={"color": "#8E8E93", "margin-bottom": "16px"},
            ),
            html.P(
                obj_detail.get(
                    "description", obj.get("description", "No description available")
                ),
                style={
                    "color": "#E5E5E7",
                    "font-size": "14px",
                    "margin-bottom": "24px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                "📊 Object Details",
                                style={"color": "#FFFFFF", "margin-bottom": "16px"},
                            ),
                            create_real_object_stats(obj_detail, object_type),
                        ],
                        style={
                            "background": "#1C1C1E",
                            "padding": "16px",
                            "border-radius": "8px",
                            "border": "1px solid #38383A",
                        },
                    ),
                    # Add relationships section
                    html.Div(
                        [
                            html.H3(
                                "🔗 Relationships",
                                style={"color": "#FFFFFF", "margin-bottom": "16px"},
                            ),
                            create_real_relationships_display(obj_detail, object_type),
                        ],
                        style={
                            "background": "#1C1C1E",
                            "padding": "16px",
                            "border-radius": "8px",
                            "border": "1px solid #38383A",
                            "margin-top": "16px",
                        },
                    ),
                ],
                style={"display": "flex", "flex-direction": "column"},
            ),
        ]
    )


def create_real_relationships_display(obj_detail: dict, object_type: str):
    """Create relationships display with real data and interactive bubbles"""
    try:
        # First, try to extract immediate relationships from object detail
        immediate_relationships = extract_immediate_relationships(
            obj_detail, object_type
        )

        # Also try to get enhanced relationships from backend
        obj_id = obj_detail.get("id")
        relationships_data = None
        reverse_relationships_data = None

        if obj_id is not None:
            try:
                relationships_data = backend_client.get_object_relationships(
                    object_type, str(obj_id)
                )
            except Exception as e:
                print(f"Error fetching relationships: {e}")

            # Also try to get reverse relationships for comprehensive analysis
            try:
                reverse_response = backend_client._make_request(
                    f"/api/reverse-relationships/{object_type}/{obj_id}"
                )
                if reverse_response:
                    reverse_relationships_data = reverse_response
            except Exception as e:
                print(f"Error fetching reverse relationships: {e}")

        # Combine immediate, backend, and reverse relationships
        final_relationships = {}

        # Use immediate relationships as baseline
        if immediate_relationships:
            final_relationships.update(immediate_relationships)

        # Override with backend relationships if available
        if relationships_data and relationships_data.get("relationships"):
            backend_rels = relationships_data["relationships"]
            for rel_type, count in backend_rels.items():
                if count > 0:
                    final_relationships[rel_type] = count

        # Add reverse relationships
        if reverse_relationships_data and reverse_relationships_data.get(
            "relationships"
        ):
            reverse_rels = reverse_relationships_data["relationships"]
            for rel_type, count in reverse_rels.items():
                if count > 0:
                    # Use the higher count if we have both forward and reverse
                    final_relationships[rel_type] = max(
                        final_relationships.get(rel_type, 0), count
                    )

        # Create relationship bubbles
        if final_relationships:
            bubble_items = []
            color_map = {
                "policies": "#007AFF",
                "profiles": "#FF9F0A",
                "scripts": "#34C759",
                "packages": "#FF3B30",
                "groups": "#AF52DE",
                "computer_groups": "#AF52DE",
                "computers": "#5856D6",
            }

            for rel_type, count in final_relationships.items():
                if count > 0:
                    display_name = rel_type.replace("_", " ").title()
                    color = color_map.get(rel_type, "#8E8E93")

                    # Create clickable bubble
                    bubble = html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        str(count),
                                        style={
                                            "font-size": "18px",
                                            "font-weight": "700",
                                            "color": "white",
                                        },
                                    ),
                                    html.Div(
                                        display_name,
                                        style={
                                            "font-size": "11px",
                                            "font-weight": "500",
                                            "color": "white",
                                            "opacity": "0.9",
                                            "margin-top": "2px",
                                        },
                                    ),
                                ],
                                className="bubble-circle",
                                style={
                                    "background": color,
                                    "border-radius": "50%",
                                    "width": "70px",
                                    "height": "70px",
                                    "display": "flex",
                                    "flex-direction": "column",
                                    "align-items": "center",
                                    "justify-content": "center",
                                    "cursor": "pointer",
                                    "transition": "all 0.3s ease",
                                    "box-shadow": "0 4px 12px rgba(0,0,0,0.15)",
                                    "border": "3px solid rgba(255,255,255,0.2)",
                                },
                            ),
                            html.Div(
                                display_name,
                                style={
                                    "text-align": "center",
                                    "margin-top": "8px",
                                    "font-size": "12px",
                                    "font-weight": "600",
                                    "color": "#8E8E93",
                                },
                            ),
                        ],
                        className="relationship-bubble",
                        id={
                            "type": "relationship-bubble",
                            "object_type": rel_type,
                            "source_type": object_type,
                            "source_id": (
                                str(obj_detail.get("id", ""))
                                if obj_detail.get("id") is not None
                                else ""
                            ),
                        },
                        style={
                            "display": "flex",
                            "flex-direction": "column",
                            "align-items": "center",
                            "margin": "0 12px 16px 0",
                            "min-width": "80px",
                        },
                    )

                    bubble_items.append(bubble)

            if bubble_items:
                # Create bubbles container
                bubbles_container = html.Div(
                    [
                        html.Div(
                            "🔗 Related Objects",
                            style={
                                "font-size": "16px",
                                "font-weight": "700",
                                "color": "#FFFFFF",
                                "margin-bottom": "16px",
                            },
                        ),
                        html.Div(
                            bubble_items,
                            style={
                                "display": "flex",
                                "flex-wrap": "wrap",
                                "align-items": "flex-start",
                                "gap": "8px",
                            },
                        ),
                        # Add status indicator
                        html.Div(
                            [
                                html.P(
                                    (
                                        "Enhanced analysis in progress..."
                                        if (
                                            relationships_data
                                            and relationships_data.get("source")
                                            == "processing"
                                        )
                                        else (
                                            "From object scope"
                                            if immediate_relationships
                                            and not (
                                                relationships_data
                                                and relationships_data.get(
                                                    "relationships"
                                                )
                                            )
                                            else "Click bubbles to explore relationships"
                                        )
                                    ),
                                    style={
                                        "color": "#8E8E93",
                                        "font-size": "12px",
                                        "font-style": "italic",
                                        "margin-top": "12px",
                                        "text-align": "center",
                                    },
                                )
                            ]
                        ),
                    ],
                    style={
                        "background": "#1C1C1E",
                        "padding": "20px",
                        "border-radius": "12px",
                        "border": "1px solid #38383A",
                        "margin-top": "16px",
                    },
                )

                return bubbles_container

        # Show "No relationships found" when there are no relationships
        return html.Div(
            [
                html.P(
                    "No relationships found",
                    style={
                        "color": "#8E8E93",
                        "font-style": "italic",
                        "text-align": "center",
                    },
                )
            ],
            style={
                "background": "#1C1C1E",
                "padding": "20px",
                "border-radius": "12px",
                "border": "1px solid #38383A",
                "margin-top": "16px",
            },
        )

    except Exception as e:
        return html.Div(
            [
                html.P(
                    f"Error loading relationships: {str(e)}",
                    style={
                        "color": "#FF3B30",
                        "font-style": "italic",
                        "text-align": "center",
                    },
                )
            ],
            style={
                "background": "#1C1C1E",
                "padding": "20px",
                "border-radius": "12px",
                "border": "1px solid #38383A",
                "margin-top": "16px",
            },
        )


def extract_immediate_relationships(obj_detail: dict, object_type: str):
    """Extract comprehensive relationship counts from object detail data"""
    relationships = {}

    if object_type == "policies":
        # For policies, get relationships from scope and configuration
        if obj_detail.get("scope"):
            scope = obj_detail["scope"]
            if scope.get("computer_groups", 0) > 0:
                relationships["computer_groups"] = scope["computer_groups"]
            if scope.get("computers", 0) > 0:
                relationships["computers"] = scope["computers"]
            if scope.get("buildings", 0) > 0:
                relationships["buildings"] = scope["buildings"]
            if scope.get("departments", 0) > 0:
                relationships["departments"] = scope["departments"]

        if obj_detail.get("packages", 0) > 0:
            relationships["packages"] = obj_detail["packages"]

        if obj_detail.get("scripts", 0) > 0:
            relationships["scripts"] = obj_detail["scripts"]

        # Add category relationship
        if obj_detail.get("category"):
            relationships["categories"] = 1

    elif object_type == "profiles":
        # For profiles, get scope information
        if obj_detail.get("scope"):
            scope = obj_detail["scope"]
            if scope.get("computer_groups", 0) > 0:
                relationships["computer_groups"] = scope["computer_groups"]
            if scope.get("computers", 0) > 0:
                relationships["computers"] = scope["computers"]
            if scope.get("buildings", 0) > 0:
                relationships["buildings"] = scope["buildings"]
            if scope.get("departments", 0) > 0:
                relationships["departments"] = scope["departments"]

        # Add category relationship
        if obj_detail.get("category"):
            relationships["categories"] = 1

    elif object_type == "groups":
        # For groups, we have computer count and can find reverse relationships
        if obj_detail.get("computers", 0) > 0:
            relationships["computers"] = obj_detail["computers"]

        # TODO: Add reverse lookup for policies/profiles that scope to this group
        # This would require scanning all policies/profiles - implement as needed

    elif object_type == "categories":
        # For categories, we need reverse lookup for policies/profiles that use this category
        # TODO: Implement reverse lookup by scanning all policies/profiles
        pass

    elif object_type == "scripts":
        # For scripts, find policies that use this script
        # TODO: Implement reverse lookup
        pass

    elif object_type == "packages":
        # For packages, find policies that use this package
        # TODO: Implement reverse lookup
        pass

    return relationships


def render_relationship_detail_view(
    source_object: dict, source_type: str, target_type: str
):
    """Render a detailed view of related objects when clicking on a relationship bubble"""

    # Get the source object's relationships
    relationships = extract_immediate_relationships(source_object, source_type)
    target_count = relationships.get(target_type, 0)

    if target_count == 0:
        return html.Div(
            [
                html.Button(
                    "← Back to Object", id="back-to-object", className="dash-button"
                ),
                html.H2(f"No {target_type.replace('_', ' ').title()} Found"),
                html.P(
                    f"This {source_type.rstrip('s')} has no {target_type.replace('_', ' ')} relationships.",
                    style={"color": "#8E8E93", "margin-top": "16px"},
                ),
            ]
        )

    # Create header
    source_name = source_object.get("name", "Unknown")
    header = html.Div(
        [
            html.Button(
                "← Back to Object", id="back-to-object", className="dash-button"
            ),
            html.H2(
                f"{target_type.replace('_', ' ').title()} Related to {source_name}"
            ),
            html.P(
                f"Found {target_count} {target_type.replace('_', ' ')} related to this {source_type.rstrip('s')}",
                style={"color": "#8E8E93", "margin-bottom": "24px"},
            ),
        ]
    )

    # Create relationship details based on type
    relationship_items = []

    if target_type == "computer_groups" and source_type in ["policies", "profiles"]:
        # Show which groups are scoped
        relationship_items.append(
            html.Div(
                [
                    html.H3(
                        "Scoped Computer Groups",
                        style={"color": "#FFFFFF", "margin-bottom": "16px"},
                    ),
                    html.P(
                        f"This {source_type.rstrip('s')} is scoped to {target_count} computer group(s).",
                        style={"color": "#E5E5E7", "margin-bottom": "16px"},
                    ),
                    html.Div(
                        [
                            html.P(
                                "💡 To see the specific groups, check the object's scope configuration in JAMF Pro.",
                                style={
                                    "color": "#FF9F0A",
                                    "font-style": "italic",
                                    "font-size": "14px",
                                },
                            )
                        ],
                        style={
                            "background": "#1C1C1E",
                            "padding": "16px",
                            "border-radius": "8px",
                            "border": "1px solid #38383A",
                        },
                    ),
                ]
            )
        )

    elif target_type == "computers" and source_type == "groups":
        # Show computer count for groups
        relationship_items.append(
            html.Div(
                [
                    html.H3(
                        "Member Computers",
                        style={"color": "#FFFFFF", "margin-bottom": "16px"},
                    ),
                    html.P(
                        f"This group contains {target_count} computer(s).",
                        style={"color": "#E5E5E7", "margin-bottom": "16px"},
                    ),
                    html.Div(
                        [
                            html.P(
                                "💡 To see the specific computers, check the group membership in JAMF Pro.",
                                style={
                                    "color": "#34C759",
                                    "font-style": "italic",
                                    "font-size": "14px",
                                },
                            )
                        ],
                        style={
                            "background": "#1C1C1E",
                            "padding": "16px",
                            "border-radius": "8px",
                            "border": "1px solid #38383A",
                        },
                    ),
                ]
            )
        )

    elif target_type == "packages" and source_type == "policies":
        # Show package relationships
        relationship_items.append(
            html.Div(
                [
                    html.H3(
                        "Associated Packages",
                        style={"color": "#FFFFFF", "margin-bottom": "16px"},
                    ),
                    html.P(
                        f"This policy deploys {target_count} package(s).",
                        style={"color": "#E5E5E7", "margin-bottom": "16px"},
                    ),
                    html.Div(
                        [
                            html.P(
                                "📦 These packages will be installed when the policy executes.",
                                style={
                                    "color": "#FF3B30",
                                    "font-style": "italic",
                                    "font-size": "14px",
                                },
                            )
                        ],
                        style={
                            "background": "#1C1C1E",
                            "padding": "16px",
                            "border-radius": "8px",
                            "border": "1px solid #38383A",
                        },
                    ),
                ]
            )
        )

    elif target_type == "scripts" and source_type == "policies":
        # Show script relationships
        relationship_items.append(
            html.Div(
                [
                    html.H3(
                        "Associated Scripts",
                        style={"color": "#FFFFFF", "margin-bottom": "16px"},
                    ),
                    html.P(
                        f"This policy executes {target_count} script(s).",
                        style={"color": "#E5E5E7", "margin-bottom": "16px"},
                    ),
                    html.Div(
                        [
                            html.P(
                                "⚙️ These scripts will run when the policy executes.",
                                style={
                                    "color": "#34C759",
                                    "font-style": "italic",
                                    "font-size": "14px",
                                },
                            )
                        ],
                        style={
                            "background": "#1C1C1E",
                            "padding": "16px",
                            "border-radius": "8px",
                            "border": "1px solid #38383A",
                        },
                    ),
                ]
            )
        )

    elif target_type == "categories":
        # Show category relationship
        category_name = source_object.get("category", "Unknown Category")
        relationship_items.append(
            html.Div(
                [
                    html.H3(
                        "Category Assignment",
                        style={"color": "#FFFFFF", "margin-bottom": "16px"},
                    ),
                    html.P(
                        f"This {source_type.rstrip('s')} is assigned to the category: {category_name}",
                        style={"color": "#E5E5E7", "margin-bottom": "16px"},
                    ),
                    html.Div(
                        [
                            html.P(
                                "📁 Categories help organize and manage JAMF objects.",
                                style={
                                    "color": "#8E8E93",
                                    "font-style": "italic",
                                    "font-size": "14px",
                                },
                            )
                        ],
                        style={
                            "background": "#1C1C1E",
                            "padding": "16px",
                            "border-radius": "8px",
                            "border": "1px solid #38383A",
                        },
                    ),
                ]
            )
        )

    else:
        # Generic relationship display
        relationship_items.append(
            html.Div(
                [
                    html.H3(
                        f"{target_type.replace('_', ' ').title()} Relationship",
                        style={"color": "#FFFFFF", "margin-bottom": "16px"},
                    ),
                    html.P(
                        f"This {source_type.rstrip('s')} has {target_count} {target_type.replace('_', ' ')} relationship(s).",
                        style={"color": "#E5E5E7", "margin-bottom": "16px"},
                    ),
                    html.Div(
                        [
                            html.P(
                                "🔗 Check JAMF Pro for detailed relationship information.",
                                style={
                                    "color": "#007AFF",
                                    "font-style": "italic",
                                    "font-size": "14px",
                                },
                            )
                        ],
                        style={
                            "background": "#1C1C1E",
                            "padding": "16px",
                            "border-radius": "8px",
                            "border": "1px solid #38383A",
                        },
                    ),
                ]
            )
        )

    return html.Div(
        [header, html.Div(relationship_items, style={"margin-top": "24px"})]
    )


# App layout (identical to live Dash)
app.layout = html.Div(
    [
        dcc.Store(
            id="app-state",
            data={
                "current_view": "dashboard",
                "selected_object": None,
                "stored_objects_data": {},
            },
        ),
        dcc.Store(id="objects-data", data={}),
        # Navigation header
        html.Div(
            [
                html.Div(
                    [
                        html.H1("📋 JPAPI Computer Dash", className="nav-title"),
                        html.P(
                            "Enterprise Device Management • Microservice Architecture",
                            className="nav-subtitle",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Span("🟢"), html.Span("JPAPI Backend Connected")],
                            className="status-indicator status-connected",
                        ),
                        html.Button(
                            "🔄 Refresh",
                            id="refresh-btn",
                            style={
                                "background": "#1C1C1E",
                                "color": "#8E8E93",
                                "border": "1px solid #38383A",
                                "padding": "8px 16px",
                                "border-radius": "8px",
                                "font-size": "12px",
                                "cursor": "pointer",
                                "margin-left": "12px",
                                "transition": "all 0.2s ease",
                            },
                        ),
                    ],
                    style={"display": "flex", "align-items": "center"},
                ),
            ],
            className="nav-header",
        ),
        # Main content area
        html.Div(id="main-content", style={"padding": "0 24px"}),
    ],
    style={"background": "#000000", "min-height": "100vh", "color": "#FFFFFF"},
)


@app.callback(
    [
        Output("main-content", "children"),
        Output("objects-data", "data"),
        Output("app-state", "data", allow_duplicate=True),
    ],
    [
        Input("app-state", "data"),
        Input("refresh-btn", "n_clicks"),
        Input({"type": "stat-card", "object_type": dash.dependencies.ALL}, "n_clicks"),
        Input(
            {
                "type": "object-card",
                "object_type": dash.dependencies.ALL,
                "object_id": dash.dependencies.ALL,
            },
            "n_clicks",
        ),
    ],
    prevent_initial_call=True,
)
def update_main_content(
    app_state, refresh_clicks, stat_card_clicks, object_card_clicks
):
    """Update main content based on current view"""

    current_view = app_state.get("current_view", "dashboard")

    # Handle stat card clicks
    ctx = dash.callback_context
    if ctx.triggered:
        trigger_id = ctx.triggered[0]["prop_id"]
        if "stat-card" in trigger_id and stat_card_clicks and any(stat_card_clicks):
            # Find which stat card was clicked
            for i, clicks in enumerate(stat_card_clicks):
                if clicks:
                    object_types = [
                        "policies",
                        "profiles",
                        "scripts",
                        "packages",
                        "groups",
                        "categories",
                    ]
                    if i < len(object_types):
                        content, objects = render_object_list(object_types[i])
                        objects_data = {
                            "objects": objects,
                            "object_type": object_types[i],
                        }
                        # Update app state with stored objects data
                        new_app_state = app_state.copy()
                        new_app_state["stored_objects_data"] = objects_data
                        return content, objects_data, new_app_state

        # Handle object card clicks
        elif (
            "object-card" in trigger_id
            and object_card_clicks
            and any(object_card_clicks)
        ):
            # Find which object card was clicked
            for i, clicks in enumerate(object_card_clicks):
                if clicks:
                    # Get the object details from the stored data
                    stored_data = app_state.get("stored_objects_data", {})
                    objects = stored_data.get("objects", [])
                    object_type = stored_data.get("object_type", "policies")

                    if i < len(objects):
                        obj = objects[i]
                        content = render_object_detail(obj, object_type)
                        return content, stored_data, app_state

    if current_view == "dashboard":
        return render_dashboard(), {}, app_state
    elif current_view == "relationship_detail":
        # Handle relationship detail view
        rel_detail = app_state.get("relationship_detail", {})
        source_type = rel_detail.get("source_type")
        source_id = rel_detail.get("source_id")
        target_type = rel_detail.get("target_type")

        if source_type and source_id and target_type:
            # Get the source object details
            try:
                source_obj_detail = backend_client.get_object_detail(
                    source_type, str(source_id)
                )
                if source_obj_detail and source_obj_detail.get("object"):
                    source_object = source_obj_detail["object"]
                    content = render_relationship_detail_view(
                        source_object, source_type, target_type
                    )
                    return content, {}, app_state
            except Exception as e:
                print(f"Error loading relationship detail: {e}")

        # Fallback if something went wrong
        return (
            html.Div(
                [
                    html.H2("Error Loading Relationship Details"),
                    html.P(
                        "Unable to load relationship information.",
                        style={"color": "#FF3B30"},
                    ),
                ]
            ),
            {},
            app_state,
        )
    elif current_view == "object_detail":
        # Handle object detail view
        selected_obj = app_state.get("selected_object", {})
        if selected_obj and selected_obj.get("id") and selected_obj.get("type"):
            obj_id = selected_obj["id"]
            obj_type = selected_obj["type"]
            # Create a mock object for render_object_detail
            mock_obj = {"id": obj_id, "name": f"Object {obj_id}"}
            content = render_object_detail(mock_obj, obj_type)
            return content, {}, app_state
        else:
            return render_dashboard(), {}, app_state
    else:
        content, objects = render_object_list(current_view)
        objects_data = {"objects": objects, "object_type": current_view}
        # Update app state with stored objects data
        new_app_state = app_state.copy()
        new_app_state["stored_objects_data"] = objects_data
        return content, objects_data, new_app_state


# Removed callback that was causing loops - objects data is now handled directly in update_main_content


# Separate callback for back-to-dashboard button
@app.callback(
    Output("app-state", "data", allow_duplicate=True),
    [Input("back-to-dashboard", "n_clicks")],
    [State("app-state", "data")],
    prevent_initial_call=True,
)
def go_back_to_dashboard(back_clicks, current_state):
    """Handle back to dashboard navigation"""
    if back_clicks:
        return {"current_view": "dashboard", "selected_object": None}
    return current_state


# Separate callback for back-to-list button
@app.callback(
    Output("app-state", "data", allow_duplicate=True),
    [Input("back-to-list", "n_clicks")],
    [State("app-state", "data")],
    prevent_initial_call=True,
)
def go_back_to_list(back_clicks, current_state):
    """Handle back to list navigation"""
    if back_clicks:
        stored_data = current_state.get("stored_objects_data", {})
        object_type = stored_data.get("object_type", "policies")
        return {"current_view": object_type, "selected_object": None}
    return current_state


# Callback for relationship bubble clicks
@app.callback(
    Output("app-state", "data", allow_duplicate=True),
    [
        Input(
            {
                "type": "relationship-bubble",
                "object_type": ALL,
                "source_type": ALL,
                "source_id": ALL,
            },
            "n_clicks",
        )
    ],
    [State("app-state", "data")],
    prevent_initial_call=True,
)
def handle_relationship_bubble_click(n_clicks_list, current_state):
    """Handle clicks on relationship bubbles to show detailed relationship view"""
    if not any(n_clicks_list) or not ctx.triggered:
        return current_state

    # Get the triggered component
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == "{}":
        return current_state

    try:
        import json

        bubble_id = json.loads(triggered_id)
        target_object_type = bubble_id["object_type"]
        source_object_type = bubble_id["source_type"]
        source_object_id = bubble_id["source_id"]

        # Store the relationship detail view info
        return {
            "current_view": "relationship_detail",
            "selected_object": None,
            "relationship_detail": {
                "source_type": source_object_type,
                "source_id": source_object_id,
                "target_type": target_object_type,
            },
            "stored_objects_data": current_state.get("stored_objects_data", {}),
        }
    except Exception as e:
        print(f"Error handling bubble click: {e}")
        return current_state


# Callback for back-to-object button
@app.callback(
    Output("app-state", "data", allow_duplicate=True),
    [Input("back-to-object", "n_clicks")],
    [State("app-state", "data")],
    prevent_initial_call=True,
)
def go_back_to_object(back_clicks, current_state):
    """Handle back to object navigation from relationship detail view"""
    if back_clicks and current_state.get("relationship_detail"):
        rel_detail = current_state["relationship_detail"]
        source_type = rel_detail["source_type"]
        source_id = rel_detail["source_id"]

        # Go back to the object detail view
        return {
            "current_view": "object_detail",
            "selected_object": {"id": source_id, "type": source_type},
            "stored_objects_data": current_state.get("stored_objects_data", {}),
        }
    return current_state


# Simple refresh callback
@app.callback(
    Output("refresh-status", "children"),
    Input("simple-refresh-btn", "n_clicks"),
    prevent_initial_call=True,
)
def handle_simple_refresh(n_clicks):
    """Handle simple refresh button"""
    if n_clicks:
        print("🔄 Simple refresh triggered")
        # Force refresh by updating a timestamp or similar
        return f"Refreshed at {datetime.now().strftime('%H:%M:%S')}"
    return ""


# Loading indicator callback
@app.callback(
    Output("loading-indicator", "children"),
    [Input({"type": "stat-card", "object_type": dash.dependencies.ALL}, "n_clicks")],
    prevent_initial_call=True,
)
def show_loading_when_navigating(stat_clicks):
    """Show loading indicator when clicking stat cards"""
    if any(stat_clicks):
        return [create_loading_spinner("Loading objects...")]
    return []


def start_enhanced_backend():
    """Start the enhanced backend API in background"""
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "src/jamf_backend_enhanced.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("🚀 Enhanced backend started on port 8900")
        return backend_process
    except Exception as e:
        print(f"❌ Failed to start enhanced backend: {e}")
        return None


def main():
    """Main launcher function with enhanced backend integration"""
    global launcher_running

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🚀 Starting Enhanced JAMF Dashboard App Launcher...")
    print("🔧 Starting enhanced backend API...")
    print("🌐 Frontend will be available at: http://127.0.0.1:8060")
    print("💡 Persistent browser window with auto-reload")
    print("🔒 Launching in app mode...")

    # Kill any existing processes
    kill_existing_processes()

    # Start enhanced backend
    backend_process = start_enhanced_backend()
    if not backend_process:
        print("⚠️  Backend failed to start, continuing with launcher only...")
    else:
        print("✅ Enhanced backend running on port 8900")
        time.sleep(3)  # Give backend time to start

    # Launch browser window
    if not launch_browser_window():
        print("❌ Failed to launch browser window")
        return

    # Start health monitoring in background
    health_thread = threading.Thread(target=monitor_server_health)
    health_thread.daemon = True
    health_thread.start()

    try:
        # Run the Dash app (enhanced frontend on port 8060)
        app.run(debug=False, host="127.0.0.1", port=8060, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        launcher_running = False
        if browser_process:
            browser_process.terminate()
        if backend_process:
            backend_process.terminate()
            print("🛑 Enhanced backend stopped")


if __name__ == "__main__":
    main()
