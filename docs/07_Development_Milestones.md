# Development Milestones
## VisionTrace AI — Intelligent Video Search Platform

**Version:** 1.0  
**Date:** August 5, 2026  
**Status:** Draft — Awaiting Approval

---

## Overview

Development is organized into **6 milestones** (M0–M5). Each milestone produces a working, deployable increment. Milestones build on each other — no milestone begins until the previous one is stable and passing all relevant tests.

```
M0  ─── Project Foundation & Infrastructure
M1  ─── Auth, User Management & Video Upload
M2  ─── AI Processing Pipeline (Frame → Embedding → Index)
M3  ─── Search Engine (Image + Text Query → Results)
M4  ─── Results UI, Video Player & Reports
M5  ─── Admin Dashboard, Polish & Production Hardening
```

---

## M0 — Project Foundation & Infrastructure

**Goal:** All tooling, configuration, and infrastructure scaffolding is in place. Every developer can clone the repo and have a fully working local environment running with a single command.

**Duration:** ~1 week

### Backend Tasks
- [ ] Initialize Python project with `pyproject.toml` and `requirements.txt` (pinned versions)
- [ ] Set up FastAPI app skeleton with router structure
- [ ] Configure SQLAlchemy async engine and Alembic migration environment
- [ ] Create initial Alembic migration with all core tables (`users`, `videos`, `processing_jobs`, `frames`, `detections`, `tracks`, `embeddings`, `search_sessions`, `search_results`)
- [ ] Configure Celery with Redis broker and result backend
- [ ] Add structlog JSON logging with request ID middleware
- [ ] Add `/health` and `/readiness` endpoints
- [ ] Configure CORS, rate limiting (slowapi), and security headers middleware
- [ ] Add Sentry SDK initialization (backend)
- [ ] Write Pytest base configuration and first smoke test

### Frontend Tasks
- [ ] Initialize React + Vite + TypeScript project (strict mode)
- [ ] Configure TailwindCSS and Shadcn UI
- [ ] Set up ESLint + Prettier
- [ ] Configure React Router v6 with route scaffolding (placeholder pages)
- [ ] Set up Zustand store structure and TanStack Query client
- [ ] Set up Axios instance with base URL, interceptors, and request ID header
- [ ] Add Sentry SDK initialization (frontend)
- [ ] Create shared layout: top navigation bar, sidebar placeholder, main content area

### Infrastructure Tasks
- [ ] Create monorepo folder structure (`/frontend`, `/backend`, `/docs`, `/docker`)
- [ ] Write `docker-compose.yml` with services: `api`, `worker`, `redis`, `db`
- [ ] Write `Dockerfile` for backend (multi-stage, python:3.11-slim)
- [ ] Write `Dockerfile` for frontend (multi-stage, node:20-alpine build → Nginx serve)
- [ ] Configure `.env.example` files for frontend and backend
- [ ] Set up Supabase project: create `videos` and `frames` storage buckets with policies
- [ ] Configure GitHub repository with branch protection on `main`
- [ ] Set up GitHub Actions CI pipeline: lint → test → build

**Milestone M0 Definition of Done:**
- `docker compose up` starts all services with no errors
- `GET /health` returns `200 OK`
- All Alembic migrations apply cleanly on a fresh database
- Frontend renders a placeholder dashboard at `localhost:5173`
- CI pipeline passes on a clean branch

---

## M1 — Auth, User Management & Video Upload

**Goal:** Users can register, log in, and upload videos. Uploaded videos appear in the library with status tracking.

**Duration:** ~1.5 weeks

