
def get_type(element):
    try:
        return element.split("/")[4]
    except Exception as e:
        return ""


def same_type_filter(pairs):
    filtered_pairs = []

    for pair in pairs:
        first_type = get_type(pair[0])
        second_type = get_type(pair[1])

        if first_type == "" or second_type == "":
            if "wikia" in pair[0] and "wikia" in pair[1]:
                filtered_pairs.append(pair)
            else:
                continue
        if first_type == second_type:
            filtered_pairs.append(pair)
    return filtered_pairs

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