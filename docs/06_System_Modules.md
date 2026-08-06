# System Modules
## VisionTrace AI — Intelligent Video Search Platform

**Version:** 1.0  
**Date:** August 5, 2026  
**Status:** Draft — Awaiting Approval

---

## Module Map Overview

```
VisionTrace AI
├── Frontend (React + Vite + TypeScript)
│   ├── MOD-F1  Auth Module
│   ├── MOD-F2  Video Library Module
│   ├── MOD-F3  Upload Module
│   ├── MOD-F4  Search Module
│   ├── MOD-F5  Results Module
│   ├── MOD-F6  Video Player Module
│   ├── MOD-F7  Report Module
│   ├── MOD-F8  Search History Module
│   └── MOD-F9  Admin Dashboard Module
│
├── Backend API (FastAPI + Python)
│   ├── MOD-B1  Auth & User Module
│   ├── MOD-B2  Video Ingestion Module
│   ├── MOD-B3  Pipeline Orchestration Module
│   ├── MOD-B4  Search Module
│   ├── MOD-B5  Results & History Module
│   ├── MOD-B6  Report Generation Module
│   └── MOD-B7  Admin Module
│
├── AI Pipeline (Celery Workers)
│   ├── MOD-AI1  Frame Extraction Worker
│   ├── MOD-AI2  Object Detection Worker
│   ├── MOD-AI3  Object Tracking Worker
│   ├── MOD-AI4  Embedding Generation Worker
│   └── MOD-AI5  Index Builder Worker
│
└── Shared / Infrastructure
    ├── MOD-S1  Database Layer (PostgreSQL + SQLAlchemy)
    ├── MOD-S2  Storage Layer (Supabase Storage)
    ├── MOD-S3  Vector Store Layer (FAISS)
    ├── MOD-S4  Cache / Broker Layer (Redis)
    └── MOD-S5  Observability Layer (Logging + Sentry)
```

---

## Frontend Modules

---

### MOD-F1 — Auth Module

**Purpose:** Handles all user-facing authentication flows.

**Components:**
- `LoginPage` — email/password form, error handling, redirect on success
- `RegisterPage` — registration form with validation
- `AuthGuard` — HOC/wrapper that redirects unauthenticated users to login
- `RoleGuard` — HOC that restricts pages to specific roles
- `useAuthStore` (Zustand) — stores current user, access token, and auth state
- `authService` — Axios calls to `/api/auth/*` endpoints, token refresh interceptor

**Key Interactions:**
- Calls `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/refresh`, `POST /api/auth/logout`
- JWT access token stored in memory; refresh token in httpOnly cookie
- TanStack Query handles token refresh on 401 responses

---

### MOD-F2 — Video Library Module

**Purpose:** Displays all uploaded videos; entry point for selecting a video.

**Components:**
- `VideoLibraryPage` — paginated/infinite scroll grid of video cards
- `VideoCard` — thumbnail, title, duration, upload date, status badge, action menu
- `VideoStatusBadge` — displays Uploaded / Processing / Ready / Error with color coding
- `VideoFilterBar` — search by title, sort by date/name
- `useVideoStore` (Zustand) — cached list of videos
- `videoService` — API calls to `/api/videos/*`

**Key Interactions:**
- Polls `/api/videos` for status updates while any video is in "Processing" state
- VideoCard delete action calls `DELETE /api/videos/{id}` with confirmation dialog

---

### MOD-F3 — Upload Module

**Purpose:** Handles video file selection, validation, and upload.

**Components:**
- `UploadPage` / `UploadModal` — drag-and-drop zone + file picker
- `UploadForm` — title, description fields + file drop area
- `UploadProgressBar` — real-time byte-level progress indicator
- `FileValidator` — client-side size and type checks before upload begins
- `uploadService` — multipart POST to `/api/videos/upload` with Axios progress event

**Key Interactions:**
- Emits upload progress events to `UploadProgressBar` via Axios `onUploadProgress`
- On completion, invalidates the video library query to trigger a re-fetch

---

### MOD-F4 — Search Module

**Purpose:** Provides image-based and text-based search interfaces.

**Components:**
- `SearchPage` — tabbed interface: "Search by Image" | "Search by Text"
- `ImageSearchPanel` — image drop zone, preview, video selector, Top-K control, submit button
- `TextSearchPanel` — text input with character counter, suggestions chips, video selector, submit button
- `VideoSelector` — multi-select dropdown of Ready videos, or "All Videos"
- `TopKSelector` — segmented control: 10 / 20 / 50
- `searchService` — API calls to `/api/search/image` and `/api/search/text`

**Key Interactions:**
- Image panel sends multipart form data to `/api/search/image`
- Text panel sends JSON body to `/api/search/text`
- Both redirect to the Results page on success, passing the `session_id`

---

### MOD-F5 — Results Module

**Purpose:** Displays search results with scoring, filtering, and sorting.

