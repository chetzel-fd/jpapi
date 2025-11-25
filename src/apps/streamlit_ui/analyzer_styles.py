#!/usr/bin/env python3
"""
Analyzer Styles - Gabagool Brand Theme
Reuses base styles from jpapi_manager and adds analyzer-specific styles
"""

from ui_styles import ColorTheme, LayoutConstants


def get_analyzer_css() -> str:
    """Get analyzer-specific CSS that extends the base Gabagool theme"""
    colors = ColorTheme
    layout = LayoutConstants

    return f"""
    <style>
    /* ===== BASE THEME (from jpapi_manager) ===== */
    .stApp {{
        background: {colors.NAVY_DARK};
        color: {colors.WHITE};
    }}
    
    /* ===== ANALYZER HEADER ===== */
    .analyzer-header {{
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
    
    .analyzer-title {{
        font-size: 32px;
        font-weight: 700;
        color: {colors.WHITE};
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }}
    
    .analyzer-title .icon {{
        color: {colors.BLUE_LIGHT};
        margin-right: 8px;
    }}
    
    .analyzer-subtitle {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        color: {colors.TEXT_LIGHT};
        margin-top: 8px;
    }}
    
    /* ===== MODE SELECTOR TABS ===== */
    .mode-tabs {{
        display: flex;
        gap: 12px;
        margin: 20px 0;
        border-bottom: 2px solid {colors.BORDER_LIGHT};
        padding-bottom: 0;
    }}
    
    .mode-tab {{
        background: transparent;
        border: none;
        border-bottom: 3px solid transparent;
        color: {colors.TEXT_LIGHT};
        padding: 12px 20px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .mode-tab:hover {{
        color: {colors.BLUE_LIGHT};
        border-bottom-color: {colors.BLUE_LIGHT};
    }}
    
    .mode-tab.active {{
        color: {colors.YELLOW_PRIMARY};
        border-bottom-color: {colors.YELLOW_PRIMARY};
        background: rgba(255, 220, 46, 0.1);
    }}
    
    /* ===== RELATIONSHIP CARDS ===== */
    .relationship-card {{
        background: linear-gradient(135deg, {colors.NAVY_DARK} 0%, {colors.NAVY_MID} 100%);
        border: {layout.BORDER_WIDTH_THICK} solid {colors.BLUE_PRIMARY};
        border-radius: {layout.BORDER_RADIUS_MEDIUM};
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0, 120, 255, 0.3);
        transition: all 0.3s ease;
    }}
    
    .relationship-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 120, 255, 0.4);
        border-color: {colors.BLUE_LIGHT};
    }}
    
    .relationship-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid {colors.BORDER_LIGHT};
    }}
    
    .relationship-card-title {{
        font-size: 20px;
        font-weight: 700;
        color: {colors.YELLOW_PRIMARY};
    }}
    
    .relationship-card-badge {{
        background: {colors.BLUE_PRIMARY};
        color: {colors.WHITE};
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
    }}
    
    /* ===== OBJECT REFERENCE CARDS (nested) ===== */
    .object-ref-card {{
        background: rgba(0, 120, 255, 0.1);
        border: 1px solid {colors.BLUE_PRIMARY};
        border-radius: {layout.BORDER_RADIUS_SMALL};
        padding: 12px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    
    .object-ref-card:hover {{
        background: rgba(0, 120, 255, 0.2);
        border-color: {colors.BLUE_LIGHT};
        transform: translateX(4px);
    }}
    
    .object-ref-icon {{
        font-size: 20px;
        min-width: 24px;
    }}
    
    .object-ref-content {{
        flex: 1;
    }}
    
    .object-ref-name {{
        color: {colors.WHITE};
        font-weight: 600;
        font-size: 14px;
    }}
    
    .object-ref-meta {{
        color: {colors.TEXT_LIGHT};
        font-size: 12px;
        margin-top: 4px;
    }}
    
    /* ===== ORPHAN CARDS ===== */
    .orphan-card {{
        background: linear-gradient(135deg, #3d2a00 0%, #4d3500 100%);
        border: {layout.BORDER_WIDTH_THICK} solid {colors.YELLOW_PRIMARY};
        border-radius: {layout.BORDER_RADIUS_MEDIUM};
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(255, 220, 46, 0.3);
        position: relative;
    }}
    
    .orphan-card::before {{
        content: '⚠️';
        position: absolute;
        top: -10px;
        right: 20px;
        font-size: 24px;
        background: {colors.NAVY_DARK};
        padding: 4px 8px;
        border-radius: 50%;
    }}
    
    .orphan-card-title {{
        color: {colors.YELLOW_PRIMARY};
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 8px;
    }}
    
    .orphan-card-meta {{
        color: {colors.TEXT_LIGHT};
        font-size: 14px;
        margin-bottom: 12px;
    }}
    
    .orphan-card-stats {{
        display: flex;
        gap: 16px;
        margin-top: 12px;
    }}
    
    .orphan-stat {{
        background: rgba(255, 220, 46, 0.1);
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
    }}
    
    .orphan-stat-label {{
        color: {colors.TEXT_LIGHT};
        font-weight: 600;
    }}
    
    .orphan-stat-value {{
        color: {colors.YELLOW_PRIMARY};
        font-weight: 700;
        margin-left: 4px;
    }}
    
    /* ===== IMPACT ANALYSIS CARDS ===== */
    .impact-card {{
        border-radius: {layout.BORDER_RADIUS_MEDIUM};
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }}
    
    .impact-card.low-risk {{
        background: linear-gradient(135deg, #0d3d1f 0%, #165c2f 100%);
        border: {layout.BORDER_WIDTH_THICK} solid #28a745;
    }}
    
    .impact-card.medium-risk {{
        background: linear-gradient(135deg, #4d3500 0%, #6d4a00 100%);
        border: {layout.BORDER_WIDTH_THICK} solid #ffc107;
    }}
    
    .impact-card.high-risk {{
        background: linear-gradient(135deg, #3d0d0d 0%, #5d1a1a 100%);
        border: {layout.BORDER_WIDTH_THICK} solid #dc3545;
    }}
    
    .impact-risk-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 16px;
    }}
    
    .impact-risk-badge.low {{
        background: #28a745;
        color: white;
    }}
    
    .impact-risk-badge.medium {{
        background: #ffc107;
        color: #1a1a1a;
    }}
    
    .impact-risk-badge.high {{
        background: #dc3545;
        color: white;
    }}
    
    .impact-details {{
        margin: 16px 0;
    }}
    
    .impact-detail-item {{
        display: flex;
        align-items: start;
        gap: 8px;
        margin: 8px 0;
        color: {colors.WHITE};
    }}
    
    .impact-detail-bullet {{
        font-size: 18px;
        min-width: 20px;
    }}
    
    .impact-recommendations {{
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid {colors.YELLOW_PRIMARY};
        padding: 12px;
        margin-top: 16px;
        border-radius: 4px;
    }}
    
    .impact-recommendations-title {{
        color: {colors.YELLOW_PRIMARY};
        font-weight: 700;
        margin-bottom: 8px;
    }}
    
    /* ===== DEPENDENCY TREE ===== */
    .dependency-tree {{
        margin: 20px 0;
    }}
    
    .tree-node {{
        margin-left: 24px;
        position: relative;
        padding-left: 20px;
        border-left: 2px solid {colors.BORDER_LIGHT};
    }}
    
    .tree-node::before {{
        content: '';
        position: absolute;
        left: -2px;
        top: 16px;
        width: 16px;
        height: 2px;
        background: {colors.BORDER_LIGHT};
    }}
    
    .tree-node-card {{
        background: rgba(0, 120, 255, 0.05);
        border: 1px solid {colors.BORDER_LIGHT};
        border-radius: {layout.BORDER_RADIUS_SMALL};
        padding: 8px 12px;
        margin: 8px 0;
        font-size: 14px;
    }}
    
    .tree-node-card:hover {{
        background: rgba(0, 120, 255, 0.1);
        border-color: {colors.BLUE_PRIMARY};
    }}
    
    /* ===== STATS SECTION ===== */
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 20px 0;
    }}
    
    .stat-card {{
        background: linear-gradient(135deg, {colors.NAVY_LIGHT} 0%, {colors.NAVY_MID} 100%);
        border: 1px solid {colors.BORDER_LIGHT};
        border-radius: {layout.BORDER_RADIUS_SMALL};
        padding: 16px;
        text-align: center;
    }}
    
    .stat-value {{
        font-size: 32px;
        font-weight: 700;
        color: {colors.BLUE_LIGHT};
        display: block;
    }}
    
    .stat-label {{
        font-size: 12px;
        color: {colors.TEXT_LIGHT};
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 8px;
    }}
    
    /* ===== EMPTY STATE ===== */
    .empty-state {{
        text-align: center;
        padding: 60px 20px;
        color: {colors.TEXT_LIGHT};
    }}
    
    .empty-state-icon {{
        font-size: 64px;
        margin-bottom: 16px;
        opacity: 0.5;
    }}
    
    .empty-state-title {{
        font-size: 20px;
        font-weight: 600;
        color: {colors.WHITE};
        margin-bottom: 8px;
    }}
    
    .empty-state-description {{
        font-size: 14px;
        color: {colors.TEXT_LIGHT};
    }}
    
    /* ===== LOADING STATE ===== */
    .loading-spinner {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
    }}
    
    .loading-text {{
        color: {colors.TEXT_LIGHT};
        margin-top: 16px;
        font-size: 14px;
    }}
    
    /* ===== SECTION HEADERS ===== */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid {colors.BORDER_LIGHT};
    }}
    
    .section-header-icon {{
        font-size: 24px;
    }}
    
    .section-header-title {{
        font-size: 20px;
        font-weight: 700;
        color: {colors.WHITE};
    }}
    
    .section-header-count {{
        background: {colors.BLUE_PRIMARY};
        color: {colors.WHITE};
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
    }}
    
    /* ===== OBJECT TYPE BADGES ===== */
    .object-type-badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }}
    
    .object-type-badge.policies {{
        background: rgba(0, 120, 255, 0.2);
        color: {colors.BLUE_LIGHT};
        border: 1px solid {colors.BLUE_PRIMARY};
    }}
    
    .object-type-badge.profiles {{
        background: rgba(108, 99, 255, 0.2);
        color: #8b7fff;
        border: 1px solid #6c63ff;
    }}
    
    .object-type-badge.groups {{
        background: rgba(52, 211, 153, 0.2);
        color: #34d399;
        border: 1px solid #10b981;
    }}
    
    .object-type-badge.scripts {{
        background: rgba(251, 146, 60, 0.2);
        color: #fb923c;
        border: 1px solid #f97316;
    }}
    
    .object-type-badge.packages {{
        background: rgba(168, 85, 247, 0.2);
        color: #a855f7;
        border: 1px solid #9333ea;
    }}
    
    /* ===== BUTTONS (inherit from jpapi_manager) ===== */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {colors.YELLOW_PRIMARY} 0%, {colors.YELLOW_DARK} 100%) !important;
        border: {layout.BORDER_WIDTH_THIN} solid {colors.YELLOW_PRIMARY} !important;
        color: {colors.NAVY_MID} !important;
        font-weight: 700 !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, {colors.YELLOW_LIGHT} 0%, {colors.YELLOW_PRIMARY} 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(255, 220, 46, 0.5) !important;
    }}
    
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
    
    /* ===== HIDE STREAMLIT ELEMENTS ===== */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """


def get_hide_sidebar_css() -> str:
    """Get CSS to hide Streamlit sidebar"""
    return """
<style>
    .css-1d391kg {display: none;}
    .css-1lcbmhc {display: none;}
    [data-testid="stSidebar"] {display: none;}
</style>
"""







