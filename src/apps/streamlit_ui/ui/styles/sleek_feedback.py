"""
Sleek feedback styling for fluid, modern UI interactions
"""

import streamlit as st


class SleekFeedbackStyles:
    """Sleek feedback styling for modern UI interactions"""

    @staticmethod
    def apply_sleek_styles():
        """Apply sleek, fluid feedback styles"""
        st.markdown(
            """
            <style>
            /* Sleek Notification Styles */
            .sleek-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                max-width: 400px;
                background: rgba(30, 41, 59, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                animation: slideInRight 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                transform-origin: top right;
            }
            
            .sleek-notification.dismissing {
                animation: slideOutRight 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%) scale(0.8);
                    opacity: 0;
                }
                to {
                    transform: translateX(0) scale(1);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0) scale(1);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%) scale(0.8);
                    opacity: 0;
                }
            }
            
            /* Sleek Loading Indicators */
            .sleek-loading {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                background: rgba(51, 147, 255, 0.1);
                border: 1px solid rgba(51, 147, 255, 0.3);
                border-radius: 8px;
                color: #3393ff;
                font-size: 14px;
                font-weight: 500;
                animation: pulse 2s infinite;
            }
            
            .sleek-loading::before {
                content: '';
                width: 16px;
                height: 16px;
                border: 2px solid rgba(51, 147, 255, 0.3);
                border-top: 2px solid #3393ff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Sleek Success Feedback */
            .sleek-success {
                background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(40, 167, 69, 0.05) 100%);
                border: 1px solid rgba(40, 167, 69, 0.3);
                border-radius: 8px;
                padding: 12px 16px;
                color: #28a745;
                font-weight: 500;
                animation: successSlide 0.3s ease-out;
            }
            
            @keyframes successSlide {
                from {
                    transform: translateY(-10px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            /* Sleek Error Feedback */
            .sleek-error {
                background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(220, 53, 69, 0.05) 100%);
                border: 1px solid rgba(220, 53, 69, 0.3);
                border-radius: 8px;
                padding: 12px 16px;
                color: #dc3545;
                font-weight: 500;
                animation: errorShake 0.5s ease-out;
            }
            
            @keyframes errorShake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }
            
            /* Sleek Progress Bars */
            .sleek-progress {
                width: 100%;
                height: 4px;
                background: rgba(51, 147, 255, 0.2);
                border-radius: 2px;
                overflow: hidden;
                position: relative;
            }
            
            .sleek-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #3393ff 0%, #1a86ff 100%);
                border-radius: 2px;
                transition: width 0.3s ease;
                position: relative;
            }
            
            .sleek-progress-bar::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
                animation: shimmer 2s infinite;
            }
            
            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            
            /* Sleek FAB Status */
            .fab-status {
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border: 1px solid rgba(51, 147, 255, 0.3);
                border-radius: 12px;
                padding: 16px;
                margin: 8px 0;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            }
            
            .fab-status-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 12px;
            }
            
            .fab-status-title {
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
            }
            
            .fab-status-badge {
                background: rgba(51, 147, 255, 0.2);
                color: #3393ff;
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }
            
            /* Sleek Button Interactions */
            .sleek-button {
                background: linear-gradient(135deg, #3393ff 0%, #1a86ff 100%);
                border: none;
                border-radius: 8px;
                color: white;
                padding: 8px 16px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                position: relative;
                overflow: hidden;
            }
            
            .sleek-button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(51, 147, 255, 0.3);
            }
            
            .sleek-button:active {
                transform: translateY(0);
            }
            
            .sleek-button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: left 0.5s;
            }
            
            .sleek-button:hover::before {
                left: 100%;
            }
            
            /* Sleek Card Interactions */
            .sleek-card {
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(51, 147, 255, 0.2);
                border-radius: 12px;
                padding: 16px;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .sleek-card:hover {
                border-color: rgba(51, 147, 255, 0.5);
                box-shadow: 0 8px 24px rgba(51, 147, 255, 0.1);
                transform: translateY(-2px);
            }
            
            .sleek-card.selected {
                border-color: #3393ff;
                background: rgba(51, 147, 255, 0.1);
                box-shadow: 0 0 20px rgba(51, 147, 255, 0.3);
            }
            
            /* Sleek Status Indicators */
            .status-indicator {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }
            
            .status-indicator.active {
                background: rgba(40, 167, 69, 0.2);
                color: #28a745;
                border: 1px solid rgba(40, 167, 69, 0.3);
            }
            
            .status-indicator.warning {
                background: rgba(255, 193, 7, 0.2);
                color: #ffc107;
                border: 1px solid rgba(255, 193, 7, 0.3);
            }
            
            .status-indicator.error {
                background: rgba(220, 53, 69, 0.2);
                color: #dc3545;
                border: 1px solid rgba(220, 53, 69, 0.3);
            }
            
            /* Sleek Transitions */
            * {
                transition: all 0.2s ease;
            }
            
            /* Hide default Streamlit elements that conflict */
            .stAlert {
                border-radius: 8px !important;
                border: none !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
            }
            
            .stSuccess {
                background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(40, 167, 69, 0.05) 100%) !important;
                border: 1px solid rgba(40, 167, 69, 0.3) !important;
                color: #28a745 !important;
            }
            
            .stWarning {
                background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 193, 7, 0.05) 100%) !important;
                border: 1px solid rgba(255, 193, 7, 0.3) !important;
                color: #ffc107 !important;
            }
            
            .stError {
                background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(220, 53, 69, 0.05) 100%) !important;
                border: 1px solid rgba(220, 53, 69, 0.3) !important;
                color: #dc3545 !important;
            }
            
            .stInfo {
                background: linear-gradient(135deg, rgba(51, 147, 255, 0.1) 0%, rgba(51, 147, 255, 0.05) 100%) !important;
                border: 1px solid rgba(51, 147, 255, 0.3) !important;
                color: #3393ff !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
