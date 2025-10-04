# semantic_module.py (No changes needed)

import logging
from sentence_transformers import SentenceTransformer, util

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

model = SentenceTransformer('all-MiniLM-L6-v2')  # Model for embedding semantic search

def semantic_search(jd_embedding, bullets, num=5):  
    bullet_embeddings = model.encode(bullets, convert_to_tensor=True)
    # Compute cosine similarity scores
    similarities = util.pytorch_cos_sim(jd_embedding, bullet_embeddings)[0].cpu().numpy()
    # Pair scores with bullets
    scored_bullets = list(zip(similarities, bullets))
    # Sort by similarity (descending)
    sorted_bullets = sorted(scored_bullets, key=lambda x: x[0], reverse=True)
    # Return top 3 most relevant points
    return sorted_bullets[:num]