import networkx as nx
#from Trust.hitting_time import RandomWalks
from Trust.random_walks import RandomWalks


class BL_PHT:
    def __init__(self, graph_data, seed_node, number_of_positive_random_walks, p_reset_probability,
                 number_of_negative_random_walks, n_reset_probability):
        if isinstance(graph_data, pd.DataFrame):
            graph = RandomWalks.create_graph_from_df(graph_data, source_col='source', target_col='target')
        else:
            graph = graph_data

        self.graph = graph
        self.pnrw = number_of_positive_random_walks
        self.prp = p_reset_probability
        self.nnrw = number_of_negative_random_walks
        self.nrp = n_reset_probability
        self.seed_node = seed_node

        self.reputation_scores = {}
        self.random_walks = RandomWalks(self.graph)
        self.random_walks.seed_node = seed_node
        self.random_walks.run_with_all_negative_walks(seed_node, self.pnrw, self.prp,
                                                      self.nnrw, self.nrp)
        self.compute_reputation_scores(seed_node)


    def compute_reputation_scores(self, seed_node):
        from Trust.hitting_time import RandomWalks  # Import inside the method

        self.random_walks = RandomWalks(self.graph)
        self.random_walks.seed_node = seed_node
        self.random_walks.run_with_all_negative_walks(seed_node, self.pnrw, self.prp,
                                                      self.nnrw, self.nrp)

        pos_hits_sum = self.random_walks.get_number_positive_hits_sum(seed_node)
        neg_hits_sum = self.random_walks.get_number_negative_hits_sum(seed_node)
        all_hits = max(1, pos_hits_sum + neg_hits_sum)

        print(f"Positive Hits Sum: {pos_hits_sum}, Negative Hits Sum: {neg_hits_sum}, All Hits: {all_hits}")

        for target_node in self.graph.nodes():
            pos_hits = self.random_walks.get_number_positive_hits(seed_node, target_node)
            neg_hits = self.random_walks.get_number_negative_hits(seed_node, target_node)

            pos_score = pos_hits / max(1, pos_hits_sum)
            neg_score = neg_hits / max(1, neg_hits_sum)

            reputation = pos_score - neg_score
            self.reputation_scores[target_node] = reputation

    def compute(self, seed_node: int, target_node: int) -> float:
        print(f"Computing hitting time from {seed_node} to {target_node}")

        if not self.graph.has_node(seed_node):
            print(f"Node {seed_node} is not in the graph.")

        if not self.graph.has_node(seed_node):
            print(f"Node {seed_node} is not in the graph.")
            # Handle this case accordingly, e.g., return an error or choose another node.

        # ... (existing code)

        total_hits = self.random_walks.get_total_positive_hits(seed_node, target_node)
        all_hits = self.random_walks.get_total_positive_walk_hits_sum(seed_node) \
                   - self.random_walks.get_total_positive_hits(seed_node, seed_node)
        all_hits = max(1, all_hits)

        print(f"Total Hits: {total_hits}, All Hits: {all_hits}")

        return total_hits / all_hits - self.reputation_scores.get(target_node, 0)