**Components:**
- `ResultsPage` — loads results by `session_id` from URL param
- `ResultsToolbar` — sort selector, score filter slider, view toggle (grid/list), export buttons
- `ResultGrid` / `ResultList` — responsive layout of result cards
- `ResultCard` — thumbnail with bbox overlay, video name, timestamp, score badge, click handler
- `SimilarityBadge` — color-coded badge: High (green) / Medium (yellow) / Low (red)
- `DisclaimerBanner` — fixed/sticky banner with mandatory AI disclaimer text
- `resultsService` — API call to `GET /api/search/sessions/{session_id}/results`

**Key Interactions:**
- Clicking a ResultCard updates the VideoPlayer module to seek to that timestamp
- Score filter and sort are applied client-side on the loaded results set
- "Export CSV" and "Export PDF" buttons trigger the Report Module

---

### MOD-F6 — Video Player Module

**Purpose:** In-browser video playback with timestamp navigation and result markers.

**Components:**
- `VideoPlayerPanel` — wraps HTML5 `<video>` element with custom controls
- `PlayerControls` — play/pause, seek bar, volume, time display, fullscreen
- `TimelineMarkers` — overlays result timestamp dots on the seek bar
- `MarkerTooltip` — shows similarity score on hover over a timeline marker
- `usePlayerStore` (Zustand) — current video URL, current time, seek target

**Key Interactions:**
- Receives `seekTo(timestamp)` calls from ResultCard clicks
- Loads video via signed Supabase Storage URL from `GET /api/videos/{id}/stream-url`
- Timeline markers derived from the current results set

---

### MOD-F7 — Report Module

**Purpose:** Generates and downloads CSV and PDF exports of search results.

**Components:**
- `ExportCSVButton` — triggers client-side CSV generation and download
- `ExportPDFModal` — collects report title, generates PDF via jsPDF + html2canvas
- `csvExporter` — utility that transforms results array to CSV blob
- `pdfExporter` — utility that renders results into a jsPDF document with thumbnails and disclaimer

**Key Interactions:**
- Receives current results array and search session metadata from the Results Module
- PDF generation is entirely client-side (no server round-trip required)
- AI disclaimer is programmatically injected into both CSV and PDF outputs

---

### MOD-F8 — Search History Module

**Purpose:** Displays and manages the user's saved search sessions.

**Components:**
- `SearchHistoryPage` — chronological list of past searches
- `HistoryItem` — query type icon, preview, date, result count, view/delete actions
- `historyService` — API calls to `GET /api/search/sessions` and `DELETE /api/search/sessions/{id}`

**Key Interactions:**
- Clicking "View" navigates to `ResultsPage` with the historical `session_id`
- Delete action removes the session record (does not affect video data)

---

### MOD-F9 — Admin Dashboard Module

**Purpose:** System overview and administrative controls, restricted to Admin role.

**Components:**
- `AdminDashboardPage` — metrics overview + pipeline job table + user management table
- `SystemMetricsCards` — total videos, total searches, active users, queue depth
- `PipelineJobTable` — all processing jobs with status, step, timestamps, retry action
- `UserManagementTable` — user list with role selector, status toggle, create user button
- `adminService` — API calls to `/api/admin/*` endpoints

**Key Interactions:**
- Polls `/api/admin/metrics` every 30 seconds for live stats
- "Retry" button calls `POST /api/admin/jobs/{job_id}/retry`

---

## Backend API Modules

---

### MOD-B1 — Auth & User Module

**Purpose:** User registration, login, token management, and user CRUD.

**Responsibilities:**
- Password hashing and verification (bcrypt)
- JWT access token generation and validation
- Refresh token issuance and rotation
- User creation, role assignment, deactivation
- Current user profile endpoint

**Routes:** `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /users/me`, `PUT /users/me/password`, `GET /users` (Admin), `PUT /users/{id}` (Admin)

**Dependencies:** `users` table, bcrypt, python-jose

---

### MOD-B2 — Video Ingestion Module

**Purpose:** Handles video file upload, metadata persistence, and storage.

**Responsibilities:**
- Receive multipart video upload
- Validate file type (MIME + magic bytes) and size
- Upload raw video to Supabase Storage `videos` bucket
- Persist video metadata to `videos` table
- Trigger AI pipeline task via Celery

**Routes:** `POST /videos/upload`, `GET /videos`, `GET /videos/{id}`, `DELETE /videos/{id}`, `GET /videos/{id}/stream-url`

**Dependencies:** `videos` table, Supabase Storage client, Celery producer

---

### MOD-B3 — Pipeline Orchestration Module

**Purpose:** Manages Celery task chains and tracks pipeline job state.

**Responsibilities:**
- Define and enqueue the 5-step Celery task chain per video
- Write pipeline step status to `processing_jobs` table
- Expose job status to frontend polling
- Support admin job retry

**Routes:** `GET /videos/{id}/job-status`, `POST /admin/jobs/{job_id}/retry`

**Dependencies:** `processing_jobs` table, Redis, Celery

---

### MOD-B4 — Search Module

