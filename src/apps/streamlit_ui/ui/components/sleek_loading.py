"""
Sleek loading components that auto-dismiss and provide fluid feedback
"""

import streamlit as st
import time
from typing import Optional


class SleekLoadingManager:
    """Manages sleek, auto-dismissing loading indicators"""

    def __init__(self):
        if "loading_states" not in st.session_state:
            st.session_state.loading_states = {}

    def show_loading(
        self,
        key: str,
        message: str = "Loading...",
        duration: float = 2.0,
        auto_dismiss: bool = True,
    ) -> None:
        """Show a sleek loading indicator that auto-dismisses"""
        st.session_state.loading_states[key] = {
            "message": message,
            "start_time": time.time(),
            "duration": duration,
            "auto_dismiss": auto_dismiss,
            "active": True,
        }

    def hide_loading(self, key: str) -> None:
        """Hide a loading indicator"""
        if key in st.session_state.loading_states:
            st.session_state.loading_states[key]["active"] = False

    def render_loading_indicators(self) -> None:
        """Render all active loading indicators"""
        current_time = time.time()
        active_indicators = []

        for key, state in st.session_state.loading_states.items():
            if not state["active"]:
                continue

            elapsed = current_time - state["start_time"]

            # Auto-dismiss if duration exceeded
            if state["auto_dismiss"] and elapsed > state["duration"]:
                state["active"] = False
                continue

            active_indicators.append((key, state, elapsed))

        # Render active indicators
        for key, state, elapsed in active_indicators:
            self._render_single_loading(key, state, elapsed)

    def _render_single_loading(self, key: str, state: dict, elapsed: float) -> None:
        """Render a single loading indicator"""
        message = state["message"]
        duration = state["duration"]
        progress = min(100, (elapsed / duration) * 100)

        # Calculate remaining time
        remaining = max(0, duration - elapsed)

        st.markdown(
            f"""
            <div class="sleek-loading-container" 
                 style="
                     position: fixed;
                     top: 20px;
                     left: 50%;
                     transform: translateX(-50%);
                     z-index: 1000;
                     background: rgba(30, 41, 59, 0.95);
                     backdrop-filter: blur(10px);
                     border: 1px solid rgba(51, 147, 255, 0.3);
                     border-radius: 12px;
                     padding: 16px 24px;
                     box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                     animation: slideInDown 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                 ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    color: #3393ff;
                    font-weight: 500;
                ">
                    <div class="sleek-spinner"></div>
                    <span>{message}</span>
                    <span style="
                        font-size: 12px;
                        opacity: 0.7;
                        margin-left: 8px;
                    ">{remaining:.1f}s</span>
                </div>
                <div class="sleek-progress" style="margin-top: 8px;">
                    <div class="sleek-progress-bar" style="width: {progress}%;"></div>
                </div>
            </div>
            
            <style>
                @keyframes slideInDown {{
                    from {{
                        transform: translateX(-50%) translateY(-20px);
                        opacity: 0;
                    }}
                    to {{
                        transform: translateX(-50%) translateY(0);
                        opacity: 1;
                    }}
                }}
                
                .sleek-spinner {{
                    width: 20px;
                    height: 20px;
                    border: 2px solid rgba(51, 147, 255, 0.3);
                    border-top: 2px solid #3393ff;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }}
                
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    def show_success_feedback(
        self, message: str, duration: float = 2.0, auto_dismiss: bool = True
    ) -> None:
        """Show sleek success feedback that auto-dismisses"""
        st.markdown(
            f"""
            <div class="sleek-success-feedback" 
                 style="
                     position: fixed;
                     top: 20px;
                     left: 50%;
                     transform: translateX(-50%);
                     z-index: 1000;
                     background: linear-gradient(135deg, rgba(40, 167, 69, 0.95) 0%, rgba(40, 167, 69, 0.9) 100%);
                     backdrop-filter: blur(10px);
                     border: 1px solid rgba(40, 167, 69, 0.5);
                     border-radius: 12px;
                     padding: 16px 24px;
                     box-shadow: 0 8px 32px rgba(40, 167, 69, 0.3);
                     color: white;
                     font-weight: 500;
                     animation: successSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                 ">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 18px;">✅</span>
                    <span>{message}</span>
                </div>
            </div>
            
            <style>
                @keyframes successSlideIn {{
                    from {{
                        transform: translateX(-50%) translateY(-20px);
                        opacity: 0;
                        scale: 0.8;
                    }}
                    to {{
                        transform: translateX(-50%) translateY(0);
                        opacity: 1;
                        scale: 1;
                    }}
                }}
                
                .sleek-success-feedback {{
                    animation: successSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                }}
            </style>
            
            <script>
                setTimeout(() => {{
                    const element = document.querySelector('.sleek-success-feedback');
                    if (element) {{
                        element.style.animation = 'successSlideOut 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                        setTimeout(() => element.remove(), 300);
                    }}
                }}, {int(duration * 1000)});
                
                @keyframes successSlideOut {{
                    from {{
                        transform: translateX(-50%) translateY(0);
                        opacity: 1;
                        scale: 1;
                    }}
                    to {{
                        transform: translateX(-50%) translateY(-20px);
                        opacity: 0;
                        scale: 0.8;
                    }}
                }}
            </script>
            """,
            unsafe_allow_html=True,
        )

    def show_error_feedback(
        self, message: str, duration: float = 5.0, auto_dismiss: bool = True
    ) -> None:
        """Show sleek error feedback that auto-dismisses"""
        st.markdown(
            f"""
            <div class="sleek-error-feedback" 
                 style="
                     position: fixed;
                     top: 20px;
                     left: 50%;
                     transform: translateX(-50%);
                     z-index: 1000;
                     background: linear-gradient(135deg, rgba(220, 53, 69, 0.95) 0%, rgba(220, 53, 69, 0.9) 100%);
                     backdrop-filter: blur(10px);
                     border: 1px solid rgba(220, 53, 69, 0.5);
                     border-radius: 12px;
                     padding: 16px 24px;
                     box-shadow: 0 8px 32px rgba(220, 53, 69, 0.3);
                     color: white;
                     font-weight: 500;
                     animation: errorShakeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                 ">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 18px;">❌</span>
                    <span>{message}</span>
                </div>
            </div>
            
            <style>
                @keyframes errorShakeIn {{
                    0% {{
                        transform: translateX(-50%) translateY(-20px);
                        opacity: 0;
                        scale: 0.8;
                    }}
                    50% {{
                        transform: translateX(-50%) translateY(0);
                        opacity: 1;
                        scale: 1.05;
                    }}
                    100% {{
                        transform: translateX(-50%) translateY(0);
                        opacity: 1;
                        scale: 1;
                    }}
                }}
                
                .sleek-error-feedback {{
                    animation: errorShakeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                }}
            </style>
            
            <script>
                setTimeout(() => {{
                    const element = document.querySelector('.sleek-error-feedback');
                    if (element) {{
                        element.style.animation = 'errorSlideOut 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                        setTimeout(() => element.remove(), 300);
                    }}
                }}, {int(duration * 1000)});
                
                @keyframes errorSlideOut {{
                    from {{
                        transform: translateX(-50%) translateY(0);
                        opacity: 1;
                        scale: 1;
                    }}
                    to {{
                        transform: translateX(-50%) translateY(-20px);
                        opacity: 0;
                        scale: 0.8;
                    }}
                }}
            </script>
            """,
            unsafe_allow_html=True,
        )

    def show_operation_feedback(
        self, operation: str, success: bool = True, details: Optional[str] = None
    ) -> None:
        """Show operation feedback with sleek styling"""
        if success:
            message = f"✅ {operation} completed successfully"
            if details:
                message += f" - {details}"
            self.show_success_feedback(message)
        else:
            message = f"❌ {operation} failed"
            if details:
                message += f" - {details}"
            self.show_error_feedback(message)

    def clear_all_loading(self) -> None:
        """Clear all loading indicators"""
        st.session_state.loading_states = {}