### Backend Tasks
- [ ] Implement `POST /auth/register` with email validation and bcrypt password hashing
- [ ] Implement `POST /auth/login` with JWT access + refresh token generation
- [ ] Implement `POST /auth/refresh` with refresh token rotation
- [ ] Implement `POST /auth/logout` with refresh token invalidation
- [ ] Implement `GET /users/me` and `PUT /users/me/password`
- [ ] Implement role-based dependency (`require_role`) for route protection
- [ ] Implement `POST /videos/upload`: MIME + magic bytes validation, Supabase upload, DB insert, Celery task trigger (stubbed)
- [ ] Implement `GET /videos`: paginated list scoped to current user
- [ ] Implement `GET /videos/{id}`: single video with job status
- [ ] Implement `DELETE /videos/{id}`: storage deletion + DB cascade
- [ ] Implement `GET /videos/{id}/stream-url`: generate signed Supabase URL
- [ ] Write Pytest tests for all auth and video endpoints

### Frontend Tasks
- [ ] Build `LoginPage` with form validation (React Hook Form + Zod)
- [ ] Build `RegisterPage` with matching password and strength validation
- [ ] Implement `AuthGuard` and `RoleGuard` route wrappers
- [ ] Implement `useAuthStore` with token storage and automatic refresh
- [ ] Build `VideoLibraryPage` with `VideoCard` and `VideoStatusBadge`
- [ ] Build `UploadPage` with drag-and-drop, file picker, title/description form, and `UploadProgressBar`
- [ ] Implement status polling (every 5s) for videos in "Processing" state
- [ ] Build video delete confirmation dialog
- [ ] Implement sort and filter bar for video library
- [ ] Wire navigation: login → dashboard → library → upload

**Milestone M1 Definition of Done:**
- User can register, log in, and stay logged in across refreshes
- JWT refresh works transparently on 401
- Video upload completes with progress, file appears in Supabase Storage
- Video status transitions from "Uploaded" to "Processing" (pipeline stubbed) to demonstrating the status badge correctly
- Delete removes video from storage and DB
- All M1 API tests pass

---

## M2 — AI Processing Pipeline

**Goal:** Uploaded videos are fully processed automatically: frames extracted, objects detected and tracked, embeddings generated, FAISS index built, video marked Ready.

**Duration:** ~2 weeks

### Backend / Worker Tasks
- [ ] Implement `MOD-AI1` Frame Extraction Worker: OpenCV frame extraction at configurable FPS, JPEG upload to Supabase `frames` bucket, frame records written to DB
- [ ] Implement `MOD-AI2` Object Detection Worker: YOLOv8 inference on all frames, detection records written to DB
- [ ] Implement `MOD-AI3` Object Tracking Worker: ByteTrack across detection sequence, track IDs assigned and written to DB
- [ ] Implement `MOD-AI4` Embedding Generation Worker: OpenCLIP crop embeddings in batches of 32, embedding metadata written to DB; whole-frame fallback for empty frames
- [ ] Implement `MOD-AI5` Index Builder Worker: FAISS `IndexFlatIP` built from all embeddings, serialized to persistent volume, video status set to "Ready"
- [ ] Implement Celery task chain wiring all 5 workers in sequence
- [ ] Implement per-step status updates to `processing_jobs` table
- [ ] Implement Celery retry logic (max 3 attempts, exponential backoff) for each worker
- [ ] Load YOLO model once at worker startup (not per-task)
- [ ] Load OpenCLIP model once at worker startup (not per-task)
- [ ] Implement `GET /videos/{id}/job-status` endpoint returning per-step progress
- [ ] Add Flower monitoring service to docker-compose
- [ ] Write integration tests for each worker using a short test video clip

### Frontend Tasks
- [ ] Upgrade status polling to display per-step pipeline progress ("Extracting frames… 34%")
- [ ] Display pipeline error details when status is "Error"
- [ ] Add "Processing" skeleton animation to video card

**Milestone M2 Definition of Done:**
- Uploading a video triggers the full pipeline automatically
- Video transitions through all pipeline steps and reaches "Ready" status
- FAISS index file exists on disk for the processed video
- Embedding count in DB matches expected frame × detection count
- Pipeline integration test passes on a 30-second test video
- Failed task retries up to 3 times and marks video as "Error" after exhaustion

---

## M3 — Search Engine (Image Query + Text Query)

**Goal:** Users can search Ready videos by uploading an image or entering a text query and receive ranked similarity results.

**Duration:** ~1.5 weeks

