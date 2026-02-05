"""
Visualization Module for Commit Graph
=====================================

Provides functions to visualize the commit DAG using networkx and matplotlib.

Dependencies:
- networkx: For graph construction and layout
- matplotlib: For rendering

Install: pip install networkx matplotlib

Features:
- Displays commit DAG with nodes and edges
- Color-codes branches (current branch in red, others in blue)
- Shows commit hashes and messages
- Saves to PNG file
"""

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    from typing import TYPE_CHECKING
    
    if TYPE_CHECKING:
        from repository import Repository
    
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("Warning: Visualization dependencies not available")
    print("Install with: pip install networkx matplotlib")


def visualize_commit_graph(repo: 'Repository', output_file: str = 'graph.png'):
    """
    Visualize commit DAG and save to file.
    
    Args:
        repo: Repository object
        output_file: Output filename for graph image
        
    Algorithm:
    1. Create directed graph using NetworkX
    2. Add nodes (commits) with labels
    3. Add edges (parent-child relationships)
    4. Apply hierarchical layout (Sugiyama)
    5. Color-code nodes based on branches
    6. Render and save using matplotlib
    
    Time Complexity: O(V + E) where V = commits, E = edges
    """
    if not VISUALIZATION_AVAILABLE:
        raise ImportError("Visualization dependencies not installed")
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes (commits)
    node_labels = {}
    for commit_hash, commit in repo.commits.items():
        short_hash = commit_hash[:8]
        G.add_node(short_hash)
        # Create label with hash and message
        message = commit.message[:30] + '...' if len(commit.message) > 30 else commit.message
        node_labels[short_hash] = f"{short_hash}\n{message}"
    
    # Add edges (parent -> child relationships)
    for parent_hash, children in repo.commit_graph.items():
        for child_hash in children:
            G.add_edge(parent_hash[:8], child_hash[:8])
    
    if len(G.nodes()) == 0:
        print("No commits to visualize")
        return
    
    # Determine node colors based on branches
    node_colors = []
    for node in G.nodes():
        is_current_branch = False
        is_other_branch = False
        
        # Check if this commit is HEAD of any branch
        for branch_name, commit_hash in repo.branches.items():
            if commit_hash and commit_hash[:8] == node:
                if branch_name == repo.current_branch:
                    is_current_branch = True
                else:
                    is_other_branch = True
        
        if is_current_branch:
            node_colors.append('red')
        elif is_other_branch:
            node_colors.append('lightblue')
        else:
            node_colors.append('lightgray')
    
    # Create layout
    # Use hierarchical layout if possible, otherwise spring layout
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    except:
        try:
            # Topological sort for DAG layout
            layers = {}
            for node in nx.topological_sort(G):
                # Assign layer based on longest path from root
                predecessors = list(G.predecessors(node))
                if not predecessors:
                    layers[node] = 0
                else:
                    layers[node] = max(layers[p] for p in predecessors) + 1
            
            # Position nodes based on layers
            pos = {}
            layer_counts = {}
            for node, layer in layers.items():
                if layer not in layer_counts:
                    layer_counts[layer] = 0
                x = layer_counts[layer]
                y = -layer  # Negative so oldest is at bottom
                pos[node] = (x * 2, y * 2)
                layer_counts[layer] += 1
        except:
            # Fall back to spring layout
            pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Create figure
    plt.figure(figsize=(14, 10))
    
    # Draw graph
    nx.draw(G, pos,
            labels=node_labels,
            node_color=node_colors,
            node_size=3000,
            font_size=8,
            font_weight='bold',
            arrows=True,
            arrowsize=20,
            edge_color='gray',
            arrowstyle='->',
            with_labels=True)
    
    # Add title
    plt.title('Commit Graph (DAG)', fontsize=16, fontweight='bold')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='red', label=f'Current Branch ({repo.current_branch})'),
        Patch(facecolor='lightblue', label='Other Branches'),
        Patch(facecolor='lightgray', label='Commits')
    ]
    plt.legend(handles=legend_elements, loc='upper left')
    
    # Save to file
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Commit graph visualized and saved to {output_file}")


def export_dot_format(repo: 'Repository', output_file: str = 'graph.dot'):
    """
    Export commit graph in DOT format for Graphviz.
    
    Args:
        repo: Repository object
        output_file: Output filename for DOT file
        
    DOT format can be rendered using Graphviz:
    dot -Tpng graph.dot -o graph.png
    """
    dot_content = repo.get_commit_graph_dot()
    
    with open(output_file, 'w') as f:
        f.write(dot_content)
    
    print(f"DOT format exported to {output_file}")
    print("Render with: dot -Tpng graph.dot -o graph.png")


if __name__ == '__main__':
    print("Visualization Module")
    print(f"Dependencies available: {VISUALIZATION_AVAILABLE}")
    
    if not VISUALIZATION_AVAILABLE:
        print("\nTo install dependencies, run:")
        print("pip install networkx matplotlib")
