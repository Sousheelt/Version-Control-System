"""
Test Suite for VCS - Version Control System
===========================================

Comprehensive tests for all VCS components:
- Merkle Tree operations
- Commit creation and integrity
- Repository operations
- Branch management
- Merge and conflict detection
- Rollback functionality

Run: python test_vcs.py
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

# Import VCS components
from merkle_tree import MerkleTree, MerkleNode
from commit import Commit
from repository import Repository


class TestResult:
    """Track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def record_pass(self, test_name):
        self.passed += 1
        print(f"✓ {test_name}")
    
    def record_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"✗ {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 70)
        print(f"Test Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"\nFailed tests:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        print("=" * 70)
        return self.failed == 0


class VCSTestSuite:
    """Comprehensive test suite for VCS."""
    
    def __init__(self):
        self.results = TestResult()
        self.test_dir = None
    
    def setup(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="vcs_test_"))
        os.chdir(self.test_dir)
    
    def teardown(self):
        """Clean up test directory."""
        if self.test_dir and self.test_dir.exists():
            os.chdir("..")
            shutil.rmtree(self.test_dir)
    
    def run_test(self, test_func):
        """Run a single test function."""
        test_name = test_func.__name__.replace('test_', '').replace('_', ' ').title()
        try:
            test_func()
            self.results.record_pass(test_name)
        except AssertionError as e:
            self.results.record_fail(test_name, str(e))
        except Exception as e:
            self.results.record_fail(test_name, f"Error: {e}")
    
    # ========================================================================
    # Merkle Tree Tests
    # ========================================================================
    
    def test_merkle_tree_empty(self):
        """Test Merkle tree with no files."""
        tree = MerkleTree([])
        root_hash = tree.get_root_hash()
        assert root_hash != "", "Empty tree should have hash"
    
    def test_merkle_tree_single_file(self):
        """Test Merkle tree with single file."""
        files = [("file1.txt", "content1")]
        tree = MerkleTree(files)
        root_hash = tree.get_root_hash()
        assert len(root_hash) == 64, "SHA-256 hash should be 64 hex chars"
    
    def test_merkle_tree_multiple_files(self):
        """Test Merkle tree with multiple files."""
        files = [
            ("file1.txt", "content1"),
            ("file2.txt", "content2"),
            ("file3.txt", "content3")
        ]
        tree = MerkleTree(files)
        root_hash = tree.get_root_hash()
        assert len(root_hash) == 64, "Root hash should be SHA-256"
    
    def test_merkle_tree_same_content_same_hash(self):
        """Test that identical content produces identical hash."""
        files1 = [("file.txt", "content")]
        files2 = [("file.txt", "content")]
        
        tree1 = MerkleTree(files1)
        tree2 = MerkleTree(files2)
        
        assert tree1.get_root_hash() == tree2.get_root_hash(), \
            "Same content should produce same hash"
    
    def test_merkle_tree_different_content_different_hash(self):
        """Test that different content produces different hash."""
        files1 = [("file.txt", "content1")]
        files2 = [("file.txt", "content2")]
        
        tree1 = MerkleTree(files1)
        tree2 = MerkleTree(files2)
        
        assert tree1.get_root_hash() != tree2.get_root_hash(), \
            "Different content should produce different hash"
    
    def test_merkle_proof_generation(self):
        """Test Merkle proof generation."""
        files = [
            ("file1.txt", "content1"),
            ("file2.txt", "content2")
        ]
        tree = MerkleTree(files)
        proof = tree.get_proof("file1.txt")
        assert isinstance(proof, list), "Proof should be a list"
    
    def test_merkle_proof_verification(self):
        """Test Merkle proof verification."""
        files = [
            ("file1.txt", "content1"),
            ("file2.txt", "content2")
        ]
        tree = MerkleTree(files)
        root = tree.get_root_hash()
        proof = tree.get_proof("file1.txt")
        
        is_valid = tree.verify_proof("file1.txt", "content1", proof, root)
        assert is_valid, "Valid proof should verify"
    
    # ========================================================================
    # Commit Tests
    # ========================================================================
    
    def test_commit_creation(self):
        """Test basic commit creation."""
        files = {"file1.txt": "content1"}
        commit = Commit("Initial commit", files)
        
        assert commit.hash != "", "Commit should have hash"
        assert len(commit.hash) == 64, "Commit hash should be SHA-256"
        assert commit.message == "Initial commit"
    
    def test_commit_with_parent(self):
        """Test commit with parent."""
        files1 = {"file1.txt": "content1"}
        commit1 = Commit("First", files1)
        
        files2 = {"file1.txt": "content1", "file2.txt": "content2"}
        commit2 = Commit("Second", files2, parents=[commit1.hash])
        
        assert commit1.hash in commit2.parents, "Parent should be recorded"
    
    def test_commit_integrity_valid(self):
        """Test commit integrity verification (valid)."""
        files = {"file1.txt": "content1"}
        commit = Commit("Test", files)
        
        assert commit.verify_integrity(), "Valid commit should verify"
    
    def test_commit_integrity_tampered(self):
        """Test commit integrity verification (tampered)."""
        files = {"file1.txt": "content1"}
        commit = Commit("Test", files)
        
        # Tamper with files
        commit.files["file1.txt"] = "tampered"
        
        assert not commit.verify_integrity(), "Tampered commit should fail"
    
    def test_commit_unique_hashes(self):
        """Test that different commits have different hashes."""
        files = {"file1.txt": "content1"}
        commit1 = Commit("Message 1", files)
        commit2 = Commit("Message 2", files)
        
        assert commit1.hash != commit2.hash, "Different messages should produce different hashes"
    
    # ========================================================================
    # Repository Tests
    # ========================================================================
    
    def test_repository_init(self):
        """Test repository initialization."""
        repo = Repository(".")
        result = repo.init()
        
        assert ".vcs" in result.lower() or "initialized" in result.lower()
        assert Path(".vcs").exists(), ".vcs directory should be created"
    
    def test_repository_add_file(self):
        """Test adding file to staging."""
        repo = Repository(".")
        repo.init()
        
        # Create test file
        with open("test.txt", "w") as f:
            f.write("test content")
        
        result = repo.add("test.txt")
        assert "added" in result.lower() or "staged" in result.lower()
        assert "test.txt" in repo.staging_area
    
    def test_repository_commit(self):
        """Test creating a commit."""
        repo = Repository(".")
        repo.init()
        
        # Create and stage file
        with open("test.txt", "w") as f:
            f.write("test content")
        repo.add("test.txt")
        
        # Commit
        result = repo.commit("Test commit")
        assert "test commit" in result.lower() or "changed" in result.lower()
        assert repo.head is not None, "HEAD should be set"
        assert len(repo.commits) == 1, "Should have one commit"
    
    def test_repository_multiple_commits(self):
        """Test multiple commits."""
        repo = Repository(".")
        repo.init()
        
        # First commit
        with open("file1.txt", "w") as f:
            f.write("content1")
        repo.add("file1.txt")
        repo.commit("First commit")
        
        # Second commit
        with open("file2.txt", "w") as f:
            f.write("content2")
        repo.add("file2.txt")
        repo.commit("Second commit")
        
        assert len(repo.commits) == 2, "Should have two commits"
    
    def test_repository_status(self):
        """Test repository status."""
        repo = Repository(".")
        repo.init()
        
        status = repo.status()
        assert "main" in status.lower(), "Should show current branch"
    
    def test_repository_log(self):
        """Test commit log."""
        repo = Repository(".")
        repo.init()
        
        # Create commit
        with open("test.txt", "w") as f:
            f.write("test")
        repo.add("test.txt")
        repo.commit("Test commit")
        
        log = repo.log()
        assert "test commit" in log.lower(), "Log should contain commit message"
    
    # ========================================================================
    # Branch Tests
    # ========================================================================
    
    def test_branch_creation(self):
        """Test creating a branch."""
        repo = Repository(".")
        repo.init()
        
        result = repo.create_branch("feature")
        assert "created" in result.lower() or "feature" in result.lower()
        assert "feature" in repo.branches
    
    def test_branch_switch(self):
        """Test switching branches."""
        repo = Repository(".")
        repo.init()
        
        # Create initial commit
        with open("test.txt", "w") as f:
            f.write("test")
        repo.add("test.txt")
        repo.commit("Initial")
        
        # Create and switch to branch
        repo.create_branch("feature")
        result = repo.switch_branch("feature")
        
        assert repo.current_branch == "feature", "Should be on feature branch"
    
    def test_branch_list(self):
        """Test listing branches."""
        repo = Repository(".")
        repo.init()
        
        repo.create_branch("feature")
        branches = repo.list_branches()
        
        assert "main" in branches, "Should list main branch"
        assert "feature" in branches, "Should list feature branch"
    
    # ========================================================================
    # Merge Tests
    # ========================================================================
    
    def test_merge_fast_forward(self):
        """Test fast-forward merge."""
        repo = Repository(".")
        repo.init()
        
        # Initial commit on main
        with open("file1.txt", "w") as f:
            f.write("content1")
        repo.add("file1.txt")
        repo.commit("Initial")
        
        # Create feature branch and add commit
        repo.create_branch("feature")
        repo.switch_branch("feature")
        
        with open("file2.txt", "w") as f:
            f.write("content2")
        repo.add("file2.txt")
        repo.commit("Feature commit")
        
        # Switch back and merge
        repo.switch_branch("main")
        result = repo.merge("feature")
        
        assert "merge" in result.lower() or "fast" in result.lower()
    
    def test_merge_no_conflict(self):
        """Test merge without conflicts."""
        repo = Repository(".")
        repo.init()
        
        # Initial commit
        with open("base.txt", "w") as f:
            f.write("base")
        repo.add("base.txt")
        repo.commit("Base")
        
        # Feature branch
        repo.create_branch("feature")
        repo.switch_branch("feature")
        with open("feature.txt", "w") as f:
            f.write("feature")
        repo.add("feature.txt")
        repo.commit("Add feature")
        
        # Main branch
        repo.switch_branch("main")
        with open("main.txt", "w") as f:
            f.write("main")
        repo.add("main.txt")
        repo.commit("Add main file")
        
        # Merge
        result = repo.merge("feature")
        assert "conflict" not in result.lower() or "merged" in result.lower()
    
    def test_merge_conflict_detection(self):
        """Test merge conflict detection."""
        repo = Repository(".")
        repo.init()
        
        # Initial commit
        with open("conflict.txt", "w") as f:
            f.write("original")
        repo.add("conflict.txt")
        repo.commit("Base")
        
        # Feature branch - modify file
        repo.create_branch("feature")
        repo.switch_branch("feature")
        with open("conflict.txt", "w") as f:
            f.write("feature version")
        repo.add("conflict.txt")
        repo.commit("Feature change")
        
        # Main branch - modify same file
        repo.switch_branch("main")
        with open("conflict.txt", "w") as f:
            f.write("main version")
        repo.add("conflict.txt")
        repo.commit("Main change")
        
        # Merge should detect conflict
        result = repo.merge("feature")
        assert "conflict" in result.lower(), "Should detect conflict"
    
    # ========================================================================
    # Rollback Tests
    # ========================================================================
    
    def test_rollback_single_commit(self):
        """Test rolling back one commit."""
        repo = Repository(".")
        repo.init()
        
        # Create two commits
        with open("file1.txt", "w") as f:
            f.write("v1")
        repo.add("file1.txt")
        first_hash = repo.commit("First")
        
        with open("file2.txt", "w") as f:
            f.write("v2")
        repo.add("file2.txt")
        repo.commit("Second")
        
        # Rollback
        result = repo.rollback(1)
        assert "rolled back" in result.lower() or "rollback" in result.lower()
    
    def test_rollback_multiple_commits(self):
        """Test rolling back multiple commits."""
        repo = Repository(".")
        repo.init()
        
        # Create three commits
        for i in range(3):
            with open(f"file{i}.txt", "w") as f:
                f.write(f"content{i}")
            repo.add(f"file{i}.txt")
            repo.commit(f"Commit {i}")
        
        # Rollback 2 commits
        repo.rollback(2)
        assert len(repo.rollback_stack) == 0, "Stack should have 0 items (started with 2)"
    
    # ========================================================================
    # Integration Tests
    # ========================================================================
    
    def test_complete_workflow(self):
        """Test complete workflow: init, add, commit, branch, merge."""
        repo = Repository(".")
        repo.init()
        
        # Initial commit
        with open("README.md", "w") as f:
            f.write("# Project")
        repo.add("README.md")
        repo.commit("Initial commit")
        
        # Create feature branch
        repo.create_branch("feature")
        repo.switch_branch("feature")
        
        # Add feature
        with open("feature.py", "w") as f:
            f.write("def feature(): pass")
        repo.add("feature.py")
        repo.commit("Add feature")
        
        # Merge back
        repo.switch_branch("main")
        result = repo.merge("feature")
        
        assert len(repo.commits) >= 2, "Should have at least 2 commits"
    
    def test_persistence(self):
        """Test repository state persistence."""
        repo = Repository(".")
        repo.init()
        
        # Create commit
        with open("test.txt", "w") as f:
            f.write("test")
        repo.add("test.txt")
        repo.commit("Test")
        commit_hash = repo.head
        
        # Load repository
        repo2 = Repository.load(".")
        
        assert repo2.head == commit_hash, "HEAD should persist"
        assert len(repo2.commits) == len(repo.commits), "Commits should persist"
    
    def test_audit_log(self):
        """Test audit log functionality."""
        repo = Repository(".")
        repo.init()
        
        with open("test.txt", "w") as f:
            f.write("test")
        repo.add("test.txt")
        repo.commit("Test")
        
        audit = repo.get_audit_log()
        assert "init" in audit.lower(), "Should log init"
        assert "add" in audit.lower(), "Should log add"
        assert "commit" in audit.lower(), "Should log commit"
    
    # ========================================================================
    # Run All Tests
    # ========================================================================
    
    def run_all(self):
        """Run all tests."""
        print("=" * 70)
        print("  VCS Test Suite")
        print("=" * 70)
        
        # Get all test methods
        test_methods = [
            getattr(self, method) for method in dir(self)
            if method.startswith('test_') and callable(getattr(self, method))
        ]
        
        print(f"\nRunning {len(test_methods)} tests...\n")
        
        # Run each test in isolated environment
        for test_method in test_methods:
            self.setup()
            self.run_test(test_method)
            self.teardown()
        
        # Print summary
        success = self.results.summary()
        return success


def main():
    """Main entry point for test suite."""
    suite = VCSTestSuite()
    success = suite.run_all()
    
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
