#!/usr/bin/env python3
"""
Scripts Command for jpapi CLI
Advanced script management operations including download, backup, and migration
"""
from argparse import ArgumentParser, Namespace
import argparse
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
import json
import time
import re

# Add base to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base.command import BaseCommand

class ScriptsCommand(BaseCommand):
    """Command for advanced script management operations"""
    
    def __init__(self):
        super().__init__(
            name="scripts",
            description="📜 Advanced script management (download, backup, migrate)"
        )
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add scripts command arguments"""
        subparsers = parser.add_subparsers(dest='script_action', help='Script action to perform')
        
        # Download command
        download_parser = subparsers.add_parser('download', help='Download all scripts from JAMF')
        download_parser.add_argument('--output-dir', default='exports/scripts',
                                   help='Output directory for downloaded scripts')
        download_parser.add_argument('--format', choices=['files', 'json', 'both'], default='both',
                                   help='Output format')
        download_parser.add_argument('--category', help='Filter by script category')
        download_parser.add_argument('--include-metadata', action='store_true',
                                   help='Include JAMF metadata in JSON files')
        download_parser.add_argument('--backup', action='store_true',
                                   help='Create backup with timestamp')
        # Don't call setup_common_args to avoid format conflict
        
        # Backup command
        backup_parser = subparsers.add_parser('backup', help='Create complete script backup')
        backup_parser.add_argument('--output-dir', default='script_backup', 
                                 help='Output directory for backup')
        backup_parser.add_argument('--compress', action='store_true',
                                 help='Create compressed archive')
        
        # Migrate command
        migrate_parser = subparsers.add_parser('migrate', help='Prepare scripts for GitHub migration')
        migrate_parser.add_argument('--output-dir', default='github_scripts', 
                                  help='Output directory for GitHub-ready scripts')
        migrate_parser.add_argument('--create-readme', action='store_true',
                                  help='Generate README.md with script documentation')
        migrate_parser.add_argument('--organize-by-category', action='store_true',
                                  help='Organize scripts into category folders')
        
        # Info command
        info_parser = subparsers.add_parser('info', help='Show script information and statistics')
        info_parser.add_argument('--category', help='Filter by script category')
        info_parser.add_argument('--detailed', action='store_true',
                               help='Show detailed information')
    
    def execute(self, args: Namespace) -> int:
        """Execute the scripts command"""
        if not self.check_auth(args):
            return 1
        
        try:
            if not args.script_action:
                print("📜 Script Management Commands:")
                print()
                print("💾 Download & Backup:")
                print("   jpapi scripts download --output-dir my_scripts")
                print("   jpapi scripts backup --compress")
                print()
                print("🚀 Migration:")
                print("   jpapi scripts migrate --create-readme --organize-by-category")
                print()
                print("ℹ️  Information:")
                print("   jpapi scripts info --detailed")
                print()
                print("🔧 Available Actions:")
                print("   download, backup, migrate, info")
                return 1
            
            # Route to appropriate handler
            if args.script_action == 'download':
                return self._download_scripts(args)
            elif args.script_action == 'backup':
                return self._backup_scripts(args)
            elif args.script_action == 'migrate':
                return self._migrate_scripts(args)
            elif args.script_action == 'info':
                return self._info_scripts(args)
            else:
                print(f"❌ Unknown script action: {args.script_action}")
                return 1
                
        except Exception as e:
            return self.handle_api_error(e)
    
    def _download_scripts(self, args: Namespace) -> int:
        """Download all scripts from JAMF"""
        try:
            print("📥 Downloading Scripts...")
            
            # Get scripts list
            response = self.auth.api_request('GET', '/JSSResource/scripts')
            
            if 'scripts' not in response or 'script' not in response['scripts']:
                print("❌ No scripts found")
                return 1
            
            scripts = response['scripts']['script']
            
            # Apply category filter if specified
            if args.category:
                scripts = [s for s in scripts 
                         if args.category.lower() in s.get('category', '').lower()]
            
            # Create output directory
            output_dir = Path(args.output_dir)
            if args.backup:
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                output_dir = output_dir / f"backup_{timestamp}"
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"📁 Output directory: {output_dir.absolute()}")
            
            # Download scripts
            downloaded_scripts = []
            failed_scripts = []
            downloaded_files = []
            
            for script in scripts:
                script_id = script.get('id')
                script_name = script.get('name', f'script_{script_id}')
                
                print(f"📥 Downloading: {script_name} (ID: {script_id})")
                
                try:
                    # Get detailed script info
                    detail_response = self.auth.api_request('GET', f'/JSSResource/scripts/id/{script_id}')
                    
                    if 'script' in detail_response:
                        script_data = detail_response['script']
                        downloaded_scripts.append(script_data)
                        
                        file_paths = []
                        
                        # Save script files if requested
                        if args.format in ['files', 'both']:
                            script_file = self._save_script_file(script_data, output_dir)
                            if script_file:
                                file_paths.append(script_file)
                                downloaded_files.append(script_file)
                        
                        # Save metadata if requested
                        if args.format in ['json', 'both'] and args.include_metadata:
                            metadata_file = self._save_script_metadata(script_data, output_dir)
                            if metadata_file:
                                file_paths.append(metadata_file)
                        
                        print(f"   ✅ Downloaded: {script_name}")
                        if file_paths:
                            print(f"      📁 Files: {', '.join(str(f) for f in file_paths)}")
                    else:
                        print(f"   ❌ No script data for: {script_name}")
                        failed_scripts.append(script)
                
                except Exception as e:
                    print(f"   ❌ Error downloading {script_name}: {e}")
                    failed_scripts.append(script)
                
                # Rate limiting
                time.sleep(0.5)
            
            # Create summary
            summary = {
                'download_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_scripts': len(scripts),
                'downloaded_count': len(downloaded_scripts),
                'failed_count': len(failed_scripts),
                'scripts': downloaded_scripts,
                'failed_scripts': failed_scripts
            }
            
            summary_file = output_dir / 'download_summary.json'
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Final report
            print("\n" + "=" * 50)
            print("📊 Download Summary:")
            print(f"   Total scripts: {len(scripts)}")
            print(f"   Downloaded: {len(downloaded_scripts)}")
            print(f"   Failed: {len(failed_scripts)}")
            print(f"   Files created: {len(downloaded_files)}")
            print(f"   Summary: {summary_file}")
            
            if downloaded_files:
                print(f"\n📁 Downloaded Files:")
                for file_path in downloaded_files[:10]:  # Show first 10
                    print(f"   {file_path}")
                if len(downloaded_files) > 10:
                    print(f"   ... and {len(downloaded_files) - 10} more files")
            
            if failed_scripts:
                print("\n❌ Failed downloads:")
                for script in failed_scripts:
                    print(f"   - {script.get('name', 'Unknown')} (ID: {script.get('id', 'N/A')})")
            
            return 0 if not failed_scripts else 1
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _backup_scripts(self, args: Namespace) -> int:
        """Create complete script backup"""
        try:
            print("💾 Creating Script Backup...")
            
            # Use download functionality with backup settings
            backup_args = Namespace()
            backup_args.output_dir = args.output_dir
            backup_args.format = 'both'
            backup_args.include_metadata = True
            backup_args.backup = True
            backup_args.category = None
            
            result = self._download_scripts(backup_args)
            
            if result == 0:
                print("✅ Script backup completed successfully")
                
                if args.compress:
                    print("📦 Creating compressed archive...")
                    # TODO: Add compression functionality
                    print("   (Compression not yet implemented)")
            
            return result
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _migrate_scripts(self, args: Namespace) -> int:
        """Prepare scripts for GitHub migration"""
        try:
            print("🚀 Preparing Scripts for GitHub Migration...")
            
            # Create GitHub-ready directory structure
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Download scripts
            download_args = Namespace()
            download_args.output_dir = str(output_dir)
            download_args.format = 'both'
            download_args.include_metadata = True
            download_args.backup = False
            download_args.category = None
            
            result = self._download_scripts(download_args)
            
            if result == 0:
                # Organize by category if requested
                if args.organize_by_category:
                    self._organize_scripts_by_category(output_dir)
                
                # Create README if requested
                if args.create_readme:
                    self._create_github_readme(output_dir)
                
                print("✅ Scripts prepared for GitHub migration")
                print(f"📁 Ready for commit: {output_dir.absolute()}")
            
            return result
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _info_scripts(self, args: Namespace) -> int:
        """Show script information and statistics"""
        try:
            print("📊 Script Information & Statistics...")
            
            # Get scripts list
            response = self.auth.api_request('GET', '/JSSResource/scripts')
            
            if 'scripts' not in response or 'script' not in response['scripts']:
                print("❌ No scripts found")
                return 1
            
            scripts = response['scripts']['script']
            
            # Apply category filter if specified
            if args.category:
                scripts = [s for s in scripts 
                         if args.category.lower() in s.get('category', '').lower()]
            
            # Calculate statistics
            total_scripts = len(scripts)
            categories = {}
            priorities = {}
            has_content = 0
            
            for script in scripts:
                # Category stats
                category = script.get('category', 'Uncategorized')
                categories[category] = categories.get(category, 0) + 1
                
                # Priority stats
                priority = script.get('priority', 'None')
                priorities[priority] = priorities.get(priority, 0) + 1
                
                # Content check
                if script.get('script_contents'):
                    has_content += 1
            
            # Display statistics
            print(f"\n📈 Script Statistics:")
            print(f"   Total Scripts: {total_scripts}")
            print(f"   With Content: {has_content}")
            print(f"   Without Content: {total_scripts - has_content}")
            
            print(f"\n📂 By Category:")
            for category, count in sorted(categories.items()):
                print(f"   {category}: {count}")
            
            print(f"\n⭐ By Priority:")
            for priority, count in sorted(priorities.items()):
                print(f"   {priority}: {count}")
            
            if args.detailed:
                print(f"\n📋 Script Details:")
                for script in scripts[:10]:  # Show first 10
                    print(f"   ID {script.get('id', 'N/A')}: {script.get('name', 'N/A')}")
                    print(f"      Category: {script.get('category', 'N/A')}")
                    print(f"      Priority: {script.get('priority', 'N/A')}")
                    print(f"      Has Content: {'Yes' if script.get('script_contents') else 'No'}")
                    print()
                
                if len(scripts) > 10:
                    print(f"   ... and {len(scripts) - 10} more scripts")
            
            return 0
            
        except Exception as e:
            return self.handle_api_error(e)
    
    def _save_script_file(self, script_data: Dict, output_dir: Path) -> Optional[Path]:
        """Save script as individual .sh file"""
        try:
            script_name = script_data.get('name', 'unknown')
            script_id = script_data.get('id', 'unknown')
            script_content = script_data.get('script_contents', '')
            
            # Sanitize filename
            safe_name = re.sub(r'[^\w\s-]', '', script_name).strip()
            safe_name = re.sub(r'[\s_-]+', '_', safe_name)
            
            # Create script file
            script_file = output_dir / f"{script_id}_{safe_name}.sh"
            
            with open(script_file, 'w') as f:
                f.write(f"#!/bin/bash\n")
                f.write(f"# JAMF Script: {script_name}\n")
                f.write(f"# Script ID: {script_id}\n")
                f.write(f"# Category: {script_data.get('category', 'N/A')}\n")
                f.write(f"# Priority: {script_data.get('priority', 'N/A')}\n")
                f.write(f"# Parameters: {script_data.get('parameter4', 'None')}\n")
                f.write(f"# Info: {script_data.get('info', 'N/A')}\n")
                f.write(f"#\n")
                f.write(f"# Downloaded from JAMF Pro\n")
                f.write(f"# Download Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"\n")
                if script_content:
                    f.write(script_content)
                else:
                    f.write("# No script content found\n")
            
            # Make executable
            script_file.chmod(0o755)
            
            return script_file
            
        except Exception as e:
            print(f"   ⚠️ Error saving script file: {e}")
            return None
    
    def _save_script_metadata(self, script_data: Dict, output_dir: Path) -> Optional[Path]:
        """Save script metadata as JSON file"""
        try:
            script_name = script_data.get('name', 'unknown')
            script_id = script_data.get('id', 'unknown')
            
            # Sanitize filename
            safe_name = re.sub(r'[^\w\s-]', '', script_name).strip()
            safe_name = re.sub(r'[\s_-]+', '_', safe_name)
            
            # Create metadata file
            metadata_file = output_dir / f"{script_id}_{safe_name}.json"
            
            with open(metadata_file, 'w') as f:
                json.dump(script_data, f, indent=2)
            
            return metadata_file
            
        except Exception as e:
            print(f"   ⚠️ Error saving metadata: {e}")
            return None
    
    def _organize_scripts_by_category(self, output_dir: Path) -> None:
        """Organize scripts into category folders"""
        try:
            print("📁 Organizing scripts by category...")
            
            # Find all script files
            script_files = list(output_dir.glob("*.sh"))
            json_files = list(output_dir.glob("*.json"))
            
            for script_file in script_files:
                # Extract category from filename or metadata
                category = "Uncategorized"
                
                # Try to find corresponding JSON file
                json_file = output_dir / f"{script_file.stem}.json"
                if json_file.exists():
                    try:
                        with open(json_file, 'r') as f:
                            metadata = json.load(f)
                            category = metadata.get('category', 'Uncategorized')
                    except:
                        pass
                
                # Create category directory
                category_dir = output_dir / category
                category_dir.mkdir(exist_ok=True)
                
                # Move files
                new_script_file = category_dir / script_file.name
                script_file.rename(new_script_file)
                
                if json_file.exists():
                    new_json_file = category_dir / json_file.name
                    json_file.rename(new_json_file)
            
            print(f"   ✅ Organized scripts into category folders")
            
        except Exception as e:
            print(f"   ⚠️ Error organizing scripts: {e}")
    
    def _create_github_readme(self, output_dir: Path) -> None:
        """Create README.md for GitHub repository"""
        try:
            print("📝 Creating GitHub README...")
            
            readme_content = f"""# JAMF Pro Scripts

