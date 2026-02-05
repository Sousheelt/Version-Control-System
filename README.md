VCS — A Git-Like Version Control System in Python

This project is a lightweight, educational Version Control System (VCS) implemented entirely in Python.
It demonstrates how core version-control concepts work internally, including commits, branching, merging, rollback, DAG history, and cryptographic integrity using Merkle Trees and SHA-256 hashing.

The goal is learning and clarity rather than performance or full Git compatibility.

Features:
Repository initialization with persistent state
File staging and commits
Commit history stored as a Directed Acyclic Graph (DAG)
Branch creation, listing, and checkout
Merge support with conflict detection
Rollback (undo) of commits
SHA-256 hashing for commits
Merkle Tree–based file integrity verification
Audit log of repository actions
Commit graph visualization (PNG or DOT format)
CLI interface similar to Git

How It Works

Commits
Each commit stores:
  Commit message
  Author
  Timestamp
  Parent commit hashes
  File snapshots
  Merkle root hash
A commit hash is computed using SHA-256 over all commit metadata.
Commits form a DAG, enabling branching and merging.

Merkle Trees
Every commit builds a Merkle Tree from tracked files.
Each leaf node represents a file (filename + content).
Parent hashes are computed bottom-up.
This allows:
  Fast integrity checks
  Proof that a file existed in a commit
  Detection of tampering

Branching and Merging
Branches are pointers to commit hashes.
Merges support:
  Fast-forward merges
  Three-way merges using a common ancestor
  Conflict detection when the same file diverges

Rollback
A rollback stack tracks previous HEAD commits.
Rolling back restores files from earlier commits.
