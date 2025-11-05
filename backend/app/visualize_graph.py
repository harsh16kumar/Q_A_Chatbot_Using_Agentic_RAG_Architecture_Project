from graphviz import Digraph

def visualize_workflow():
    dot = Digraph("Workflow", format="png")

    # Nodes
    nodes = [
        "retrieve",
        "grade_documents",
        "extract_contact",
        "extract_cgpa",
        "check_cgpa",
        "send_email",
        "generate",
        "END",
    ]
    for node in nodes:
        dot.node(node, node, shape="box")

    # Edges
    edges = [
        ("retrieve", "grade_documents"),
        ("grade_documents", "extract_contact", "if route == 'generate'"),
        ("grade_documents", "retrieve", "if route == 'retrieve'"),
        ("extract_contact", "extract_cgpa"),
        ("extract_cgpa", "check_cgpa"),
        ("check_cgpa", "send_email", "if route == 'send_email'"),
        ("check_cgpa", "generate", "if route == 'generate'"),
        ("send_email", "generate"),
        ("generate", "END"),
    ]
    for src, dst, *label in edges:
        dot.edge(src, dst, label=label[0] if label else "")

    # Save and render
    dot.render("workflow_graph", directory=".", cleanup=True)
    print("Graph saved as workflow_graph.png")

if __name__ == "__main__":
    visualize_workflow()
