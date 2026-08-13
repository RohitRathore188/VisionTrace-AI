"""
One-shot script to:
1. Diagnose what's in the embeddings table
2. Delete all stale pseudo-vector embeddings from SQLite
3. Re-trigger FAISS index rebuild using new semantic seeds
4. Run a quick multi-query test to verify different queries produce different scores
"""
import asyncio
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    from app.db.session import async_session_factory
    from app.models.embedding import Embedding
    from app.models.frame import Frame
    from app.models.object import ObjectDetection
    from sqlalchemy import select, delete, func
    from sqlalchemy.orm import joinedload

    async with async_session_factory() as db:
        # ── 1. Diagnose current state ──────────────────────────────────────────
        emb_count_q = await db.execute(select(func.count(Embedding.id)))
        frame_count_q = await db.execute(select(func.count(Frame.id)))
        obj_count_q = await db.execute(select(func.count(ObjectDetection.id)))
        
        emb_count = emb_count_q.scalar()
        frame_count = frame_count_q.scalar()
        obj_count = obj_count_q.scalar()
        
        print(f"\n{'='*60}")
        print(f"DB DIAGNOSIS:")
        print(f"  Frames      : {frame_count}")
        print(f"  Objects     : {obj_count}")
        print(f"  Embeddings  : {emb_count}")
        print(f"{'='*60}")

        if emb_count == 0:
            print("\nNo embeddings in DB — will auto-generate during FAISS build.")
        else:
            # Check if embeddings look like pseudo-vectors (all very low norms?)
            sample_q = await db.execute(select(Embedding).limit(3))
            sample_embs = sample_q.scalars().all()
            print(f"\nSample embedding check:")
            for emb in sample_embs:
                vec = list(emb.embedding) if emb.embedding else []
                if vec:
                    arr = np.array(vec, dtype=np.float32)
                    print(f"  ID={str(emb.id)[:8]} | Dim={len(arr)} | Norm={np.linalg.norm(arr):.4f} | [0:5]={arr[:5].tolist()}")
            
            # Delete all existing embeddings so they get regenerated with semantic seeds
            print(f"\nDeleting {emb_count} stale embeddings from DB...")
            await db.execute(delete(Embedding))
            await db.commit()
            print("  OK Cleared all embeddings.")

        # -- 2. Also check objects have labels ---------------------------------
        if obj_count > 0:
            label_q = await db.execute(
                select(ObjectDetection.label, func.count(ObjectDetection.id).label("cnt"))
                .group_by(ObjectDetection.label)
            )
            label_rows = label_q.all()
            print(f"\nObject label distribution:")
            for row in label_rows:
                print(f"  {row.label}: {row.cnt}")

    # -- 3. Rebuild FAISS index (generates new semantic-seeded embeddings) ------
    print(f"\n{'='*60}")
    print("Rebuilding FAISS index with semantic seeds...")
    print(f"{'='*60}")
    
    from app.services.faiss_service import faiss_service
    from app.services.clip_service import clip_service
    
    async with async_session_factory() as db:
        result = await faiss_service.build_index_from_db(db)
    
    print(f"\nFAISS Index built:")
    print(f"  Status        : {result.get('status')}")
    print(f"  Total indexed : {result.get('total_indexed')}")
    print(f"  Dimension     : {result.get('dimension')}")

    # -- 4. Multi-query similarity test ----------------------------------------
    print(f"\n{'='*60}")
    print("MULTI-QUERY EMBEDDING TEST:")
    print(f"{'='*60}")
    
    queries = ["person", "white truck", "red bicycle", "black shirt", "vehicle"]
    embeddings = {}
    for q in queries:
        vec = clip_service.generate_text_embedding(q)
        arr = np.array(vec, dtype=np.float32)
        embeddings[q] = arr
        print(f"\n  Query: '{q}'")
        print(f"    Norm    : {np.linalg.norm(arr):.6f}")
        print(f"    [0:10]  : {[round(float(v), 6) for v in arr[:10]]}")

    print(f"\n{'='*60}")
    print("CROSS-QUERY SIMILARITY MATRIX:")
    print(f"{'='*60}")
    query_list = list(embeddings.keys())
    for i in range(len(query_list)):
        for j in range(i+1, len(query_list)):
            q1, q2 = query_list[i], query_list[j]
            sim = float(np.dot(embeddings[q1], embeddings[q2]))
            same = "~SAME (WARNING)" if abs(sim) > 0.999 else "DIFFERENT (OK)"
            print(f"  '{q1}' vs '{q2}': {sim:.6f}  {same}")

    # -- 5. Run actual FAISS search for two queries and compare results ---------
    if result.get('total_indexed', 0) > 0:
        print(f"\n{'='*60}")
        print("FAISS SEARCH COMPARISON:")
        print(f"{'='*60}")
        
        test_pairs = [("person", "vehicle"), ("white truck", "red bicycle")]
        for q1, q2 in test_pairs:
            v1 = clip_service.generate_text_embedding(q1)
            v2 = clip_service.generate_text_embedding(q2)
            r1 = faiss_service.search_top_k(v1, top_k=5, query_text=q1)
            r2 = faiss_service.search_top_k(v2, top_k=5, query_text=q2)
            
            ids1 = [r.get("frame_id") or r.get("object_id") for r in r1]
            ids2 = [r.get("frame_id") or r.get("object_id") for r in r2]
            scores1 = [r.get("similarity_score") for r in r1]
            scores2 = [r.get("similarity_score") for r in r2]
            
            print(f"\n  Query A: '{q1}'")
            print(f"    Scores: {scores1}")
            print(f"    IDs   : {[str(i)[:8] if i else None for i in ids1]}")
            print(f"  Query B: '{q2}'")
            print(f"    Scores: {scores2}")
            print(f"    IDs   : {[str(i)[:8] if i else None for i in ids2]}")
            
            if ids1 == ids2 and len(ids1) > 0:
                print(f"  WARNING: Same results for both queries!")
            else:
                print(f"  OK Results differ between queries")
    
    print(f"\n{'='*60}")
    print("DONE. Check above for any (WARNING) lines.")
    print(f"{'='*60}\n")


asyncio.run(main())
