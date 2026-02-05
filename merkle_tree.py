"""Merkle Tree - Binary tree with SHA-256 for file integrity verification."""

import hashlib
from typing import List, Optional, Tuple


class MerkleNode:
    """Node in Merkle Tree with hash and optional children."""
    def __init__(self, hash_value: str, left=None, right=None, data: Optional[str] = None):
        self.hash = hash_value
        self.left = left
        self.right = right
        self.data = data
    
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


class MerkleTree:
    """Binary tree for file integrity using SHA-256 hashing."""
    
    def __init__(self, file_data: List[Tuple[str, str]]):
        self.file_data = file_data
        self.root = self._build_tree()
    
    @staticmethod
    def compute_hash(data: str) -> str:
        """Compute SHA-256 hash."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _build_tree(self) -> Optional[MerkleNode]:
        """Build tree bottom-up from leaves."""
        if not self.file_data:
            return None
        
        # Create leaf nodes
        nodes = [MerkleNode(
            self.compute_hash(f"{filename}:{content}"),
            data=f"{filename}:{content}"
        ) for filename, content in self.file_data]
        
        # Build tree
        while len(nodes) > 1:
            next_level = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                parent_hash = self.compute_hash(left.hash + right.hash)
                next_level.append(MerkleNode(parent_hash, left, right))
            nodes = next_level
        
        return nodes[0] if nodes else None
    
    def get_root_hash(self) -> str:
        """Get root hash."""
        return self.root.hash if self.root else ""
    
    def get_proof(self, filename: str) -> Optional[List[str]]:
        """Get Merkle proof for file."""
        if not self.root:
            return None
        
        # Find target
        target_data = None
        for fn, content in self.file_data:
            if fn == filename:
                target_data = f"{fn}:{content}"
                break
        
        if not target_data:
            return None
        
        target_hash = self.compute_hash(target_data)
        proof = []
        
        def collect_proof(node, target, proof_list, is_left):
            if not node or node.is_leaf():
                return node and node.hash == target
            
            if collect_proof(node.left, target, proof_list, True):
                if node.right:
                    proof_list.append(('R', node.right.hash))
                return True
            elif collect_proof(node.right, target, proof_list, False):
                if node.left:
                    proof_list.append(('L', node.left.hash))
                return True
            return False
        
        collect_proof(self.root, target_hash, proof, True)
        return [f"{side}:{hash}" for side, hash in proof]
    
    def verify_proof(self, filename: str, content: str, proof: List[str]) -> bool:
        """Verify file with Merkle proof."""
        current_hash = self.compute_hash(f"{filename}:{content}")
        
        for item in proof:
            side, sibling_hash = item.split(':', 1)
            if side == 'L':
                current_hash = self.compute_hash(sibling_hash + current_hash)
            else:
                current_hash = self.compute_hash(current_hash + sibling_hash)
        
        return current_hash == self.root.hash if self.root else False
    
    def verify_integrity(self) -> bool:
        """Verify tree structure integrity."""
        if not self.root:
            return len(self.file_data) == 0
        
        def verify_node(node):
            if not node:
                return True
            if node.is_leaf():
                return True
            
            left_hash = node.left.hash if node.left else ""
            right_hash = node.right.hash if node.right else ""
            expected = self.compute_hash(left_hash + right_hash)
            
            return (node.hash == expected and 
                    verify_node(node.left) and 
                    verify_node(node.right))
        
        return verify_node(self.root)
