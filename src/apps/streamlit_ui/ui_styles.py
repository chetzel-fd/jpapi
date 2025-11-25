#!/usr/bin/env python3
"""
UI Styles for JPAPI Manager Streamlit App
Extracted CSS and JavaScript for cleaner code organization
"""


# Color constants for the Gabagool Brand theme
class ColorTheme:
    """Brand colors for consistent theming"""

    # Primary colors
    NAVY_DARK = "#00143b"
    NAVY_MID = "#001c55"
    NAVY_LIGHT = "#00194d"
    BLUE_PRIMARY = "#0078ff"
    BLUE_LIGHT = "#3393ff"
    BLUE_ACCENT = "#0060cc"

    # Accent colors
    YELLOW_PRIMARY = "#ffdc2e"
    YELLOW_LIGHT = "#ffe043"
    YELLOW_DARK = "#e6c629"
    GOLD = "#ffc107"
    GOLD_DARK = "#ffb300"

    # Text colors
    WHITE = "#ffffff"
    TEXT_LIGHT = "#b9c4cb"
    TEXT_DARK = "#1a1a1a"

    # Functional colors
    BORDER_LIGHT = "#334977"
    ERROR_RED = "#dc3545"


# Layout constants
class LayoutConstants:
    """Layout measurements for consistent spacing"""

    FAB_TOP_POSITION = "193px"
    FAB_RIGHT_POSITION = "70px"
    FAB_MIN_WIDTH = "280px"
    FAB_HEIGHT = "50px"

    BUTTON_SIZE = "40px"
    BORDER_WIDTH_THIN = "1px"
    BORDER_WIDTH_THICK = "2px"
    BORDER_WIDTH_EXTRA = "3px"

    BORDER_RADIUS_SMALL = "8px"
    BORDER_RADIUS_MEDIUM = "12px"
    BORDER_RADIUS_LARGE = "16px"
    BORDER_RADIUS_CIRCLE = "50%"


def get_hide_sidebar_css() -> str:
    """Get CSS to hide Streamlit sidebar"""
    return """
<style>
    .css-1d391kg {display: none;}
    .css-1lcbmhc {display: none;}
    [data-testid="stSidebar"] {display: none;}
</style>
"""


