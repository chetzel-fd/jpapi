#!/usr/bin/env python3
"""
JAMF Framework Analytics Application
Integrated analytics app for the JAMF Enterprise Framework
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..analytics import ComprehensiveCollector, JSONAnalyticsEngine
from ..jpapi_framework import AppMetadata, JPAPIApplication


class AnalyticsApp(JPAPIApplication):
    """
    Framework Analytics Application

    Provides high-performance analytics using JSON export data
    with full framework integration
    """

    def __init__(self, framework, tenant=None):
        super().__init__(framework, tenant)

        # Initialize analytics engine with framework integration
        self.analytics_engine = JSONAnalyticsEngine(
            framework=framework,
            export_dir="tmp/exports",
            cache_dir="tmp/cache/analytics",
        )

        # Initialize comprehensive collector (lazy loading)
        self._comprehensive_collector = None

        # FastAPI app for analytics API
        self.api_app = FastAPI(
            title="JAMF Framework Analytics API",
            description="High-performance analytics using JSON export data",
            version="2.0.0",
        )

        # Add CORS middleware
        self.api_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup API routes
        self._setup_routes()

        self.logger.info("🚀 Analytics App initialized")
        self.logger.info(f"   📊 Analytics engine: ready")
        self.logger.info(f"   🌡️ Adaptive caching: enabled")

    def get_metadata(self) -> AppMetadata:
        """Return application metadata"""
        return AppMetadata(
            id="analytics",
            name="JAMF Analytics Engine",
            description="High-performance analytics using JSON export data with adaptive caching",
            version="2.0.0",
            category="Analytics",
            icon="📊",
            entry_point=self.launch,
            permissions=["analytics.read", "analytics.admin", "cache.manage"],
            multi_tenant=True,
            real_time=True,
        )

    def initialize(self) -> bool:
        """Initialize the analytics application"""
        try:
            # Analytics engine is already initialized in __init__
            self.logger.info("Analytics app initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize analytics app: {e}")
            return False

    def launch(self, **kwargs) -> Any:
        """Launch the analytics application"""
        port = kwargs.get("port", 8901)
        host = kwargs.get("host", "0.0.0.0")
        return self.start(port, host)

    def _setup_routes(self):
        """Setup FastAPI routes for analytics"""

        @self.api_app.get("/")
        async def root():
            return {
                "message": "JAMF Framework Analytics API",
                "version": "2.0.0",
                "description": "High-performance analytics using JSON export data",
                "framework_integrated": True,
                "endpoints": {
                    "health": "/api/health",
                    "stats": "/api/stats",
                    "objects": "/api/objects/{type}",
                    "relationships": "/api/relationships/{type}/{id}",
                    "scan": "/api/scan",
                    "adaptive_stats": "/api/adaptive/stats",
                    "force_sync": "/api/adaptive/sync/{type}",
                    "populate_real_data": "/api/adaptive/populate",
                    "comprehensive_status": "/api/comprehensive/status",
                    "start_comprehensive": "/api/comprehensive/start",
                    "jpapi_status": "/api/jpapi/status",
                    "jpapi_sync": "/api/jpapi/sync",
                    "jpapi_cache": "/api/jpapi/cache/{action}",
                },
                "features": [
                    "Framework integration with unified auth",
                    "Adaptive cache system with temperature-based sync",
                    "Real JAMF data population",
                    "Intelligent access pattern learning",
                    "Background sync scheduling",
                    "Zero interference with existing systems",
                ],
            }

        @self.api_app.get("/api/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "analytics_engine": "operational",
                "framework_connected": self.framework is not None,
                "export_directory": str(self.analytics_engine.export_dir),
                "cache_items": len(self.analytics_engine._memory_cache),
                "adaptive_cache": self.analytics_engine.adaptive_cache.get_cache_statistics(),
            }

        @self.api_app.get("/api/stats")
        async def get_stats():
            """Get fast statistics from export data"""
            try:
                return self.analytics_engine.get_stats()
            except Exception as e:
                self.logger.error(f"Error getting stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.get("/api/cache/stats")
        async def get_cache_stats():
            """Get cache statistics (compatibility endpoint)"""
            try:
                return self.analytics_engine.get_stats()
            except Exception as e:
                self.logger.error(f"Error getting cache stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.get("/api/objects/{object_type}")
        async def get_objects(
            object_type: str, limit: int = Query(1000, ge=1, le=5000)
        ):
            """Get objects from export data"""
            try:
                return self.analytics_engine.get_objects(object_type, limit)
            except Exception as e:
                self.logger.error(f"Error getting objects: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.get("/api/relationships/{object_type}/{object_id}")
        async def get_relationships(object_type: str, object_id: str):
            """Get relationship data from exports"""
            try:
                return self.analytics_engine.get_relationships(object_type, object_id)
            except Exception as e:
                self.logger.error(f"Error getting relationships: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.post("/api/scan")
        async def scan_exports():
            """Manually trigger export directory scan"""
            try:
                count = self.analytics_engine.scan_exports()
                return {
                    "status": "completed",
                    "processed_files": count,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error scanning exports: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.get("/api/adaptive/stats")
        async def get_adaptive_stats():
            """Get adaptive cache statistics"""
            try:
                cache_stats = (
                    self.analytics_engine.adaptive_cache.get_cache_statistics()
                )
                objects_needing_sync = (
                    self.analytics_engine.adaptive_cache.get_objects_needing_sync()
                )

                return {
                    "cache_statistics": cache_stats,
                    "objects_needing_sync": len(objects_needing_sync),
                    "sync_queue": [
                        {
                            "object_key": obj_key,
                            "temperature": metrics.temperature.value,
                        }
                        for obj_key, metrics in objects_needing_sync[:10]
                    ],
                    "jamf_connected": self.analytics_engine.auth is not None,
                    "sync_errors": self.analytics_engine.sync_errors,
                    "last_sync_times": {
                        k: datetime.fromtimestamp(v).isoformat()
                        for k, v in self.analytics_engine.last_sync_times.items()
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error getting adaptive stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.post("/api/adaptive/sync/{object_type}")
        async def force_sync_object_type(object_type: str):
            """Force sync for a specific object type"""
            try:
                self.analytics_engine._sync_object_type(object_type)
                return {
                    "status": "sync_initiated",
                    "object_type": object_type,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error forcing sync: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.post("/api/adaptive/populate")
        async def populate_real_data():
            """Populate with real JAMF data"""
            try:
                if not self.analytics_engine.auth:
                    raise HTTPException(
                        status_code=503, detail="JAMF authentication not available"
                    )

                # Trigger export of all supported data types
                export_commands = ["groups", "devices", "profiles"]
                results = {}

                for obj_type in export_commands:
                    try:
                        self.analytics_engine._sync_object_type(obj_type)
                        results[obj_type] = "success"
                    except Exception as e:
                        results[obj_type] = f"error: {str(e)}"

                return {
                    "status": "population_initiated",
                    "results": results,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error populating data: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # Framework integration endpoints
        @self.api_app.get("/api/framework/status")
        async def get_framework_status():
            """Get framework integration status"""
            try:
                framework_status = (
                    self.framework.get_status() if self.framework else None
                )

                return {
                    "framework_connected": self.framework is not None,
                    "framework_status": framework_status,
                    "app_status": self.get_status(),
                    "analytics_ready": True,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error getting framework status: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # Comprehensive Collection endpoints
        @self.api_app.get("/api/comprehensive/status")
        async def get_comprehensive_status():
            """Get comprehensive collection status"""
            try:
                if not self._comprehensive_collector:
                    return {
                        "status": "not_initialized",
                        "message": "Comprehensive collector not initialized",
                        "total_objects": 0,
                        "completion_rate": 0,
                    }

                status = self._comprehensive_collector.get_collection_status()
                return {
                    "status": "initialized",
                    "collection_status": status,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error getting comprehensive status: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.post("/api/comprehensive/start")
        async def start_comprehensive_collection(
            object_types: Optional[List[str]] = None, max_workers: int = 4
        ):
            """Start comprehensive data collection"""
            try:
                if not self.analytics_engine.auth:
                    raise HTTPException(
                        status_code=503, detail="JAMF authentication not available"
                    )

                # Initialize collector if needed
                if not self._comprehensive_collector:
                    self._comprehensive_collector = ComprehensiveCollector(
                        auth=self.analytics_engine.auth,
                        analytics_engine=self.analytics_engine,
                        cache_dir="tmp/cache/comprehensive",
                    )

                # Default object types
                if object_types is None:
                    object_types = ["policies", "groups", "profiles", "devices"]

                # Start collection in background
                import threading

                def run_collection():
                    try:
                        self._comprehensive_collector.start_comprehensive_collection(
                            object_types=object_types, max_workers=max_workers
                        )
                    except Exception as e:
                        self.logger.error(f"Comprehensive collection error: {e}")

                collection_thread = threading.Thread(target=run_collection, daemon=True)
                collection_thread.start()

                return {
                    "status": "started",
                    "object_types": object_types,
                    "max_workers": max_workers,
                    "message": "Comprehensive collection started in background",
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                self.logger.error(f"Error starting comprehensive collection: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # JPAPI Integration endpoints
        @self.api_app.get("/api/jpapi/status")
        async def get_jpapi_status():
            """Get jpapi integration status"""
            try:
                integration_status = (
                    self.analytics_engine.jpapi_integration.get_integration_status()
                )
                return {
                    "status": "success",
                    "integration_status": integration_status,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error getting jpapi status: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.post("/api/jpapi/sync")
        async def sync_with_jpapi():
            """Sync analytics with jpapi exports"""
            try:
                sync_results = (
                    self.analytics_engine.jpapi_integration.sync_with_jpapi_exports()
                )
                return {
                    "status": "success",
                    "sync_results": sync_results,
                    "message": "Sync with jpapi completed",
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error syncing with jpapi: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.post("/api/jpapi/cache/{action}")
        async def manage_jpapi_cache(action: str):
            """Manage jpapi and analytics caches"""
            try:
                if action not in ["clear", "sync", "status"]:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid action: {action}"
                    )

                cache_results = (
                    self.analytics_engine.jpapi_integration.cache_management_bridge(
                        action
                    )
                )
                return {
                    "status": "success",
                    "action": action,
                    "results": cache_results,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error managing cache: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.api_app.post("/api/jpapi/launch/{interface}")
        async def launch_jpapi_interface(interface: str):
            """Launch jpapi GUI interface"""
            try:
                success = (
                    self.analytics_engine.jpapi_integration.launch_jpapi_gui(
                        interface
                    )
                )

                if success:
                    return {
                        "status": "success",
                        "interface": interface,
                        "message": f"JPAPI {interface} interface launched",
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to launch {interface} interface",
                    )

            except Exception as e:
                self.logger.error(f"Error launching jpapi interface: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def start(self, port: int = 8901, host: str = "0.0.0.0"):
        """Start the analytics app"""
        self.logger.info(f"🚀 Starting Analytics App on {host}:{port}")

        # Scan exports on startup
        self.analytics_engine.scan_exports()

        # Start the FastAPI server
        uvicorn.run(self.api_app, host=host, port=port, log_level="info")

    def stop(self):
        """Stop the analytics app"""
        self.logger.info("🛑 Stopping Analytics App")
        # Cleanup if needed

    def get_status(self) -> Dict[str, Any]:
        """Get app status"""
        return {
            "name": self.name,
            "status": "running",
            "analytics_engine": "operational",
            "adaptive_cache": self.analytics_engine.adaptive_cache.get_cache_statistics(),
            "last_scan": datetime.now().isoformat(),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get app metrics"""
        cache_stats = self.analytics_engine.adaptive_cache.get_cache_statistics()

        return {
            "total_objects_tracked": cache_stats["total_objects"],
            "objects_needing_sync": cache_stats["objects_needing_sync"],
            "temperature_distribution": cache_stats["temperature_distribution"],
            "cache_size_bytes": cache_stats["database_size"],
            "memory_cache_items": len(self.analytics_engine._memory_cache),
            "sync_errors": len(self.analytics_engine.sync_errors),
        }


# Factory function for framework registration
def create_analytics_app(framework):
    """Create and return an analytics app instance"""
    return AnalyticsApp(framework)
