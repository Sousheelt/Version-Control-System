"""Repository - Core VCS managing DAG, branches, staging, and rollback."""

import os
import json
import pickle
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from commit import Commit
from pathlib import Path


class Repository:
    """Main repository managing commits (HashMap), DAG (Adjacency List), branches, staging, and rollback stack."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.vcs_dir = self.repo_path / '.vcs'
        self.commits: Dict[str, Commit] = {}  # Hash map for O(1) lookup
        self.commit_graph: Dict[str, List[str]] = {}  # Adjacency list for DAG
        self.branches: Dict[str, str] = {}
        self.staging_area: Dict[str, str] = {}
        self.rollback_stack: List[str] = []
        self.current_branch: str = 'main'
        self.head: Optional[str] = None
        self.audit_log: List[Dict] = []
    
    def init(self) -> str:
        """Initialize repository with .vcs structure."""
        if self.vcs_dir.exists():
            return "Repository already initialized"
        
        self.vcs_dir.mkdir(parents=True)
        (self.vcs_dir / 'commits').mkdir()
        (self.vcs_dir / 'objects').mkdir()
        (self.vcs_dir / 'refs').mkdir()
        
        self.branches['main'] = None
        self.current_branch = 'main'
        self._save_repo_state()
        self._log_action('init', 'Repository initialized')
        
        return f"Initialized empty VCS repository in {self.vcs_dir}"
    
    def add(self, filepath: str) -> str:
        """Add file to staging area."""
        full_path = self.repo_path / filepath
        if not full_path.exists():
            return f"Error: File '{filepath}' not found"
        
        if full_path.is_dir():
            return f"Error: '{filepath}' is a directory. Add files individually."
        
        try:
            # Read file in binary mode first to detect encoding
            with open(full_path, 'rb') as f:
                raw_content = f.read()
            
            # Try to decode with proper encoding detection
            try:
                # Check for UTF-16 BOM
                if raw_content.startswith(b'\xff\xfe') or raw_content.startswith(b'\xfe\xff'):
                    content = raw_content.decode('utf-16')
                # Check for UTF-8 BOM
                elif raw_content.startswith(b'\xef\xbb\xbf'):
                    content = raw_content.decode('utf-8-sig')
                else:
                    # Default to UTF-8
                    content = raw_content.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to latin-1 which never fails
                content = raw_content.decode('latin-1')
            
            self.staging_area[filepath] = content
            self._save_repo_state()
            self._log_action('add', f'Staged {filepath}')
            return f"Added '{filepath}' to staging area"
        except Exception as e:
            return f"Error reading '{filepath}': {e}"
    
    def commit(self, message: str, author: str = "default") -> str:
        """Create commit from staged files."""
        if not self.staging_area:
            return "Nothing to commit (staging area empty)"
        
        parents = [self.head] if self.head else []
        commit = Commit(message, self.staging_area.copy(), parents, author)
        
        # Update data structures
        self.commits[commit.hash] = commit
        if self.head:
            self.rollback_stack.append(self.head)
            self.commit_graph.setdefault(self.head, []).append(commit.hash)
        
        self.head = commit.hash
        self.branches[self.current_branch] = commit.hash
        
        # Save commit to disk
        commit_file = self.vcs_dir / 'commits' / f'{commit.hash}.pkl'
        with open(commit_file, 'wb') as f:
            pickle.dump(commit, f)
        
        self.staging_area.clear()
        self._save_repo_state()
        self._log_action('commit', f'{commit.hash[:8]}: {message}')
        
        return f"[{self.current_branch} {commit.hash[:8]}] {message}\n {len(commit.files)} file(s) changed"
    
    def status(self) -> str:
        """Show current branch, HEAD, and staged files."""
        output = [f"On branch: {self.current_branch}"]
        
        if self.head:
            commit = self.commits.get(self.head)
            output.append(f"HEAD: {self.head[:8]} - {commit.message if commit else 'Unknown'}")
        else:
            output.append("No commits yet")
        
        if self.staging_area:
            output.append(f"\nStaged files ({len(self.staging_area)}):")
            output.extend(f"  - {f}" for f in self.staging_area.keys())
        else:
            output.append("\nNothing staged")
        
        return '\n'.join(output)
    
    def log(self, limit: Optional[int] = None) -> str:
        """Display commit history from HEAD."""
        if not self.head:
            return "No commits yet"
        
        output, visited, count = [], set(), 0
        stack = [self.head]
        
        while stack and (limit is None or count < limit):
            hash = stack.pop()
            if hash in visited:
                continue
            
            visited.add(hash)
            commit = self.commits.get(hash)
            if not commit:
                continue
            
            output.append(f"commit {hash}")
            output.append(f"Author: {commit.author}")
            output.append(f"Date:   {commit.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            output.append(f"\n    {commit.message}\n")
            
            stack.extend(commit.parents)
            count += 1
        
        return '\n'.join(output)
    
    def rollback(self, steps: int = 1) -> str:
        """Undo last N commits using stack."""
        if not self.head:
            return "No commits to rollback"
        
        if steps <= 0:
            return "Steps must be positive"
        
        if len(self.rollback_stack) < steps:
            return f"Cannot rollback {steps} steps (only {len(self.rollback_stack)} available)"
        
        # Pop from stack
        for _ in range(steps):
            if self.rollback_stack:
                self.head = self.rollback_stack.pop()
        
        self.branches[self.current_branch] = self.head
        
        # Restore files
        if self.head:
            commit = self.commits[self.head]
            for filename, content in commit.files.items():
                filepath = self.repo_path / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        self._save_repo_state()
        self._log_action('rollback', f'Rolled back {steps} commit(s)')
        
        return f"Rolled back {steps} commit(s)\nHEAD now at: {self.head[:8] if self.head else 'None'}"
    
    def create_branch(self, branch_name: str) -> str:
        """Create new branch at current HEAD."""
        if branch_name in self.branches:
            return f"Branch '{branch_name}' already exists"
        
        self.branches[branch_name] = self.head
        self._save_repo_state()
        self._log_action('branch', f'Created {branch_name}')
        
        return f"Created branch '{branch_name}'"
    
    def switch_branch(self, branch_name: str) -> str:
        """Switch to different branch."""
        if branch_name not in self.branches:
            return f"Branch '{branch_name}' does not exist"
        
        self.current_branch = branch_name
        self.head = self.branches[branch_name]
        
        # Restore files from branch HEAD
        if self.head:
            commit = self.commits[self.head]
            for filename, content in commit.files.items():
                filepath = self.repo_path / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        self._save_repo_state()
        self._log_action('checkout', f'Switched to {branch_name}')
        
        return f"Switched to branch '{branch_name}'\nHEAD at {self.head[:8] if self.head else 'None'}: {self.commits[self.head].message if self.head else ''}"
    
    def list_branches(self) -> str:
        """List all branches."""
        if not self.branches:
            return "No branches"
        
        output = ["Branches:"]
        for name, hash in self.branches.items():
            marker = '*' if name == self.current_branch else ' '
            hash_str = hash[:8] if hash else 'None'
            output.append(f"  {marker} {name} -> {hash_str}")
        
        return '\n'.join(output)
    
    def merge(self, source_branch: str) -> str:
        """Merge source branch into current branch."""
        if source_branch not in self.branches:
            return f"Branch '{source_branch}' does not exist"
        
        if source_branch == self.current_branch:
            return "Cannot merge branch into itself"
        
        source_hash = self.branches[source_branch]
        if not source_hash:
            return f"Branch '{source_branch}' has no commits"
        
        if not self.head:
            return "Current branch has no commits"
        
        # Fast-forward if possible
        if self._is_ancestor(self.head, source_hash):
            self.head = source_hash
            self.branches[self.current_branch] = source_hash
            self._save_repo_state()
            return f"Fast-forward merge: {source_branch} into {self.current_branch}"
        
        # Already merged
        if self._is_ancestor(source_hash, self.head):
            return f"Already up to date"
        
        # Find common ancestor
        ancestor_hash = self._find_common_ancestor(self.head, source_hash)
        
        if not ancestor_hash:
            return "No common ancestor found - cannot merge unrelated histories"
        
        # Detect conflicts
        current_commit = self.commits[self.head]
        source_commit = self.commits[source_hash]
        ancestor_commit = self.commits[ancestor_hash]
        
        conflicts = self._detect_conflicts(current_commit, source_commit, ancestor_commit)
        
        if conflicts:
            return f"Merge conflict detected in {len(conflicts)} file(s): {', '.join(conflicts)}\nPlease resolve manually, then add and commit."
        
        # Merge files
        merged_files = current_commit.files.copy()
        for filename, content in source_commit.files.items():
            if filename not in merged_files or merged_files[filename] != content:
                merged_files[filename] = content
        
        # Create merge commit
        merge_commit = Commit(
            f"Merge branch '{source_branch}' into {self.current_branch}",
            merged_files,
            [self.head, source_hash],
            "system"
        )
        
        self.commits[merge_commit.hash] = merge_commit
        self.commit_graph.setdefault(self.head, []).append(merge_commit.hash)
        self.commit_graph.setdefault(source_hash, []).append(merge_commit.hash)
        
        commit_file = self.vcs_dir / 'commits' / f'{merge_commit.hash}.pkl'
        with open(commit_file, 'wb') as f:
            pickle.dump(merge_commit, f)
        
        self.head = merge_commit.hash
        self.branches[self.current_branch] = merge_commit.hash
        self._save_repo_state()
        self._log_action('merge', f'{source_branch} into {self.current_branch}')
        
        return f"Merged '{source_branch}' into '{self.current_branch}'\nMerge commit: {merge_commit.hash[:8]}"
    
    def _is_ancestor(self, ancestor_hash: str, descendant_hash: str) -> bool:
        """Check if ancestor_hash is ancestor of descendant_hash using BFS."""
        visited, queue = set(), [descendant_hash]
        
        while queue:
            current = queue.pop(0)
            if current == ancestor_hash:
                return True
            if current in visited:
                continue
            
            visited.add(current)
            commit = self.commits.get(current)
            if commit:
                queue.extend(commit.parents)
        
        return False
    
    def _find_common_ancestor(self, hash1: str, hash2: str) -> Optional[str]:
        """Find LCA of two commits using BFS."""
        ancestors1 = set()
        queue = [hash1]
        
        while queue:
            current = queue.pop(0)
            if current in ancestors1:
                continue
            ancestors1.add(current)
            commit = self.commits.get(current)
            if commit:
                queue.extend(commit.parents)
        
        queue = [hash2]
        visited = set()
        
        while queue:
            current = queue.pop(0)
            if current in ancestors1:
                return current
            if current in visited:
                continue
            visited.add(current)
            commit = self.commits.get(current)
            if commit:
                queue.extend(commit.parents)
        
        return None
    
    def _detect_conflicts(self, commit1: Commit, commit2: Commit, ancestor: Commit) -> List[str]:
        """Detect merge conflicts between two commits."""
        conflicts = []
        all_files = set(commit1.files.keys()) | set(commit2.files.keys()) | set(ancestor.files.keys())
        
        for filename in all_files:
            in1, in2, in_anc = filename in commit1.files, filename in commit2.files, filename in ancestor.files
            
            if in1 and in2:
                if commit1.files[filename] != commit2.files[filename]:
                    if in_anc:
                        if (commit1.files[filename] != ancestor.files[filename] and 
                            commit2.files[filename] != ancestor.files[filename]):
                            conflicts.append(filename)
                    else:
                        conflicts.append(filename)
        
        return conflicts
    
    def get_commit_graph_dot(self) -> str:
        """Generate DOT format for Graphviz."""
        lines = ['digraph CommitGraph {', '  rankdir=BT;']
        
        for hash, commit in self.commits.items():
            short = hash[:8]
            label = f"{short}\\n{commit.message[:20]}"
            lines.append(f'  "{short}" [label="{label}"];')
            for parent in commit.parents:
                lines.append(f'  "{short}" -> "{parent[:8]}";')
        
        lines.append('}')
        return '\n'.join(lines)
    
    def _log_action(self, action: str, details: str):
        """Record action in audit log."""
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        })
    
    def get_audit_log(self) -> str:
        """Return formatted audit log."""
        if not self.audit_log:
            return "No actions recorded"
        
        output = ["Audit Log:"]
        for entry in self.audit_log:
            output.append(f"[{entry['timestamp']}] {entry['action']}: {entry['details']}")
        return '\n'.join(output)
    
    def _save_repo_state(self):
        """Persist repository state to .vcs/state.json."""
        state = {
            'current_branch': self.current_branch,
            'head': self.head,
            'branches': self.branches,
            'staging_area': self.staging_area,
            'rollback_stack': self.rollback_stack,
            'commit_hashes': list(self.commits.keys()),
            'commit_graph': self.commit_graph,
            'audit_log': self.audit_log
        }
        
        with open(self.vcs_dir / 'state.json', 'w') as f:
            json.dump(state, f, indent=2)
    
    @staticmethod
    def load(repo_path: str) -> 'Repository':
        """Load repository from disk."""
        repo = Repository(repo_path)
        state_file = repo.vcs_dir / 'state.json'
        
        if not state_file.exists():
            raise FileNotFoundError("Repository not initialized")
        
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        repo.current_branch = state.get('current_branch', 'main')
        repo.head = state.get('head')
        repo.branches = state.get('branches', {})
        repo.staging_area = state.get('staging_area', {})
        repo.rollback_stack = state.get('rollback_stack', [])
        repo.commit_graph = state.get('commit_graph', {})
        repo.audit_log = state.get('audit_log', [])
        
        # Load commits
        for hash in state.get('commit_hashes', []):
            commit_file = repo.vcs_dir / 'commits' / f'{hash}.pkl'
            if commit_file.exists():
                with open(commit_file, 'rb') as f:
                    repo.commits[hash] = pickle.load(f)
        
        return repo
