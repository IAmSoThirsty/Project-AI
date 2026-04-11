#                                           [2026-04-09 05:45]
#                                          Productivity: Ultimate
"""
Threat Intelligence Integration
================================

Real-time integration with threat intelligence sources:
- MITRE ATT&CK framework
- CVE/NVD databases
- Threat feeds (commercial and open source)
- Custom intelligence sources
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class MITREAttackIntegration:
    """
    MITRE ATT&CK framework integration.
    
    Provides access to tactics, techniques, and procedures (TTPs).
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize MITRE ATT&CK integration.
        
        Args:
            cache_dir: Directory for caching framework data
        """
        self.cache_dir = cache_dir or Path("data/mitre_attack")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.techniques: Dict[str, dict] = {}
        self.tactics: Dict[str, dict] = {}
        self.groups: Dict[str, dict] = {}
        self.software: Dict[str, dict] = {}
        
        self.last_update = None
        
        self._load_cache()
        logger.info("MITRE ATT&CK integration initialized")
    
    def _load_cache(self):
        """Load cached MITRE data."""
        cache_file = self.cache_dir / "attack_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.techniques = data.get('techniques', {})
                    self.tactics = data.get('tactics', {})
                    self.groups = data.get('groups', {})
                    self.software = data.get('software', {})
                    self.last_update = datetime.fromisoformat(data.get('last_update', 
                                                                        datetime.now().isoformat()))
                logger.info(f"Loaded {len(self.techniques)} techniques from cache")
            except Exception as e:
                logger.error(f"Failed to load MITRE cache: {e}")
    
    def _save_cache(self):
        """Save MITRE data to cache."""
        cache_file = self.cache_dir / "attack_cache.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'techniques': self.techniques,
                    'tactics': self.tactics,
                    'groups': self.groups,
                    'software': self.software,
                    'last_update': datetime.now().isoformat()
                }, f, indent=2)
            logger.info("MITRE cache saved")
        except Exception as e:
            logger.error(f"Failed to save MITRE cache: {e}")
    
    async def update(self):
        """
        Update MITRE ATT&CK data.
        
        In production, this would fetch from:
        https://github.com/mitre/cti
        """
        logger.info("Updating MITRE ATT&CK framework...")
        
        # Simulated data (in production, fetch from MITRE CTI)
        sample_techniques = {
            "T1190": {
                "name": "Exploit Public-Facing Application",
                "description": "Adversaries may attempt to exploit a weakness in an Internet-facing host",
                "tactics": ["initial-access"],
                "platforms": ["Linux", "Windows", "macOS"],
                "data_sources": ["Application Log", "Network Traffic"],
                "mitigations": ["M1048", "M1030"],
                "detection": "Monitor application logs for abnormal behavior"
            },
            "T1059": {
                "name": "Command and Scripting Interpreter",
                "description": "Adversaries may abuse command and script interpreters",
                "tactics": ["execution"],
                "platforms": ["Linux", "Windows", "macOS"],
                "sub_techniques": ["T1059.001", "T1059.003", "T1059.006"],
                "detection": "Monitor executed commands and arguments"
            },
            "T1003": {
                "name": "OS Credential Dumping",
                "description": "Adversaries may attempt to dump credentials",
                "tactics": ["credential-access"],
                "platforms": ["Linux", "Windows"],
                "requires_permissions": ["Administrator", "SYSTEM", "root"],
                "detection": "Monitor processes accessing credential stores"
            },
            "T1071": {
                "name": "Application Layer Protocol",
                "description": "Adversaries may communicate using application layer protocols",
                "tactics": ["command-and-control"],
                "platforms": ["Linux", "Windows", "macOS"],
                "sub_techniques": ["T1071.001", "T1071.004"],
                "detection": "Monitor network data for unusual data flows"
            },
            "T1566": {
                "name": "Phishing",
                "description": "Adversaries may send phishing messages to gain access",
                "tactics": ["initial-access"],
                "platforms": ["Linux", "Windows", "macOS", "Office 365", "SaaS"],
                "sub_techniques": ["T1566.001", "T1566.002", "T1566.003"],
                "detection": "Network intrusion detection systems and email gateways"
            },
            "T1068": {
                "name": "Exploitation for Privilege Escalation",
                "description": "Adversaries may exploit software vulnerabilities",
                "tactics": ["privilege-escalation"],
                "platforms": ["Linux", "Windows", "macOS"],
                "detection": "Monitor for unusual system calls and exploits"
            },
            "T1021": {
                "name": "Remote Services",
                "description": "Adversaries may use valid accounts to log into remote services",
                "tactics": ["lateral-movement"],
                "platforms": ["Linux", "Windows", "macOS"],
                "sub_techniques": ["T1021.001", "T1021.002", "T1021.004"],
                "detection": "Monitor remote login behavior and authentication logs"
            },
            "T1048": {
                "name": "Exfiltration Over Alternative Protocol",
                "description": "Adversaries may steal data using protocols other than C2",
                "tactics": ["exfiltration"],
                "platforms": ["Linux", "Windows", "macOS"],
                "detection": "Monitor network traffic for unusual protocols"
            }
        }
        
        self.techniques.update(sample_techniques)
        
        # Sample tactics
        sample_tactics = {
            "initial-access": {
                "name": "Initial Access",
                "description": "Trying to get into your network"
            },
            "execution": {
                "name": "Execution",
                "description": "Trying to run malicious code"
            },
            "credential-access": {
                "name": "Credential Access",
                "description": "Trying to steal account names and passwords"
            },
            "lateral-movement": {
                "name": "Lateral Movement",
                "description": "Trying to move through your environment"
            },
            "exfiltration": {
                "name": "Exfiltration",
                "description": "Trying to steal data"
            }
        }
        
        self.tactics.update(sample_tactics)
        
        self.last_update = datetime.now()
        self._save_cache()
        
        logger.info(f"Updated MITRE ATT&CK: {len(self.techniques)} techniques, "
                   f"{len(self.tactics)} tactics")
    
    def get_technique(self, technique_id: str) -> Optional[dict]:
        """Get technique details by ID."""
        return self.techniques.get(technique_id)
    
    def get_techniques_by_tactic(self, tactic: str) -> List[dict]:
        """Get all techniques for a tactic."""
        return [
            {'id': tid, **tdata}
            for tid, tdata in self.techniques.items()
            if tactic in tdata.get('tactics', [])
        ]
    
    def enrich_technique_ids(self, technique_ids: List[str]) -> Dict[str, dict]:
        """Enrich technique IDs with full details."""
        return {
            tid: self.techniques.get(tid, {'name': 'Unknown', 'description': 'No data'})
            for tid in technique_ids
        }


class CVEDatabase:
    """
    CVE/NVD database integration.
    
    Provides access to vulnerability information.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize CVE database.
        
        Args:
            cache_dir: Directory for caching CVE data
        """
        self.cache_dir = cache_dir or Path("data/cve_database")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cves: Dict[str, dict] = {}
        self.last_update = None
        
        self._load_cache()
        logger.info("CVE database initialized")
    
    def _load_cache(self):
        """Load cached CVE data."""
        cache_file = self.cache_dir / "cve_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.cves = data.get('cves', {})
                    self.last_update = datetime.fromisoformat(data.get('last_update',
                                                                        datetime.now().isoformat()))
                logger.info(f"Loaded {len(self.cves)} CVEs from cache")
            except Exception as e:
                logger.error(f"Failed to load CVE cache: {e}")
    
    def _save_cache(self):
        """Save CVE data to cache."""
        cache_file = self.cache_dir / "cve_cache.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'cves': self.cves,
                    'last_update': datetime.now().isoformat()
                }, f, indent=2)
            logger.info("CVE cache saved")
        except Exception as e:
            logger.error(f"Failed to save CVE cache: {e}")
    
    async def update(self):
        """
        Update CVE database.
        
        In production, this would fetch from NVD API:
        https://nvd.nist.gov/developers/vulnerabilities
        """
        logger.info("Updating CVE database...")
        
        # Simulated CVE data
        sample_cves = {
            "CVE-2024-1234": {
                "description": "Remote code execution vulnerability in web framework",
                "severity": "CRITICAL",
                "cvss_v3": 9.8,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "published": "2024-01-15",
                "last_modified": "2024-02-01",
                "cwe": "CWE-78",
                "references": ["https://example.com/advisory"],
                "affected_products": ["WebFramework 1.0-2.5"]
            },
            "CVE-2024-5678": {
                "description": "SQL injection in database connector",
                "severity": "HIGH",
                "cvss_v3": 8.1,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N",
                "published": "2024-02-10",
                "last_modified": "2024-02-15",
                "cwe": "CWE-89",
                "references": ["https://example.com/cve-5678"],
                "affected_products": ["DBConnector 3.x"]
            },
            "CVE-2024-9012": {
                "description": "Authentication bypass in SSO system",
                "severity": "CRITICAL",
                "cvss_v3": 9.1,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N",
                "published": "2024-03-01",
                "last_modified": "2024-03-05",
                "cwe": "CWE-287",
                "references": ["https://example.com/sso-vuln"],
                "affected_products": ["SSOSystem 2.0"]
            }
        }
        
        self.cves.update(sample_cves)
        self.last_update = datetime.now()
        self._save_cache()
        
        logger.info(f"Updated CVE database: {len(self.cves)} entries")
    
    def get_cve(self, cve_id: str) -> Optional[dict]:
        """Get CVE details by ID."""
        return self.cves.get(cve_id)
    
    def search_by_severity(self, min_severity: str = "HIGH") -> List[dict]:
        """Search CVEs by minimum severity."""
        severity_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        min_level = severity_levels.index(min_severity)
        
        return [
            {'id': cve_id, **cve_data}
            for cve_id, cve_data in self.cves.items()
            if severity_levels.index(cve_data.get('severity', 'LOW')) >= min_level
        ]
    
    def get_recent_cves(self, days: int = 7) -> List[dict]:
        """Get CVEs published in last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        
        recent = []
        for cve_id, cve_data in self.cves.items():
            published = datetime.fromisoformat(cve_data.get('published', '2000-01-01'))
            if published >= cutoff:
                recent.append({'id': cve_id, **cve_data})
        
        return recent


