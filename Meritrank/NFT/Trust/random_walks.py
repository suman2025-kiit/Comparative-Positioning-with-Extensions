import networkx as nx
import random

class RandomWalks:
    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.counters = {node: {'positive': 0, 'negative': 0} for node in graph.nodes()}

    def run_with_all_negative_walks(self, seed_node, number_of_positive_random_walks, p_reset_probability, number_of_negative_random_walks, n_reset_probability):
        self.run(seed_node, number_of_positive_random_walks, p_reset_probability, True)
        self.run(seed_node, number_of_negative_random_walks, n_reset_probability, False)

    def run(self, seed_node, number_of_walks, reset_probability, is_positive):
        for _ in range(number_of_walks):
            current_node = seed_node
            while random.random() > reset_probability:
                neighbors = list(self.graph.neighbors(current_node))
                if not neighbors:
                    break
                next_node = random.choice(neighbors)
                walk_type = 'positive' if is_positive else 'negative'
                self.counters[seed_node][walk_type] += 1
                current_node = next_node

    def get_number_positive_hits(self, seed_node, target_node):
        return self.counters[seed_node]['positive']

    def get_number_negative_hits(self, seed_node, target_node):
        return self.counters[seed_node]['negative']
