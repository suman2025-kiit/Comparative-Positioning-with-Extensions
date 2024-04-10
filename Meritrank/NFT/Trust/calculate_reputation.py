import pandas as pd
from Trust.hitting_time import BL_PHT
import networkx as nx

def calculate_reputation_for_events(art_metadata_df: pd.DataFrame, graph: nx.Graph) -> pd.DataFrame:
    seed_node = '1'  # Replace with your actual seed node ID
    bl_pht = BL_PHT(graph, seed_node)
    reputation_scores = bl_pht.compute_reputation_scores()

    def apply_compute(row, bl_pht_instance, reputation_scores):
        creator_reputation = reputation_scores.get(row['creator'], 0)
        owner_reputation = reputation_scores.get(row['owner'], 0)
        return bl_pht_instance.compute(row['creator'], row['owner'], row['amountInETH'], row['event'])

    listed_rows = art_metadata_df[art_metadata_df['event'] == 'Listed'].copy()
    listed_rows['Reputation'] = listed_rows.apply(apply_compute, axis=1, bl_pht_instance=bl_pht, reputation_scores=reputation_scores)

    price_changed_rows = art_metadata_df[art_metadata_df['event'] == 'PriceChanged'].copy()
    price_changed_rows['Reputation'] = price_changed_rows.apply(apply_compute, axis=1, bl_pht_instance=bl_pht, reputation_scores=reputation_scores)

    art_metadata_df = pd.concat([art_metadata_df, listed_rows[['token_id', 'Reputation']]], ignore_index=True)
    art_metadata_df = pd.concat([art_metadata_df, price_changed_rows[['token_id', 'Reputation']]], ignore_index=True)

    return art_metadata_df
