#!/usr/bin/env python3
"""
AGENT-081: Security Concepts to Controls Links Specialist
Systematically adds bidirectional wiki links from security concepts to controls.
"""

import re
import sqlite3
from pathlib import Path
from typing import List, Tuple, Dict, Set
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SecurityWikiLinker:
    """Add wiki links from security concepts to implementing controls."""
    
    def __init__(self, db_path: str = "session.db", repo_root: str = "."):
        self.db_path = db_path
        self.repo_root = Path(repo_root)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Mapping of control IDs to wiki link targets
        self.control_link_map = {
            # Constitutional & Governance
            'octoreflex': '[[src/app/core/octoreflex.py|OctoReflex]]',
            'cerberus-hydra': '[[src/app/core/cerberus_hydra.py|Cerberus Hydra]]',
            'fourlaws': '[[src/app/core/ai_systems.py#FourLaws|Four Laws]]',
            'command-override': '[[src/app/core/command_override.py|Command Override System]]',
            'triumvirate': '[[src/app/core/council_hub.py|Triumvirate Governance]]',
            
            # Authentication & Access Control
            'auth-jwt': '[[src/app/core/security/auth.py|JWT Authentication]]',
            'user-manager': '[[src/app/core/user_manager.py|User Manager]]',
            'mfa-auth': '[[src/app/security/advanced/mfa_auth.py|MFA Authentication]]',
            'access-control': '[[src/app/core/access_control.py|Access Control]]',
            
            # Encryption
            'god-tier-encryption': '[[utils/encryption/god_tier_encryption.py|7-Layer Encryption]]',
            'fernet-encryption': '[[src/app/integrations/encryption_fernet.py|Fernet Encryption]]',
            
            # Threat Detection & Response
            'honeypot': '[[src/app/core/honeypot_detector.py|Honeypot Detector]]',
            'incident-responder': '[[src/app/core/incident_responder.py|Incident Responder]]',
            'threat-detection': '[[kernel/threat_detection.py|Threat Detection Engine]]',
            'security-resources': '[[src/app/core/security_resources.py|Security Resources]]',
            
            # Security Frameworks
            'ai-security-framework': '[[src/app/security/ai_security_framework.py|AI Security Framework]]',
            'agent-security': '[[src/app/security/agent_security.py|Agent Security]]',
            'asymmetric-security': '[[src/app/core/asymmetric_security_engine.py|Asymmetric Security]]',
            'security-enforcer': '[[src/app/core/security_enforcer.py|Security Enforcer]]',
            'security-ops-center': '[[src/app/core/security_operations_center.py|Security Operations Center]]',
            
            # Data Protection
            'database-security': '[[src/app/security/database_security.py|Database Security]]',
            'path-security': '[[src/app/security/path_security.py|Path Security]]',
            'location-tracker': '[[src/app/core/location_tracker.py|Location Tracker]]',
            
            # Monitoring
            'security-metrics': '[[src/app/monitoring/security_metrics.py|Security Metrics]]',
            'security-monitoring': '[[src/app/core/security_monitoring.py|Security Monitoring]]',
            
            # Emergency
            'emergency-alert': '[[src/app/core/emergency_alert.py|Emergency Alert]]',
            
            # Network
            'ip-blocking': '[[src/app/core/ip_blocking_system.py|IP Blocking]]',
            'contrarian-firewall': '[[src/app/security/contrarian_firewall.py|Contrarian Firewall]]',
            'wifi-security': '[[src/app/infrastructure/networking/wifi_security.py|WiFi Security]]',
            
            # Validation
            'input-validation': '[[src/app/gui/input_validation.py|Input Validation]]',
            'data-validation': '[[src/app/security/data_validation.py|Data Validation]]',
            
            # Advanced
            'cybersecurity-knowledge': '[[src/app/core/cybersecurity_knowledge.py|Cybersecurity Knowledge]]',
            'hydra-50-security': '[[src/app/core/hydra_50_security.py|Hydra 50 Security]]',
            'novel-security': '[[src/app/core/novel_security_scenarios.py|Security Scenarios]]',
            'red-team': '[[src/app/core/red_team_stress_test.py|Red Team Testing]]',
            'red-hat-defense': '[[src/app/core/red_hat_expert_defense.py|Red Hat Defense]]',
        }
        
    def get_concepts_for_doc(self, doc_path: str) -> List[Tuple[str, str, str]]:
        """Get all security concepts referenced in a document."""
        query = """
        SELECT id, concept_name, description 
        FROM security_concepts 
        WHERE doc_file = ?
        ORDER BY concept_name
        """
        cursor = self.conn.execute(query, (doc_path,))
        return [(row['id'], row['concept_name'], row['description']) 
                for row in cursor.fetchall()]
    
    def get_controls_for_concept(self, concept_id: str) -> List[Tuple[str, str, str, str]]:
        """Get all controls that implement/mitigate a concept."""
        query = """
        SELECT c.id, c.control_name, ccl.link_type, ccl.strength
        FROM security_controls c
        JOIN concept_control_links ccl ON c.id = ccl.control_id
        WHERE ccl.concept_id = ?
        ORDER BY 
            CASE ccl.strength 
                WHEN 'primary' THEN 1 
                WHEN 'secondary' THEN 2 
                ELSE 3 
            END,
            c.control_name
        """
        cursor = self.conn.execute(query, (concept_id,))
        return [(row['id'], row['control_name'], row['link_type'], row['strength']) 
                for row in cursor.fetchall()]
    
    def add_implementation_section(self, content: str, concept_name: str, 
                                   controls: List[Tuple[str, str, str, str]]) -> str:
        """Add an Implementation section after a concept description."""
        if not controls:
            return content
        
        # Build implementation section
        impl_section = f"\n\n### Implementation\n\n"
        
        # Group controls by link type
        primary_controls = [c for c in controls if c[3] == 'primary']
        secondary_controls = [c for c in controls if c[3] == 'secondary']
        related_controls = [c for c in controls if c[3] == 'related']
        
        if primary_controls:
            impl_section += "**Primary Controls:**\n\n"
            for control_id, control_name, link_type, _ in primary_controls:
                wiki_link = self.control_link_map.get(control_id, f"[[{control_id}]]")
                impl_section += f"- {wiki_link} - {link_type.capitalize()}s {concept_name}\n"
        
        if secondary_controls:
            impl_section += "\n**Secondary Controls:**\n\n"
            for control_id, control_name, link_type, _ in secondary_controls:
                wiki_link = self.control_link_map.get(control_id, f"[[{control_id}]]")
                impl_section += f"- {wiki_link} - {link_type.capitalize()}s {concept_name}\n"
        
        if related_controls:
            impl_section += "\n**Related Controls:**\n\n"
            for control_id, control_name, link_type, _ in related_controls:
                wiki_link = self.control_link_map.get(control_id, f"[[{control_id}]]")
                impl_section += f"- {wiki_link} - {link_type.capitalize()}s {concept_name}\n"
        
        return content + impl_section
    
    def find_concept_mentions(self, content: str, concept_name: str) -> List[Tuple[int, str]]:
        """Find all mentions of a concept in content."""
        mentions = []
        lines = content.split('\n')
        
        # Create regex patterns for various mentions
        patterns = [
            re.compile(rf'\b{re.escape(concept_name)}\b', re.IGNORECASE),
            re.compile(rf'\b{re.escape(concept_name.upper())}\b'),
            re.compile(rf'\b{re.escape(concept_name.lower())}\b'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                if pattern.search(line) and '[[' not in line:  # Not already a wiki link
                    mentions.append((line_num, line))
                    break
        
        return mentions
    
    def add_inline_wiki_links(self, content: str, concept_name: str, 
                              controls: List[Tuple[str, str, str, str]]) -> Tuple[str, int]:
        """Add inline wiki links to control mentions."""
        if not controls:
            return content, 0
        
        links_added = 0
        
        # For each primary control, add inline links
        for control_id, control_name, _, strength in controls:
            if strength != 'primary':
                continue
                
            wiki_link = self.control_link_map.get(control_id, f"[[{control_id}|{control_name}]]")
            
            # Replace mentions of control name with wiki link
            # But be careful not to replace inside existing wiki links or code blocks
            pattern = re.compile(
                rf'(?<!\[\[)(?<!`)\b{re.escape(control_name)}\b(?!`|]])',
                re.IGNORECASE
            )
            
            new_content, count = pattern.subn(wiki_link, content, count=3)  # Limit to first 3 mentions
            if count > 0:
                content = new_content
                links_added += count
        
        return content, links_added
    
    def process_document(self, doc_path: str) -> Tuple[str, int, int]:
        """Process a single document and add wiki links."""
        file_path = self.repo_root / doc_path
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None, 0, 0
        
        logger.info(f"Processing: {doc_path}")
        
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        modified_content = original_content
        total_concepts = 0
        total_links = 0
        
        # Get concepts for this document
        concepts = self.get_concepts_for_doc(doc_path)
        
        for concept_id, concept_name, description in concepts:
            total_concepts += 1
            
            # Get controls for this concept
            controls = self.get_controls_for_concept(concept_id)
            
            if not controls:
                logger.debug(f"  No controls for concept: {concept_name}")
                continue
            
            # Add inline wiki links
            modified_content, links_count = self.add_inline_wiki_links(
                modified_content, concept_name, controls
            )
            total_links += links_count
            
            logger.info(f"  Added {links_count} links for: {concept_name}")
        
        # Update database
        self.conn.execute(
            """UPDATE doc_files 
               SET processing_status = 'processed', 
                   concept_count = ?, 
                   link_count = ? 
               WHERE file_path = ?""",
            (total_concepts, total_links, doc_path)
        )
        self.conn.commit()
        
        return modified_content if modified_content != original_content else None, total_concepts, total_links
    
    def process_all_documents(self) -> Dict[str, any]:
        """Process all pending documents."""
        query = "SELECT file_path FROM doc_files WHERE processing_status = 'pending'"
        cursor = self.conn.execute(query)
        doc_paths = [row['file_path'] for row in cursor.fetchall()]
        
        results = {
            'total_docs': len(doc_paths),
            'processed': 0,
            'updated': 0,
            'total_concepts': 0,
            'total_links': 0,
            'files_updated': []
        }
        
        for doc_path in doc_paths:
            modified_content, concepts, links = self.process_document(doc_path)
            
            results['processed'] += 1
            results['total_concepts'] += concepts
            results['total_links'] += links
            
            if modified_content:
                # Write updated content
                file_path = self.repo_root / doc_path
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                results['updated'] += 1
                results['files_updated'].append(doc_path)
                
                logger.info(f"✓ Updated {doc_path}: {concepts} concepts, {links} links")
            else:
                logger.info(f"○ No changes: {doc_path}")
        
        return results
    
    def generate_traceability_matrix(self, output_path: str):
        """Generate security concept-to-control traceability matrix."""
        query = """
        SELECT 
            sc.concept_name,
            sc.concept_type,
            sc.doc_file,
            GROUP_CONCAT(c.control_name, ', ') as controls,
            COUNT(ccl.control_id) as control_count,
            sc.implementation_status
        FROM security_concepts sc
        LEFT JOIN concept_control_links ccl ON sc.id = ccl.concept_id
        LEFT JOIN security_controls c ON ccl.control_id = c.id
        GROUP BY sc.id
        ORDER BY sc.concept_type, sc.concept_name
        """
        
        cursor = self.conn.execute(query)
        rows = cursor.fetchall()
        
        # Build markdown table
        content = """---
title: "Security Traceability Matrix"
id: "agent-081-security-traceability"
type: "report"
version: "1.0.0"
created_date: "2026-02-08"
status: "active"
category: "security"
tags:
  - "area:security"
  - "type:traceability"
  - "type:matrix"
  - "phase:5-cross-linking"
  - "agent:081"
---

# AGENT-081 Security Traceability Matrix

**Generated:** 2026-02-08  
**Agent:** AGENT-081 Security Concepts to Controls Links Specialist  
**Mission:** ~350 bidirectional wiki links from concepts to controls

## Executive Summary

This matrix provides comprehensive traceability from security concepts (threats, defenses, controls, frameworks) to their actual implementations in the codebase.

### Coverage Statistics

"""
        
        # Calculate statistics
        total_concepts = len(rows)
        implemented = sum(1 for row in rows if row['control_count'] > 0)
        unimplemented = total_concepts - implemented
        total_mappings = sum(row['control_count'] for row in rows)
        
        content += f"- **Total Security Concepts:** {total_concepts}\n"
        content += f"- **Implemented Concepts:** {implemented}\n"
        content += f"- **Unimplemented Concepts:** {unimplemented}\n"
        content += f"- **Total Concept→Control Mappings:** {total_mappings}\n"
        content += f"- **Average Controls per Concept:** {total_mappings / total_concepts:.1f}\n\n"
        
        content += "## Traceability Matrix\n\n"
        content += "| Concept | Type | Status | Controls | Source Document |\n"
        content += "|---------|------|--------|----------|----------------|\n"
        
        for row in rows:
            concept_name = row['concept_name']
            concept_type = row['concept_type'] or 'N/A'
            status = '✅' if row['control_count'] > 0 else '❌'
            controls = row['controls'] or 'None'
            doc_file = row['doc_file'].split('/')[-1]  # Just filename
            
            content += f"| {concept_name} | {concept_type} | {status} | {controls} | {doc_file} |\n"
        
        # Unimplemented controls report
        content += "\n## Unimplemented Security Concepts\n\n"
        unimplemented_rows = [row for row in rows if row['control_count'] == 0]
        
        if unimplemented_rows:
            content += "The following security concepts do not have implementing controls:\n\n"
            for row in unimplemented_rows:
                content += f"- **{row['concept_name']}** ({row['concept_type']})\n"
                content += f"  - Source: `{row['doc_file']}`\n"
                content += f"  - Status: {row['implementation_status']}\n\n"
        else:
            content += "✅ All security concepts have implementing controls!\n\n"
        
        # Write matrix
        output_file = self.repo_root / output_path
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✓ Generated traceability matrix: {output_path}")
        return total_concepts, implemented, total_mappings
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main execution."""
    logger.info("=== AGENT-081: Security Concepts to Controls Links ===")
    
    linker = SecurityWikiLinker(repo_root="T:\\Project-AI-main")
    
    try:
        # Process all documents
        logger.info("\n📝 Processing documentation files...")
        results = linker.process_all_documents()
        
        logger.info("\n" + "="*60)
        logger.info("PROCESSING RESULTS")
        logger.info("="*60)
        logger.info(f"Documents processed: {results['processed']}")
        logger.info(f"Documents updated: {results['updated']}")
        logger.info(f"Total concepts: {results['total_concepts']}")
        logger.info(f"Total links added: {results['total_links']}")
        
        # Generate traceability matrix
        logger.info("\n📊 Generating traceability matrix...")
        total, implemented, mappings = linker.generate_traceability_matrix(
            "AGENT-081-SECURITY-TRACEABILITY.md"
        )
        
        logger.info("\n" + "="*60)
        logger.info("TRACEABILITY MATRIX")
        logger.info("="*60)
        logger.info(f"Total concepts: {total}")
        logger.info(f"Implemented: {implemented}")
        logger.info(f"Total mappings: {mappings}")
        logger.info(f"Coverage: {implemented/total*100:.1f}%")
        
        logger.info("\n✅ MISSION COMPLETE")
        
    finally:
        linker.close()


if __name__ == "__main__":
    main()
