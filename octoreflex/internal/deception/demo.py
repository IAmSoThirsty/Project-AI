#!/usr/bin/env python3
"""
OctoReflex Deception Demo

Demonstrates the comprehensive deception framework including:
- Honeypots (SSH, HTTP, Database)
- Port rotation with frequency hopping
- TCP decoys
- Cost amplification
- Analytics and metrics
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add kernel module to path
kernel_path = Path(__file__).parent.parent.parent.parent / "kernel"
sys.path.insert(0, str(kernel_path))

from deception import (
    DeceptionOrchestrator,
    DeceptionStrategy,
    IPRotationManager,
    AttackerCostAnalytics,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_deception_orchestrator():
    """Demonstrate deception orchestrator"""
    logger.info("=" * 60)
    logger.info("DECEPTION ORCHESTRATOR DEMO")
    logger.info("=" * 60)
    
    orchestrator = DeceptionOrchestrator()
    
    # Create deception environment for a suspicious user
    user_id = 12345
    threat_type = "privilege_escalation_and_credential_theft"
    
    env = orchestrator.create_environment(
        user_id=user_id,
        threat_type=threat_type,
        strategy=DeceptionStrategy.ADAPTIVE
    )
    
    logger.info("\nDeception environment created:")
    logger.info(f"  Environment ID: {env.env_id}")
    logger.info(f"  Strategy: {env.strategy.value}")
    logger.info(f"  Resources: {len(env.resources)} fake items")
    
    # Simulate attacker actions
    logger.info("\nSimulating attacker actions...")
    
    actions = [
        "cat /etc/shadow",
        "cat /etc/passwd",
        "ls -la /root/.ssh/",
        "cat /root/.ssh/id_rsa",
        "whoami",
        "sudo -l",
        "cat /opt/secrets/api_keys.txt",
        "find / -name '*.sql'",
        "cat /var/backups/production_db_backup.sql",
        "tar czf /tmp/exfil.tar.gz /etc /opt/secrets",
    ]
    
    for action in actions:
        result = orchestrator.record_action(user_id, action)
        
        logger.info(f"\n  Action: {action}")
        logger.info(f"    Confidence: {result.get('confidence', 0):.2f}")
        logger.info(f"    Bubblegum ready: {result.get('bubblegum_ready', False)}")
        
        # Generate fake response
        response = orchestrator.get_fake_response(user_id, action)
        if len(response) > 100:
            logger.info(f"    Response: {response[:100]}...")
        else:
            logger.info(f"    Response: {response}")
        
        await asyncio.sleep(0.5)
        
        # Check if Bubblegum triggered
        if "ATTACKER_EXPOSED" in str(result.get("message", "")):
            logger.critical("\n🎯 BUBBLEGUM PROTOCOL TRIGGERED!")
            logger.critical(f"  Attacker caught red-handed after {result['actions_logged']} actions")
            logger.critical(f"  Time in trap: {result['time_in_trap']:.1f} seconds")
            break
    
    # Get final stats
    stats = orchestrator.get_stats()
    logger.info("\n" + "=" * 60)
    logger.info("DECEPTION STATISTICS")
    logger.info("=" * 60)
    logger.info(f"Active environments: {stats['active_environments']}")
    logger.info(f"Total Bubblegum triggers: {stats['total_bubblegum_triggers']}")
    
    if stats['environments']:
        for env_info in stats['environments']:
            logger.info(f"\nEnvironment for user {env_info['user_id']}:")
            logger.info(f"  Threat: {env_info['threat_type']}")
            logger.info(f"  Actions: {env_info['actions']}")
            logger.info(f"  Confidence: {env_info['confidence']:.2f}")
            logger.info(f"  Resources: {env_info['resources']}")


async def demo_ip_rotation():
    """Demonstrate IP rotation"""
    logger.info("\n" + "=" * 60)
    logger.info("IP ROTATION DEMO")
    logger.info("=" * 60)
    
    ip_manager = IPRotationManager()
    ip_manager.configure_ip_pool("10.0.1.0/24", pool_size=50)
    
    logger.info(f"\nIP pool configured with {len(ip_manager.ip_pool)} addresses")
    
    # Show current IP
    current_ip = ip_manager.get_current_ip()
    logger.info(f"Current IP: {current_ip}")
    
    # Force rotation
    logger.info("\nForcing IP rotation...")
    ip_manager.rotate_ip()
    new_ip = ip_manager.get_current_ip()
    logger.info(f"New IP: {new_ip}")
    
    # Get stats
    stats = ip_manager.get_stats()
    logger.info("\nIP Rotation Stats:")
    logger.info(f"  Pool size: {stats['pool_size']}")
    logger.info(f"  Current IP: {stats['current_ip']}")
    logger.info(f"  Current index: {stats['current_index']}")
    logger.info(f"  Rotation interval: {stats['rotation_interval']}s")


async def demo_cost_analytics():
    """Demonstrate attacker cost analytics"""
    logger.info("\n" + "=" * 60)
    logger.info("ATTACKER COST ANALYTICS DEMO")
    logger.info("=" * 60)
    
    analytics = AttackerCostAnalytics()
    
    # Simulate various attacker activities
    logger.info("\nSimulating attacker activities...")
    
    attacker_ips = [
        "192.168.1.100",
        "192.168.1.101",
        "192.168.1.102",
    ]
    
    # Simulate connections
    for i, ip in enumerate(attacker_ips):
        for j in range(5 + i * 3):  # Different activity levels
            analytics.record_connection(ip, duration=2.5 + j * 0.5)
            analytics.record_auth_attempt(ip, f"admin{j}", f"password{j}")
            analytics.record_bandwidth_waste(ip, 50000 + j * 10000)
            analytics.record_decoy_hit(ip, "ssh_honeypot")
    
    # Calculate total costs
    cost_analysis = analytics.calculate_total_cost()
    
    logger.info("\n" + "=" * 60)
    logger.info("COST ANALYSIS")
    logger.info("=" * 60)
    logger.info(f"\n💰 Total Cost Imposed: ${cost_analysis['total_cost_usd']:.2f}")
    logger.info(f"\nBreakdown:")
    logger.info(f"  CPU cost: ${cost_analysis['cpu_cost_usd']:.2f}")
    logger.info(f"  Bandwidth cost: ${cost_analysis['bandwidth_cost_usd']:.2f}")
    logger.info(f"  Time cost: ${cost_analysis['time_cost_usd']:.2f}")
    
    logger.info(f"\nResource Waste:")
    logger.info(f"  CPU hours: {cost_analysis['cpu_hours_wasted']:.2f}")
    logger.info(f"  Bandwidth GB: {cost_analysis['bandwidth_gb_wasted']:.4f}")
    logger.info(f"  Connections: {cost_analysis['connections_wasted']}")
    logger.info(f"  Auth attempts: {cost_analysis['auth_attempts_wasted']}")
    logger.info(f"  Unique attackers: {cost_analysis['unique_attackers']}")
    
    # Get top attackers
    logger.info("\n" + "=" * 60)
    logger.info("TOP ATTACKERS")
    logger.info("=" * 60)
    
    top_attackers = analytics.get_top_attackers(limit=5)
    for i, (ip, profile) in enumerate(top_attackers, 1):
        logger.info(f"\n{i}. {ip}")
        logger.info(f"   Connections: {profile['connections']}")
        logger.info(f"   Auth attempts: {profile['auth_attempts']}")
        logger.info(f"   Bandwidth wasted: {profile['bandwidth_wasted']} bytes")
        logger.info(f"   Attack types: {profile['attack_types']}")


async def demo_comprehensive_stats():
    """Show comprehensive statistics"""
    logger.info("\n" + "=" * 60)
    logger.info("COMPREHENSIVE STATISTICS")
    logger.info("=" * 60)
    
    # Create all components
    orchestrator = DeceptionOrchestrator()
    ip_manager = IPRotationManager()
    analytics = AttackerCostAnalytics()
    
    # Configure
    ip_manager.configure_ip_pool("10.0.2.0/24", pool_size=100)
    
    # Create some environments
    for user_id in range(1000, 1005):
        orchestrator.create_environment(
            user_id=user_id,
            threat_type="data_exfiltration",
            strategy=DeceptionStrategy.ADAPTIVE
        )
    
    # Simulate some activity
    for i in range(20):
        ip = f"192.168.1.{100 + (i % 10)}"
        analytics.record_connection(ip, duration=3.0)
        analytics.record_auth_attempt(ip, "admin", "password123")
        analytics.record_bandwidth_waste(ip, 100000)
        analytics.record_decoy_hit(ip, "http_honeypot" if i % 2 else "ssh_honeypot")
    
    # Get all stats
    deception_stats = orchestrator.get_stats()
    ip_stats = ip_manager.get_stats()
    cost_stats = analytics.get_stats()
    
    logger.info("\n📊 Deception Framework Status:")
    logger.info(f"  Active environments: {deception_stats['active_environments']}")
    logger.info(f"  Bubblegum triggers: {deception_stats['total_bubblegum_triggers']}")
    
    logger.info("\n🔄 IP Rotation Status:")
    logger.info(f"  Pool size: {ip_stats['pool_size']}")
    logger.info(f"  Current IP: {ip_stats['current_ip']}")
    
    logger.info("\n💰 Cost Analysis:")
    cost_analysis = cost_stats['cost_analysis']
    logger.info(f"  Total cost imposed: ${cost_analysis['total_cost_usd']:.2f}")
    logger.info(f"  Unique attackers tracked: {cost_analysis['unique_attackers']}")
    
    logger.info("\n📈 Attack Metrics:")
    metrics = cost_stats['metrics']
    logger.info(f"  Total connections: {metrics['total_connections']}")
    logger.info(f"  Auth attempts: {metrics['total_auth_attempts']}")
    logger.info(f"  Bandwidth wasted: {metrics['total_bandwidth_wasted']} bytes")
    logger.info(f"  Decoy hits: {metrics['total_decoy_hits']}")
    logger.info(f"  Attack types: {metrics['attack_types']}")


async def main():
    """Main demo entry point"""
    logger.info("🎭 OctoReflex Deception Framework Demo")
    logger.info("Demonstrating comprehensive deception mechanisms\n")
    
    try:
        # Run demos
        await demo_deception_orchestrator()
        await asyncio.sleep(1)
        
        await demo_ip_rotation()
        await asyncio.sleep(1)
        
        await demo_cost_analytics()
        await asyncio.sleep(1)
        
        await demo_comprehensive_stats()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ DEMO COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info("\nKey Takeaways:")
        logger.info("  ✓ Deception environments waste attacker resources")
        logger.info("  ✓ Bubblegum Protocol catches attackers at critical moment")
        logger.info("  ✓ IP rotation makes tracking difficult")
        logger.info("  ✓ Cost analytics quantify attacker waste")
        logger.info("  ✓ Comprehensive metrics provide visibility")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
