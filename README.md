# Git-Like Version Control System

A lightweight Git-inspired Version Control System implemented in Python to demonstrate the internal working of modern distributed version control systems.

The project implements core Git concepts such as commit history, branching, merging, rollback, and cryptographic integrity verification using SHA-256 and Merkle Trees while maintaining a persistent repository structure.

---

## 🚀 Features

- Repository initialization
- File staging and commits
- DAG-based commit history
- Branch creation and checkout
- Merge support with conflict detection
- Commit rollback
- SHA-256 commit hashing
- Merkle Tree-based file integrity verification
- Persistent repository state
- Repository audit logging
- Commit graph visualization
- Interactive command-line interface

---

## 🛠 Technologies Used

- Python 3
- SHA-256 Cryptographic Hashing
- Merkle Trees
- Directed Acyclic Graphs (DAG)
- NetworkX
- Matplotlib
- Pickle Serialization
- Object-Oriented Programming

---

## 📂 Project Structure

```
Version-Control-System/

├── main.py                 # Application entry point
├── cli.py                  # Command-line interface
├── repository.py           # Repository management
├── commit.py               # Commit object and hashing
├── merkle_tree.py          # Merkle Tree implementation
├── visualization.py        # Commit graph visualization
├── demo.py                 # Feature demonstration
├── test_vcs.py             # Unit tests
└── README.md
```

---

## ⚙️ System Architecture

```
Working Directory
        │
        ▼
  Staging Area
        │
        ▼
     Commit Object
        │
        ├── SHA-256 Commit Hash
        ├── Merkle Root
        ├── Parent References
        └── File Snapshots
               │
               ▼
      Commit DAG
               │
        Branch Management
               │
        Merge / Rollback
```

---

## 🔍 Core Concepts

### Commit Management

Each commit stores:

- Commit message
- Author
- Timestamp
- Parent commit references
- File snapshots
- Merkle Root
- SHA-256 Commit Hash

---

### Merkle Trees

Every commit constructs a Merkle Tree from tracked files.

Benefits include:

- File integrity verification
- Tamper detection
- Efficient change validation
- Cryptographic proof of repository state

---

### Commit DAG

Commits are organized as a Directed Acyclic Graph (DAG), enabling:

- Multiple branches
- Merge operations
- Parent tracking
- Rollback support

---

## ▶️ Usage

Initialize repository

```bash
python main.py init
```

Stage files

```bash
python main.py add filename.txt
```

Create commit

```bash
python main.py commit "Initial Commit"
```

View history

```bash
python main.py log
```

Create branch

```bash
python main.py branch feature
```

Switch branch

```bash
python main.py checkout feature
```

Merge branch

```bash
python main.py merge feature
```

Rollback commit

```bash
python main.py rollback
```

Visualize commit graph

```bash
python main.py visualize
```

---

## 📊 Key Implementations

- Persistent repository metadata
- Commit hashing using SHA-256
- Merkle Tree construction
- DAG-based commit storage
- Branch and merge operations
- Conflict detection
- Repository audit trail
- Commit graph visualization

---

## 📈 Future Improvements

- Three-way merge algorithm
- Remote repositories
- Push/Pull functionality
- Diff engine
- File compression
- Packfile storage
- Binary file tracking
- Distributed synchronization

---

## 🎯 Applications

- Version Control Education
- Distributed Systems
- Data Integrity Verification
- Git Internals Learning
- Software Engineering Coursework

---

## 📚 Learning Outcomes

This project demonstrates practical implementation of:

- Version Control Systems
- Cryptographic Hashing
- Merkle Trees
- Directed Acyclic Graphs
- Data Structures & Algorithms
- Repository Management
- Command-Line Interface Design
- Software Architecture