**Purpose:** Accepts search queries, runs FAISS similarity search, and returns results.

**Responsibilities:**
- Accept image upload or text string as query
- Generate query embedding using OpenCLIP
- Load target FAISS index(es) and run top-K search
- Map FAISS result IDs to frame/detection metadata from PostgreSQL
- Persist search session and results
- Return ranked results to the frontend

**Routes:** `POST /search/image`, `POST /search/text`

**Dependencies:** `search_sessions`, `search_results`, `frames`, `detections`, `embeddings` tables; FAISS indexes; OpenCLIP model (loaded once at startup)

---

### MOD-B5 — Results & History Module

**Purpose:** Retrieves saved search results and manages search session history.

**Responsibilities:**
- Fetch results for a given session ID
- List all sessions for the current user
- Delete a session and its results

**Routes:** `GET /search/sessions`, `GET /search/sessions/{session_id}/results`, `DELETE /search/sessions/{session_id}`

**Dependencies:** `search_sessions`, `search_results` tables

---

### MOD-B6 — Report Generation Module

**Purpose:** Server-side support for report data (CSV is client-side; PDF metadata from server).

**Responsibilities:**
- Provide a structured results export endpoint for server-rendered reports if needed
- Return signed URLs for frame thumbnails used in PDF generation

**Routes:** `GET /search/sessions/{session_id}/export` (returns structured JSON for client-side rendering)

**Dependencies:** Supabase Storage (signed URL generation), `search_results`, `frames` tables

---

### MOD-B7 — Admin Module

**Purpose:** Administrative endpoints for metrics, job management, and user administration.

**Responsibilities:**
- Aggregate system metrics
- List all pipeline jobs with filtering
- Requeue failed jobs
- Expose Celery/Flower monitoring passthrough

**Routes:** `GET /admin/metrics`, `GET /admin/jobs`, `POST /admin/jobs/{id}/retry`, `GET /admin/users`, `PUT /admin/users/{id}`

**Dependencies:** All tables, Celery, Redis

---

## AI Pipeline Worker Modules

---

### MOD-AI1 — Frame Extraction Worker

**Purpose:** Extract individual frames from a video file at a configurable rate.

**Technology:** OpenCV (`cv2`)  
**Input:** Supabase signed URL for raw video file  
**Output:** JPEG frames uploaded to Supabase `frames` bucket; frame metadata written to `frames` table  
**Config:** `FRAME_EXTRACTION_FPS` (default: 1)

---

### MOD-AI2 — Object Detection Worker

**Purpose:** Run YOLOv8 detection on every extracted frame.

**Technology:** Ultralytics YOLOv8  
**Input:** Frame paths from `frames` table for the given video  
**Output:** Detection records (bounding box, class, confidence) written to `detections` table  
**Config:** `YOLO_MODEL_PATH`, `YOLO_CONFIDENCE_THRESHOLD` (default: 0.4)

---

### MOD-AI3 — Object Tracking Worker

**Purpose:** Assign persistent track IDs to detections across frames.

**Technology:** ByteTrack  
**Input:** Ordered detection records from `detections` table for the given video  
**Output:** Track ID assigned to each detection; track records written to `tracks` table

---

### MOD-AI4 — Embedding Generation Worker

**Purpose:** Generate OpenCLIP visual embeddings for each detected crop.

**Technology:** open_clip_torch  
**Input:** Detection bounding boxes + frame images from Supabase Storage  
**Output:** 512-dim L2-normalized embedding vectors; embedding metadata written to `embeddings` table  
**Config:** `CLIP_MODEL_NAME`, `CLIP_PRETRAINED`, batch size 32

---

### MOD-AI5 — Index Builder Worker

**Purpose:** Build and persist the FAISS vector index for the video.

**Technology:** faiss-cpu  
**Input:** Embedding vectors from `embeddings` table for the given video  
**Output:** Serialized FAISS `IndexFlatIP` file at `{FAISS_INDEX_PATH}/{video_id}.index`; video status updated to "Ready"  
**Config:** `FAISS_INDEX_PATH`

---

## Shared / Infrastructure Modules

---

### MOD-S1 — Database Layer

**Technology:** PostgreSQL 15 + SQLAlchemy 2 (async) + Alembic  
**Responsibilities:** ORM model definitions, session management, migrations, connection pooling

---

### MOD-S2 — Storage Layer

**Technology:** Supabase Storage (S3-compatible)  
**Responsibilities:** Video upload, frame storage, signed URL generation, bucket policy management

---

### MOD-S3 — Vector Store Layer

**Technology:** FAISS (faiss-cpu)  
**Responsibilities:** Index creation, serialization/deserialization, similarity search execution

---

### MOD-S4 — Cache / Broker Layer

**Technology:** Redis  
**Responsibilities:** Celery task broker, Celery result backend, optional session caching

---

### MOD-S5 — Observability Layer

**Technology:** structlog, Sentry SDK, Flower  
**Responsibilities:** Structured JSON logging, request ID propagation, error capture, Celery monitoring dashboard
