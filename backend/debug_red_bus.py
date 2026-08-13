import asyncio
from app.services.faiss_service import faiss_service
from app.services.clip_service import clip_service
from app.db.session import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        await faiss_service.build_index_from_db(db)
        q_vec = clip_service.generate_text_embedding("red bus")
        print("FAISS Index total vectors:", len(faiss_service._metadata_map))
        import uuid
        target_vid = uuid.UUID("53d21b7b-2190-4887-a348-a45b0eb1cd3d")
        
        # Count how many vectors in metadata_map belong to target_vid
        vid_count = sum(1 for m in faiss_service._metadata_map.values() if m.get("video_id") == str(target_vid))
        print(f"Vectors in metadata_map for video {target_vid}: {vid_count}")

        res = faiss_service.search_top_k(
            query_vector=q_vec,
            top_k=5,
            video_ids=[target_vid],
            min_score=0.0,
            query_text="red bus"
        )
        print("\nResults for 'red bus':")
        for r in res:
            print(f" - [{r.get('type')}] Label: {r.get('label')} | Score: {r.get('similarity_score')} | Time: {r.get('timestamp_seconds')}s")

if __name__ == "__main__":
    asyncio.run(main())
