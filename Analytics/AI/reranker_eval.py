import time
import warnings
from sentence_transformers import CrossEncoder

from .utils import rerank
from Shared.LLM import LLM
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

print("Loading rerankers...")
rerankers = {
    "mmarco-mMiniLMv2 (multilingual)": CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"),
    "bge-reranker-base (EN/ZH)":       CrossEncoder("BAAI/bge-reranker-base"),
    "slovakbert-sts (SK)":             CrossEncoder("kinit/slovakbert-sts-stsb"),
}
print("All rerankers loaded.\n")

llm = LLM()
vdb = Vector_DB_Qdrant('rent-bot-index')

TOP_N = 50

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

QUERY = """
 NADPIS: 2-izbový byt na prenájom v Bratislave - moderná výšková budova \nOPIS: Ponúkame na prenájom moderný 2 \nizbový byt v prestížnej výškovej budove v srdci Bratislavy. Byt sa nachádza na jednom z najvyšších poschodí, čo \nzaručuje nádherný výhľad na panorámu mesta. Súčasťou bytu je priestranný balkón, ideálny na relaxáciu po náročnom dni. K bytu patrí aj jedno parkovacie miesto, čo je v tejto modernej štvrti plnej mrakodrapov veľkou výhodou.
"""

query = " ".join(QUERY.strip().splitlines())
if query:

    # Embed and search
    embedding = llm.get_embedding(query, model='text-embedding-3-large')
    results = vdb.enriched_filtered_vector_search(embedding, 50, [], score_threshold=None)[0]

    if not results.points:
        print("No results.\n")

    print(f"\n[{len(results.points)} results retrieved from vector DB]\n")

    # Apply each reranker and print results
    for name, model in rerankers.items():
        t_start = time.time()
        reranked = rerank(query, results.points, model)
        t_total = time.time() - t_start
        print(f"--- {name} ({t_total:.2f}s) ---")
        for i, point in enumerate(reranked[:TOP_N], 1):
            print(f"{i:2}. [{point.score:.4f}] {point.payload.get('source_url', 'N/A')}")
        print()
