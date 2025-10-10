import streamlit as st
import pandas as pd
from pathlib import Path

# Page config
st.set_page_config(
    page_title="JPAPI Manager",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Simple CSS
st.markdown(
    """
<style>
    .main .block-container {
        background: #252729;
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1600px;
    }
    
    .stButton > button {
        background: #3393ff;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-weight: 500;
        font-size: 11px;
        height: 32px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #1a86ff;
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }
</style>
""",
    unsafe_allow_html=True,
)


def load_data(object_type="searches", environment="sandbox"):
    """Load data with proper environment filtering"""
    try:
        # Try multiple data directory locations
        possible_dirs = [
            Path("storage/data/csv-exports"),
            Path("data/csv-exports"),
            Path("exports"),
        ]

        csv_dir = None
        for dir_path in possible_dirs:
            if dir_path.exists():
                csv_dir = dir_path
                break

        if not csv_dir:
            csv_dir = Path("storage/data/csv-exports")
            csv_dir.mkdir(parents=True, exist_ok=True)

        # Look for environment-specific files first
        patterns = [
            f"{environment}-{object_type}-export-*.csv",
            f"{environment}-{object_type}*.csv",
            f"*-{object_type}-export-*.csv",  # Fallback
            f"*{object_type}*.csv",  # Fallback
        ]

        files = []
        for pattern in patterns:
            files.extend(list(csv_dir.glob(pattern)))

        files = list(set(files))  # Remove duplicates

        if not files:
            st.warning(f"No {object_type} files found for {environment} environment")
            return pd.DataFrame(
                {
                    "Name": [f"Sample {object_type.title()} {i}" for i in range(1, 6)],
                    "ID": [1000 + i for i in range(1, 6)],
                    "Type": [object_type.title()] * 5,
                    "Status": ["Active", "Active", "Draft", "Active", "Active"],
                    "Last Modified": [
                        "2024-01-15",
                        "2024-01-14",
                        "2024-01-13",
                        "2024-01-12",
                        "2024-01-11",
                    ],
                }
            )

        # Get the most recent file
        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        st.success(f"Found {len(files)} files, using: {latest_file.name}")

        # Load the CSV
        df = pd.read_csv(latest_file)

        # Standardize columns
        if "name" in df.columns:
            df["Name"] = df["name"]
        if "id" in df.columns:
            df["ID"] = df["id"]
        if "type" in df.columns:
            df["Type"] = df["type"]
        if "status" in df.columns:
            df["Status"] = df["status"]
        elif "enabled" in df.columns:
            df["Status"] = df["enabled"].map({True: "Active", False: "Draft"})
        else:
            df["Status"] = "Active"

        if "Last Modified" not in df.columns:
            df["Last Modified"] = "2024-01-15"

        # Ensure required columns
        required_columns = ["Name", "ID", "Type", "Status", "Last Modified"]
        for col in required_columns:
            if col not in df.columns:
                if col == "Name":
                    df[col] = f"Sample {object_type.title()}"
                elif col == "ID":
                    df[col] = range(1001, 1001 + len(df))
                elif col == "Type":
                    df[col] = object_type.title()
                elif col == "Status":
                    df[col] = "Active"
                elif col == "Last Modified":
                    df[col] = "2024-01-15"

        return df

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(
            {
                "Name": [f"Sample {object_type.title()} {i}" for i in range(1, 6)],
                "ID": [1000 + i for i in range(1, 6)],
                "Type": [object_type.title()] * 5,
                "Status": ["Active", "Active", "Draft", "Active", "Active"],
                "Last Modified": [
                    "2024-01-15",
                    "2024-01-14",
                    "2024-01-13",
                    "2024-01-12",
                    "2024-01-11",
                ],
            }
        )


def main():
    # Initialize session state
    if "current_environment" not in st.session_state:
        st.session_state.current_environment = "sandbox"
    if "current_object_type" not in st.session_state:
        st.session_state.current_object_type = "searches"

    # Header
    st.markdown("### ⚡ JPAPI Manager")
    st.caption("jamf.company.com")

    # Controls
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        env = st.selectbox(
            "Environment",
            ["sandbox", "production"],
            index=0 if st.session_state.current_environment == "sandbox" else 1,
            key="env_selector",
        )
        if env != st.session_state.current_environment:
            st.session_state.current_environment = env
            st.rerun()

    with col2:
        object_type = st.selectbox(
            "Object Type",
            ["searches", "policies", "profiles", "packages", "groups"],
            index=0,
            key="object_type_selector",
        )
        if object_type != st.session_state.current_object_type:
            st.session_state.current_object_type = object_type
            st.rerun()

    with col3:
        st.caption(f"📊 {object_type} • {env}")

    # Load data
    data = load_data(
        object_type=st.session_state.current_object_type,
        environment=st.session_state.current_environment,
    )

    # Show data
    st.markdown("### Objects")
    cols = st.columns(3)

    for idx, row in data.iterrows():
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"**{row['Name']}**")
                st.caption(f"ID: {row['ID']} • {row['Type']}")

                # Status badge
                if row["Status"] == "Active":
                    st.markdown(
                        '<span style="background: rgba(40, 167, 69, 0.2); color: #28a745; padding: 4px 8px; border-radius: 6px; font-size: 11px;">✅ Active</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<span style="background: rgba(255, 193, 7, 0.2); color: #ffc107; padding: 4px 8px; border-radius: 6px; font-size: 11px;">⚠️ Draft</span>',
                        unsafe_allow_html=True,
                    )

                st.markdown("---")


if __name__ == "__main__":
    main()
