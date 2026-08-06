# Technical Requirements
## VisionTrace AI — Intelligent Video Search Platform

**Version:** 1.0  
**Date:** August 5, 2026  
**Status:** Draft — Awaiting Approval

---

## 1. System Architecture Overview

VisionTrace AI follows a **decoupled three-tier architecture**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│         React + Vite + TypeScript + TailwindCSS + ShadcnUI      │
│                     Hosted on Vercel                            │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / REST + WebSocket
┌────────────────────────────▼────────────────────────────────────┐
│                       API LAYER                                  │
│              FastAPI (Python 3.11+)                              │
│         REST API · Background Workers · Job Queue               │
│                    Hosted on Railway                             │
└──────┬────────────────────┬────────────────────────┬────────────┘
       │                    │                         │
┌──────▼──────┐   ┌─────────▼──────────┐   ┌────────▼───────────┐
│  PostgreSQL  │   │   FAISS Index      │   │  Supabase Storage  │
│  (Metadata)  │   │  (Vector Store)    │   │  (Files/Thumbs)    │
└─────────────┘   └────────────────────┘   └────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │       AI PIPELINE           │
              │  YOLO · ByteTrack · CLIP    │
              │  (Background Worker Process) │
              └─────────────────────────────┘
```

---

## 2. Frontend Technical Requirements

### 2.1 Framework & Tooling
| Requirement | Specification |
|---|---|
| Framework | React 18+ |
| Build Tool | Vite 5+ |
| Language | TypeScript 5+ (strict mode enabled) |
| Styling | TailwindCSS 3+ |
| Component Library | Shadcn UI (Radix UI primitives) |
| State Management | Zustand (lightweight global state) |
| Server State / Data Fetching | TanStack Query (React Query v5) |
| Routing | React Router v6 |
| Form Handling | React Hook Form + Zod validation |
| HTTP Client | Axios |
| Video Player | Video.js or native HTML5 `<video>` with custom controls |
| File Upload | React Dropzone |
| Charts / Scores | Recharts |
| Export (PDF) | jsPDF + html2canvas |
| Linting | ESLint + Prettier |

### 2.2 Browser Support
- Chrome 110+
- Firefox 110+
- Edge 110+
- Safari 16+ (best effort)

### 2.3 Environment Variables (Frontend)
```
VITE_API_BASE_URL          # Backend API base URL
VITE_SUPABASE_URL          # Supabase project URL
VITE_SUPABASE_ANON_KEY     # Supabase anon public key
```

---

## 3. Backend Technical Requirements

### 3.1 Framework & Runtime
| Requirement | Specification |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI 0.111+ |
| ASGI Server | Uvicorn with Gunicorn workers |
| Task Queue | Celery 5+ with Redis broker |
| ORM | SQLAlchemy 2+ (async) |
| Database Migrations | Alembic |
| Data Validation | Pydantic v2 |
| Authentication | JWT (python-jose) + bcrypt |
| File Handling | python-multipart |
| HTTP Client | httpx |
| Logging | Python structlog + JSON formatter |
| Testing | Pytest + pytest-asyncio |

### 3.2 Background Processing
- Celery workers handle all AI pipeline tasks asynchronously
- Redis acts as the message broker and result backend
- Each video triggers a single Celery task chain:
  `extract_frames → detect_objects → track_objects → generate_embeddings → index_embeddings`
- Job status is written back to PostgreSQL after each step

### 3.3 Environment Variables (Backend)
```
DATABASE_URL               # PostgreSQL connection string
REDIS_URL                  # Redis broker URL
SUPABASE_URL               # Supabase project URL
SUPABASE_SERVICE_KEY       # Supabase service role key (server-side only)
SECRET_KEY                 # JWT signing secret
ALGORITHM                  # JWT algorithm (HS256)
ACCESS_TOKEN_EXPIRE_MINUTES
FAISS_INDEX_PATH           # Local path for FAISS index file(s)
FRAME_EXTRACTION_FPS       # Frames per second to extract (default: 1)
MAX_VIDEO_SIZE_MB           # Max upload size in MB (default: 2048)
YOLO_MODEL_PATH            # Path to YOLO weights file
CLIP_MODEL_NAME            # OpenCLIP model name (e.g., ViT-B-32)
CLIP_PRETRAINED            # OpenCLIP pretrained weights (e.g., laion2b_s34b_b79k)
TOP_K_RESULTS              # Default number of search results to return (default: 20)
```

---

## 4. AI / ML Technical Requirements

### 4.1 Object Detection — YOLO
| Requirement | Specification |
|---|---|
| Library | Ultralytics YOLOv8 |
| Default Model | YOLOv8n (nano) for CPU; YOLOv8m (medium) for GPU |
| Input | Individual video frames (JPEG/PNG) |
| Output | Bounding boxes, class labels, confidence scores per frame |
| Confidence Threshold | 0.4 (configurable) |

### 4.2 Multi-Object Tracking — ByteTrack
| Requirement | Specification |
|---|---|
| Library | ByteTrack (standalone Python implementation) |
| Input | YOLO detection results per frame sequence |
| Output | Track IDs assigned across frames for each detected object |
| Purpose | Group detections of the same object across consecutive frames |

### 4.3 Embedding Generation — OpenCLIP
| Requirement | Specification |
|---|---|
| Library | open_clip_torch |
| Default Model | ViT-B/32 pretrained on LAION-2B |
| Image Embedding | 512-dimensional float32 vector per cropped detection region |
| Text Embedding | 512-dimensional float32 vector per query string |
| Normalization | L2-normalized before indexing and search |
| Batch Processing | Frame crops batched (batch size 32) for efficiency |

### 4.4 Vector Search — FAISS
| Requirement | Specification |
|---|---|
| Library | faiss-cpu (v1.0 default); faiss-gpu optional |
| Index Type | `IndexFlatIP` (inner product on L2-normalized vectors = cosine similarity) |
| Index Granularity | One FAISS index per video (allows per-video search isolation) |
| Index Storage | Serialized to disk at `FAISS_INDEX_PATH/{video_id}.index` |
| Metadata Mapping | FAISS result IDs mapped to frame/detection records in PostgreSQL |
| Top-K | Configurable, default 20 |

### 4.5 Future Phase — InsightFace
- Face detection and recognition pipeline (not in v1.0)
- Will produce 512-dim ArcFace embeddings for face crops
- Subject to strict privacy and consent controls before activation

---

## 5. Database Technical Requirements

### 5.1 PostgreSQL Schema Requirements
| Requirement | Specification |
|---|---|
| Version | PostgreSQL 15+ |
| Hosting | Railway managed PostgreSQL |
| Connection Pooling | PgBouncer or SQLAlchemy async pool (pool_size=10) |
| UUID Primary Keys | All tables use UUID v4 |
| Timestamps | `created_at`, `updated_at` on all tables (UTC) |
| Soft Deletes | `deleted_at` nullable field on User, Video tables |

### 5.2 Core Tables (High-Level)
- `users` — user accounts and roles
- `videos` — uploaded video metadata and processing status
- `processing_jobs` — per-video pipeline job tracking with step statuses
- `frames` — extracted frame metadata (video_id, timestamp, storage path)
- `detections` — YOLO detection results per frame (bounding box, class, confidence)
- `tracks` — ByteTrack-assigned track IDs linking detections across frames
- `embeddings` — CLIP embedding metadata (frame_id, detection_id, faiss_index_id)
- `search_sessions` — user search queries and parameters
- `search_results` — matched frames per search session with scores

---

## 6. Storage Technical Requirements

### 6.1 Supabase Storage
| Requirement | Specification |
|---|---|
| Service | Supabase Storage (S3-compatible) |
| Buckets | `videos` (raw uploads), `frames` (extracted frames/thumbnails) |
| Access Control | Signed URLs for private access; public URLs for thumbnails |
| Max File Size | 2 GB per video (enforced at API layer) |
| Frame Format | JPEG at 80% quality for storage efficiency |

---

## 7. Infrastructure & Deployment Technical Requirements

### 7.1 Containerization
| Requirement | Specification |
|---|---|
| Container Runtime | Docker 24+ |
| Orchestration | Docker Compose (development); Railway (production) |
| Base Images | `python:3.11-slim` (backend), `node:20-alpine` (frontend build) |
| Multi-stage builds | Frontend build artifact served via Vercel CDN |

### 7.2 Services in Docker Compose (Development)
```
services:
  api          # FastAPI app
  worker       # Celery worker
  redis        # Redis broker
  db           # PostgreSQL
