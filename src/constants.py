from llm_util import instantiate_embed_model


EMBEDDINGS_COLLECTION_NAME = "chunked_reviews"
EMBEDDINGS_INDEX= 'chunked_reviews_content_index'
NUM_CANDIDATES=50
EMBED_MODEL = instantiate_embed_model("intfloat/e5-large-v2", 'HF')
