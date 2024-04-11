import pandas as pd
import json
import networkx as nx
from Trust.hitting_time import BL_PHT

def create_graph_from_raw_data(raw_data):
    graph = nx.Graph()
    for token_id, token_data in raw_data.items():
        if isinstance(token_data, dict):
            creator_id = token_data.get('creator', {}).get('id', None)
            owner_id = token_data.get('owner', {}).get('id', None)
            if creator_id and token_id:
                graph.add_edge(creator_id, token_id, type='creator')
            if owner_id and token_id:
                graph.add_edge(owner_id, token_id, type='owner')
    return graph

def load_data(file_path):
    with open(file_path, 'r') as file:
        raw_data = json.load(file)

    graph = create_graph_from_raw_data(raw_data)

    # Initialize BL_PHT with the graph and a default seed node
    # Replace 'default_seed_node_id' with the actual seed node ID
    default_seed_node_id = '1' 
    bl_pht = BL_PHT(graph, default_seed_node_id)
    bl_pht.compute_reputation_scores()  # Compute initial reputation scores for all nodes

    # Prepare dataframes to hold the results
    listed_df = pd.DataFrame(columns=['token_id', 'creator', 'owner', 'amountInETH', 'event', 'Reputation'])
    price_changed_df = pd.DataFrame(columns=['token_id', 'creator', 'owner', 'amountInETH', 'event', 'Reputation'])

    # Process each NFT data for reputation score
    for token_id, token_data in raw_data.items():
        if isinstance(token_data, dict) and 'nftHistory' in token_data:
            for event in token_data['nftHistory']:
                event_type = event.get('event', None)
                amount_in_eth = event.get('amountInETH', 0)
                creator_id = token_data.get('creator', {}).get('id', None)
                owner_id = token_data.get('owner', {}).get('id', None)
                reputation = bl_pht.compute(creator_id, owner_id, amount_in_eth, event_type)

                # Create a new row for the dataframe
                new_row = {
                    'token_id': token_id,
                    'creator': creator_id,
                    'owner': owner_id,
                    'amountInETH': amount_in_eth,
                    'event': event_type,
                    'Reputation': reputation
                }

                if event_type == 'Listed':
                    listed_df = listed_df.append(new_row, ignore_index=True)
                elif event_type == 'PriceChanged':
                    price_changed_df = price_changed_df.append(new_row, ignore_index=True)

    # Output the DataFrames to CSV
    listed_df.to_csv('Listed_events.csv', index=False)
    price_changed_df.to_csv('Price_Changed_events.csv', index=False)

    # Example: Printing the first few rows from each dataframe
    print(listed_df.head())
    print(price_changed_df.head())

# Example usage
file_path = 'fixed_nft_data.json'
load_data(file_path)