class ThreatFeedAggregator:
    """
    Aggregates threat intelligence from multiple feeds.
    
    Combines indicators from various sources.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize threat feed aggregator.
        
        Args:
            cache_dir: Directory for caching feed data
        """
        self.cache_dir = cache_dir or Path("data/threat_feeds")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.indicators: Dict[str, dict] = {}
        self.feeds: Dict[str, dict] = {}
        
        # Register feeds
        self._register_default_feeds()
        
        logger.info("Threat feed aggregator initialized")
    
    def _register_default_feeds(self):
        """Register default threat feeds."""
        self.feeds = {
            "abuse_ch": {
                "name": "Abuse.ch",
                "type": "malware",
                "enabled": True,
                "url": "https://example.com/feed1"
            },
            "emerging_threats": {
                "name": "Emerging Threats",
                "type": "multi",
                "enabled": True,
                "url": "https://example.com/feed2"
            },
            "talos": {
                "name": "Cisco Talos",
                "type": "multi",
                "enabled": True,
                "url": "https://example.com/feed3"
            }
        }
    
    async def update_feed(self, feed_name: str):
        """
        Update specific threat feed.
        
        Args:
            feed_name: Name of feed to update
        """
        if feed_name not in self.feeds:
            logger.error(f"Unknown feed: {feed_name}")
            return
        
        feed = self.feeds[feed_name]
        if not feed['enabled']:
            return
        
        logger.info(f"Updating threat feed: {feed['name']}")
        
        # Simulated feed data (in production, fetch from actual feeds)
        sample_indicators = {
            f"{feed_name}_ip_1": {
                "type": "ip",
                "value": "198.51.100.42",
                "threat_type": "malware_c2",
                "confidence": 0.9,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "source": feed_name,
                "tags": ["botnet", "malware"]
            },
            f"{feed_name}_domain_1": {
                "type": "domain",
                "value": "malicious-domain.example",
                "threat_type": "phishing",
                "confidence": 0.85,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "source": feed_name,
                "tags": ["phishing", "credential_theft"]
            },
            f"{feed_name}_hash_1": {
                "type": "hash",
                "value": "a1b2c3d4e5f6",
                "threat_type": "ransomware",
                "confidence": 0.95,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "source": feed_name,
                "tags": ["ransomware", "encryption"]
            }
        }
        
        self.indicators.update(sample_indicators)
        logger.info(f"Updated {feed_name}: {len(sample_indicators)} indicators")
    
    async def update_all_feeds(self):
        """Update all enabled threat feeds."""
        tasks = [
            self.update_feed(feed_name)
            for feed_name, feed in self.feeds.items()
            if feed['enabled']
        ]
        await asyncio.gather(*tasks)
        
        logger.info(f"Updated all feeds: {len(self.indicators)} total indicators")
    
    def search_indicator(self, indicator_type: str, value: str) -> Optional[dict]:
        """Search for specific indicator."""
        for ind_id, ind_data in self.indicators.items():
            if ind_data['type'] == indicator_type and ind_data['value'] == value:
                return {'id': ind_id, **ind_data}
        return None
    
    def get_indicators_by_type(self, indicator_type: str) -> List[dict]:
        """Get all indicators of specific type."""
        return [
            {'id': ind_id, **ind_data}
            for ind_id, ind_data in self.indicators.items()
            if ind_data['type'] == indicator_type
        ]
    
    def get_high_confidence_indicators(self, min_confidence: float = 0.8) -> List[dict]:
        """Get high-confidence indicators."""
        return [
            {'id': ind_id, **ind_data}
            for ind_id, ind_data in self.indicators.items()
            if ind_data.get('confidence', 0) >= min_confidence
        ]