This repository contains scripts exported from JAMF Pro.

## Export Information

- **Export Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Source**: JAMF Pro Development Environment
- **Total Scripts**: {len(list(output_dir.glob('*.sh')))}

## Script Categories

"""
            
            # Add category information
            categories = set()
            for script_file in output_dir.glob("*.sh"):
                json_file = output_dir / f"{script_file.stem}.json"
                if json_file.exists():
                    try:
                        with open(json_file, 'r') as f:
                            metadata = json.load(f)
                            category = metadata.get('category', 'Uncategorized')
                            categories.add(category)
                    except:
                        pass
            
            for category in sorted(categories):
                readme_content += f"- {category}\n"
            
            readme_content += f"""
## Usage

Each script is saved as an individual `.sh` file with the following naming convention:
`{{script_id}}_{{script_name}}.sh`

Scripts include:
- Original JAMF Pro metadata in comments
- Executable permissions
- Full script content

## Metadata

Detailed metadata for each script is available in corresponding `.json` files.

## Migration Notes

These scripts were exported from JAMF Pro for migration to GitHub. 
Please review and test scripts before deploying in production environments.
"""
            
            readme_file = output_dir / 'README.md'
            with open(readme_file, 'w') as f:
                f.write(readme_content)
            
            print(f"   ✅ Created README.md")
            
        except Exception as e:
            print(f"   ⚠️ Error creating README: {e}")
