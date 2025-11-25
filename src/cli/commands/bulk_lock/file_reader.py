"""
File Reader Module - Single Responsibility: Read user data from various sources
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import csv
import requests
from datetime import datetime


class FileReader(ABC):
    """Abstract base class for file readers - Open/Closed Principle"""

    @abstractmethod
    def read(self, source: str) -> Tuple[List[Dict[str, str]], Optional[object], Path]:
        """
        Read users from file source
        
        Returns:
            Tuple of (users_list, original_dataframe, file_path)
            users_list: List of dicts with 'username' and optional 'hostname'
        """
        pass

    def _should_skip_user(self, username: str, lock_code: Optional[str]) -> bool:
        """Check if user should be skipped (already has lock code)"""
        if lock_code and str(lock_code).strip():
            print(f"   ⏭️  Skipping {username} - already has lock code")
            return True
        return False


class CSVFileReader(FileReader):
    """Reads users from CSV files - Single Responsibility"""

    def read(self, source: str) -> Tuple[List[Dict[str, str]], Optional[object], Path]:
        csv_path = Path(source)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {source}")

        users = []
        username_col = None
        email_col = None
        hostname_col = None
        lock_code_col = None

        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Find relevant columns (case-insensitive)
            if reader.fieldnames:
                for col in reader.fieldnames:
                    col_lower = col.lower()
                    if "username" in col_lower or "user" in col_lower:
                        username_col = col
                    if "email" in col_lower:
                        email_col = col
                    if "hostname" in col_lower or "computer" in col_lower:
                        hostname_col = col
                    if "lock" in col_lower and "code" in col_lower:
                        lock_code_col = col

            # Read users
            for row in reader:
                username = ""
                hostname = ""

                # Get username/email
                if email_col and row.get(email_col):
                    username = row[email_col].strip()
                elif username_col and row.get(username_col):
                    username = row[username_col].strip()

                # Skip if no username/email
                if not username:
                    continue

                # Skip if already has lock code
                lock_code = row.get(lock_code_col, "").strip() if lock_code_col else None
                if self._should_skip_user(username, lock_code):
                    continue

                # Get hostname if available
                if hostname_col and row.get(hostname_col):
                    hostname = row[hostname_col].strip()

                # Add user with optional hostname
                user_entry = {"username": username}
                if hostname:
                    user_entry["hostname"] = hostname
                users.append(user_entry)

        return users, None, csv_path


class ExcelFileReader(FileReader):
    """Reads users from Excel files - Single Responsibility"""

    def read(self, source: str) -> Tuple[List[Dict[str, str]], Optional[object], Path]:
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas and openpyxl required for Excel support: pip install pandas openpyxl"
            )

        file_path = Path(source)
        df = pd.read_excel(file_path)
        users = []
        username_col = None

        # Find username/email column
        for col in df.columns:
            if "username" in col.lower() or "email" in col.lower():
                username_col = col
                break

        if username_col:
            # Check each row - skip if column E (index 4) has a value
            for idx, row in df.iterrows():
                username = str(row[username_col]).strip()
                if username and username != "nan":
                    # Check if column E has a value (already locked)
                    if len(df.columns) > 4:
                        lock_code = row.iloc[4] if pd.notna(row.iloc[4]) else None
                        if self._should_skip_user(username, str(lock_code) if lock_code else None):
                            continue
                    users.append({"username": username})

        return users, df, file_path


class SharePointFileReader(FileReader):
    """Reads users from SharePoint Excel files - Single Responsibility"""

    def read(self, source: str) -> Tuple[List[Dict[str, str]], Optional[object], Path]:
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas and openpyxl required for SharePoint support: pip install pandas openpyxl"
            )

        # Convert SharePoint sharing link to direct download URL
        download_url = self._convert_sharepoint_url(source)

        print(f"   Downloading file...")
        response = requests.get(download_url, allow_redirects=True)
        response.raise_for_status()

        # Save temporarily
        temp_file = Path(
            f'temp_sharepoint_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        with open(temp_file, "wb") as f:
            f.write(response.content)

        print(f"   ✅ Downloaded successfully")
        print(f"   📋 Checking for existing lock codes in column E...")

        # Read Excel file
        df = pd.read_excel(temp_file)
        users = []
        username_col = None
        skipped_count = 0

        # Find username/email column
        for col in df.columns:
            if "username" in col.lower() or "email" in col.lower():
                username_col = col
                break

        if username_col:
            # Check each row - skip if column E (index 4) has a value
            for idx, row in df.iterrows():
                username = str(row[username_col]).strip()
                if username and username != "nan":
                    # Check if column E has a value (already locked)
                    if len(df.columns) > 4:
                        lock_code = row.iloc[4] if pd.notna(row.iloc[4]) else None
                        if self._should_skip_user(username, str(lock_code) if lock_code else None):
                            skipped_count += 1
                            continue
                    users.append({"username": username})

        if skipped_count > 0:
            print(f"   ℹ️  Skipped {skipped_count} users with existing lock codes")

        return users, df, temp_file

    def _convert_sharepoint_url(self, url: str) -> str:
        """Convert SharePoint sharing URL to direct download URL"""
        if "?e=" in url:
            base_url = url.split("?e=")[0]
            return base_url + "?download=1"
        return url + "?download=1"


class FileReaderFactory:
    """Factory for creating appropriate file reader - Dependency Inversion"""

    @staticmethod
    def create(source: str) -> FileReader:
        """Create appropriate file reader based on source type"""
        source_lower = source.lower()
        
        if "sharepoint.com" in source_lower:
            return SharePointFileReader()
        elif source_lower.endswith((".xlsx", ".xls")):
            return ExcelFileReader()
        else:
            return CSVFileReader()









