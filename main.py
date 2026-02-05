#!/usr/bin/env python3
"""
VCS - Version Control System with Secure Commit Tracking
========================================================

Main entry point for the Version Control System.

Usage:
    python main.py <command> [arguments]
    
Or make executable and use directly:
    chmod +x main.py
    ./main.py <command> [arguments]

For help:
    python main.py help

Author: VCS Development Team
Date: 2025
"""

import sys
from cli import CLIHandler


def main():
    """
    Main entry point for VCS application.
    
    Delegates to CLI handler for command processing.
    """
    if len(sys.argv) < 2:
        print("VCS - Version Control System")
        print("Usage: python main.py <command> [arguments]")
        print("Try: python main.py help")
        sys.exit(0)
    
    # Create CLI handler and process commands
    cli = CLIHandler()
    cli.run(sys.argv[1:])


if __name__ == '__main__':
    main()
