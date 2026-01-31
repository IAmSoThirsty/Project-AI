#!/usr/bin/env python3
"""
Complete Documentation Maintenance System

Integrates test documentation updates and historical document organization.
This is the master script that should be run after CI tests complete.

Features:
1. Parse CI test artifacts and update documentation
2. Organize obsolete documents into historical folder
3. Update all references
4. Generate comprehensive reports
5. Commit changes to git
"""

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('documentation_maintenance.log')
    ]
)
logger = logging.getLogger(__name__)


class DocumentationMaintenanceSystem:
    """Master documentation maintenance system."""
    
    def __init__(self, dry_run: bool = False, skip_commit: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.skip_commit = skip_commit
        self.verbose = verbose
        self.logger = logging.getLogger(f"{__name__}.DocumentationMaintenanceSystem")
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
    
    def run_test_documentation_updater(self) -> bool:
        """Run the test documentation updater."""
        self.logger.info("=" * 80)
        self.logger.info("STEP 1: UPDATE TEST DOCUMENTATION")
        self.logger.info("=" * 80)
        
        cmd = ['python3', 'scripts/update_test_documentation.py']
        
        if self.dry_run:
            cmd.append('--dry-run')
        
        if self.skip_commit:
            cmd.append('--no-commit')
        
        if self.verbose:
            cmd.append('--verbose')
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info("Test documentation updater completed successfully")
            
            if self.verbose:
                self.logger.debug(result.stdout)
            
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Test documentation updater failed: {e}")
            if e.output:
                self.logger.error(e.output)
            return False
        except Exception as e:
            self.logger.error(f"Error running test documentation updater: {e}")
            return False
    
    def run_historical_docs_organizer(self, check_age: bool = True, age_threshold: int = 7) -> bool:
        """Run the historical docs organizer."""
        self.logger.info("=" * 80)
        self.logger.info("STEP 2: ORGANIZE HISTORICAL DOCUMENTATION")
        self.logger.info("=" * 80)
        
        cmd = ['python3', 'scripts/organize_historical_docs.py']
        
        if self.dry_run:
            cmd.append('--dry-run')
        
        if check_age:
            cmd.append('--check-age')
            cmd.extend(['--age-threshold', str(age_threshold)])
        else:
            cmd.append('--no-check-age')
        
        if self.verbose:
            cmd.append('--verbose')
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info("Historical docs organizer completed successfully")
            
            if self.verbose:
                self.logger.debug(result.stdout)
            
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Historical docs organizer failed: {e}")
            if e.output:
                self.logger.error(e.output)
            return False
        except Exception as e:
            self.logger.error(f"Error running historical docs organizer: {e}")
            return False
    
    def generate_master_report(self) -> None:
        """Generate master report of all maintenance activities."""
        self.logger.info("=" * 80)
        self.logger.info("STEP 3: GENERATE MASTER REPORT")
        self.logger.info("=" * 80)
        
        report = f"""# Documentation Maintenance Report

**Generated:** {datetime.now().isoformat()}
**Mode:** {'DRY RUN' if self.dry_run else 'PRODUCTION'}

## Activities Completed

### ✅ Test Documentation Update

The test documentation updater has processed CI artifacts and updated the following:

- Test statistics and badges
- Category-level pass/fail counts
- Failed test examples
- Overall test status

**Report:** See `test_documentation_update_summary.md`

### ✅ Historical Documentation Organization

The historical documentation organizer has:

- Identified obsolete documents
- Moved them to `docs/historical/`
- Updated all references in active files
- Created historical index

**Report:** See `historical_docs_organization_report.md`

## Next Steps

1. Review the generated reports
2. Verify that documentation is accurate
3. Commit changes if running in production mode
4. Push to remote repository

## Files Modified

Run `git status` to see all modified files.

## Logs

- Test Documentation Updater: `test_report_updater.log`
- Historical Docs Organizer: `historical_docs_organizer.log`
- Master System: `documentation_maintenance.log`

---

*Generated by Documentation Maintenance System v1.0.0*
"""
        
        report_path = Path("documentation_maintenance_report.md")
        report_path.write_text(report)
        
        self.logger.info(f"Master report saved to {report_path}")
    
    def commit_changes(self) -> bool:
        """Commit all documentation changes."""
        if self.skip_commit or self.dry_run:
            self.logger.info("Skipping commit step (dry-run or skip-commit enabled)")
            return True
        
        self.logger.info("=" * 80)
        self.logger.info("STEP 4: COMMIT CHANGES")
        self.logger.info("=" * 80)
        
        try:
            # Check if there are changes to commit
            result = subprocess.run(['git', 'diff', '--quiet'], capture_output=True)
            
            if result.returncode == 0:
                self.logger.info("No changes to commit")
                return True
            
            # Configure git
            subprocess.run(['git', 'config', 'user.name', 'Documentation Maintainer'], check=True)
            subprocess.run(['git', 'config', 'user.email', 'ci@project-ai.local'], check=True)
            
            # Add all documentation changes
            self.logger.info("Adding documentation changes...")
            subprocess.run(['git', 'add', '*.md'], check=True)
            subprocess.run(['git', 'add', 'docs/'], check=True)
            subprocess.run(['git', 'add', '.test-report-updater.config.json'], check=True)
            subprocess.run(['git', 'add', 'scripts/'], check=True)
            
            # Commit
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_message = f"chore: automated documentation maintenance [{timestamp}]"
            
            self.logger.info(f"Committing with message: {commit_message}")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            self.logger.info("Successfully committed documentation changes")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error committing changes: {e}")
            return False
    
    def run(self, check_age: bool = True, age_threshold: int = 7) -> int:
        """Run the complete maintenance system."""
        self.logger.info("=" * 80)
        self.logger.info("DOCUMENTATION MAINTENANCE SYSTEM")
        self.logger.info("=" * 80)
        self.logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'PRODUCTION'}")
        self.logger.info(f"Skip Commit: {self.skip_commit}")
        self.logger.info(f"Check Age: {check_age} (threshold: {age_threshold} days)")
        self.logger.info("=" * 80)
        
        # Step 1: Update test documentation
        if not self.run_test_documentation_updater():
            self.logger.error("Test documentation update failed")
            return 1
        
        # Step 2: Organize historical docs
        if not self.run_historical_docs_organizer(check_age, age_threshold):
            self.logger.error("Historical docs organization failed")
            return 1
        
        # Step 3: Generate master report
        self.generate_master_report()
        
        # Step 4: Commit changes (if not dry-run)
        if not self.commit_changes():
            self.logger.error("Failed to commit changes")
            return 1
        
        # Summary
        self.logger.info("=" * 80)
        self.logger.info("DOCUMENTATION MAINTENANCE COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info("All steps completed successfully")
        self.logger.info("Review reports:")
        self.logger.info("  - documentation_maintenance_report.md")
        self.logger.info("  - test_documentation_update_summary.md")
        self.logger.info("  - historical_docs_organization_report.md")
        
        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Complete Documentation Maintenance System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script integrates:
1. Test documentation updates from CI artifacts
2. Historical documentation organization
3. Automated git commits

Examples:
  # Run complete maintenance (production)
  python run_documentation_maintenance.py

  # Dry run to preview changes
  python run_documentation_maintenance.py --dry-run

  # Skip git commit step
  python run_documentation_maintenance.py --no-commit

  # Check files older than 14 days
  python run_documentation_maintenance.py --age-threshold 14

  # Disable age checking
  python run_documentation_maintenance.py --no-check-age

  # Verbose output
  python run_documentation_maintenance.py --verbose
        """
    )
    
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='Run without making changes')
    parser.add_argument('--no-commit', action='store_true',
                       help='Skip git commit step')
    parser.add_argument('--check-age', action='store_true', default=True,
                       help='Check file age for obsolescence (default: enabled)')
    parser.add_argument('--no-check-age', action='store_false', dest='check_age',
                       help='Disable age-based checking')
    parser.add_argument('--age-threshold', type=int, default=7,
                       help='Age threshold in days (default: 7)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Create system
    system = DocumentationMaintenanceSystem(
        dry_run=args.dry_run,
        skip_commit=args.no_commit,
        verbose=args.verbose
    )
    
    # Run
    return system.run(
        check_age=args.check_age,
        age_threshold=args.age_threshold
    )


if __name__ == '__main__':
    sys.exit(main())
