import torch
import open_clip
import numpy as np

print(f"torch: {torch.__version__}")
print(f"open_clip: {open_clip.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

# Test model load
print("Loading ViT-B-32 model...")
try:
    model, _, preprocess = open_clip.create_model_and_transforms(
        'ViT-B-32',
        pretrained='laion2b_s34b_b79k'
    )
    tokenizer = open_clip.get_tokenizer('ViT-B-32')
    model = model.eval()
    print("Model loaded successfully!")

    # Test text embedding
    queries = ["person", "white truck", "red bicycle", "black shirt"]
    embeddings = []
    for q in queries:
        tokens = tokenizer([q])
        with torch.no_grad():
            feats = model.encode_text(tokens)
            feats /= feats.norm(dim=-1, keepdim=True)
            vec = feats[0].numpy()
            embeddings.append(vec)
            print(f"\nQuery: '{q}'")
            print(f"  Dim: {len(vec)}, Norm: {np.linalg.norm(vec):.6f}")
            print(f"  [0:10]: {[round(float(v), 6) for v in vec[:10]]}")

    # Verify embeddings are different
    print("\n--- Cosine Similarity Matrix ---")
    for i in range(len(queries)):
        for j in range(i+1, len(queries)):
            sim = float(np.dot(embeddings[i], embeddings[j]))
            print(f"  '{queries[i]}' vs '{queries[j]}': {sim:.6f}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
