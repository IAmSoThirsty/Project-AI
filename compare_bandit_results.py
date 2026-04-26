#!/usr/bin/env python3
"""Compare Bandit security scan results before and after fixes."""

import json
import sys
from pathlib import Path
from collections import defaultdict

def load_report(filepath):
    """Load and parse a Bandit JSON report."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_report(report):
    """Extract metrics from a Bandit report."""
    results = report.get('results', [])
    
    # Count by severity
    severity_counts = defaultdict(int)
    for issue in results:
        severity_counts[issue['issue_severity']] += 1
    
    # Count by test ID
    test_counts = defaultdict(int)
    for issue in results:
        test_counts[issue['test_id']] += 1
    
    # Group by file
    file_issues = defaultdict(list)
    for issue in results:
        file_issues[issue['filename']].append(issue)
    
    return {
        'total': len(results),
        'high': severity_counts.get('HIGH', 0),
        'medium': severity_counts.get('MEDIUM', 0),
        'low': severity_counts.get('LOW', 0),
        'test_counts': dict(test_counts),
        'file_issues': dict(file_issues),
        'metrics': report.get('metrics', {})
    }

def main():
    # Load reports
    print("Loading Bandit reports...")
    original = load_report('bandit-report.json')
    new = load_report('bandit-report-post-fix.json')
    
    # Analyze both
    print("Analyzing reports...")
    original_stats = analyze_report(original)
    new_stats = analyze_report(new)
    
    # Print summary
    print("\n" + "="*80)
    print("BANDIT SECURITY SCAN COMPARISON")
    print("="*80)
    
    print("\n📊 OVERALL METRICS:")
    print(f"  Total Issues:  {original_stats['total']} → {new_stats['total']} (Δ {new_stats['total'] - original_stats['total']:+d})")
    print(f"  HIGH severity: {original_stats['high']} → {new_stats['high']} (Δ {new_stats['high'] - original_stats['high']:+d})")
    print(f"  MEDIUM:        {original_stats['medium']} → {new_stats['medium']} (Δ {new_stats['medium'] - original_stats['medium']:+d})")
    print(f"  LOW:           {original_stats['low']} → {new_stats['low']} (Δ {new_stats['low'] - original_stats['low']:+d})")
    
    print("\n🎯 KEY SECURITY FIXES:")
    
    # B602 - shell injection
    b602_before = original_stats['test_counts'].get('B602', 0)
    b602_after = new_stats['test_counts'].get('B602', 0)
    print(f"  B602 (shell injection): {b602_before} → {b602_after} (Δ {b602_after - b602_before:+d})")
    
    # B324 - weak MD5
    b324_before = original_stats['test_counts'].get('B324', 0)
    b324_after = new_stats['test_counts'].get('B324', 0)
    print(f"  B324 (weak MD5 hash):   {b324_before} → {b324_after} (Δ {b324_after - b324_before:+d})")
    
    print("\n📈 ISSUE TYPE BREAKDOWN:")
    all_tests = set(original_stats['test_counts'].keys()) | set(new_stats['test_counts'].keys())
    for test_id in sorted(all_tests):
        before = original_stats['test_counts'].get(test_id, 0)
        after = new_stats['test_counts'].get(test_id, 0)
        if before != after:
            delta = after - before
            print(f"  {test_id}: {before} → {after} ({delta:+d})")
    
    # Find fixed files
    print("\n✅ FIXED FILES:")
    original_files = set(original_stats['file_issues'].keys())
    new_files = set(new_stats['file_issues'].keys())
    fixed_files = original_files - new_files
    
    if fixed_files:
        for filepath in sorted(fixed_files):
            issues = original_stats['file_issues'][filepath]
            print(f"  ✓ {filepath} - {len(issues)} issue(s) resolved")
    else:
        print("  (None - issues reduced in existing files)")
    
    # Remaining issues by file
    if new_stats['file_issues']:
        print("\n⚠️  REMAINING ISSUES BY FILE:")
        for filepath in sorted(new_stats['file_issues'].keys()):
            issues = new_stats['file_issues'][filepath]
            high = sum(1 for i in issues if i['issue_severity'] == 'HIGH')
            medium = sum(1 for i in issues if i['issue_severity'] == 'MEDIUM')
            low = sum(1 for i in issues if i['issue_severity'] == 'LOW')
            
            severity_str = []
            if high: severity_str.append(f"{high}H")
            if medium: severity_str.append(f"{medium}M")
            if low: severity_str.append(f"{low}L")
            
            print(f"  • {filepath}: {', '.join(severity_str)}")
    else:
        print("\n🎉 NO REMAINING ISSUES!")
    
    print("\n" + "="*80)
    
    # Save detailed comparison as JSON
    comparison = {
        'original': original_stats,
        'new': new_stats,
        'delta': {
            'total': new_stats['total'] - original_stats['total'],
            'high': new_stats['high'] - original_stats['high'],
            'medium': new_stats['medium'] - original_stats['medium'],
            'low': new_stats['low'] - original_stats['low']
        }
    }
    
    with open('bandit_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2)
    
    print("✓ Detailed comparison saved to: bandit_comparison.json")
    
    # Exit with appropriate code
    if new_stats['high'] == 0:
        print("\n✅ SUCCESS: All HIGH severity issues resolved!")
        return 0
    else:
        print(f"\n⚠️  WARNING: {new_stats['high']} HIGH severity issue(s) remaining")
        return 1

if __name__ == '__main__':
    sys.exit(main())
