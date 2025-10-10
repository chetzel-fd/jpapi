#!/usr/bin/env python3
"""
JAMF Framework Analytics Frontend
Dash frontend integrated with the JAMF Enterprise Framework
"""
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import dash
import requests
from dash import Input, Output, State, callback, dcc, html

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..jpapi_framework import AppMetadata, JPAPIApplication


class AnalyticsFrontend(JPAPIApplication):
    """
    Framework Analytics Frontend Application

    Provides a beautiful Dash interface for analytics data
    with full framework integration
    """

    def __init__(self, framework, tenant=None):
        super().__init__(framework, tenant)

        # Backend configuration
        self.analytics_backend_url = "http://localhost:8901"
        self.fallback_backend_url = "http://localhost:8900"

        # Collection status tracking
        self.collection_status = {
            "is_running": False,
            "phase": "",
            "percentage": 0,
            "message": "",
            "last_update": 0,
        }
        self.status_lock = threading.Lock()

        # Initialize Dash app
        self.dash_app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.dash_app.title = "JAMF Framework Analytics"

        # Setup styling and layout
        self._setup_styling()
        self._setup_layout()
        self._setup_callbacks()

        self.logger.info("🚀 Analytics Frontend initialized")
        self.logger.info(f"   📊 Analytics backend: {self.analytics_backend_url}")
        self.logger.info(f"   🎨 Dash app: ready")

    def get_metadata(self) -> AppMetadata:
        """Return application metadata"""
        return AppMetadata(
            id="analytics_frontend",
            name="JAMF Analytics Dashboard",
            description="Beautiful Dash frontend for JAMF analytics with framework integration",
            version="2.0.0",
            category="Analytics",
            icon="📈",
            entry_point=self.launch,
            permissions=["analytics.view", "dashboard.access"],
            multi_tenant=True,
            real_time=True,
        )

    def initialize(self) -> bool:
        """Initialize the analytics frontend application"""
        try:
            # Dash app is already initialized in __init__
            self.logger.info("Analytics frontend initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize analytics frontend: {e}")
            return False

    def launch(self, **kwargs) -> Any:
        """Launch the analytics frontend application"""
        port = kwargs.get("port", 8902)
        host = kwargs.get("host", "0.0.0.0")
        debug = kwargs.get("debug", False)
        return self.start(port, host, debug)

    def _setup_styling(self):
        """Setup Apple-style CSS and styling"""
        self.dash_app.index_string = """
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    /* Apple System Fonts */
                    body, * {
                        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', sans-serif !important;
                        -webkit-font-smoothing: antialiased;
                        -moz-osx-font-smoothing: grayscale;
                    }
                    
                    /* Dark Apple Theme */
                    body {
                        background: #000000 !important;
                        color: #FFFFFF !important;
                        margin: 0;
                        padding: 0;
                    }
                    
                    /* Main container */
                    #react-entry-point {
                        background: #000000;
                        min-height: 100vh;
                        color: #FFFFFF;
                    }
                    
                    /* Stat cards */
                    .stat-card {
                        background: #1C1C1E;
                        border: 1px solid #38383A;
                        border-radius: 8px;
                        padding: 20px;
                        text-align: center;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                        position: relative;
                        overflow: hidden;
                        transition: all 0.3s ease;
                        cursor: pointer;
                        color: #FFFFFF;
                        min-height: 120px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    }
                    
                    .stat-card:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
                        border-color: #48484A;
                    }
                    
                    .stat-number {
                        font-size: 32px;
                        font-weight: 700;
                        color: #FFFFFF;
                        margin-bottom: 8px;
                        line-height: 1.1;
                    }
                    
                    .stat-label {
                        font-size: 14px;
                        color: #8E8E93;
                        font-weight: 500;
                    }
                    
                    /* Framework integration styling */
                    .framework-header {
                        background: linear-gradient(135deg, #1C1C1E, #2C2C2E);
                        padding: 20px;
                        border-bottom: 1px solid #38383A;
                    }
                    
                    .framework-badge {
                        background: #007AFF;
                        color: white;
                        padding: 4px 12px;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: 600;
                        margin-left: 10px;
                    }
                    
                    /* Status indicators */
                    .status-connected {
                        color: #34C759;
                        font-weight: 600;
                    }
                    
                    .status-error {
                        color: #FF3B30;
                        font-weight: 600;
                    }
                    
                    .status-warning {
                        color: #FF9F0A;
                        font-weight: 600;
                    }
                    
                    /* Temperature indicators */
                    .temp-blazing { color: #FF3B30; }
                    .temp-hot { color: #FF9F0A; }
                    .temp-warm { color: #FFCC02; }
                    .temp-cool { color: #34C759; }
                    .temp-cold { color: #007AFF; }
                    .temp-frozen { color: #8E8E93; }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        """

    def _setup_layout(self):
        """Setup Dash app layout"""
        self.dash_app.layout = html.Div(
            [
                # Framework Header
                html.Div(
                    [
                        html.Div(
                            [
                                html.H1(
                                    [
                                        "📊 JAMF Framework Analytics",
                                        html.Span(
                                            "FRAMEWORK", className="framework-badge"
                                        ),
                                    ],
                                    style={
                                        "color": "#FFFFFF",
                                        "margin": "0",
                                        "display": "flex",
                                        "align-items": "center",
                                    },
                                ),
                                html.P(
                                    "High-performance analytics with framework integration",
                                    style={"color": "#8E8E93", "margin": "10px 0 0 0"},
                                ),
                            ]
                        ),
                        html.Div(id="framework-status", style={"margin-top": "15px"}),
                    ],
                    className="framework-header",
                ),
                # Main content
                html.Div(id="main-content", style={"padding": "24px"}),
                # Hidden stores
                dcc.Store(id="analytics-data", data={}),
                dcc.Store(id="framework-state", data={}),
                # Auto-refresh interval
                dcc.Interval(id="interval-component", interval=30000, n_intervals=0),
            ],
            style={"background": "#000000", "min-height": "100vh", "color": "#FFFFFF"},
        )

    def _setup_callbacks(self):
        """Setup Dash callbacks"""

        @self.dash_app.callback(
            [Output("framework-state", "data"), Output("framework-status", "children")],
            [Input("interval-component", "n_intervals")],
        )
        def update_framework_status(n_intervals):
            """Update framework connection status"""
            try:
                # Test analytics backend
                response = requests.get(
                    f"{self.analytics_backend_url}/api/framework/status", timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    status_element = html.Div(
                        [
                            html.Span(
                                "✅ Framework Connected", className="status-connected"
                            ),
                            html.Span(
                                f" • Analytics Ready • {data.get('analytics_ready', False)}",
                                style={"color": "#8E8E93", "margin-left": "10px"},
                            ),
                        ]
                    )
                    return data, status_element
                else:
                    raise Exception(f"HTTP {response.status_code}")

            except Exception as e:
                error_element = html.Div(
                    [
                        html.Span(
                            "❌ Framework Disconnected", className="status-error"
                        ),
                        html.Span(
                            f" • {str(e)[:50]}",
                            style={"color": "#8E8E93", "margin-left": "10px"},
                        ),
                    ]
                )
                return {}, error_element

        @self.dash_app.callback(
            [Output("analytics-data", "data"), Output("main-content", "children")],
            [
                Input("framework-state", "data"),
                Input("interval-component", "n_intervals"),
            ],
        )
        def update_analytics_content(framework_state, n_intervals):
            """Update main analytics content"""
            try:
                # Get analytics data
                start_time = time.time()
                response = requests.get(
                    f"{self.analytics_backend_url}/api/stats", timeout=10
                )
                load_time = time.time() - start_time

                if response.status_code != 200:
                    return {}, self._create_error_display(
                        f"Analytics error: HTTP {response.status_code}"
                    )

                stats_data = response.json()

                # Create dashboard
                dashboard = self._create_framework_dashboard(
                    stats_data, load_time, framework_state
                )

                return stats_data, dashboard

            except Exception as e:
                return {}, self._create_error_display(f"Connection error: {str(e)}")

        @self.dash_app.callback(
            Output("start-collection-btn", "children"),
            [Input("start-collection-btn", "n_clicks")],
            prevent_initial_call=True,
        )
        def start_comprehensive_collection(n_clicks):
            """Start comprehensive collection via API"""
            if n_clicks:
                try:
                    # Start collection
                    response = requests.post(
                        f"{self.analytics_backend_url}/api/comprehensive/start",
                        json={"max_workers": 4},
                        timeout=10,
                    )

                    if response.status_code == 200:
                        return "🔄 Collection Started..."
                    else:
                        return "❌ Start Failed"

                except Exception as e:
                    return "❌ Error"

            return "🚀 Start Collection"

    def _create_framework_dashboard(self, stats_data, load_time, framework_state):
        """Create the main framework analytics dashboard"""

        # Extract stats
        groups_count = stats_data.get("groups", 0)
        policies_count = stats_data.get("policies", 0)
        profiles_count = stats_data.get("profiles", 0)
        devices_count = stats_data.get("devices", 0)

        latest_export = stats_data.get("latest_export", "Unknown")
        total_files = stats_data.get("total_export_files", 0)
        adaptive_cache = stats_data.get("adaptive_cache", {})

        return html.Div(
            [
                # Performance metrics
                html.Div(
                    [
                        html.H2("⚡ Framework Analytics Performance"),
                        html.Div(
                            [
                                html.Span(
                                    f"🚀 Load time: {load_time:.3f}s • ",
                                    style={"color": "#34C759"},
                                ),
                                html.Span(
                                    f"📁 {total_files} export files • ",
                                    style={"color": "#8E8E93"},
                                ),
                                html.Span(
                                    f"🌡️ {adaptive_cache.get('total_objects', 0)} tracked objects • ",
                                    style={"color": "#007AFF"},
                                ),
                                html.Span(
                                    f"🕒 Latest: {latest_export[:19] if latest_export != 'Unknown' else 'Unknown'}",
                                    style={"color": "#8E8E93"},
                                ),
                            ],
                            style={"margin-bottom": "24px"},
                        ),
                    ]
                ),
                # Stats cards
                html.Div(
                    [
                        self._create_stat_card(
                            "Computer Groups", groups_count, "groups", "#AF52DE"
                        ),
                        self._create_stat_card(
                            "Policies", policies_count, "policies", "#007AFF"
                        ),
                        self._create_stat_card(
                            "Profiles", profiles_count, "profiles", "#FF9F0A"
                        ),
                        self._create_stat_card(
                            "Devices", devices_count, "devices", "#34C759"
                        ),
                    ],
                    style={
                        "display": "grid",
                        "grid-template-columns": "repeat(auto-fit, minmax(200px, 1fr))",
                        "gap": "16px",
                        "margin-bottom": "32px",
                    },
                ),
                # Comprehensive collection panel
                self._create_comprehensive_collection_panel(),
                # Adaptive cache insights
                self._create_adaptive_cache_panel(adaptive_cache),
                # Framework integration benefits
                self._create_framework_benefits_panel(framework_state),
            ]
        )

    def _create_comprehensive_collection_panel(self):
        """Create comprehensive collection control panel"""
        try:
            # Get collection status
            response = requests.get(
                f"{self.analytics_backend_url}/api/comprehensive/status", timeout=5
            )

            if response.status_code == 200:
                status_data = response.json()
                collection_status = status_data.get("collection_status", {})

                # Status indicators
                total_objects = collection_status.get("total_objects", 0)
                completion_rate = collection_status.get("completion_rate", 0)
                status_counts = collection_status.get("status_counts", {})

                # Create status display
                if total_objects > 0:
                    status_text = f"{completion_rate:.1f}% Complete"
                    status_color = (
                        "#34C759"
                        if completion_rate > 80
                        else "#FF9F0A" if completion_rate > 40 else "#FF453A"
                    )
                else:
                    status_text = "Not Started"
                    status_color = "#8E8E93"

                return html.Div(
                    [
                        html.H3(
                            "🎯 Comprehensive Data Collection",
                            style={"color": "#FFFFFF", "margin-bottom": "16px"},
                        ),
                        # Status row
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            "Status: ", style={"color": "#8E8E93"}
                                        ),
                                        html.Span(
                                            status_text,
                                            style={
                                                "color": status_color,
                                                "font-weight": "bold",
                                            },
                                        ),
                                    ],
                                    style={"margin-bottom": "8px"},
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            f"Total Objects: {total_objects} • ",
                                            style={"color": "#8E8E93"},
                                        ),
                                        html.Span(
                                            f"Completed: {status_counts.get('completed', 0)} • ",
                                            style={"color": "#34C759"},
                                        ),
                                        html.Span(
                                            f"Failed: {status_counts.get('failed', 0)}",
                                            style={"color": "#FF453A"},
                                        ),
                                    ],
                                    style={"margin-bottom": "16px"},
                                ),
                            ]
                        ),
                        # Progress bar
                        html.Div(
                            [
                                html.Div(
                                    style={
                                        "width": f"{completion_rate}%",
                                        "height": "8px",
                                        "background": status_color,
                                        "border-radius": "4px",
                                        "transition": "width 0.3s ease",
                                    }
                                )
                            ],
                            style={
                                "width": "100%",
                                "height": "8px",
                                "background": "#38383A",
                                "border-radius": "4px",
                                "margin-bottom": "16px",
                            },
                        ),
                        # Control buttons
                        html.Div(
                            [
                                html.Button(
                                    "🚀 Start Collection",
                                    id="start-collection-btn",
                                    style={
                                        "background": "#007AFF",
                                        "color": "white",
                                        "border": "none",
                                        "padding": "8px 16px",
                                        "border-radius": "6px",
                                        "margin-right": "8px",
                                        "cursor": "pointer",
                                    },
                                ),
                                html.Button(
                                    "📊 View Status",
                                    id="status-collection-btn",
                                    style={
                                        "background": "#8E8E93",
                                        "color": "white",
                                        "border": "none",
                                        "padding": "8px 16px",
                                        "border-radius": "6px",
                                        "cursor": "pointer",
                                    },
                                ),
                            ]
                        ),
                        # Collection info
                        html.Div(
                            [
                                html.P(
                                    "☕ Caffeinate keeps system awake during collection",
                                    style={
                                        "color": "#8E8E93",
                                        "margin": "8px 0 4px 0",
                                        "font-size": "14px",
                                    },
                                ),
                                html.P(
                                    "⚡ Smart prioritization: hot objects collected first",
                                    style={
                                        "color": "#8E8E93",
                                        "margin": "4px 0",
                                        "font-size": "14px",
                                    },
                                ),
                                html.P(
                                    "🔄 Resumable progress with automatic retry",
                                    style={
                                        "color": "#8E8E93",
                                        "margin": "4px 0 0 0",
                                        "font-size": "14px",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "background": "#1C1C1E",
                        "border": "1px solid #38383A",
                        "border-left": "4px solid #007AFF",
                        "border-radius": "8px",
                        "padding": "20px",
                        "margin-bottom": "24px",
                    },
                )

            else:
                return html.Div(
                    [
                        html.H3(
                            "🎯 Comprehensive Data Collection",
                            style={"color": "#FFFFFF"},
                        ),
                        html.P(
                            "Collection service not available",
                            style={"color": "#FF453A"},
                        ),
                    ],
                    style={
                        "background": "#1C1C1E",
                        "border": "1px solid #38383A",
                        "border-radius": "8px",
                        "padding": "20px",
                        "margin-bottom": "24px",
                    },
                )

        except Exception as e:
            return html.Div(
                [
                    html.H3(
                        "🎯 Comprehensive Data Collection", style={"color": "#FFFFFF"}
                    ),
                    html.P(
                        f"Error loading collection status: {str(e)}",
                        style={"color": "#FF453A"},
                    ),
                ],
                style={
                    "background": "#1C1C1E",
                    "border": "1px solid #38383A",
                    "border-radius": "8px",
                    "padding": "20px",
                    "margin-bottom": "24px",
                },
            )

    def _create_stat_card(self, title, count, card_type, color):
        """Create a stat card"""
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(str(count), className="stat-number"),
                        html.Div(title, className="stat-label"),
                    ]
                )
            ],
            className=f"stat-card {card_type}",
            style={
                "background": "#1C1C1E",
                "border": "1px solid #38383A",
                "border-left": f"4px solid {color}",
                "border-radius": "8px",
                "padding": "20px",
                "text-align": "center",
                "min-height": "120px",
                "display": "flex",
                "flex-direction": "column",
                "justify-content": "center",
            },
        )

    def _create_adaptive_cache_panel(self, cache_data):
        """Create adaptive cache insights panel"""
        temp_dist = cache_data.get("temperature_distribution", {})

        return html.Div(
            [
                html.H3("🌡️ Adaptive Cache Intelligence", style={"color": "#FFFFFF"}),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    "Temperature Distribution",
                                    style={"color": "#34C759"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span(
                                                    "🔥 Blazing: ",
                                                    className="temp-blazing",
                                                ),
                                                html.Span(
                                                    str(temp_dist.get("blazing", 0))
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Span(
                                                    "🌶️ Hot: ", className="temp-hot"
                                                ),
                                                html.Span(str(temp_dist.get("hot", 0))),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Span(
                                                    "☀️ Warm: ", className="temp-warm"
                                                ),
                                                html.Span(
                                                    str(temp_dist.get("warm", 0))
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Span(
                                                    "🌤️ Cool: ", className="temp-cool"
                                                ),
                                                html.Span(
                                                    str(temp_dist.get("cool", 0))
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Span(
                                                    "❄️ Cold: ", className="temp-cold"
                                                ),
                                                html.Span(
                                                    str(temp_dist.get("cold", 0))
                                                ),
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.Span(
                                                    "🧊 Frozen: ",
                                                    className="temp-frozen",
                                                ),
                                                html.Span(
                                                    str(temp_dist.get("frozen", 0))
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                            ],
                            style={"flex": "1", "margin-right": "20px"},
                        ),
                        html.Div(
                            [
                                html.H4("Smart Sync", style={"color": "#007AFF"}),
                                html.Div(
                                    [
                                        html.Div(
                                            f"Objects needing sync: {cache_data.get('objects_needing_sync', 0)}"
                                        ),
                                        html.Div(
                                            f"Total tracked: {cache_data.get('total_objects', 0)}"
                                        ),
                                        html.Div("Automatic background sync enabled"),
                                        html.Div("Temperature-based scheduling"),
                                    ]
                                ),
                            ],
                            style={"flex": "1"},
                        ),
                    ],
                    style={"display": "flex"},
                ),
            ],
            style={
                "background": "#1C1C1E",
                "border-radius": "12px",
                "padding": "20px",
                "border": "1px solid #38383A",
                "margin-bottom": "32px",
            },
        )

    def _create_framework_benefits_panel(self, framework_state):
        """Create framework integration benefits panel"""
        return html.Div(
            [
                html.H3(
                    "🏢 Framework Integration Benefits", style={"color": "#FFFFFF"}
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    "🔐 Unified Security", style={"color": "#34C759"}
                                ),
                                html.Ul(
                                    [
                                        html.Li("Framework authentication"),
                                        html.Li("Multi-tenant support"),
                                        html.Li("Centralized access control"),
                                        html.Li("Audit logging"),
                                    ]
                                ),
                            ],
                            style={"flex": "1", "margin-right": "20px"},
                        ),
                        html.Div(
                            [
                                html.H4(
                                    "⚡ Enhanced Performance",
                                    style={"color": "#007AFF"},
                                ),
                                html.Ul(
                                    [
                                        html.Li("Shared cache infrastructure"),
                                        html.Li("Optimized resource usage"),
                                        html.Li("Background processing"),
                                        html.Li("Smart data routing"),
                                    ]
                                ),
                            ],
                            style={"flex": "1", "margin-right": "20px"},
                        ),
                        html.Div(
                            [
                                html.H4("🔧 Management", style={"color": "#FF9F0A"}),
                                html.Ul(
                                    [
                                        html.Li("Centralized configuration"),
                                        html.Li("Health monitoring"),
                                        html.Li("Automated scaling"),
                                        html.Li("Service discovery"),
                                    ]
                                ),
                            ],
                            style={"flex": "1"},
                        ),
                    ],
                    style={"display": "flex"},
                ),
            ],
            style={
                "background": "#1C1C1E",
                "border-radius": "12px",
                "padding": "20px",
                "border": "1px solid #38383A",
            },
        )

    def _create_error_display(self, error_message):
        """Create error display"""
        return html.Div(
            [
                html.H2("❌ Connection Error"),
                html.P(error_message, style={"color": "#FF3B30"}),
                html.Div(
                    [
                        html.H3("🔧 Troubleshooting", style={"color": "#FFFFFF"}),
                        html.Ul(
                            [
                                html.Li("Ensure the framework is running"),
                                html.Li("Check analytics app status"),
                                html.Li("Verify network connectivity"),
                                html.Li("Check framework logs"),
                            ]
                        ),
                    ],
                    style={
                        "background": "#1C1C1E",
                        "border-radius": "12px",
                        "padding": "20px",
                        "border": "1px solid #38383A",
                        "margin-top": "20px",
                    },
                ),
            ],
            style={"padding": "40px", "text-align": "center"},
        )

    def start(self, port: int = 8902, host: str = "0.0.0.0", debug: bool = False):
        """Start the analytics frontend"""
        self.logger.info(f"🚀 Starting Analytics Frontend on {host}:{port}")
        self.dash_app.run(debug=debug, host=host, port=port)

    def stop(self):
        """Stop the analytics frontend"""
        self.logger.info("🛑 Stopping Analytics Frontend")

    def get_status(self) -> Dict[str, Any]:
        """Get app status"""
        return {
            "name": self.name,
            "status": "running",
            "frontend_type": "dash",
            "backend_url": self.analytics_backend_url,
        }


# Factory function for framework registration
def create_analytics_frontend(framework):
    """Create and return an analytics frontend instance"""
    return AnalyticsFrontend(framework)
