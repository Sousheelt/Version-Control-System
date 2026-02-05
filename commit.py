"""Commit - DAG node with SHA-256 hash and Merkle root for integrity."""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional
from merkle_tree import MerkleTree


class Commit:
    """Commit node in DAG with unique hash, Merkle root, parents, and metadata."""
    
    def __init__(self, message: str, files: Dict[str, str], parents: List[str] = None,
                 author: str = "default", timestamp: Optional[datetime] = None):
        self.message = message
        self.files = files.copy()
        self.parents = parents if parents else []
        self.author = author
        self.timestamp = timestamp if timestamp else datetime.now()
        
        # Build Merkle Tree
        file_data = [(filename, content) for filename, content in sorted(files.items())]
        self.merkle_tree = MerkleTree(file_data)
        self.merkle_root = self.merkle_tree.get_root_hash()
        
        # Compute unique hash
        self.hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute SHA-256 from parents, merkle root, and metadata."""
        data = {
            'parents': sorted(self.parents),
            'merkle_root': self.merkle_root,
            'message': self.message,
            'author': self.author,
            'timestamp': self.timestamp.isoformat()
        }
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify commit hash hasn't been tampered."""
        return self.hash == self._compute_hash()
    
    def get_file_proof(self, filename: str) -> Optional[List[str]]:
        """Get Merkle proof for file inclusion."""
        return self.merkle_tree.get_proof(filename)
    
    def verify_file(self, filename: str, content: str, proof: List[str]) -> bool:
        """Verify file with Merkle proof."""
        return self.merkle_tree.verify_proof(filename, content, proof)
    
    def __repr__(self) -> str:
        return f"Commit(hash={self.hash[:8]}, message='{self.message}', author='{self.author}')"
    
    def to_dict(self) -> Dict:
        """Serialize to dict."""
        return {
            'hash': self.hash,
            'message': self.message,
            'author': self.author,
            'timestamp': self.timestamp.isoformat(),
            'parents': self.parents,
            'merkle_root': self.merkle_root,
            'files': self.files
        }
