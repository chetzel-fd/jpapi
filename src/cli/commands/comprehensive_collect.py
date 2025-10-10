#!/usr/bin/env python3
"""
CLI Command: Comprehensive Collection
Provides comprehensive data collection with caffeinate and progress display
"""
import sys
import time
import threading
from pathlib import Path
from typing import List, Optional

# Using proper package structure via pip install -e .

from cli.base.command import BaseCommand
from framework.analytics.json_engine import JSONAnalyticsEngine
from framework.analytics.comprehensive_collector import ComprehensiveCollector
from core.auth.login_manager import UnifiedJamfAuth
from core.logging.command_mixin import log_operation, with_progress


class ProgressDisplay:
    """Enhanced CLI progress display with animations"""

    def __init__(self):
        self.current_phase = ""
        self.current_message = ""
        self.current_percentage = 0
        self.animation_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.animation_index = 0
        self.display_thread = None
        self.stop_display = False
        self.lock = threading.Lock()
        self.last_update = 0

    def start_display(self):
        """Start animated progress display"""
        self.stop_display = False
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()

    def stop_display_animation(self):
        """Stop animated progress display"""
        self.stop_display = True
        if self.display_thread:
            self.display_thread.join(timeout=1)
        print()  # New line after stopping

    def update_progress(self, progress_data):
        """Update progress from callback"""
        with self.lock:
            self.current_phase = progress_data.get("phase", "")
            self.current_message = progress_data.get("message", "")
            self.current_percentage = progress_data.get("percentage", 0)
            self.last_update = time.time()

    def _display_loop(self):
        """Main display loop with animation"""
        while not self.stop_display:
            with self.lock:
                if (
                    self.current_phase and time.time() - self.last_update < 30
                ):  # Show for 30 seconds max
                    # Create progress bar
                    bar_width = 25
                    filled = int(bar_width * self.current_percentage / 100)
                    bar = "█" * filled + "░" * (bar_width - filled)

                    # Animation character
                    anim_char = self.animation_chars[self.animation_index]
                    self.animation_index = (self.animation_index + 1) % len(
                        self.animation_chars
                    )

                    # Phase emoji
                    phase_emoji = {
                        "starting": "🚀",
                        "discovery": "🔍",
                        "collection": "📊",
                        "relationships": "🔗",
                        "complete": "✅",
                        "interrupted": "⏸️",
                        "error": "❌",
                    }.get(self.current_phase, "⚡")

                    # Truncate message if too long
                    message = (
                        self.current_message[:40] + "..."
                        if len(self.current_message) > 40
                        else self.current_message
                    )

                    # Display progress
                    print(
                        f"\r{anim_char} {phase_emoji} [{bar}] {self.current_percentage:5.1f}% {message}",
                        end="",
                        flush=True,
                    )

            time.sleep(0.15)