def get_custom_css() -> str:
    """Get main custom CSS for JPAPI Manager"""
    colors = ColorTheme
    layout = LayoutConstants

    return f"""
    <style>
    /* Dark theme base - Gabagool Brand */
    .stApp {{
        background: {colors.NAVY_DARK};
        color: {colors.WHITE};
    }}
    
    /* Ensure main container allows sticky */
    .main .block-container {{
        padding-top: 0 !important;
    }}
    
    /* Header styling - sticky at top */
    .elegant-header {{
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 999 !important;
        background: linear-gradient(135deg, {colors.NAVY_DARK} 0%, {colors.NAVY_MID} 50%, {colors.NAVY_LIGHT} 100%) !important;
        border: {layout.BORDER_WIDTH_THICK} solid {colors.BLUE_PRIMARY};
        border-radius: 0 0 {layout.BORDER_RADIUS_MEDIUM} {layout.BORDER_RADIUS_MEDIUM};
        padding: 20px;
        margin: -1rem -1rem 1rem -1rem;
        box-shadow: 0 4px 12px rgba(0, 120, 255, 0.5);
    }}

    .header-content {{
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .header-title {{
        font-size: 32px;
        font-weight: 700;
        color: {colors.WHITE};
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }}

    .header-title span.emphasis {{
        color: {colors.YELLOW_PRIMARY};
        font-weight: 800;
    }}

    .header-subtitle {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        color: {colors.TEXT_LIGHT};
        margin-top: 8px;
    }}

    .label {{
        color: {colors.BLUE_LIGHT};
        font-weight: 700;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
    }}

    .value {{
        color: {colors.WHITE};
        font-weight: 500;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }}
    
    .bullet {{
        color: {colors.BLUE_LIGHT};
        font-weight: bold;
        font-size: 18px;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
    }}

    .url-link {{
        color: {colors.YELLOW_PRIMARY};
        text-decoration: none;
        font-size: 14px;
        font-weight: 600;
    }}

    .url-link:hover {{
        text-decoration: underline;
        color: {colors.YELLOW_LIGHT};
    }}
    
    /* Object card styling - Gabagool Navy gradient */
    .object-card {{
        background: linear-gradient(135deg, {colors.NAVY_DARK} 0%, {colors.NAVY_MID} 100%);
        border: {layout.BORDER_WIDTH_THIN} solid {colors.BORDER_LIGHT};
        border-radius: {layout.BORDER_RADIUS_SMALL};
        padding: 16px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }}
    
    .object-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 220, 46, 0.3);
        border-color: {colors.YELLOW_PRIMARY};
    }}

    .object-card:hover .object-title {{
        color: {colors.YELLOW_PRIMARY};
    }}

    .object-card.selected {{
        border: {layout.BORDER_WIDTH_THICK} solid {colors.BLUE_PRIMARY} !important;
        background: linear-gradient(135deg, {colors.NAVY_LIGHT} 0%, {colors.NAVY_MID} 100%) !important;
        box-shadow: 0 0 12px rgba(0, 120, 255, 0.5) !important;
    }}

    .object-card.selected .object-title {{
        color: {colors.YELLOW_PRIMARY} !important;
    }}
    
    .object-title {{
        font-size: 18px;
        font-weight: 600;
        color: {colors.WHITE};
        margin-bottom: 8px;
    }}

    .object-title span.highlight {{
        color: {colors.YELLOW_PRIMARY};
        font-weight: 700;
    }}
    
    .object-details {{
        font-size: 14px;
        color: {colors.TEXT_LIGHT};
        line-height: 1.4;
    }}

    /* FAB styling - Starts inside header, becomes sticky when scrolling */
    .stPopover > div:first-child {{
        position: fixed !important;
        top: {layout.FAB_TOP_POSITION} !important;
        right: {layout.FAB_RIGHT_POSITION} !important;
        z-index: 1000 !important;
        background: linear-gradient(135deg, {colors.NAVY_DARK} 0%, {colors.NAVY_MID} 100%) !important;
        border: {layout.BORDER_WIDTH_THICK} solid {colors.BLUE_PRIMARY} !important;
        border-radius: {layout.BORDER_RADIUS_MEDIUM} !important;
        padding: 8px 14px !important;
        box-shadow: 0 4px 12px rgba(0, 120, 255, 0.5) !important;
        backdrop-filter: blur(10px) !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        min-width: {layout.FAB_MIN_WIDTH} !important;
        text-align: center !important;
    }}

    .stPopover > div:first-child:hover {{
        transform: scale(1.05) !important;
        box-shadow: 0 8px 24px rgba(255, 220, 46, 0.4) !important;
        background: linear-gradient(135deg, {colors.BLUE_ACCENT} 0%, {colors.BLUE_LIGHT} 100%) !important;
        border-color: {colors.YELLOW_PRIMARY} !important;
    }}
    
    .stPopover > div:first-child button {{
        background: transparent !important;
        border: none !important;
        color: {colors.WHITE} !important;
        padding: 0 !important;
        margin: 0 !important;
        width: {layout.FAB_MIN_WIDTH} !important;
        min-height: {layout.FAB_HEIGHT} !important;
        height: {layout.FAB_HEIGHT} !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }}
    
    .stPopover > div:first-child button p {{
        display: none !important;
    }}

    /* Theme-consistent primary button - Gabagool Yellow for CTAs */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {colors.YELLOW_PRIMARY} 0%, {colors.YELLOW_DARK} 100%) !important;
        border: {layout.BORDER_WIDTH_THIN} solid {colors.YELLOW_PRIMARY} !important;
        color: {colors.NAVY_MID} !important;
        font-weight: 700 !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, {colors.YELLOW_LIGHT} 0%, {colors.YELLOW_PRIMARY} 100%) !important;
        border-color: {colors.YELLOW_LIGHT} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(255, 220, 46, 0.5) !important;
    }}

    /* Hyperlinks - Gabagool Blue */
    a, a:link, a:visited {{
        color: {colors.BLUE_PRIMARY} !important;
        text-decoration: none !important;
    }}

    a:hover {{
        color: {colors.BLUE_LIGHT} !important;
        text-decoration: underline !important;
    }}

    /* Secondary buttons - Blue theme */
    .stButton > button[kind="secondary"] {{
        background: transparent !important;
        border: {layout.BORDER_WIDTH_THIN} solid {colors.BLUE_PRIMARY} !important;
        color: {colors.BLUE_PRIMARY} !important;
        font-weight: 600 !important;
    }}

    .stButton > button[kind="secondary"]:hover {{
        background: rgba(0, 120, 255, 0.1) !important;
        border-color: {colors.BLUE_LIGHT} !important;
    }}

    /* Modern Check Circle Button - Wrapped in custom div for targeting */
    .select-btn-wrapper {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}
    
    .select-btn-wrapper [data-testid="stButton"] button,
    .select-btn-wrapper button[data-testid="baseButton-secondary"],
    .select-btn-wrapper div[data-testid="stButton"] button,
    .select-btn-wrapper button {{
        width: {layout.BUTTON_SIZE} !important;
        height: {layout.BUTTON_SIZE} !important;
        min-width: {layout.BUTTON_SIZE} !important;
        max-width: {layout.BUTTON_SIZE} !important;
        min-height: {layout.BUTTON_SIZE} !important;
        max-height: {layout.BUTTON_SIZE} !important;
        border-radius: {layout.BORDER_RADIUS_CIRCLE} !important;
        border: {layout.BORDER_WIDTH_EXTRA} solid {colors.BORDER_LIGHT} !important;
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        padding: 0 !important;
        font-size: 20px !important;
        font-weight: bold !important;
        line-height: 1 !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* Hover state for unselected buttons */
    .select-btn-wrapper.unselected [data-testid="stButton"] button:hover,
    .select-btn-wrapper.unselected button:hover {{
        border-color: {colors.GOLD} !important;
        transform: scale(1.1) !important;
        background: rgba(255, 193, 7, 0.1) !important;
        background-color: rgba(255, 193, 7, 0.1) !important;
        background-image: none !important;
    }}

    /* Selected state (checkmark) - Yellow/Gold */
    .select-btn-wrapper.selected [data-testid="stButton"] button,
    .select-btn-wrapper.selected button[data-testid="baseButton-secondary"],
    .select-btn-wrapper.selected div[data-testid="stButton"] button,
    .select-btn-wrapper.selected button {{
        border-color: {colors.GOLD} !important;
        background: {colors.GOLD} !important;
        background-color: {colors.GOLD} !important;
        background-image: linear-gradient(135deg, {colors.GOLD} 0%, {colors.GOLD_DARK} 100%) !important;
        box-shadow: 0 0 0 4px rgba(255, 193, 7, 0.3) !important;
        color: {colors.TEXT_DARK} !important;
    }}
    
    .select-btn-wrapper.selected button p {{
        color: {colors.TEXT_DARK} !important;
    }}

    /* Hover state for selected buttons */
    .select-btn-wrapper.selected [data-testid="stButton"] button:hover,
    .select-btn-wrapper.selected button:hover {{
        background: {colors.GOLD_DARK} !important;
        background-color: {colors.GOLD_DARK} !important;
        background-image: linear-gradient(135deg, {colors.GOLD_DARK} 0%, {colors.GOLD} 100%) !important;
        box-shadow: 0 0 0 6px rgba(255, 193, 7, 0.4) !important;
        transform: scale(1.15) !important;
    }}

    /* Hide form container styling completely - ONLY for forms with keys starting with "form_" */
    form[data-testid*="stForm"],
    .stForm {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }}

    /* Modern Circular Checkbox Style - Target our specific wrapper */
    .circular-checkbox-wrapper {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}
    
    .circular-checkbox-wrapper .stCheckbox,
    .circular-checkbox-wrapper label {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}
    
    /* Hide label text */
    .circular-checkbox-wrapper label span:last-child {{
        display: none !important;
    }}

    /* Style the checkbox as a circle */
    .circular-checkbox-wrapper input[type="checkbox"] {{
        width: {layout.BUTTON_SIZE} !important;
        height: {layout.BUTTON_SIZE} !important;
        min-width: {layout.BUTTON_SIZE} !important;
        min-height: {layout.BUTTON_SIZE} !important;
        border-radius: {layout.BORDER_RADIUS_CIRCLE} !important;
        border: {layout.BORDER_WIDTH_EXTRA} solid {colors.BORDER_LIGHT} !important;
        background-color: transparent !important;
        background-image: none !important;
        background: transparent !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        appearance: none !important;
        -webkit-appearance: none !important;
        -moz-appearance: none !important;
        position: relative !important;
        margin: 0 auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* Hover state - unselected */
    .circular-checkbox-wrapper input[type="checkbox"]:hover {{
        border-color: {colors.BLUE_PRIMARY} !important;
        transform: scale(1.1) !important;
        background-color: rgba(0, 120, 255, 0.1) !important;
        background: rgba(0, 120, 255, 0.1) !important;
    }}

    /* Checked state - blue gradient */
    .circular-checkbox-wrapper input[type="checkbox"]:checked {{
        border-color: {colors.BLUE_PRIMARY} !important;
        background: linear-gradient(135deg, {colors.BLUE_PRIMARY} 0%, {colors.BLUE_LIGHT} 100%) !important;
        background-color: {colors.BLUE_PRIMARY} !important;
        background-image: linear-gradient(135deg, {colors.BLUE_PRIMARY} 0%, {colors.BLUE_LIGHT} 100%) !important;
        box-shadow: 0 0 0 4px rgba(0, 120, 255, 0.2) !important;
    }}

    /* Checkmark symbol for checked state */
    .circular-checkbox-wrapper input[type="checkbox"]:checked::before {{
        content: '✓' !important;
        color: {colors.WHITE} !important;
        font-size: 22px !important;
        font-weight: bold !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        display: block !important;
    }}

    /* Hover state - checked */
    .circular-checkbox-wrapper input[type="checkbox"]:checked:hover {{
        background: linear-gradient(135deg, {colors.BLUE_LIGHT} 0%, {colors.BLUE_PRIMARY} 100%) !important;
        background-color: {colors.BLUE_LIGHT} !important;
        background-image: linear-gradient(135deg, {colors.BLUE_LIGHT} 0%, {colors.BLUE_PRIMARY} 100%) !important;
        box-shadow: 0 0 0 6px rgba(0, 120, 255, 0.3) !important;
        transform: scale(1.15) !important;
    }}

    /* Delete Modal Overlay - Streamlit offline style */
    .delete-modal-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(8px);
        z-index: 999999;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    
    .delete-modal {{
        background: linear-gradient(135deg, #001428 0%, {colors.NAVY_LIGHT} 100%);
        border: {layout.BORDER_WIDTH_EXTRA} solid {colors.ERROR_RED};
        border-radius: {layout.BORDER_RADIUS_LARGE};
        padding: 40px;
        max-width: 700px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 20px 80px rgba(220, 53, 69, 0.5);
        animation: modalSlideIn 0.3s ease-out;
    }}
    
    @keyframes modalSlideIn {{
        from {{
            transform: translateY(-50px);
            opacity: 0;
        }}
        to {{
            transform: translateY(0);
            opacity: 1;
        }}
    }}
    
    .modal-header {{
        text-align: center;
        margin-bottom: 30px;
    }}
    
    .modal-header h2 {{
        color: {colors.ERROR_RED};
        font-size: 32px;
        margin: 0 0 10px 0;
        text-shadow: 0 2px 8px rgba(220, 53, 69, 0.5);
    }}

</style>
"""


def get_javascript() -> str:
    """Get JavaScript for FAB and object selection"""
    return """
    <script>
    function toggleFabMenu() {
        // This will be handled by Streamlit session state
        console.log('FAB clicked');
    }
    </script>
    """
