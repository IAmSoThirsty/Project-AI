#!/usr/bin/env python3
"""
IncrediBuild Dashboard - Real-time monitoring of distributed builds
"""

import time
import os
import sys
from pathlib import Path
from datetime import datetime

# Simple CLI dashboard for build monitoring


class BuildDashboard:
    """Simple CLI dashboard for monitoring builds"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display(self, pool_status: dict, cache_stats: dict, cost_data: dict):
        """Display dashboard"""
        self.clear_screen()
        
        runtime = time.time() - self.start_time
        
        print("=" * 80)
        print("  IncrediBuild Distributed Compilation Dashboard")
        print("=" * 80)
        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Uptime: {self._format_duration(runtime)}")
        print("=" * 80)
        print()
        
        # Pool Status
        print("  RESOURCE POOL STATUS")
        print("  " + "-" * 76)
        total = pool_status.get('total_nodes', 0)
        available = pool_status.get('available_nodes', 0)
        busy = pool_status.get('busy_nodes', 0)
        utilization = pool_status.get('utilization', 0)
        
        print(f"  Total Nodes:     {total}")
        print(f"  Available:       {available}")
        print(f"  Busy:            {busy}")
        print(f"  Utilization:     {utilization*100:.1f}%  {'█' * int(utilization*40)}")
        print(f"  Cost/Hour:       ${pool_status.get('cost_per_hour', 0):.2f}")
        print()
        
        # Cache Stats
        print("  CACHE STATISTICS")
        print("  " + "-" * 76)
        print(f"  Total Entries:   {cache_stats.get('total_entries', 0)}")
        print(f"  Backend:         {cache_stats.get('backend', 'N/A')}")
        print(f"  Redis:           {'✅ Enabled' if cache_stats.get('redis_enabled') else '❌ Disabled'}")
        print(f"  S3:              {'✅ Enabled' if cache_stats.get('s3_enabled') else '❌ Disabled'}")
        print()
        
        # Cost Tracking
        print("  COST TRACKING")
        print("  " + "-" * 76)
        daily = cost_data.get('daily', 0)
        daily_limit = cost_data.get('daily_limit', 50)
        monthly = cost_data.get('monthly', 0)
        monthly_limit = cost_data.get('monthly_limit', 1000)
        
        print(f"  Daily:           ${daily:.2f} / ${daily_limit:.2f}  ({daily/daily_limit*100:.1f}%)")
        print(f"  Monthly:         ${monthly:.2f} / ${monthly_limit:.2f}  ({monthly/monthly_limit*100:.1f}%)")
        print()
        
        print("  " + "=" * 76)
        print("  Press Ctrl+C to exit")
        print("=" * 80)
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def run_demo(self):
        """Run demo dashboard with mock data"""
        try:
            while True:
                # Mock data that changes over time
                t = int(time.time() % 60)
                
                pool_status = {
                    'total_nodes': 10,
                    'available_nodes': max(2, 10 - (t % 8)),
                    'busy_nodes': min(8, t % 8),
                    'utilization': min(8, t % 8) / 10,
                    'cost_per_hour': 0.85,
                }
                
                cache_stats = {
                    'total_entries': 150 + t,
                    'backend': 'hybrid',
                    'redis_enabled': True,
                    's3_enabled': True,
                }
                
                cost_data = {
                    'daily': 12.50 + (t * 0.1),
                    'daily_limit': 50.0,
                    'monthly': 142.00,
                    'monthly_limit': 1000.0,
                }
                
                self.display(pool_status, cache_stats, cost_data)
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\nDashboard stopped.")
            sys.exit(0)


if __name__ == '__main__':
    dashboard = BuildDashboard()
    dashboard.run_demo()