```

### 7.3 Production Deployment
| Component | Host |
|---|---|
| Frontend | Vercel (CDN-distributed static site) |
| Backend API | Railway (containerized FastAPI) |
| Celery Workers | Railway (containerized workers) |
| Redis | Railway managed Redis |
| PostgreSQL | Railway managed PostgreSQL |
| File Storage | Supabase Storage |
| FAISS Indexes | Railway persistent volume |

### 7.4 CI/CD
- GitHub Actions pipeline
- On push to `main`: lint → test → build → deploy
- Frontend deploy to Vercel via Vercel GitHub integration
- Backend deploy to Railway via Railway GitHub integration

---

## 8. Security Technical Requirements

| Requirement | Specification |
|---|---|
| Authentication | JWT Bearer tokens (access + refresh) |
| Password Hashing | bcrypt (12 rounds) |
| Transport Security | HTTPS enforced on all endpoints (TLS 1.2+) |
| CORS | Strict origin allowlist (frontend domain only) |
| Rate Limiting | 100 requests/minute per IP on API (via slowapi) |
| File Validation | MIME type + magic bytes check on upload |
| SQL Injection | Parameterized queries via SQLAlchemy ORM only |
| Secrets Management | Environment variables via Railway/Vercel secrets (never in code) |
| FAISS Index Access | Isolated per video; no cross-user index leakage |
| Input Sanitization | All text query inputs sanitized and length-limited (max 512 chars) |

---

## 9. Performance Technical Requirements

| Metric | Target | Approach |
|---|---|---|
| Search latency | < 3s end-to-end | FAISS in-memory index + async FastAPI |
| Frame extraction throughput | ≥ 10 FPS equivalent | OpenCV batch extraction |
| Embedding batch throughput | ≥ 100 crops/min on CPU | OpenCLIP batched inference |
| API response time (non-AI) | < 200ms p95 | SQLAlchemy async queries |
| Concurrent users | 50 simultaneous (v1.0) | Uvicorn + Gunicorn multi-worker |
| Video upload speed | Depends on client bandwidth | Chunked multipart upload |

---

## 10. Observability Requirements

| Requirement | Tool |
|---|---|
| Structured logging | structlog (JSON output) |
| API request tracing | FastAPI middleware (request ID injection) |
| Celery task monitoring | Flower dashboard |
| Error tracking | Sentry (Python SDK + React SDK) |
| Health checks | `/health` and `/readiness` endpoints on API |
| Uptime monitoring | UptimeRobot or Railway built-in |
