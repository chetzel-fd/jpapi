#!/usr/bin/env python3
"""
JPAPI Performance Monitor
Tracks the 20% bash / 80% Python split and performance metrics
"""
import time
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

class PerformanceMonitor:
    """Monitor jpapi performance and architecture split"""
    
    def __init__(self, log_file: str = "tmp/performance.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.bash_operations = ['list', 'status']
        self.python_operations = ['export', 'search', 'analyze', 'devices', 'tools', 'launch', 'create', 'move', 'update']
    
    def log_operation(self, command: str, execution_time: float, success: bool):
        """Log an operation with timing"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'execution_time': execution_time,
            'success': success,
            'type': 'bash' if command.split()[0] in self.bash_operations else 'python'
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_performance_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get performance statistics for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        bash_times = []
        python_times = []
        bash_count = 0
        python_count = 0
        total_operations = 0
        successful_operations = 0
        
        if not self.log_file.exists():
            return {'error': 'No performance data available'}
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    
                    if entry_time >= cutoff_date:
                        total_operations += 1
                        if entry['success']:
                            successful_operations += 1
                        
                        if entry['type'] == 'bash':
                            bash_times.append(entry['execution_time'])
                            bash_count += 1
                        else:
                            python_times.append(entry['execution_time'])
                            python_count += 1
                            
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        
        # Calculate statistics
        bash_avg = sum(bash_times) / len(bash_times) if bash_times else 0
        python_avg = sum(python_times) / len(python_times) if python_times else 0
        
        bash_percentage = (bash_count / total_operations * 100) if total_operations > 0 else 0
        python_percentage = (python_count / total_operations * 100) if total_operations > 0 else 0
        
        return {
            'period_days': days,
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'success_rate': (successful_operations / total_operations * 100) if total_operations > 0 else 0,
            'bash': {
                'count': bash_count,
                'percentage': bash_percentage,
                'avg_time': bash_avg,
                'target_percentage': 20
            },
            'python': {
                'count': python_count,
                'percentage': python_percentage,
                'avg_time': python_avg,
                'target_percentage': 80
            },
            'architecture_compliance': {
                'bash_within_target': abs(bash_percentage - 20) <= 5,
                'python_within_target': abs(python_percentage - 80) <= 5,
                'bash_deviation': abs(bash_percentage - 20),
                'python_deviation': abs(python_percentage - 80)
            }
        }
    
    def print_performance_report(self, days: int = 7):
        """Print a formatted performance report"""
        stats = self.get_performance_stats(days)
        
        if 'error' in stats:
            print(f"❌ {stats['error']}")
            return
        
        print("📊 JPAPI Performance Report")
        print("=" * 40)
        print(f"Period: Last {days} days")
        print(f"Total Operations: {stats['total_operations']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print()
        
        print("🔹 Bash Operations (Target: 20%)")
        print(f"   Count: {stats['bash']['count']}")
        print(f"   Percentage: {stats['bash']['percentage']:.1f}%")
        print(f"   Avg Time: {stats['bash']['avg_time']:.3f}s")
        print(f"   Target Deviation: {stats['architecture_compliance']['bash_deviation']:.1f}%")
        print()
        
        print("🔹 Python Operations (Target: 80%)")
        print(f"   Count: {stats['python']['count']}")
        print(f"   Percentage: {stats['python']['percentage']:.1f}%")
        print(f"   Avg Time: {stats['python']['avg_time']:.3f}s")
        print(f"   Target Deviation: {stats['architecture_compliance']['python_deviation']:.1f}%")
        print()
        
        # Architecture compliance
        bash_ok = stats['architecture_compliance']['bash_within_target']
        python_ok = stats['architecture_compliance']['python_within_target']
        
        print("🏗️  Architecture Compliance:")
        print(f"   Bash (20%): {'✅' if bash_ok else '⚠️'}")
        print(f"   Python (80%): {'✅' if python_ok else '⚠️'}")
        
        if not (bash_ok and python_ok):
            print()
            print("💡 Recommendations:")
            if not bash_ok:
                print(f"   - Bash operations are {stats['bash']['percentage']:.1f}% (target: 20%)")
                if stats['bash']['percentage'] > 25:
                    print("   - Consider moving some operations to Python")
                else:
                    print("   - Consider adding more bash operations for simple tasks")
            
            if not python_ok:
                print(f"   - Python operations are {stats['python']['percentage']:.1f}% (target: 80%)")
                if stats['python']['percentage'] < 75:
                    print("   - Consider moving complex operations to Python")
                else:
                    print("   - Consider moving simple operations to bash")

def main():
    """Main function for command line usage"""
    monitor = PerformanceMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "report":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            monitor.print_performance_report(days)
        elif sys.argv[1] == "stats":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            stats = monitor.get_performance_stats(days)
            print(json.dumps(stats, indent=2))
        else:
            print("Usage: performance_monitor.py [report|stats] [days]")
    else:
        monitor.print_performance_report()

if __name__ == "__main__":
    main()
