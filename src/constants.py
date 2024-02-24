from src.llm_util import instantiate_embed_model


EMBEDDINGS_COLLECTION_NAME = "chunked_reviews_openai"
EMBEDDINGS_INDEX= 'chunked_reviews_openai_index'
NUM_CANDIDATES=50
# EMBED_MODEL = instantiate_embed_model("intfloat/e5-large-v2", 'HF')
EMBED_MODEL = instantiate_embed_model("text-embedding-3-large", 'openai')
NEIGHBORHOOD_DISTANCE_THRESHOLD = 0.5   # in miles