### Backend Tasks
- [ ] Implement `POST /search/image`: receive query image, generate OpenCLIP embedding, load target FAISS index(es), run top-K search, map results, persist session + results, return ranked list
- [ ] Implement `POST /search/text`: receive query string, validate + sanitize, generate OpenCLIP text embedding, run top-K search, same result pipeline as image search
- [ ] Implement `GET /search/sessions/{session_id}/results`: retrieve persisted results with frame metadata and signed thumbnail URLs
- [ ] Implement `GET /search/sessions`: list all sessions for current user
- [ ] Implement `DELETE /search/sessions/{session_id}`: remove session and results
- [ ] Implement "search all videos" mode: iterate over all Ready video indexes, merge and re-rank results
- [ ] Implement Top-K configuration (10 / 20 / 50) from request parameters
- [ ] Add signed URL generation for each result thumbnail in response
- [ ] Write Pytest tests for image search, text search, and result retrieval

### Frontend Tasks
- [ ] Build `SearchPage` with tab navigation: "Image Search" / "Text Search"
- [ ] Build `ImageSearchPanel` with image drop zone, preview, video selector, Top-K control
- [ ] Build `TextSearchPanel` with text input, character counter, suggestion chips
- [ ] Build `VideoSelector` multi-select dropdown
- [ ] Implement search form submission and loading state
- [ ] Build `ResultsPage` scaffold receiving `session_id` from route param
- [ ] Build `ResultCard` with thumbnail, video name, timestamp (HH:MM:SS), `SimilarityBadge`
- [ ] Implement `DisclaimerBanner` (sticky, non-dismissible)
- [ ] Build `SearchHistoryPage` and `HistoryItem` components

**Milestone M3 Definition of Done:**
- Image search returns ranked results within 3 seconds for a 30-minute processed video
- Text search returns ranked results for natural language queries
- Results correctly map similarity scores and timestamps
- Search session persisted; history page shows past searches
- All M3 API tests pass
- Disclaimer banner visible on every results view

---

## M4 — Results UI, Video Player & Reports

**Goal:** Full results experience: filter/sort, bounding box overlays, in-browser video player with timestamp seek and timeline markers, CSV and PDF export.

**Duration:** ~1.5 weeks

### Backend Tasks
- [ ] Implement `GET /search/sessions/{session_id}/export`: structured export payload including signed thumbnail URLs and bbox coordinates
- [ ] Ensure all result responses include `bbox_x`, `bbox_y`, `bbox_w`, `bbox_h` for overlay rendering
- [ ] Verify signed URL expiry is appropriate for PDF generation window

### Frontend Tasks
- [ ] Build `ResultsToolbar`: sort selector, score filter slider (0–100%), grid/list toggle, export buttons
- [ ] Implement client-side sort and filter on loaded results (no additional API call)
- [ ] Implement pagination / infinite scroll for > 20 results
- [ ] Implement `BboxOverlay`: draw bounding box on result thumbnails using canvas or CSS
- [ ] Build `VideoPlayerPanel` with HTML5 `<video>`, custom controls (play/pause, seek, volume, fullscreen)
- [ ] Implement `seekTo(timestamp)` integration: click result → player seeks to timestamp, result card highlighted
- [ ] Build `TimelineMarkers`: render result timestamp dots on seek bar, tooltip on hover
- [ ] Implement `ExportCSVButton`: generate CSV blob client-side, trigger download
- [ ] Build `ExportPDFModal`: title input, generate PDF with jsPDF, thumbnails from signed URLs, disclaimer on page 1
- [ ] Connect video player to `GET /videos/{id}/stream-url` for signed video URL

**Milestone M4 Definition of Done:**
- Score filter and sort work correctly on results without page reload
- Bounding box overlaid accurately on each result thumbnail
- Clicking a result seeks the video player to exact timestamp
- Timeline markers visible and clickable on the seek bar
- CSV export downloads with all required columns and disclaimer
- PDF report generates with thumbnails and disclaimer
- Full end-to-end user flow works: upload → process → search → results → play → export

