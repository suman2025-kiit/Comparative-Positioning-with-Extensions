import networkx as nx
from Trust.random_walks import RandomWalks

class BL_PHT:
    def __init__(self, graph: nx.Graph, seed_node: str):
        self.graph = graph
        self.seed_node = seed_node
        self.random_walks = RandomWalks(self.graph)

    def compute_reputation_scores(self):
        if self.seed_node not in self.graph:
            return {}

        self.random_walks.run_with_all_negative_walks(self.seed_node, 1000, 0.15, 500, 0.3)

        reputation_scores = {}
        for target_node in self.graph.nodes():
            if target_node is None or target_node == self.seed_node:
                continue
            pos_hits = self.random_walks.get_number_positive_hits(self.seed_node, target_node)
            neg_hits = self.random_walks.get_number_negative_hits(self.seed_node, target_node)
            pos_score = pos_hits / (pos_hits + neg_hits) if pos_hits + neg_hits > 0 else 0
            neg_score = neg_hits / (pos_hits + neg_hits) if pos_hits + neg_hits > 0 else 0
            reputation_score = pos_score - neg_score
            reputation_scores[target_node] = reputation_score
        return reputation_scores

    def compute(self, creator_node, owner_node, amount_in_eth, event_type):
        reputation_scores = self.compute_reputation_scores()
        creator_reputation = reputation_scores.get(creator_node, 0)
        owner_reputation = reputation_scores.get(owner_node, 0)
        #total_reputation = (creator_reputation + owner_reputation) * float(amount_in_eth)
        total_reputation = (creator_reputation + owner_reputation)
        return total_reputation
