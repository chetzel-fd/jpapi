"""
Result Exporter Module - Single Responsibility: Export lock results to files
"""
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import csv


class ResultExporter:
    """Exports lock results to CSV or Excel - Single Responsibility"""

    def export(
        self,
        results: List[Dict],
        original_df,
        file_path: Path,
        is_excel: bool,
    ) -> str:
        """Export results to appropriate format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if is_excel and original_df is not None:
            return self._export_to_excel(original_df, results, file_path, timestamp)
        else:
            return self._export_to_csv(results, timestamp)

    def _export_to_excel(
        self, original_df, results: List[Dict], file_path: Path, timestamp: str
    ) -> str:
        """Export results to Excel file"""
        try:
            import pandas as pd
        except ImportError:
            return self._export_to_csv(results, timestamp)

        # Create a copy of the original dataframe
        output_df = original_df.copy()

        # Create mappings from results
        username_to_data = {}
        for r in results:
            username = r["Username"]
            username_to_data[username] = {
                "computer_name": r["Device Name"],
                "passcode": r["Passcode"],
                "status": r["Status"],
            }

        # Find the username column
        username_col = None
        for col in output_df.columns:
            if "username" in col.lower() or "email" in col.lower():
                username_col = col
                break

        # Ensure we have at least 5 columns
        while len(output_df.columns) < 4:
            output_df[f"Column_{len(output_df.columns)}"] = ""

        # Add Computer Name column (D) and Lock Code column (E) if they don't exist
        if len(output_df.columns) == 4:
            output_df["Computer Name"] = ""
            output_df["Lock Code"] = ""
        elif len(output_df.columns) == 5:
            output_df["Lock Code"] = ""

        # Write computer names and passcodes
        if username_col:
            for idx, row in output_df.iterrows():
                username = str(row[username_col]).strip()
                if username in username_to_data:
                    data = username_to_data[username]
                    # Write computer name to column D (index 3)
                    if len(output_df.columns) > 3:
                        output_df.iloc[idx, 3] = data["computer_name"]
                    # Write lock code to column E (index 4)
                    if len(output_df.columns) > 4:
                        output_df.iloc[idx, 4] = data["passcode"]

        # Save to new file
        output_file = f"device_lock_results_{timestamp}.xlsx"
        output_df.to_excel(output_file, index=False, engine="openpyxl")

        print(f"   ✅ Computer names written to column D")
        print(f"   ✅ Lock codes written to column E")

        return output_file

    def _export_to_csv(self, results: List[Dict], timestamp: str) -> str:
        """Export results to CSV file"""
        output_file = f"device_lock_results_{timestamp}.csv"
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        return output_file