---

## M5 — Admin Dashboard, Polish & Production Hardening

**Goal:** Admin capabilities complete, system hardened for production, deployed and monitored.

**Duration:** ~1.5 weeks

### Backend Tasks
- [ ] Implement `GET /admin/metrics`: aggregate stats (total videos, searches today, active users, queue depth)
- [ ] Implement `GET /admin/jobs`: all pipeline jobs with filtering by status
- [ ] Implement `POST /admin/jobs/{id}/retry`: reset status and re-enqueue Celery task
- [ ] Implement Admin user management endpoints: `GET /admin/users`, `PUT /admin/users/{id}` (role, status)
- [ ] Implement `POST /admin/users`: create user with temporary password
- [ ] Add Prometheus-compatible `/metrics` endpoint (basic counters)
- [ ] Enforce request ID propagation through Celery tasks
- [ ] Final security review: CORS, rate limits, input validation, secret scanning
- [ ] Achieve ≥ 70% test coverage on API routes and service layer
- [ ] Configure Railway deployment: environment variables, persistent volume for FAISS, health check

### Frontend Tasks
- [ ] Build `AdminDashboardPage` with `SystemMetricsCards` and auto-refresh (30s)
- [ ] Build `PipelineJobTable` with status badges, retry button, pagination
- [ ] Build `UserManagementTable` with role selector, status toggle, create user modal
- [ ] Accessibility audit: keyboard navigation, ARIA labels, axe-core scan on all primary flows
- [ ] Responsive layout audit: test at 375px, 768px, 1280px, 1920px viewports
- [ ] Error boundary implementation: all pages wrapped with React error boundaries
- [ ] Loading skeleton audit: all async operations show skeletons/spinners
- [ ] Final UI polish: consistent spacing, typography, color tokens via Tailwind
- [ ] Configure Vercel deployment: environment variables, build settings

### CI/CD & Deployment Tasks
- [ ] Finalize GitHub Actions pipeline: lint → test → coverage gate (70%) → build → deploy
- [ ] Configure Sentry error alerting (email on new issues)
- [ ] Set up UptimeRobot monitors for `/health` and frontend URL
- [ ] Write production `README.md` with setup, environment variable reference, and deployment instructions
- [ ] Perform load test: 50 concurrent users, verify p95 < 3s search response
- [ ] Perform end-to-end smoke test on production environment

**Milestone M5 Definition of Done:**
- Admin dashboard live with real metrics and retry capability
- All WCAG 2.1 AA automated checks passing (axe-core)
- ≥ 70% backend test coverage achieved and enforced in CI
- Application deployed and accessible on Vercel (frontend) + Railway (backend)
- Sentry capturing errors in production
- UptimeRobot monitoring active
- Load test passes: 50 concurrent users, p95 search < 3s
- All documentation complete and committed

---

## Milestone Summary Table

| Milestone | Focus | Duration | Key Deliverable |
|---|---|---|---|
| M0 | Foundation & Infrastructure | 1 week | Running local environment, CI, DB schema |
| M1 | Auth + Video Upload | 1.5 weeks | Users can register, login, upload videos |
| M2 | AI Processing Pipeline | 2 weeks | Videos fully processed, FAISS index built |
| M3 | Search Engine | 1.5 weeks | Image + text search returns ranked results |
| M4 | Results UI + Player + Reports | 1.5 weeks | Full search-to-playback-to-export flow |
| M5 | Admin + Polish + Production | 1.5 weeks | Production-deployed, monitored, hardened |
| **Total** | | **~9 weeks** | **Production v1.0** |

---

## Post-v1.0 Roadmap (Future Phases)

| Phase | Feature |
|---|---|
| v1.1 | InsightFace face detection + face embedding search |
| v1.2 | Real-time RTSP stream ingestion |
| v1.3 | Multi-tenancy and organization workspaces |
| v1.4 | GPU-accelerated pipeline deployment option |
| v1.5 | Mobile-responsive PWA / native mobile apps |
| v2.0 | Federated search across distributed deployments |
