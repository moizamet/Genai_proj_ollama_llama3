# import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

class GenerateEmbeddings:
    model:object=None    
    


    # Compute embeddings
    

    def __init__(self):
        self.model = SentenceTransformer("avsolatorio/GIST-small-Embedding-v0", revision=None)
    
    def getEmbeddings(self,inputText):
        text=[inputText]
        print(f"Input text is: {text}")
        embeddings = self.model.encode(text).tolist()
        print(embeddings)
        # print(len(embeddings[0]))
        # print("hello %s",embeddings[0])
        return embeddings[0]








# # Compute cosine-similarity for each pair of sentences
# scores = F.cosine_similarity(embeddings.unsqueeze(1), embeddings.unsqueeze(0), dim=-1)

# print(scores.cpu().numpy())
