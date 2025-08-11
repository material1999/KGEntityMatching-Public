def select_max_similarity(triples):
    """
    Given a list of triples [node_A, node_B, similarity], return a list with only the triple
    having the maximum similarity for each unique node_B.
    """
    best_for_node_b = {}

    for node_a, node_b, similarity in triples:
        if node_b not in best_for_node_b or similarity > best_for_node_b[node_b][2]:
            best_for_node_b[node_b] = [node_a, node_b, similarity]

    return list(best_for_node_b.values())