class ThreatIntelligenceHub:
    """
    Central hub for all threat intelligence sources.
    
    Coordinates MITRE ATT&CK, CVE, and threat feed data.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize threat intelligence hub.
        
        Args:
            cache_dir: Base directory for caching
        """
        base_dir = cache_dir or Path("data/threat_intel")
        
        self.mitre = MITREAttackIntegration(base_dir / "mitre")
        self.cve = CVEDatabase(base_dir / "cve")
        self.feeds = ThreatFeedAggregator(base_dir / "feeds")
        
        self.last_full_update = None
        
        logger.info("Threat Intelligence Hub initialized")
    
    async def initialize(self):
        """Initialize and perform first update."""
        logger.info("Initializing threat intelligence...")
        await self.update_all()
        logger.info("Threat intelligence initialization complete")
    
    async def update_all(self):
        """Update all intelligence sources."""
        logger.info("Updating all threat intelligence sources...")
        
        await asyncio.gather(
            self.mitre.update(),
            self.cve.update(),
            self.feeds.update_all_feeds()
        )
        
        self.last_full_update = datetime.now()
        logger.info("All threat intelligence sources updated")
    
    def enrich_event(self, event_data: dict) -> dict:
        """
        Enrich event with threat intelligence.
        
        Args:
            event_data: Event data to enrich
            
        Returns:
            Enriched event data
        """
        enriched = event_data.copy()
        enriched['intelligence'] = {}
        
        # Enrich MITRE techniques
        if 'mitre_techniques' in event_data:
            enriched['intelligence']['mitre'] = self.mitre.enrich_technique_ids(
                event_data['mitre_techniques']
            )
        
        # Check indicators against threat feeds
        if 'source_ip' in event_data:
            indicator = self.feeds.search_indicator('ip', event_data['source_ip'])
            if indicator:
                enriched['intelligence']['threat_feed'] = indicator
        
        # Check for related CVEs
        if 'cve_ids' in event_data:
            cve_details = {
                cve_id: self.cve.get_cve(cve_id)
                for cve_id in event_data['cve_ids']
            }
            enriched['intelligence']['cves'] = cve_details
        
        return enriched
    
    def get_status(self) -> dict:
        """Get status of all intelligence sources."""
        return {
            'last_update': self.last_full_update.isoformat() if self.last_full_update else None,
            'mitre': {
                'techniques': len(self.mitre.techniques),
                'tactics': len(self.mitre.tactics),
                'last_update': self.mitre.last_update.isoformat() if self.mitre.last_update else None
            },
            'cve': {
                'entries': len(self.cve.cves),
                'last_update': self.cve.last_update.isoformat() if self.cve.last_update else None
            },
            'feeds': {
                'indicators': len(self.feeds.indicators),
                'feeds': len(self.feeds.feeds)
            }
        }
