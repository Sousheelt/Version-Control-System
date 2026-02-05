"""CLI Handler for VCS - Command pattern for user interaction."""

import sys
import argparse
from typing import List
from repository import Repository
from pathlib import Path


class CLIHandler:
    """CLI handler mapping user commands to Repository operations."""
    
    def __init__(self):
        self.repo: Repository = None
        self.repo_path = Path.cwd()
    
    def run(self, args: List[str]):
        """Main entry point for CLI."""
        if not args:
            self.print_help()
            return
        
        command, command_args = args[0], args[1:]
        
        # Commands not needing repo
        if command == 'init':
            self.cmd_init(command_args)
            return
        elif command == 'help':
            self.print_help()
            return
        
        # Load repository
        self._load_repository()
        
        # Execute command
        commands = {
            'add': self.cmd_add, 'commit': self.cmd_commit, 'status': self.cmd_status,
            'log': self.cmd_log, 'rollback': self.cmd_rollback, 'branch': self.cmd_branch,
            'checkout': self.cmd_checkout, 'branches': self.cmd_branches,
            'merge': self.cmd_merge, 'graph': self.cmd_graph, 'audit': self.cmd_audit
        }
        
        if command in commands:
            try:
                commands[command](command_args)
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"Unknown command: {command}. Use 'help' for available commands.")
    
    def _load_repository(self):
        """Load repository or exit."""
        vcs_dir = self.repo_path / '.vcs'
        if not vcs_dir.exists():
            print("Error: Not a VCS repository. Run 'vcs init' to initialize.")
            sys.exit(1)
        self.repo = Repository.load(str(self.repo_path))
    
    def cmd_init(self, args: List[str]):
        """Initialize repository."""
        self.repo = Repository(str(self.repo_path))
        print(self.repo.init())
    
    def cmd_add(self, args: List[str]):
        """Add file(s) to staging."""
        if not args:
            print("Usage: vcs add <file> [<file2> ...]")
            return
        for filepath in args:
            print(self.repo.add(filepath))
    
    def cmd_commit(self, args: List[str]):
        """Create commit."""
        parser = argparse.ArgumentParser(prog='vcs commit')
        parser.add_argument('-m', '--message', required=True, help='Commit message')
        parser.add_argument('-a', '--author', default='default', help='Author')
        try:
            parsed = parser.parse_args(args)
            print(self.repo.commit(parsed.message, parsed.author))
        except SystemExit:
            pass
    
    def cmd_status(self, args: List[str]):
        """Show status."""
        print(self.repo.status())
    
    def cmd_log(self, args: List[str]):
        """Display history."""
        parser = argparse.ArgumentParser(prog='vcs log')
        parser.add_argument('-n', '--number', type=int, help='Limit commits')
        try:
            parsed = parser.parse_args(args)
            print(self.repo.log(parsed.number))
        except SystemExit:
            pass
    
    def cmd_rollback(self, args: List[str]):
        """Rollback commits."""
        steps = 1
        if args:
            try:
                steps = int(args[0])
            except ValueError:
                print("Error: steps must be a number")
                return
        print(self.repo.rollback(steps))
    
    def cmd_branch(self, args: List[str]):
        """Create branch."""
        if not args:
            print("Usage: vcs branch <name>")
            return
        print(self.repo.create_branch(args[0]))
    
    def cmd_checkout(self, args: List[str]):
        """Switch branch."""
        if not args:
            print("Usage: vcs checkout <branch>")
            return
        print(self.repo.switch_branch(args[0]))
    
    def cmd_branches(self, args: List[str]):
        """List branches."""
        print(self.repo.list_branches())
    
    def cmd_merge(self, args: List[str]):
        """Merge branch."""
        if not args:
            print("Usage: vcs merge <branch>")
            return
        print(self.repo.merge(args[0]))
    
    def cmd_graph(self, args: List[str]):
        """Visualize commit graph."""
        parser = argparse.ArgumentParser(prog='vcs graph')
        parser.add_argument('-o', '--output', help='Output file')
        parser.add_argument('--format', choices=['png', 'dot'], default='png')
        try:
            parsed = parser.parse_args(args)
            
            if parsed.format == 'dot':
                dot_content = self.repo.get_commit_graph_dot()
                output_file = parsed.output or 'graph.dot'
                with open(output_file, 'w') as f:
                    f.write(dot_content)
                print(f"Commit graph saved to {output_file}")
            else:
                try:
                    from visualization import visualize_commit_graph
                    output_file = parsed.output or 'graph.png'
                    visualize_commit_graph(self.repo, output_file)
                    print(f"Commit graph saved to {output_file}")
                except ImportError:
                    print("Visualization unavailable. Install: pip install networkx matplotlib")
        except SystemExit:
            pass
    
    def cmd_audit(self, args: List[str]):
        """Show audit log."""
        print(self.repo.get_audit_log())
    
    def print_help(self):
        """Print help."""
        print("""VCS - Version Control System

Usage: vcs <command> [arguments]

Commands:
  init                    Initialize repository
  add <file> [...]       Add files to staging
  commit -m "msg"        Create commit (-a "author" optional)
  status                 Show status
  log [-n <num>]         Show history
  rollback [steps]       Undo commits (default: 1)
  branch <name>          Create branch
  checkout <branch>      Switch branch
  branches               List branches
  merge <branch>         Merge branch
  graph [-o file]        Visualize DAG (--format: png|dot)
  audit                  Show audit log
  help                   Show this help

Features: DAG • SHA-256 • Merkle Trees • Branch/Merge • Rollback • Audit Trail
""")


def main():
    cli = CLIHandler()
    cli.run(sys.argv[1:])


if __name__ == '__main__':
    main()
