"""
Demo Script for VCS - Version Control System
============================================

This script demonstrates all features of the VCS system including:
- Repository initialization
- File staging and commits
- Branch creation and switching
- Merging with conflict detection
- Rollback operations
- Audit trail
- Graph visualization

Run this script to see the VCS in action!
"""

import os
import sys
import shutil
from pathlib import Path


def create_test_file(filename: str, content: str):
    """Helper to create test files."""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"  Created: {filename}")


def run_vcs_command(command: str):
    """Helper to run VCS commands."""
    print(f"\n$ vcs {command}")
    os.system(f"python main.py {command}")


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo():
    """Run comprehensive VCS demonstration."""
    
    print("=" * 70)
    print("  VCS DEMONSTRATION - Git-like Version Control System")
    print("=" * 70)
    
    # Setup test directory
    test_dir = Path("vcs_demo")
    
    # Clean up if exists
    if test_dir.exists():
        print(f"\nCleaning up existing demo directory: {test_dir}")
        shutil.rmtree(test_dir)
    
    # Create and enter test directory
    test_dir.mkdir()
    os.chdir(test_dir)
    print(f"Created test directory: {test_dir.absolute()}")
    
    # ========================================================================
    print_section("1. INITIALIZE REPOSITORY")
    # ========================================================================
    run_vcs_command("init")
    
    # ========================================================================
    print_section("2. CREATE INITIAL FILES")
    # ========================================================================
    print("\nCreating test files...")
    create_test_file("README.md", "# My Project\n\nThis is a test project.")
    create_test_file("main.py", "def main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()")
    create_test_file("config.txt", "version=1.0\nauthor=demo")
    
    # ========================================================================
    print_section("3. CHECK STATUS")
    # ========================================================================
    run_vcs_command("status")
    
    # ========================================================================
    print_section("4. STAGE FILES")
    # ========================================================================
    run_vcs_command("add README.md main.py config.txt")
    run_vcs_command("status")
    
    # ========================================================================
    print_section("5. CREATE INITIAL COMMIT")
    # ========================================================================
    run_vcs_command('commit -m "Initial commit" -a "Alice"')
    
    # ========================================================================
    print_section("6. VIEW COMMIT LOG")
    # ========================================================================
    run_vcs_command("log")
    
    # ========================================================================
    print_section("7. CREATE FEATURE BRANCH")
    # ========================================================================
    run_vcs_command("branch feature-x")
    run_vcs_command("branches")
    
    # ========================================================================
    print_section("8. SWITCH TO FEATURE BRANCH")
    # ========================================================================
    run_vcs_command("checkout feature-x")
    
    # ========================================================================
    print_section("9. MAKE CHANGES ON FEATURE BRANCH")
    # ========================================================================
    print("\nModifying files on feature branch...")
    create_test_file("feature.py", "def new_feature():\n    return 'This is a new feature!'")
    create_test_file("main.py", "def main():\n    print('Hello from feature branch!')\n\nif __name__ == '__main__':\n    main()")
    
    run_vcs_command("add feature.py main.py")
    run_vcs_command('commit -m "Add new feature" -a "Bob"')
    
    # ========================================================================
    print_section("10. SWITCH BACK TO MAIN BRANCH")
    # ========================================================================
    run_vcs_command("checkout main")
    
    # ========================================================================
    print_section("11. MAKE CHANGES ON MAIN BRANCH")
    # ========================================================================
    print("\nModifying files on main branch...")
    create_test_file("config.txt", "version=1.1\nauthor=demo\ndate=2025")
    run_vcs_command("add config.txt")
    run_vcs_command('commit -m "Update config" -a "Alice"')
    
    # ========================================================================
    print_section("12. VIEW BRANCHES")
    # ========================================================================
    run_vcs_command("branches")
    
    # ========================================================================
    print_section("13. VIEW COMMIT HISTORY (MAIN)")
    # ========================================================================
    run_vcs_command("log -n 5")
    
    # ========================================================================
    print_section("14. MERGE FEATURE BRANCH (NO CONFLICTS)")
    # ========================================================================
    print("\nMerging feature-x into main...")
    run_vcs_command("merge feature-x")
    
    # ========================================================================
    print_section("15. VIEW LOG AFTER MERGE")
    # ========================================================================
    run_vcs_command("log -n 5")
    
    # ========================================================================
    print_section("16. CREATE ANOTHER BRANCH FOR CONFLICT DEMO")
    # ========================================================================
    run_vcs_command("branch conflict-branch")
    run_vcs_command("checkout conflict-branch")
    
    print("\nModifying config.txt on conflict-branch...")
    create_test_file("config.txt", "version=2.0\nauthor=conflict\nmode=test")
    run_vcs_command("add config.txt")
    run_vcs_command('commit -m "Change config on conflict branch" -a "Charlie"')
    
    # ========================================================================
    print_section("17. CREATE CONFLICTING CHANGE ON MAIN")
    # ========================================================================
    run_vcs_command("checkout main")
    print("\nModifying config.txt on main (creating conflict)...")
    create_test_file("config.txt", "version=2.0\nauthor=main\nmode=production")
    run_vcs_command("add config.txt")
    run_vcs_command('commit -m "Change config on main" -a "Alice"')
    
    # ========================================================================
    print_section("18. ATTEMPT MERGE WITH CONFLICTS")
    # ========================================================================
    print("\nAttempting to merge conflict-branch (this will detect conflicts)...")
    run_vcs_command("merge conflict-branch")
    
    # ========================================================================
    print_section("19. DEMONSTRATE ROLLBACK")
    # ========================================================================
    print("\nRolling back 1 commit...")
    run_vcs_command("rollback 1")
    run_vcs_command("log -n 3")
    
    # ========================================================================
    print_section("20. VIEW AUDIT LOG")
    # ========================================================================
    run_vcs_command("audit")
    
    # ========================================================================
    print_section("21. GENERATE COMMIT GRAPH (DOT FORMAT)")
    # ========================================================================
    print("\nGenerating commit graph in DOT format...")
    run_vcs_command("graph --format dot -o commits.dot")
    
    if Path("commits.dot").exists():
        print("\n✓ DOT file created successfully!")
        print("  To render: dot -Tpng commits.dot -o commits.png")
    
    # ========================================================================
    print_section("22. TRY VISUALIZATION (if dependencies available)")
    # ========================================================================
    print("\nAttempting to generate PNG visualization...")
    run_vcs_command("graph -o commits.png")
    
    if Path("commits.png").exists():
        print("\n✓ Visualization created successfully!")
    else:
        print("\n⚠ Visualization requires: pip install networkx matplotlib")
    
    # ========================================================================
    print_section("DEMONSTRATION COMPLETE!")
    # ========================================================================
    print("\nAll VCS features demonstrated:")
    print("  ✓ Repository initialization")
    print("  ✓ File staging and commits")
    print("  ✓ Branch creation and switching")
    print("  ✓ Merging without conflicts")
    print("  ✓ Conflict detection")
    print("  ✓ Rollback operations")
    print("  ✓ Audit trail")
    print("  ✓ Graph generation")
    
    print(f"\nTest directory: {Path.cwd()}")
    print("\nYou can explore the .vcs directory to see internals:")
    print("  - .vcs/commits/     - Serialized commit objects")
    print("  - .vcs/state.json   - Repository state")
    print("  - commits.dot       - Graph in DOT format")
    
    # Return to parent directory
    os.chdir("..")
    
    print("\n" + "=" * 70)
    print("  Demo completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
