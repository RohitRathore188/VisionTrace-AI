# Software Architecture
## VisionTrace AI — Intelligent Video Search Platform

**Version:** 1.0  
**Date:** August 5, 2026  
**Status:** Draft — Awaiting Approval

---

## Table of Contents

1. [High-Level System Architecture](#1-high-level-system-architecture)
2. [Frontend Architecture](#2-frontend-architecture)
3. [Backend Architecture](#3-backend-architecture)
4. [AI Pipeline Architecture](#4-ai-pipeline-architecture)
5. [Database Architecture](#5-database-architecture)
6. [Storage Architecture](#6-storage-architecture)
7. [Authentication Flow](#7-authentication-flow)
8. [API Request Flow](#8-api-request-flow)
9. [Video Processing Pipeline Flow](#9-video-processing-pipeline-flow)
10. [Search Pipeline Flow](#10-search-pipeline-flow)
11. [Deployment Architecture](#11-deployment-architecture)
12. [Scalability Architecture](#12-scalability-architecture)

---

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        UI[React SPA<br/>Vite + TypeScript<br/>TailwindCSS + Shadcn UI]
    end

    subgraph "API Layer - Railway"
        API[FastAPI<br/>REST Endpoints<br/>JWT Auth]
        WS[WebSocket<br/>Status Updates]
    end

    subgraph "Worker Layer - Railway"
        W1[Celery Worker 1<br/>AI Pipeline Tasks]
        W2[Celery Worker 2<br/>AI Pipeline Tasks]
        WN[Celery Worker N<br/>AI Pipeline Tasks]
    end

    subgraph "Message Broker"
        REDIS[(Redis<br/>Task Queue)]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Metadata + Results)]
        STORAGE[Supabase Storage<br/>Videos + Frames]
        FAISS[FAISS Indexes<br/>Vector Search]
    end

    subgraph "External Services"
        SENTRY[Sentry<br/>Error Tracking]
        VERCEL[Vercel CDN<br/>Static Assets]
    end

    UI -->|HTTPS REST| API
    UI -->|WSS| WS
    API -->|Enqueue Tasks| REDIS
    REDIS -->|Consume Tasks| W1
    REDIS -->|Consume Tasks| W2
    REDIS -->|Consume Tasks| WN
    API -->|Read/Write| DB
    W1 -->|Read/Write| DB
    W2 -->|Read/Write| DB
    WN -->|Read/Write| DB
    API -->|Upload/Download| STORAGE
    W1 -->|Upload/Download| STORAGE
    W2 -->|Upload/Download| STORAGE
    WN -->|Upload/Download| STORAGE
    API -->|Load Index<br/>Search| FAISS
    W1 -->|Write Index| FAISS
    W2 -->|Write Index| FAISS
    WN -->|Write Index| FAISS
    API -->|Report Errors| SENTRY
    W1 -->|Report Errors| SENTRY
    VERCEL -->|Serve UI| UI

    style UI fill:#e1f5ff
    style API fill:#fff4e6
    style W1 fill:#f3e5f5
    style W2 fill:#f3e5f5
    style WN fill:#f3e5f5
    style DB fill:#e8f5e9
    style STORAGE fill:#e8f5e9
    style FAISS fill:#e8f5e9
```

**Key Principles:**
- **Separation of Concerns:** UI, API, and Workers are independently deployable
- **Asynchronous Processing:** Long-running AI tasks handled by Celery workers
- **Stateless API:** All state persisted in PostgreSQL, Redis, or FAISS
- **Horizontal Scalability:** Add more worker replicas to increase throughput

---

## 2. Frontend Architecture

```mermaid
graph TB
    subgraph "React Application"
        subgraph "Routing Layer"
            ROUTER[React Router v6<br/>Route Definitions]
        end

        subgraph "Feature Modules"
            AUTH[Auth Module<br/>Login/Register/Guards]
            VIDEOS[Videos Module<br/>Library/Upload]
            SEARCH[Search Module<br/>Image/Text Query]
            RESULTS[Results Module<br/>Display/Filter/Sort]
            PLAYER[Player Module<br/>Video Playback]
            REPORTS[Reports Module<br/>CSV/PDF Export]
            HISTORY[History Module<br/>Past Searches]
            ADMIN[Admin Module<br/>Dashboard/Users]
        end

        subgraph "Shared Services"
            APISERVICE[API Service<br/>Axios Instance]
            AUTHSTORE[Auth Store<br/>Zustand]
            VIDEOSTORE[Video Store<br/>Zustand]
            PLAYERSTORE[Player Store<br/>Zustand]
        end

        subgraph "UI Components"
            LAYOUT[Layout Components<br/>Navbar/Sidebar]
            COMMON[Common Components<br/>Badges/Buttons/Cards]
            FORMS[Form Components<br/>Dropzone/Inputs]
        end

        subgraph "Data Fetching"
            TANSTACK[TanStack Query<br/>Server State Cache]
        end
    end

    ROUTER --> AUTH
    ROUTER --> VIDEOS
    ROUTER --> SEARCH
    ROUTER --> RESULTS
    ROUTER --> PLAYER
    ROUTER --> REPORTS
    ROUTER --> HISTORY
    ROUTER --> ADMIN

    AUTH --> AUTHSTORE
    VIDEOS --> VIDEOSTORE
    PLAYER --> PLAYERSTORE

    AUTH --> APISERVICE
    VIDEOS --> APISERVICE
    SEARCH --> APISERVICE
    RESULTS --> APISERVICE
    HISTORY --> APISERVICE
    ADMIN --> APISERVICE

    APISERVICE --> TANSTACK

    AUTH --> LAYOUT
    VIDEOS --> COMMON
    SEARCH --> FORMS
    RESULTS --> COMMON

    APISERVICE -->|HTTP/HTTPS| BACKEND[Backend API]

    style ROUTER fill:#e3f2fd
    style AUTH fill:#fff3e0
    style VIDEOS fill:#fff3e0
    style SEARCH fill:#fff3e0
    style RESULTS fill:#fff3e0
    style APISERVICE fill:#f1f8e9
    style AUTHSTORE fill:#fce4ec
    style TANSTACK fill:#e0f2f1
```

**Architecture Decisions:**

1. **Feature-First Structure:** Each feature (auth, videos, search) is self-contained with its own components, hooks, and types
2. **Zustand for Global State:** Lightweight state management for auth, video library, and player state
3. **TanStack Query for Server State:** Handles caching, refetching, and optimistic updates for API data
4. **Axios Interceptors:** Centralized token refresh, request ID injection, and error handling
5. **Component Co-location:** Feature components live alongside feature logic, not in a flat `/components` folder

---

## 3. Backend Architecture

```mermaid
graph TB
    subgraph "FastAPI Application"
        subgraph "HTTP Layer"
            MIDDLEWARE[Middleware Stack<br/>CORS/RateLimit/RequestID/Logging]
            ROUTER[API Router<br/>Route Registration]
        end

        subgraph "Route Handlers"
            AUTH_API[Auth Routes<br/>/auth/*]
            USER_API[User Routes<br/>/users/*]
            VIDEO_API[Video Routes<br/>/videos/*]
            SEARCH_API[Search Routes<br/>/search/*]
            ADMIN_API[Admin Routes<br/>/admin/*]
            SYSTEM_API[System Routes<br/>/system/*]
        end

        subgraph "Business Logic Layer"
            AUTH_SVC[Auth Service<br/>Registration/Login/Tokens]
            VIDEO_SVC[Video Service<br/>Upload/Metadata/Delete]
            STORAGE_SVC[Storage Service<br/>Supabase Upload/Download]
            SEARCH_SVC[Search Service<br/>Embedding/FAISS Search]
            INDEX_SVC[Index Service<br/>FAISS Load/Save]
            RESULT_SVC[Result Service<br/>Persistence/Retrieval]
            ADMIN_SVC[Admin Service<br/>Metrics/Jobs]
        end

        subgraph "Data Access Layer"
            MODELS[SQLAlchemy Models<br/>ORM Definitions]
            SCHEMAS[Pydantic Schemas<br/>Request/Response]
            SESSION[DB Session Factory<br/>Async Connection Pool]
        end

        subgraph "Core Infrastructure"
            SECURITY[Security Module<br/>JWT/Hashing]
            EXCEPTIONS[Exception Handlers<br/>HTTP Error Mapping]
            LOGGING[Structured Logging<br/>Request Context]
        end

        subgraph "AI Model Layer"
            CLIP_MODEL[OpenCLIP Model<br/>Singleton Instance]
            YOLO_MODEL[YOLO Model<br/>Singleton Instance]
        end
    end

    MIDDLEWARE --> ROUTER
    ROUTER --> AUTH_API
    ROUTER --> USER_API
    ROUTER --> VIDEO_API
    ROUTER --> SEARCH_API
    ROUTER --> ADMIN_API
    ROUTER --> SYSTEM_API

    AUTH_API --> AUTH_SVC
    VIDEO_API --> VIDEO_SVC
    VIDEO_API --> STORAGE_SVC
    SEARCH_API --> SEARCH_SVC
    SEARCH_API --> INDEX_SVC
    ADMIN_API --> ADMIN_SVC

    VIDEO_SVC --> MODELS
    SEARCH_SVC --> MODELS
    SEARCH_SVC --> CLIP_MODEL
    INDEX_SVC --> FAISS_IDX[(FAISS Indexes)]

    AUTH_SVC --> SECURITY
    AUTH_API --> EXCEPTIONS

    MODELS --> SESSION
    SESSION --> POSTGRES[(PostgreSQL)]

    VIDEO_SVC --> CELERY_PROD[Celery Producer<br/>Enqueue Pipeline]
    CELERY_PROD --> REDIS[(Redis)]

    style MIDDLEWARE fill:#e3f2fd
    style AUTH_SVC fill:#fff3e0
    style VIDEO_SVC fill:#fff3e0
    style SEARCH_SVC fill:#fff3e0
    style MODELS fill:#e8f5e9
    style SECURITY fill:#fce4ec
    style CLIP_MODEL fill:#f3e5f5
```

**Architecture Decisions:**

1. **Thin Route Handlers:** Routes only validate input, call services, and return responses
2. **Service Layer Encapsulation:** All business logic lives in services, not in routes
3. **Async SQLAlchemy:** Non-blocking database operations for high concurrency
4. **Singleton AI Models:** Models loaded once at startup, shared across requests
5. **Middleware Pipeline:** Request ID → Logging → Rate Limiting → CORS → Auth

---

## 4. AI Pipeline Architecture

```mermaid
graph TB
    subgraph "Celery Worker Process"
        subgraph "Task Definitions"
            T1[Task 1<br/>Frame Extraction]
            T2[Task 2<br/>Object Detection]
            T3[Task 3<br/>Object Tracking]
            T4[Task 4<br/>Embedding Generation]
            T5[Task 5<br/>Index Building]
        end

        subgraph "AI Models - Loaded Once at Startup"
            YOLO[YOLOv8 Model<br/>Object Detection]
            CLIP[OpenCLIP Model<br/>Image Encoder]
            BYTETRACK[ByteTrack Tracker<br/>Multi-Object Tracking]
        end

        subgraph "Worker Infrastructure"
            CELERY_CONSUMER[Celery Consumer<br/>Task Executor]
            RETRY_LOGIC[Retry Handler<br/>Exponential Backoff]
            STATUS_UPDATER[Status Updater<br/>DB Write]
        end
    end

    subgraph "External Dependencies"
        REDIS_BROKER[(Redis<br/>Task Queue)]
        POSTGRES_DB[(PostgreSQL<br/>Metadata Storage)]
        SUPABASE_STORAGE[Supabase Storage<br/>Video/Frame Files]
        FAISS_DISK[Persistent Volume<br/>FAISS Index Files]
    end

    REDIS_BROKER -->|Consume Task| CELERY_CONSUMER
    CELERY_CONSUMER --> T1
    T1 --> T2
    T2 --> T3
    T3 --> T4
    T4 --> T5

    T1 -->|Download Video| SUPABASE_STORAGE
    T1 -->|Upload Frames| SUPABASE_STORAGE
    T1 -->|Write Frame Metadata| POSTGRES_DB

    T2 -->|Load Model| YOLO
    T2 -->|Download Frames| SUPABASE_STORAGE
    T2 -->|Write Detections| POSTGRES_DB

    T3 -->|Use Tracker| BYTETRACK
    T3 -->|Read Detections| POSTGRES_DB
    T3 -->|Write Tracks| POSTGRES_DB

    T4 -->|Load Model| CLIP
    T4 -->|Download Frames| SUPABASE_STORAGE
    T4 -->|Write Embeddings| POSTGRES_DB

    T5 -->|Read Embeddings| POSTGRES_DB
    T5 -->|Serialize Index| FAISS_DISK
    T5 -->|Update Video Status| POSTGRES_DB

    T1 --> STATUS_UPDATER
    T2 --> STATUS_UPDATER
    T3 --> STATUS_UPDATER
    T4 --> STATUS_UPDATER
    T5 --> STATUS_UPDATER
    STATUS_UPDATER --> POSTGRES_DB

    T1 --> RETRY_LOGIC
    T2 --> RETRY_LOGIC
    T3 --> RETRY_LOGIC
    T4 --> RETRY_LOGIC
    T5 --> RETRY_LOGIC
    RETRY_LOGIC -->|Requeue on Failure| REDIS_BROKER

    style T1 fill:#e3f2fd
    style T2 fill:#fff3e0
    style T3 fill:#f3e5f5
    style T4 fill:#e0f2f1
    style T5 fill:#fce4ec
    style YOLO fill:#ffebee
    style CLIP fill:#ffebee
    style BYTETRACK fill:#ffebee
```

**Pipeline Flow:**
1. **Frame Extraction (T1):** OpenCV extracts frames at 1 FPS → upload to Supabase
2. **Object Detection (T2):** YOLOv8 detects objects in each frame → save bboxes to DB
3. **Object Tracking (T3):** ByteTrack assigns track IDs across frames → update DB
4. **Embedding Generation (T4):** OpenCLIP generates 512-dim vectors per detection → save to DB
5. **Index Building (T5):** Build FAISS index from all embeddings → serialize to disk

---

## 5. Database Architecture

```mermaid
erDiagram
    users ||--o{ videos : "uploads"
    users ||--o{ search_sessions : "performs"
    videos ||--o{ frames : "contains"
    videos ||--o{ processing_jobs : "has"
    videos ||--o{ tracks : "has"
    frames ||--o{ detections : "has"
    detections ||--o{ embeddings : "generates"
    tracks ||--o{ detections : "links"
    search_sessions ||--o{ search_results : "produces"
    frames ||--o{ search_results : "matches"

    users {
        uuid id PK
        string email UK
        string password_hash
        enum role
        boolean is_active
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    videos {
        uuid id PK
        uuid uploaded_by FK
        string title
        string filename
        int size_bytes
        int duration_seconds
        enum status
        string storage_path
        string thumbnail_url
        timestamp created_at
        timestamp indexed_at
    }

    processing_jobs {
        uuid id PK
        uuid video_id FK
        enum current_step
        jsonb step_status
        int attempt_count
        string error_message
        timestamp started_at
        timestamp completed_at
    }

    frames {
        uuid id PK
        uuid video_id FK
        int frame_number
        float timestamp_seconds
        string storage_path
        int width
        int height
        timestamp created_at
    }

    detections {
        uuid id PK
        uuid frame_id FK
        uuid track_id FK
        int class_id
        string class_name
        float confidence
        float bbox_x
        float bbox_y
        float bbox_w
        float bbox_h
        timestamp created_at
    }

    tracks {
        uuid id PK
        uuid video_id FK
        int track_id
        uuid first_frame_id FK
        uuid last_frame_id FK
        int frame_count
        timestamp created_at
    }

    embeddings {
        uuid id PK
        uuid frame_id FK
        uuid detection_id FK
        int faiss_index_id
        bytea vector
        timestamp created_at
    }

    search_sessions {
        uuid id PK
        uuid user_id FK
        enum query_type
        string query_text
        bytea query_image_hash
        int top_k
        jsonb video_ids
        timestamp created_at
    }

    search_results {
        uuid id PK
        uuid session_id FK
        uuid frame_id FK
        uuid detection_id FK
        int rank
        float similarity_score
        timestamp created_at
    }
```

**Key Design Decisions:**

1. **UUID Primary Keys:** Enables distributed ID generation without coordination
2. **Soft Deletes:** `deleted_at` field on users and videos preserves audit trail
3. **JSONB for Flexibility:** `step_status` and `video_ids` use JSONB for dynamic structures
4. **Indexed Foreign Keys:** All FK columns have indexes for join performance
5. **Timestamp Auditing:** `created_at` and `updated_at` on all tables
6. **Vector Storage:** Embeddings stored as `bytea` (or `pgvector` extension if available)

**Indexes (Performance-Critical):**
- `videos.uploaded_by` (user video list)
- `frames.video_id, frames.frame_number` (ordered frame retrieval)
- `detections.frame_id` (join to frames)
- `embeddings.faiss_index_id` (FAISS result mapping)
- `search_sessions.user_id, search_sessions.created_at DESC` (history pagination)
- `search_results.session_id, search_results.rank` (result retrieval)

---

## 6. Storage Architecture

```mermaid
graph TB
    subgraph "Supabase Storage"
        subgraph "videos Bucket"
            V1[video_uuid_1.mp4<br/>Raw Upload]
            V2[video_uuid_2.mp4<br/>Raw Upload]
            VN[video_uuid_N.mp4<br/>Raw Upload]
        end

        subgraph "frames Bucket"
            F1[video_uuid_1/<br/>frame_0001.jpg<br/>frame_0002.jpg<br/>...]
            F2[video_uuid_2/<br/>frame_0001.jpg<br/>frame_0002.jpg<br/>...]
            FN[video_uuid_N/<br/>frame_0001.jpg<br/>frame_0002.jpg<br/>...]
        end
    end

    subgraph "Railway Persistent Volume"
        subgraph "FAISS Index Storage"
            I1[video_uuid_1.index<br/>FAISS IndexFlatIP]
            I2[video_uuid_2.index<br/>FAISS IndexFlatIP]
            IN[video_uuid_N.index<br/>FAISS IndexFlatIP]
        end
    end

    subgraph "PostgreSQL Database"
        META[Video Metadata<br/>Frame Metadata<br/>Detection Metadata<br/>Embedding Metadata]
    end

    API[FastAPI API] -->|Upload Video| V1
    WORKER[Celery Worker] -->|Download Video| V1
    WORKER -->|Upload Frames| F1
    WORKER -->|Download Frames| F1
    API -->|Generate Signed URL| V1
    API -->|Generate Signed URL| F1

    WORKER -->|Write Index| I1
    API -->|Load Index for Search| I1

    API -->|Read/Write Metadata| META
    WORKER -->|Read/Write Metadata| META

    style V1 fill:#e3f2fd
    style F1 fill:#fff3e0
    style I1 fill:#f3e5f5
    style META fill:#e8f5e9
```

**Storage Strategy:**

1. **Videos Bucket (Supabase):**
   - Raw uploaded video files stored with original format
   - Access via short-lived signed URLs (1-hour expiry)
   - Public access disabled; all access requires authentication

2. **Frames Bucket (Supabase):**
   - Extracted frames organized by `video_id` prefix
   - JPEG format at 80% quality for storage efficiency
   - Thumbnail generation: resize to 320px max dimension
   - Signed URLs for thumbnails with 24-hour expiry

3. **FAISS Index Files (Railway Persistent Volume):**
   - One `.index` file per video
   - Named by `video_id.index` for easy lookup
   - Loaded into memory on-demand for search
   - No replication (can be rebuilt from DB if lost)

4. **PostgreSQL (Railway Managed):**
   - All metadata and relational data
   - Embeddings stored as `bytea` (512 floats × 4 bytes = 2 KB per embedding)
   - Daily automated backups via Railway

**Scaling Considerations:**

- **Storage Growth:** ~100 MB per hour of video (1 FPS extraction, JPEG)
- **Index Growth:** ~2 KB per detection embedding
- **Example:** 1000 hours of video = 100 GB storage + ~5 GB embeddings + ~500 MB indexes

---

## 7. Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as React UI
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Redis

    Note over User,Redis: Registration Flow
    User->>UI: Enter email + password
    UI->>API: POST /auth/register
    API->>API: Validate input
    API->>API: Hash password (bcrypt)
    API->>DB: INSERT INTO users
    DB-->>API: User record created
    API-->>UI: 201 Created
    UI-->>User: "Registration successful"

    Note over User,Redis: Login Flow
    User->>UI: Enter credentials
    UI->>API: POST /auth/login
    API->>DB: SELECT user WHERE email = ?
    DB-->>API: User record
    API->>API: Verify password (bcrypt)
    API->>API: Generate JWT access token (15 min)
    API->>API: Generate refresh token (7 days)
    API->>Redis: SETEX refresh_token_id (7 days)
    API-->>UI: Access token + Set-Cookie refresh_token
    UI->>UI: Store access token in memory
    UI-->>User: Redirect to dashboard

    Note over User,Redis: Authenticated Request Flow
    User->>UI: Click "Upload Video"
    UI->>API: POST /videos/upload<br/>Authorization: Bearer {access_token}
    API->>API: Decode & validate JWT
    API->>API: Extract user_id from JWT
    API->>API: Execute route handler
    API-->>UI: 202 Accepted

    Note over User,Redis: Token Refresh Flow
    UI->>API: POST /videos (access token expired)
    API-->>UI: 401 Unauthorized
    UI->>API: POST /auth/refresh<br/>Cookie: refresh_token
    API->>Redis: GET refresh_token_id
    Redis-->>API: Token exists
    API->>API: Validate refresh token signature
    API->>API: Generate new access token (15 min)
    API->>API: Generate new refresh token (7 days)
    API->>Redis: DEL old_refresh_token_id
    API->>Redis: SETEX new_refresh_token_id
    API-->>UI: New access token + Set-Cookie new_refresh_token
    UI->>UI: Retry original request with new token
    UI->>API: POST /videos (with new access token)
    API-->>UI: 202 Accepted

    Note over User,Redis: Logout Flow
    User->>UI: Click logout
    UI->>API: POST /auth/logout<br/>Cookie: refresh_token
    API->>Redis: DEL refresh_token_id
    API-->>UI: Set-Cookie refresh_token (expired)
    UI->>UI: Clear access token from memory
    UI-->>User: Redirect to login
```

**Security Properties:**

1. **Short-Lived Access Tokens:** 15-minute expiry reduces window for token theft
2. **HttpOnly Refresh Tokens:** Cannot be accessed by JavaScript (XSS protection)
3. **Token Rotation:** Each refresh invalidates the old refresh token
4. **Redis Whitelist:** Only valid refresh tokens exist in Redis; revocation is instant
5. **Logout = Revocation:** Logout deletes the refresh token from Redis

---

## 8. API Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant Vercel as Vercel CDN
    participant Nginx as Railway Load Balancer
    participant Middleware as FastAPI Middleware
    participant Route as Route Handler
    participant Service as Service Layer
    participant DB as PostgreSQL
    participant Storage as Supabase Storage
    participant Sentry

    Client->>Vercel: GET /dashboard
    Vercel-->>Client: Serve React SPA

    Client->>Nginx: POST /api/v1/search/image<br/>Authorization: Bearer {token}
    Nginx->>Middleware: Forward request
    
    Middleware->>Middleware: Inject X-Request-ID
    Middleware->>Middleware: Log request start
    Middleware->>Middleware: Check rate limit
    Middleware->>Middleware: Parse JWT from header
    Middleware->>Middleware: Validate JWT signature
    Middleware->>Middleware: Extract user_id from JWT
    
    Middleware->>Route: Call route handler with user context
    Route->>Route: Validate request body (Pydantic)
    Route->>Service: search_service.image_search(query_image, user_id, params)
    
    Service->>Service: Generate OpenCLIP embedding for query image
    Service->>Service: Load FAISS index from disk
    Service->>Service: Execute FAISS search (top-K)
    Service->>DB: Map FAISS IDs to embeddings table
    DB-->>Service: Embedding records
    Service->>DB: Join to detections, frames, videos
    DB-->>Service: Full result records
    Service->>Storage: Generate signed URLs for thumbnails
    Storage-->>Service: Signed URLs
    Service->>DB: INSERT search_session + search_results
    DB-->>Service: Session ID
    
    Service-->>Route: Ranked results with metadata
    Route->>Route: Serialize to Pydantic response schema
    Route-->>Middleware: Return 200 OK + JSON body
    
    Middleware->>Middleware: Log response (status, duration)
    Middleware-->>Nginx: HTTP response
    Nginx-->>Client: HTTP response with X-Request-ID header

    alt Error Occurs
        Service->>Sentry: Capture exception with context
        Service-->>Route: Raise HTTP exception
        Route->>Middleware: Exception handler catches
        Middleware->>Middleware: Log error with request_id
        Middleware-->>Client: 500 Internal Server Error + error envelope
    end
```

**Middleware Stack (Execution Order):**

1. **Request ID Injection:** Generate UUID, attach to `request.state.request_id`
2. **Structured Logging:** Bind request_id, method, path to log context
3. **Rate Limiting:** Check Redis counter; return 429 if exceeded
4. **CORS Validation:** Verify `Origin` header matches allowlist
5. **JWT Authentication:** Decode token, attach `request.state.user` (routes can override with `Depends`)
6. **Exception Handling:** Catch all exceptions, log, return standardized error envelope
7. **Response Logging:** Log status code, duration, user_id

---

## 9. Video Processing Pipeline Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as React UI
    participant API as FastAPI
    participant Storage as Supabase Storage
    participant Redis
    participant Worker as Celery Worker
    participant DB as PostgreSQL
    participant YOLO
    participant CLIP
    participant FAISS as FAISS Disk

    User->>UI: Upload video file
    UI->>API: POST /videos/upload (multipart)
    API->>API: Validate file type & size
    API->>Storage: Upload video to bucket
    Storage-->>API: storage_path
    API->>DB: INSERT video record (status=uploaded)
    DB-->>API: video_id
    API->>Redis: Enqueue pipeline chain
    Redis-->>API: task_id
    API-->>UI: 202 Accepted {video_id}
    UI->>UI: Start polling /videos/{id}/job-status
    UI-->>User: Show "Processing..." status

    Redis->>Worker: Consume Task 1: Frame Extraction
    Worker->>DB: INSERT processing_job (current_step=frame_extraction)
    Worker->>Storage: Download video file
    Storage-->>Worker: Video stream
    Worker->>Worker: Extract frames @ 1 FPS (OpenCV)
    loop For each frame
        Worker->>Storage: Upload frame JPEG
        Worker->>DB: INSERT frame record
    end
    Worker->>DB: UPDATE processing_job (step=complete)
    Worker->>Redis: Enqueue Task 2

    Redis->>Worker: Consume Task 2: Object Detection
    Worker->>DB: UPDATE processing_job (current_step=object_detection)
    Worker->>YOLO: Load model (once at startup)
    Worker->>DB: SELECT all frames for video
    loop For each frame batch
        Worker->>Storage: Download frame images
        Worker->>YOLO: Run inference
        YOLO-->>Worker: Detections (bbox, class, confidence)
        Worker->>DB: INSERT detection records
    end
    Worker->>DB: UPDATE processing_job (step=complete)
    Worker->>Redis: Enqueue Task 3

    Redis->>Worker: Consume Task 3: Object Tracking
    Worker->>DB: UPDATE processing_job (current_step=object_tracking)
    Worker->>DB: SELECT all detections ORDER BY frame_number
    Worker->>Worker: Run ByteTrack tracker
    Worker->>DB: INSERT track records + UPDATE detections with track_id
    Worker->>DB: UPDATE processing_job (step=complete)
    Worker->>Redis: Enqueue Task 4

    Redis->>Worker: Consume Task 4: Embedding Generation
    Worker->>DB: UPDATE processing_job (current_step=embedding_generation)
    Worker->>CLIP: Load model (once at startup)
    Worker->>DB: SELECT all detections
    loop For each detection batch
        Worker->>Storage: Download frame images
        Worker->>Worker: Crop detection regions
        Worker->>CLIP: Generate embeddings (batch)
        CLIP-->>Worker: 512-dim vectors (L2-normalized)
        Worker->>DB: INSERT embedding records
    end
    Worker->>DB: UPDATE processing_job (step=complete)
    Worker->>Redis: Enqueue Task 5

    Redis->>Worker: Consume Task 5: Index Building
    Worker->>DB: UPDATE processing_job (current_step=index_building)
    Worker->>DB: SELECT all embeddings ORDER BY faiss_index_id
    Worker->>Worker: Build FAISS IndexFlatIP
    Worker->>FAISS: Serialize index to disk {video_id}.index
    Worker->>DB: UPDATE video (status=ready, indexed_at=NOW())
    Worker->>DB: UPDATE processing_job (current_step=complete)

    UI->>API: GET /videos/{id}/job-status (polling)
    API->>DB: SELECT processing_job
    DB-->>API: current_step=complete
    API-->>UI: {status: ready}
    UI-->>User: "Ready to search!"
```

**Pipeline Duration (30-minute video @ 1 FPS):**
- Frame Extraction: ~2 min
- Object Detection: ~6 min (CPU) / ~1 min (GPU)
- Object Tracking: ~30 sec
- Embedding Generation: ~5 min (CPU) / ~1 min (GPU)
- Index Building: ~10 sec
- **Total (CPU):** ~14 minutes
- **Total (GPU):** ~5 minutes

---

## 10. Search Pipeline Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as React UI
    participant API as FastAPI
    participant CLIP as OpenCLIP Model
    participant FAISS as FAISS Index
    participant DB as PostgreSQL
    participant Storage as Supabase Storage

    Note over User,Storage: Image Search Flow
    User->>UI: Upload query image
    UI->>API: POST /search/image (multipart)<br/>{file, video_ids, top_k}
    API->>API: Validate image file
    API->>CLIP: Load model (singleton)
    API->>CLIP: Generate query embedding
    CLIP-->>API: 512-dim vector (L2-normalized)
    
    alt Search Single Video
        API->>FAISS: Load index from disk {video_id}.index
        FAISS-->>API: Index loaded into memory
        API->>FAISS: search(query_vector, k=top_k)
        FAISS-->>API: [(faiss_id, similarity_score), ...]
    else Search All Videos
        loop For each ready video
            API->>FAISS: Load index {video_id}.index
            API->>FAISS: search(query_vector, k=top_k)
            FAISS-->>API: Top-K results for this video
        end
        API->>API: Merge and re-rank all results globally
    end

    API->>DB: Map faiss_ids to embeddings.faiss_index_id
    DB-->>API: Embedding records
    API->>DB: JOIN embeddings → detections → frames → videos
    DB-->>API: Full result metadata
    
    loop For each result
        API->>Storage: Generate signed URL for frame thumbnail
        Storage-->>API: signed_url (expires in 24h)
    end

    API->>DB: INSERT search_session
    DB-->>API: session_id
    API->>DB: INSERT search_results (session_id, frame_id, rank, score)
    
    API-->>UI: 200 OK {session_id, results[]}
    UI->>UI: Render results with thumbnails
    UI-->>User: Display ranked matches

    Note over User,Storage: Text Search Flow
    User->>UI: Enter text query
    UI->>API: POST /search/text<br/>{query: "person in red jacket", video_ids, top_k}
    API->>API: Sanitize and validate text
    API->>CLIP: Generate text embedding
    CLIP-->>API: 512-dim vector (L2-normalized)
    API->>FAISS: search(query_vector, k=top_k)
    Note right of API: Rest of flow identical to image search

    Note over User,Storage: View Result & Jump to Timestamp
    User->>UI: Click result card
    UI->>API: GET /videos/{video_id}/stream-url
    API->>Storage: Generate signed URL (expires in 1h)
    Storage-->>API: signed_url
    API-->>UI: {url, expires_at}
    UI->>UI: Load video player with signed URL
    UI->>UI: Seek to result.timestamp_seconds
    UI-->>User: Video plays at matched moment
```

**Search Performance:**
- **Query Embedding Generation:** ~50ms (CLIP inference)
- **FAISS Search (per index):** ~10–100ms depending on index size
  - 10K vectors: ~10ms
  - 100K vectors: ~50ms
  - 1M vectors: ~200ms (switch to IndexIVFFlat)
- **Database Join & Metadata:** ~50ms
- **Signed URL Generation:** ~10ms per result
- **Total End-to-End:** < 3 seconds for 20 results from a 100K-vector index

---

## 11. Deployment Architecture

```mermaid
graph TB
    subgraph "User Devices"
        BROWSER[Web Browser<br/>Chrome/Firefox/Edge/Safari]
    end

    subgraph "Vercel - Frontend Hosting"
        CDN[Vercel CDN<br/>Global Edge Network]
        STATIC[Static Assets<br/>React Bundle + Images]
    end

    subgraph "Railway - Backend Hosting"
        subgraph "API Service"
            API1[FastAPI Instance 1<br/>Uvicorn + Gunicorn]
            API2[FastAPI Instance 2<br/>Uvicorn + Gunicorn]
            APIN[FastAPI Instance N<br/>Uvicorn + Gunicorn]
            LB[Railway Load Balancer<br/>Round Robin]
        end

        subgraph "Worker Service"
            W1[Celery Worker 1<br/>AI Pipeline]
            W2[Celery Worker 2<br/>AI Pipeline]
            WN[Celery Worker N<br/>AI Pipeline]
        end

        subgraph "Managed Services"
            REDIS_SVC[(Redis<br/>Managed Instance)]
            PG_SVC[(PostgreSQL 15<br/>Managed Instance)]
        end

        subgraph "Persistent Storage"
            VOLUME[Persistent Volume<br/>FAISS Indexes]
        end
    end

    subgraph "Supabase - Storage & Database"
        SUPABASE_STORAGE[Supabase Storage<br/>S3-Compatible<br/>Videos + Frames]
    end

    subgraph "Observability"
        SENTRY[Sentry<br/>Error Tracking]
        UPTIMEROBOT[UptimeRobot<br/>Health Monitoring]
    end

    BROWSER -->|HTTPS| CDN
    CDN --> STATIC
    BROWSER -->|API Requests<br/>HTTPS/WSS| LB
    
    LB --> API1
    LB --> API2
    LB --> APIN

    API1 --> REDIS_SVC
    API2 --> REDIS_SVC
    APIN --> REDIS_SVC

    API1 --> PG_SVC
    API2 --> PG_SVC
    APIN --> PG_SVC

    API1 --> VOLUME
    API2 --> VOLUME
    APIN --> VOLUME

    API1 --> SUPABASE_STORAGE
    API2 --> SUPABASE_STORAGE
    APIN --> SUPABASE_STORAGE

    REDIS_SVC --> W1
    REDIS_SVC --> W2
    REDIS_SVC --> WN

    W1 --> PG_SVC
    W2 --> PG_SVC
    WN --> PG_SVC

    W1 --> VOLUME
    W2 --> VOLUME
    WN --> VOLUME

    W1 --> SUPABASE_STORAGE
    W2 --> SUPABASE_STORAGE
    WN --> SUPABASE_STORAGE

    API1 --> SENTRY
    W1 --> SENTRY

    UPTIMEROBOT -->|Health Check| LB

    style BROWSER fill:#e1f5ff
    style CDN fill:#e1f5ff
    style LB fill:#fff4e6
    style API1 fill:#fff4e6
    style W1 fill:#f3e5f5
    style REDIS_SVC fill:#ffebee
    style PG_SVC fill:#e8f5e9
    style VOLUME fill:#f3e5f5
    style SUPABASE_STORAGE fill:#e8f5e9
```

**Deployment Services:**

| Service | Provider | Purpose | Scaling |
|---|---|---|---|
| Frontend | Vercel | React SPA hosting, CDN distribution | Auto-scaling edge network |
| Backend API | Railway | FastAPI REST API | Horizontal: 2–N instances |
| Celery Workers | Railway | AI pipeline processing | Horizontal: 2–N workers |
| PostgreSQL | Railway | Relational data persistence | Managed vertical scaling |
| Redis | Railway | Task broker + result backend | Managed vertical scaling |
| FAISS Indexes | Railway Persistent Volume | Vector index storage | Mounted to all API + worker instances |
| Video/Frame Storage | Supabase Storage | S3-compatible blob storage | Unlimited, pay-per-GB |
| Error Tracking | Sentry | Exception logging | Managed SaaS |
| Uptime Monitoring | UptimeRobot | Health check polling | Managed SaaS |

**Environment Variables (Deployment):**

Frontend (Vercel):
```
VITE_API_BASE_URL=https://api.visiontrace.railway.app
VITE_SUPABASE_URL=https://<project>.supabase.co
VITE_SUPABASE_ANON_KEY=<anon_key>
```

Backend (Railway):
```
DATABASE_URL=<railway_postgres_connection_string>
REDIS_URL=<railway_redis_connection_string>
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_SERVICE_KEY=<service_role_key>
SECRET_KEY=<random_256bit_key>
FAISS_INDEX_PATH=/data/faiss_indexes
SENTRY_DSN=<sentry_project_dsn>
```

**CI/CD Pipeline:**

```mermaid
graph LR
    PUSH[Push to main] --> GHA[GitHub Actions]
    GHA --> LINT[Lint: ESLint + Ruff]
    LINT --> TEST[Test: Pytest + Vitest]
    TEST --> COVERAGE[Coverage Check: ≥70%]
    COVERAGE --> BUILD_FE[Build Frontend]
    COVERAGE --> BUILD_BE[Build Backend Docker]
    BUILD_FE --> DEPLOY_FE[Deploy to Vercel]
    BUILD_BE --> DEPLOY_BE[Deploy to Railway]
    DEPLOY_FE --> SMOKE[Smoke Test]
    DEPLOY_BE --> SMOKE
    SMOKE --> NOTIFY[Notify: Slack/Email]

    style PUSH fill:#e3f2fd
    style LINT fill:#fff3e0
    style TEST fill:#fff3e0
    style DEPLOY_FE fill:#e8f5e9
    style DEPLOY_BE fill:#e8f5e9
```

---

## 12. Scalability Architecture (Millions of Frames)

```mermaid
graph TB
    subgraph "Phase 1 - Current Architecture (v1.0)"
        subgraph "Bottlenecks"
            B1[Single FAISS Index per Video<br/>O(N) search time]
            B2[Local Disk Index Storage<br/>Limited by instance disk]
            B3[CPU-Only AI Models<br/>Slow inference]
            B4[Single PostgreSQL Instance<br/>Connection pool saturation]
        end
    end

    subgraph "Phase 2 - Scale to 1M Frames per Video"
        subgraph "Optimizations"
            O1[Switch to FAISS IndexIVFFlat<br/>Sub-linear search O(sqrt N)]
            O2[GPU-Accelerated Workers<br/>5-10x faster inference]
            O3[Read Replicas for PostgreSQL<br/>Offload read-heavy queries]
            O4[Index Caching Strategy<br/>LRU cache in API memory]
        end
    end

    subgraph "Phase 3 - Scale to 100M Frames Total"
        subgraph "Distributed Architecture"
            D1[Object Storage for Indexes<br/>S3/Supabase Storage]
            D2[Horizontal Database Sharding<br/>Partition by video_id]
            D3[Distributed FAISS<br/>Index shards across nodes]
            D4[Multi-Region Deployment<br/>Geo-distributed workers]
        end
    end

    subgraph "Phase 4 - Scale to 1B+ Frames"
        subgraph "Advanced Techniques"
            A1[Vector Database<br/>Milvus/Weaviate/Qdrant]
            A2[Approximate Search<br/>Product Quantization PQ]
            A3[Hierarchical Indexing<br/>Coarse-to-fine search]
            A4[Edge Inference<br/>On-device frame extraction]
        end
    end

    B1 --> O1
    B2 --> O2
    B3 --> O3
    B4 --> O4

    O1 --> D1
    O2 --> D2
    O3 --> D3
    O4 --> D4

    D1 --> A1
    D2 --> A2
    D3 --> A3
    D4 --> A4

    style B1 fill:#ffebee
    style O1 fill:#fff3e0
    style D1 fill:#e3f2fd
    style A1 fill:#e8f5e9
```

### Scaling Strategy by Data Volume

| Data Volume | Strategy | Changes Required |
|---|---|---|
| **< 100K frames** | Current v1.0 architecture | None |
| **100K – 1M frames** | Switch to IndexIVFFlat | Update `index_builder.py`, retrain index |
| **1M – 10M frames** | Add GPU workers | Deploy GPU Railway instances |
| **10M – 100M frames** | Shard PostgreSQL, use object storage for indexes | Citus extension or partition tables; move indexes to S3 |
| **100M – 1B frames** | Distributed FAISS or vector DB | Migrate to Milvus/Qdrant/Weaviate |
| **> 1B frames** | Hierarchical search + PQ compression | Coarse video-level index → fine frame-level index |

### Index Type Comparison

| Index Type | Search Time | Build Time | Memory | Accuracy | Use Case |
|---|---|---|---|---|---|
| `IndexFlatIP` (v1.0) | O(N) | O(N) | N vectors | 100% | < 100K vectors |
| `IndexIVFFlat` | O(√N) | O(N log N) | N vectors + centroids | 95–99% | 100K – 10M vectors |
| `IndexIVFPQ` | O(√N) | O(N log N) | Compressed | 90–95% | > 10M vectors |
| Vector DB (Milvus) | O(log N) | O(N log N) | Distributed | 95–99% | > 100M vectors |

### Database Scaling Roadmap

**Current (v1.0):** Single PostgreSQL instance with connection pooling

**Phase 2 (10K videos):**
- Add read replicas for `SELECT` queries (videos, frames, results)
- Write operations remain on primary

**Phase 3 (100K videos):**
- Partition `frames`, `detections`, `embeddings` by `video_id`
- Each partition = 1000 videos
- Queries scoped to partition via `video_id` in `WHERE` clause

**Phase 4 (1M+ videos):**
- Multi-tenant sharding via Citus extension
- Each shard = geographic region or customer
- Cross-shard queries avoided via application logic

### Worker Scaling Roadmap

**Current (v1.0):** 2–4 CPU workers

**Phase 2 (GPU Acceleration):**
- Deploy GPU-enabled Railway instances (NVIDIA T4 or A10)
- 5–10x speedup on Steps 2 (YOLO) and 4 (CLIP)
- Cost: ~$1.50/hour per GPU instance

**Phase 3 (Horizontal Scaling):**
- Scale worker count based on queue depth
- Auto-scaling trigger: if `queue_depth > 10` for > 5 minutes, add +2 workers
- Max 20 workers per deployment

**Phase 4 (Distributed Processing):**
- Multi-region worker deployments (US-East, US-West, EU)
- Video routed to nearest region based on upload location
- Reduces latency for storage uploads/downloads

### Cost Projections

| Scale | Monthly Cost (Estimate) |
|---|---|
| 100 videos, 1K searches/month | ~$50 (Railway Hobby + Supabase Free) |
| 1K videos, 10K searches/month | ~$200 (Railway Pro + Supabase Pro) |
| 10K videos, 100K searches/month | ~$1,500 (Railway Scale + GPU workers + Supabase Team) |
| 100K videos, 1M searches/month | ~$10K (Dedicated infrastructure + multi-region) |

**Cost Optimization:**
- Archive old videos to cold storage (Glacier) after 90 days
- Compress FAISS indexes with Product Quantization (50% size reduction)
- Batch search queries to amortize FAISS index load time

---

## Architecture Summary

**VisionTrace AI is designed for:**
1. **Separation of Concerns:** Independent frontend, API, and worker layers
2. **Asynchronous Processing:** Long-running AI tasks offloaded to Celery workers
3. **Stateless API:** All state in PostgreSQL/Redis/FAISS; API instances are disposable
4. **Horizontal Scalability:** Add more workers or API instances without code changes
5. **Cost-Effective CPU-First Approach:** Optimized for CPU deployment; GPU as enhancement
6. **Future-Proof Index Strategy:** Easy migration from IndexFlatIP → IndexIVFFlat → Vector DB

**Next Steps:**
- Implement M0 (Foundation) and M1 (Auth + Upload) milestones
- Deploy to Railway + Vercel for staging environment
- Benchmark pipeline performance on test videos
- Optimize before moving to M2 (AI Pipeline)

---

**End of Software Architecture Document**
