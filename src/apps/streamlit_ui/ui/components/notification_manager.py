"""
Sleek notification manager with auto-dismiss and FAB integration
"""

import streamlit as st
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class NotificationManager:
    """Manages sleek, auto-dismissing notifications with FAB integration"""

    def __init__(self):
        if "notifications" not in st.session_state:
            st.session_state.notifications = []
        if "notification_settings" not in st.session_state:
            st.session_state.notification_settings = {
                "auto_dismiss_delay": 3.0,  # seconds
                "max_notifications": 5,
                "show_in_fab": True,
                "enable_sounds": False,
            }

    def add_notification(
        self,
        message: str,
        notification_type: str = "info",
        auto_dismiss: bool = True,
        duration: Optional[float] = None,
    ) -> None:
        """Add a sleek notification that auto-dismisses"""
        notification = {
            "id": len(st.session_state.notifications),
            "message": message,
            "type": notification_type,
            "timestamp": datetime.now(),
            "auto_dismiss": auto_dismiss,
            "duration": duration
            or st.session_state.notification_settings["auto_dismiss_delay"],
            "dismissed": False,
        }

        st.session_state.notifications.append(notification)

        # Keep only recent notifications
        max_notifications = st.session_state.notification_settings["max_notifications"]
        if len(st.session_state.notifications) > max_notifications:
            st.session_state.notifications = st.session_state.notifications[
                -max_notifications:
            ]

    def get_active_notifications(self) -> List[Dict]:
        """Get notifications that haven't been dismissed"""
        now = datetime.now()
        active_notifications = []

        for notification in st.session_state.notifications:
            if notification["dismissed"]:
                continue

            # Auto-dismiss expired notifications
            if notification["auto_dismiss"]:
                elapsed = (now - notification["timestamp"]).total_seconds()
                if elapsed > notification["duration"]:
                    notification["dismissed"] = True
                    continue

            active_notifications.append(notification)

        return active_notifications

    def dismiss_notification(self, notification_id: int) -> None:
        """Manually dismiss a notification"""
        for notification in st.session_state.notifications:
            if notification["id"] == notification_id:
                notification["dismissed"] = True
                break

    def clear_all_notifications(self) -> None:
        """Clear all notifications"""
        st.session_state.notifications = []

    def render_sleek_notifications(self) -> None:
        """Render sleek, auto-dismissing notifications"""
        active_notifications = self.get_active_notifications()

        if not active_notifications:
            return

        # Render notifications with sleek styling
        for notification in active_notifications:
            self._render_single_notification(notification)

    def _render_single_notification(self, notification: Dict) -> None:
        """Render a single sleek notification"""
        notification_type = notification["type"]
        message = notification["message"]
        notification_id = notification["id"]

        # Determine styling based on type
        if notification_type == "success":
            icon = "✅"
            bg_color = "rgba(40, 167, 69, 0.1)"
            border_color = "#28a745"
            text_color = "#28a745"
        elif notification_type == "warning":
            icon = "⚠️"
            bg_color = "rgba(255, 193, 7, 0.1)"
            border_color = "#ffc107"
            text_color = "#ffc107"
        elif notification_type == "error":
            icon = "❌"
            bg_color = "rgba(220, 53, 69, 0.1)"
            border_color = "#dc3545"
            text_color = "#dc3545"
        else:  # info
            icon = "ℹ️"
            bg_color = "rgba(51, 147, 255, 0.1)"
            border_color = "#3393ff"
            text_color = "#3393ff"

        # Calculate remaining time for auto-dismiss
        if notification["auto_dismiss"]:
            elapsed = (datetime.now() - notification["timestamp"]).total_seconds()
            remaining = max(0, notification["duration"] - elapsed)
            progress = min(100, (elapsed / notification["duration"]) * 100)
        else:
            remaining = 0
            progress = 0

        # Render the notification with sleek styling
        st.markdown(
            f"""
            <div class="sleek-notification" 
                 style="
                     background: {bg_color};
                     border: 1px solid {border_color};
                     border-radius: 8px;
                     padding: 12px 16px;
                     margin: 8px 0;
                     position: relative;
                     overflow: hidden;
                     animation: slideIn 0.3s ease-out;
                 ">
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    color: {text_color};
                ">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 16px;">{icon}</span>
                        <span style="font-weight: 500;">{message}</span>
                    </div>
                    <button onclick="dismissNotification({notification_id})" 
                            style="
                                background: none;
                                border: none;
                                color: {text_color};
                                cursor: pointer;
                                font-size: 18px;
                                opacity: 0.7;
                                transition: opacity 0.2s;
                            "
                            onmouseover="this.style.opacity='1'"
                            onmouseout="this.style.opacity='0.7'">
                        ×
                    </button>
                </div>
                {f'''
                <div style="
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    height: 2px;
                    background: {border_color};
                    width: {100 - progress}%;
                    transition: width 0.1s linear;
                "></div>
                ''' if notification["auto_dismiss"] else ""}
            </div>
            
            <style>
                @keyframes slideIn {{
                    from {{
                        transform: translateX(100%);
                        opacity: 0;
                    }}
                    to {{
                        transform: translateX(0);
                        opacity: 1;
                    }}
                }}
                
                @keyframes slideOut {{
                    from {{
                        transform: translateX(0);
                        opacity: 1;
                    }}
                    to {{
                        transform: translateX(100%);
                        opacity: 0;
                    }}
                }}
                
                .sleek-notification.dismissing {{
                    animation: slideOut 0.3s ease-in forwards;
                }}
            </style>
            
            <script>
                function dismissNotification(id) {{
                    // Find and hide the notification
                    const notifications = document.querySelectorAll('.sleek-notification');
                    notifications.forEach(notification => {{
                        if (notification.querySelector('button').onclick.toString().includes(id)) {{
                            notification.classList.add('dismissing');
                            setTimeout(() => notification.remove(), 300);
                        }}
                    }});
                }}
            </script>
            """,
            unsafe_allow_html=True,
        )

    def render_fab_status(self) -> None:
        """Render status information in FAB settings"""
        active_notifications = self.get_active_notifications()
        total_notifications = len(st.session_state.notifications)

        # FAB status content
        st.markdown("### 📊 Status Overview")

        # Quick stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Notifications", len(active_notifications))
        with col2:
            st.metric("Total Notifications", total_notifications)

        # Recent notifications in FAB
        if active_notifications:
            st.markdown("#### 🔔 Recent Activity")
            for notification in active_notifications[-3:]:  # Show last 3
                notification_type = notification["type"]
                message = notification["message"]
                timestamp = notification["timestamp"].strftime("%H:%M:%S")

                if notification_type == "success":
                    st.success(f"✅ {message} ({timestamp})")
                elif notification_type == "warning":
                    st.warning(f"⚠️ {message} ({timestamp})")
                elif notification_type == "error":
                    st.error(f"❌ {message} ({timestamp})")
                else:
                    st.info(f"ℹ️ {message} ({timestamp})")
        else:
            st.info("No active notifications")

        # Notification settings
        st.markdown("#### ⚙️ Notification Settings")

        auto_dismiss = st.checkbox(
            "Auto-dismiss notifications",
            value=st.session_state.notification_settings.get("auto_dismiss", True),
        )

        if auto_dismiss:
            delay = st.slider(
                "Auto-dismiss delay (seconds)",
                min_value=1.0,
                max_value=10.0,
                value=st.session_state.notification_settings["auto_dismiss_delay"],
                step=0.5,
            )
            st.session_state.notification_settings["auto_dismiss_delay"] = delay

        max_notifications = st.slider(
            "Max notifications to keep",
            min_value=3,
            max_value=20,
            value=st.session_state.notification_settings["max_notifications"],
        )
        st.session_state.notification_settings["max_notifications"] = max_notifications

        # Clear notifications button
        if st.button("🗑️ Clear All Notifications", type="secondary"):
            self.clear_all_notifications()
            st.rerun()

    def add_success(self, message: str, auto_dismiss: bool = True) -> None:
        """Add a success notification"""
        self.add_notification(message, "success", auto_dismiss)

    def add_warning(self, message: str, auto_dismiss: bool = True) -> None:
        """Add a warning notification"""
        self.add_notification(message, "warning", auto_dismiss)

    def add_error(self, message: str, auto_dismiss: bool = False) -> None:
        """Add an error notification (doesn't auto-dismiss by default)"""
        self.add_notification(message, "error", auto_dismiss, duration=10.0)

    def add_info(self, message: str, auto_dismiss: bool = True) -> None:
        """Add an info notification"""
        self.add_notification(message, "info", auto_dismiss)
