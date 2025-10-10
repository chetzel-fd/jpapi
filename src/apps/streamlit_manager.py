#!/usr/bin/env python3
"""
Streamlit Manager - Clean up and manage Streamlit applications
"""
import subprocess
import sys
import os
from pathlib import Path
import time


class StreamlitManager:
    """Manages Streamlit applications and cleanup"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.streamlit_dir = self.project_root / "src" / "apps" / "streamlit"
        self.active_processes = {}

    def list_streamlit_files(self):
        """List all Streamlit files in the project"""
        streamlit_files = []
        if self.streamlit_dir.exists():
            # Get files from main directory
            for file in self.streamlit_dir.glob("*.py"):
                if file.name != "__init__.py":
                    streamlit_files.append(file)
            # Get files from subdirectories
            for subdir in ["dashboards", "viewers", "managers"]:
                subdir_path = self.streamlit_dir / subdir
                if subdir_path.exists():
                    for file in subdir_path.glob("*.py"):
                        if file.name != "__init__.py":
                            streamlit_files.append(file)
        return streamlit_files

    def kill_all_streamlit(self):
        """Kill all running Streamlit processes"""
        try:
            subprocess.run(["pkill", "-f", "streamlit"], check=False)
            print("✅ Killed all Streamlit processes")
        except Exception as e:
            print(f"⚠️ Error killing processes: {e}")

    def clean_temp_files(self):
        """Clean up temporary files and old versions"""
        temp_files = [
            "refined_mockups.html",
            "focused_mockup.html",
            "menu_mockups.html",
        ]

        cleaned = []
        for file in temp_files:
            file_path = self.project_root / file
            if file_path.exists():
                file_path.unlink()
                cleaned.append(file)

        if cleaned:
            print(f"✅ Cleaned up: {', '.join(cleaned)}")
        else:
            print("✅ No temp files to clean")

    def get_active_ports(self):
        """Check which ports are in use"""
        import socket

        ports = [8501, 8502, 8503, 8504, 8505, 8506, 8507, 8508, 8509, 8510, 8511]
        active_ports = []

        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("localhost", port))
            if result == 0:
                active_ports.append(port)
            sock.close()

        return active_ports

    def run_streamlit(self, file_name, port=8501):
        """Run a specific Streamlit file"""
        # Try to find the file in the main directory or subdirectories
        file_path = None
        if (self.streamlit_dir / file_name).exists():
            file_path = self.streamlit_dir / file_name
        else:
            # Check subdirectories
            for subdir in ["dashboards", "viewers", "managers"]:
                subdir_path = self.streamlit_dir / subdir / file_name
                if subdir_path.exists():
                    file_path = subdir_path
                    break

        if not file_path:
            print(f"❌ File not found: {file_name}")
            return None

        try:
            cmd = [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(file_path),
                "--server.port",
                str(port),
                "--server.headless",
                "true",
            ]

            process = subprocess.Popen(cmd)
            self.active_processes[port] = process

            print(f"🚀 Started {file_name} on port {port}")
            return process

        except Exception as e:
            print(f"❌ Error starting {file_name}: {e}")
            return None

    def status(self):
        """Show current status"""
        print("📊 Streamlit Manager Status")
        print("=" * 40)

        # List available files
        files = self.list_streamlit_files()
        print(f"\n📁 Available Streamlit files ({len(files)}):")
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file.name}")

        # Check active ports
        active_ports = self.get_active_ports()
        if active_ports:
            print(f"\n🟢 Active ports: {', '.join(map(str, active_ports))}")
        else:
            print("\n🔴 No active Streamlit processes")

        # Show active processes
        if self.active_processes:
            print(f"\n⚙️ Managed processes: {len(self.active_processes)}")
            for port, process in self.active_processes.items():
                status = "running" if process.poll() is None else "stopped"
                print(f"  Port {port}: {status}")

    def cleanup(self):
        """Full cleanup"""
        print("🧹 Streamlit Manager Cleanup")
        print("=" * 40)

        # Kill all processes
        self.kill_all_streamlit()

        # Clean temp files
        self.clean_temp_files()

        # Clear managed processes
        self.active_processes.clear()

        print("✅ Cleanup complete!")

    def open_all_incognito(self):
        """Open all Streamlit files in incognito browser windows"""
        import webbrowser
        import time

        files = self.list_streamlit_files()
        if not files:
            print("❌ No Streamlit files found")
            return

        print("🌐 Opening all Streamlit files in incognito windows...")

        # Launch all files on different ports
        ports = [8501, 8502, 8503, 8504, 8505, 8506, 8507, 8508, 8509, 8510, 8511]
        launched_files = []

        for i, file in enumerate(files[: len(ports)]):
            port = ports[i]
            print(f"Starting {file.name} on port {port}...")
            process = self.run_streamlit(file.name, port)
            if process:
                launched_files.append((file.name, port))
            time.sleep(1)  # Give each one time to start

        print(f"\n✅ Launched {len(launched_files)} applications")

        # Open all in incognito windows
        print("🔒 Opening incognito browser windows...")
        for file_name, port in launched_files:
            url = f"http://localhost:{port}"
            print(f"Opening {file_name}: {url}")
            try:
                # Try different methods to open incognito
                import subprocess
                import platform

                system = platform.system()
                if system == "Darwin":  # macOS
                    # Try Chrome first, then Safari
                    try:
                        subprocess.run(
                            [
                                "open",
                                "-na",
                                "Google Chrome",
                                "--args",
                                "--incognito",
                                url,
                            ]
                        )
                    except:
                        subprocess.run(["open", "-na", "Safari", url])
                elif system == "Windows":
                    subprocess.run(["start", "chrome", "--incognito", url], shell=True)
                else:  # Linux
                    subprocess.run(["google-chrome", "--incognito", url])
            except:
                # Fallback to regular browser
                webbrowser.open_new(url)
            time.sleep(0.5)  # Small delay between opens

        print(
            f"\n🎉 All {len(launched_files)} applications opened in incognito windows!"
        )
        print("💡 Tip: Use Ctrl+Shift+N to open additional incognito windows")

    def interactive_menu(self):
        """Interactive menu for managing Streamlit apps"""
        while True:
            print("\n🎛️ Streamlit Manager")
            print("=" * 30)
            print("1. List files")
            print("2. Run file")
            print("3. Kill all")
            print("4. Cleanup")
            print("5. Status")
            print("6. Open All in Incognito")
            print("7. Exit")

            choice = input("\nSelect option (1-7): ").strip()

            if choice == "1":
                files = self.list_streamlit_files()
                print(f"\n📁 Streamlit files ({len(files)}):")
                for i, file in enumerate(files, 1):
                    print(f"  {i}. {file.name}")

            elif choice == "2":
                files = self.list_streamlit_files()
                if not files:
                    print("❌ No Streamlit files found")
                    continue

                print("\nAvailable files:")
                for i, file in enumerate(files, 1):
                    print(f"  {i}. {file.name}")

                try:
                    file_choice = int(input("Select file number: ")) - 1
                    if 0 <= file_choice < len(files):
                        port = int(input("Port (default 8501): ") or "8501")
                        self.run_streamlit(files[file_choice].name, port)
                    else:
                        print("❌ Invalid selection")
                except ValueError:
                    print("❌ Invalid input")

            elif choice == "3":
                self.kill_all_streamlit()

            elif choice == "4":
                self.cleanup()

            elif choice == "5":
                self.status()

            elif choice == "6":
                self.open_all_incognito()

            elif choice == "7":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid option")


def main():
    """Main entry point"""
    manager = StreamlitManager()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "cleanup":
            manager.cleanup()
        elif command == "kill":
            manager.kill_all_streamlit()
        elif command == "status":
            manager.status()
        elif command == "list":
            files = manager.list_streamlit_files()
            print(f"📁 Streamlit files ({len(files)}):")
            for file in files:
                print(f"  - {file.name}")
        elif command == "incognito":
            manager.open_all_incognito()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: cleanup, kill, status, list, incognito")
    else:
        manager.interactive_menu()


if __name__ == "__main__":
    main()
