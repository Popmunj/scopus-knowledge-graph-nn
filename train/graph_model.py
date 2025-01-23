from torch_geometric.nn import SAGEConv, to_hetero
import torch.nn.functional as F
from torch import Tensor
import torch
from torch_geometric.data import HeteroData

class GNN(torch.nn.Module):
    def __init__(self, hidden_channels):
        super().__init__()

        self.conv1 = SAGEConv(hidden_channels,
                              hidden_channels) # gcn
        self.conv2 = SAGEConv(hidden_channels,
                              hidden_channels)

    def forward(self, x: Tensor, edge_index: Tensor) -> Tensor:
        x = F.relu(self.conv1(x, edge_index))
        x = self.conv2(x, edge_index) # 2nd round of passing
        return x

class Classifier(torch.nn.Module):
    # dot product between source and destination
    def forward(self,
                x_auth: Tensor, edge_label_index: Tensor) -> Tensor:
        edge_feat_author = x_auth[edge_label_index[0]] # src
        edge_feat_co_author = x_auth[edge_label_index[1]] # dest

        return (edge_feat_author * edge_feat_co_author).sum(dim=-1) # elem wise op, then sum at -1
    

class Model(torch.nn.Module):
    def __init__(self, hidden_channels, data : HeteroData):
        super().__init__()
        # transform to hidden layers first
        self.author_emb = torch.nn.Embedding(data['Author'].num_nodes, hidden_channels)
        self.lit_emb = torch.nn.Linear(1536, hidden_channels)
        self.key_emb = torch.nn.Linear(1536, hidden_channels)

        self.gnn = GNN(hidden_channels)
        self.gnn = to_hetero(self.gnn, metadata=data.metadata())
        self.classifier = Classifier()

    def forward(self, data: HeteroData) -> Tensor:
        x_dict = {
            "Author": self.author_emb(data['Author'].node_id),
            "Literature": self.lit_emb(data['Literature'].x),
            "Keyword": self.key_emb(data['Keyword'].x)
        }

        x_dict = self.gnn(x_dict, data.edge_index_dict)
        pred = self.classifier(
            x_dict['Author'], 
            data['Author', 'CO_AUTHORED', 'Author'].edge_label_index
        )

        return pred