class ComprehensiveCollectCommand(BaseCommand):
    """Comprehensive data collection command"""

    def get_name(self) -> str:
        return "comprehensive-collect"

    def get_description(self) -> str:
        return "Collect comprehensive JAMF object data with smart prioritization"

    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            "--types",
            nargs="+",
            choices=["policies", "groups", "profiles", "devices"],
            default=["policies", "groups", "profiles", "devices"],
            help="Object types to collect (default: all)",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=4,
            help="Number of concurrent workers (default: 4)",
        )
        parser.add_argument(
            "--no-caffeinate",
            action="store_true",
            help="Disable caffeinate (allow system sleep)",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Minimal output (no progress animation)",
        )
        parser.add_argument(
            "--status-only", action="store_true", help="Show collection status and exit"
        )

    @log_operation("Comprehensive Data Collection")
    def execute(self, args):
        """Execute comprehensive collection"""
        try:
            # Show header
            if not args.quiet:
                self.log_info("🎯 JAMF Comprehensive Data Collection")
                self.log_info("=" * 45)

            # Initialize components
            if not args.quiet:
                self.log_info("🔐 Initializing authentication...")
            auth = JamfAuth("dev", "keychain")

            if not args.quiet:
                self.log_info("📊 Initializing analytics engine...")
            analytics = JSONAnalyticsEngine(
                framework=None,
                export_dir="tmp/exports",
                cache_dir="tmp/cache/analytics",
            )

            if not args.quiet:
                self.log_info("🎯 Initializing comprehensive collector...")
            collector = ComprehensiveCollector(
                auth=auth,
                analytics_engine=analytics,
                cache_dir="tmp/cache/comprehensive",
            )

            # Status only mode
            if args.status_only:
                status = collector.get_collection_status()
                print()
                print("📊 COLLECTION STATUS:")
                print(f"   Total objects: {status['total_objects']}")
                print(f"   Completion rate: {status['completion_rate']:.1f}%")
                print(f"   Relationships: {status['relationship_count']}")

                if status["status_counts"]:
                    print("   Status breakdown:")
                    for status_name, count in status["status_counts"].items():
                        emoji = {
                            "completed": "✅",
                            "failed": "❌",
                            "pending": "⏳",
                            "in_progress": "🔄",
                        }.get(status_name, "📋")
                        print(f"     {emoji} {status_name}: {count}")

                return True

            # Show collection info
            if not args.quiet:
                print()
                print("📊 COLLECTION CONFIGURATION:")
                print(f"   Object types: {', '.join(args.types)}")
                print(f"   Workers: {args.workers}")
                print(
                    f"   Caffeinate: {'❌ Disabled' if args.no_caffeinate else '☕ Enabled'}"
                )
                print(
                    f"   Progress display: {'❌ Quiet mode' if args.quiet else '📊 Animated'}"
                )
                print()

                # Show existing progress
                status = collector.get_collection_status()
                if status["total_objects"] > 0:
                    print(
                        f"📊 Existing progress: {status['completion_rate']:.1f}% complete"
                    )
                    print(
                        f"   ✅ Completed: {status['status_counts'].get('completed', 0)}"
                    )
                    print(f"   ❌ Failed: {status['status_counts'].get('failed', 0)}")
                    print()

            # Confirm start
            if not args.quiet:
                response = input("🤔 Start comprehensive collection? (y/N): ")
                if response.lower() != "y":
                    print("❌ Collection cancelled")
                    return False
                print()

            # Initialize progress display
            progress_display = None
            if not args.quiet:
                progress_display = ProgressDisplay()
                progress_display.start_display()

            start_time = time.time()

            try:
                # Disable caffeinate if requested
                if args.no_caffeinate:
                    collector.caffeinate_process = "disabled"

                # Start collection
                collector.start_comprehensive_collection(
                    object_types=args.types,
                    max_workers=args.workers,
                    progress_callback=(
                        progress_display.update_progress if progress_display else None
                    ),
                )

                total_time = time.time() - start_time

                if progress_display:
                    progress_display.stop_display_animation()

                # Show completion
                print("🎉 COMPREHENSIVE COLLECTION COMPLETE!")
                print(f"⏱️ Total time: {total_time/60:.1f} minutes")

                # Final status
                final_status = collector.get_collection_status()
                print(
                    f"📊 Objects collected: {final_status['status_counts'].get('completed', 0)}"
                )
                print(
                    f"❌ Failed objects: {final_status['status_counts'].get('failed', 0)}"
                )
                print(f"🔗 Relationships mapped: {final_status['relationship_count']}")

                return True

            except KeyboardInterrupt:
                if progress_display:
                    progress_display.stop_display_animation()
                print("⏸️ Collection interrupted by user")
                print("📊 Progress has been saved and can be resumed")
                return False

            except Exception as e:
                if progress_display:
                    progress_display.stop_display_animation()
                print(f"❌ Collection error: {e}")
                return False

        except Exception as e:
            print(f"❌ Command error: {e}")
            return False


# Register command
def register_command():
    """Register the comprehensive collect command"""
    return ComprehensiveCollectCommand()
