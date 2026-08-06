# Folder Planning
## VisionTrace AI — Intelligent Video Search Platform

**Version:** 1.0  
**Date:** August 5, 2026  
**Status:** Draft — Awaiting Approval

---

## Repository Root Structure

```
visiontrace-ai/
├── frontend/                   # React + Vite + TypeScript application
├── backend/                    # FastAPI + Celery Python application
├── docs/                       # All planning and architecture documents
├── docker/                     # Supplemental Docker configs and scripts
├── .github/                    # GitHub Actions CI/CD workflows
├── .env.example                # Root-level environment variable reference
├── docker-compose.yml          # Local development orchestration
├── docker-compose.prod.yml     # Production-equivalent compose (for staging)
└── README.md                   # Project overview, setup instructions
```

---

## Frontend Folder Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   └── assets/                 # Static images, icons not processed by Vite
│
├── src/
│   ├── main.tsx                # React app entry point
│   ├── App.tsx                 # Root component, Router setup
│   ├── vite-env.d.ts           # Vite environment type declarations
│   │
│   ├── assets/                 # Images, SVGs imported by components
│   │
│   ├── components/             # Reusable, domain-agnostic UI components
│   │   ├── ui/                 # Shadcn UI generated components (Button, Input, etc.)
│   │   ├── layout/             # App shell components
│   │   │   ├── AppLayout.tsx       # Root layout with nav + sidebar + main
│   │   │   ├── Navbar.tsx          # Top navigation bar
│   │   │   ├── Sidebar.tsx         # Left sidebar navigation
│   │   │   └── PageHeader.tsx      # Reusable page title + breadcrumb
│   │   ├── common/             # Generic shared components
│   │   │   ├── DisclaimerBanner.tsx    # Mandatory AI disclaimer
│   │   │   ├── SimilarityBadge.tsx     # Color-coded score badge
│   │   │   ├── StatusBadge.tsx         # Video processing status badge
│   │   │   ├── ConfirmDialog.tsx        # Reusable confirmation modal
│   │   │   ├── EmptyState.tsx          # Empty list/results placeholder
│   │   │   ├── ErrorMessage.tsx        # User-friendly error display
│   │   │   ├── LoadingSpinner.tsx      # Centered spinner
│   │   │   └── SkeletonCard.tsx        # Loading skeleton for cards
│   │   └── forms/              # Reusable form primitives
│   │       ├── FileDropzone.tsx        # Drag-and-drop file input
│   │       └── CharacterCounter.tsx    # Text field character counter
│   │
│   ├── features/               # Feature-scoped modules (co-located components, hooks, types)
│   │   │
│   │   ├── auth/
│   │   │   ├── pages/
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   └── RegisterPage.tsx
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── RegisterForm.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.ts
│   │   │   ├── store/
│   │   │   │   └── authStore.ts        # Zustand auth state
│   │   │   └── types/
│   │   │       └── auth.types.ts
│   │   │
│   │   ├── videos/
│   │   │   ├── pages/
│   │   │   │   ├── VideoLibraryPage.tsx
│   │   │   │   └── UploadPage.tsx
│   │   │   ├── components/
│   │   │   │   ├── VideoCard.tsx
│   │   │   │   ├── VideoFilterBar.tsx
│   │   │   │   ├── UploadForm.tsx
│   │   │   │   └── UploadProgressBar.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useVideos.ts        # TanStack Query hooks
│   │   │   │   └── useUpload.ts
│   │   │   └── types/
│   │   │       └── video.types.ts
│   │   │
│   │   ├── search/
│   │   │   ├── pages/
│   │   │   │   └── SearchPage.tsx
│   │   │   ├── components/
│   │   │   │   ├── ImageSearchPanel.tsx
│   │   │   │   ├── TextSearchPanel.tsx
│   │   │   │   ├── VideoSelector.tsx
│   │   │   │   ├── TopKSelector.tsx
│   │   │   │   └── QuerySuggestions.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useSearch.ts
│   │   │   └── types/
│   │   │       └── search.types.ts
│   │   │
│   │   ├── results/
│   │   │   ├── pages/
│   │   │   │   └── ResultsPage.tsx
│   │   │   ├── components/
│   │   │   │   ├── ResultsToolbar.tsx
│   │   │   │   ├── ResultGrid.tsx
│   │   │   │   ├── ResultList.tsx
│   │   │   │   ├── ResultCard.tsx
│   │   │   │   └── BboxOverlay.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useResults.ts
│   │   │   └── types/
│   │   │       └── result.types.ts
│   │   │
│   │   ├── player/
│   │   │   ├── components/
│   │   │   │   ├── VideoPlayerPanel.tsx
│   │   │   │   ├── PlayerControls.tsx
│   │   │   │   └── TimelineMarkers.tsx
│   │   │   ├── hooks/
│   │   │   │   └── usePlayer.ts
│   │   │   └── store/
│   │   │       └── playerStore.ts      # Zustand player state
│   │   │
│   │   ├── reports/
│   │   │   ├── components/
│   │   │   │   ├── ExportCSVButton.tsx
│   │   │   │   └── ExportPDFModal.tsx
│   │   │   └── utils/
│   │   │       ├── csvExporter.ts
│   │   │       └── pdfExporter.ts
│   │   │
│   │   ├── history/
│   │   │   ├── pages/
│   │   │   │   └── SearchHistoryPage.tsx
│   │   │   ├── components/
│   │   │   │   └── HistoryItem.tsx
│   │   │   └── hooks/
│   │   │       └── useHistory.ts
│   │   │
│   │   └── admin/
│   │       ├── pages/
│   │       │   └── AdminDashboardPage.tsx
│   │       ├── components/
│   │       │   ├── SystemMetricsCards.tsx
│   │       │   ├── PipelineJobTable.tsx
│   │       │   └── UserManagementTable.tsx
│   │       └── hooks/
│   │           └── useAdmin.ts
│   │
│   ├── services/               # API call functions (Axios-based, one file per domain)
│   │   ├── api.ts              # Axios instance, interceptors, request ID injection
│   │   ├── authService.ts
│   │   ├── videoService.ts
│   │   ├── searchService.ts
│   │   ├── resultsService.ts
│   │   ├── historyService.ts
│   │   └── adminService.ts
│   │
│   ├── router/
│   │   ├── index.tsx           # React Router route definitions
│   │   └── routes.ts           # Route path constants
│   │
│   ├── hooks/                  # Global/cross-feature custom hooks
│   │   ├── useDebounce.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── lib/                    # Utility functions and third-party wrappers
│   │   ├── utils.ts            # Shadcn cn() utility + general helpers
│   │   ├── formatters.ts       # Timestamp, score, file size formatters
│   │   └── validators.ts       # Shared Zod schemas
│   │
│   ├── types/                  # Global TypeScript types and interfaces
│   │   ├── api.types.ts        # Generic API response types
│   │   └── global.types.ts     # App-wide enums and shared types
│   │
│   └── styles/
│       └── globals.css         # Tailwind directives + CSS custom properties
│
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── tsconfig.app.json
├── eslint.config.js
├── .prettierrc
├── .env.example
└── package.json
```

---

## Backend Folder Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app factory, middleware registration, router mount
│   ├── config.py               # Pydantic Settings — reads all env vars, single source of truth
│   ├── dependencies.py         # Shared FastAPI dependencies (get_db, get_current_user, require_role)
│   │
│   ├── api/                    # HTTP route handlers only — thin layer, delegates to services
│   │   ├── __init__.py
│   │   ├── router.py           # Master API router — mounts all sub-routers with prefixes
│   │   ├── auth.py             # /auth/* routes
│   │   ├── users.py            # /users/* routes
│   │   ├── videos.py           # /videos/* routes
│   │   ├── search.py           # /search/* routes
│   │   ├── history.py          # /search/sessions/* routes
│   │   └── admin.py            # /admin/* routes
│   │
│   ├── services/               # Business logic layer — called by API routes and workers
│   │   ├── __init__.py
│   │   ├── auth_service.py         # Registration, login, token logic
│   │   ├── user_service.py         # User CRUD, role management
│   │   ├── video_service.py        # Video upload, metadata, deletion
│   │   ├── storage_service.py      # Supabase Storage: upload, delete, signed URLs
│   │   ├── search_service.py       # Query embedding, FAISS search, result mapping
│   │   ├── index_service.py        # FAISS index load/save/create operations
│   │   ├── result_service.py       # Result persistence and retrieval
│   │   └── admin_service.py        # Metrics aggregation, job management
│   │
│   ├── workers/                # Celery task definitions — AI pipeline steps
│   │   ├── __init__.py
│   │   ├── celery_app.py           # Celery application instance and configuration
│   │   ├── pipeline.py             # Task chain definition and orchestration
│   │   ├── frame_extraction.py     # MOD-AI1: OpenCV frame extraction task
│   │   ├── object_detection.py     # MOD-AI2: YOLOv8 detection task
│   │   ├── object_tracking.py      # MOD-AI3: ByteTrack tracking task
│   │   ├── embedding_generation.py # MOD-AI4: OpenCLIP embedding task
│   │   └── index_builder.py        # MOD-AI5: FAISS index build task
│   │
│   ├── models/                 # SQLAlchemy ORM models (one file per table group)
│   │   ├── __init__.py
│   │   ├── base.py                 # DeclarativeBase, UUID mixin, timestamp mixin
│   │   ├── user.py                 # User model
│   │   ├── video.py                # Video model + VideoStatus enum
│   │   ├── processing_job.py       # ProcessingJob model + PipelineStep enum
│   │   ├── frame.py                # Frame model
│   │   ├── detection.py            # Detection model
│   │   ├── track.py                # Track model
│   │   ├── embedding.py            # Embedding model
│   │   ├── search_session.py       # SearchSession model + QueryType enum
│   │   └── search_result.py        # SearchResult model
│   │
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py                 # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── user.py                 # UserResponse, UpdatePasswordRequest, UserAdminUpdate
│   │   ├── video.py                # VideoCreate, VideoResponse, VideoListResponse
│   │   ├── search.py               # ImageSearchRequest, TextSearchRequest, SearchResponse
│   │   ├── result.py               # ResultResponse, ResultListResponse
│   │   ├── session.py              # SessionResponse, SessionListResponse
│   │   └── admin.py                # MetricsResponse, JobResponse, JobListResponse
│   │
│   ├── db/                     # Database infrastructure
│   │   ├── __init__.py
│   │   ├── session.py              # Async SQLAlchemy engine and session factory
│   │   └── migrations/             # Alembic migration environment
│   │       ├── env.py
│   │       ├── script.py.mako
│   │       └── versions/           # Auto-generated migration files
│   │           └── 0001_initial_schema.py
│   │
│   ├── core/                   # Cross-cutting infrastructure utilities
│   │   ├── __init__.py
│   │   ├── security.py             # JWT creation/validation, password hashing
│   │   ├── middleware.py           # Request ID injection, logging middleware
│   │   ├── rate_limiter.py         # slowapi limiter instance and decorators
│   │   ├── exceptions.py           # Custom exception classes and HTTP error handlers
│   │   └── logging.py              # structlog configuration
│   │
│   └── ai/                     # AI model management (loaded once, shared across workers)
│       ├── __init__.py
│       ├── clip_model.py           # OpenCLIP model loader and inference helpers
│       ├── yolo_model.py           # YOLOv8 model loader and inference helpers
│       └── bytetrack/              # ByteTrack integration
│           ├── __init__.py
│           ├── tracker.py          # ByteTrack BYTETracker wrapper
│           └── byte_tracker.py     # Core ByteTrack algorithm (vendored or pip)
│
├── tests/
│   ├── conftest.py             # Pytest fixtures: test DB, test client, auth headers
│   ├── unit/
│   │   ├── test_security.py
│   │   ├── test_validators.py
│   │   └── test_formatters.py
│   ├── integration/
│   │   ├── test_auth.py
│   │   ├── test_videos.py
│   │   ├── test_search.py
│   │   └── test_admin.py
│   └── fixtures/
│       ├── test_video.mp4          # Short test video (< 5 seconds, included in repo)
│       └── test_query_image.jpg    # Sample query image for search tests
│
├── alembic.ini                 # Alembic configuration file
├── requirements.txt            # Pinned production dependencies
├── requirements-dev.txt        # Dev/test dependencies (pytest, ruff, black, etc.)
├── Dockerfile                  # Multi-stage Docker build for API + worker
├── .env.example
└── pyproject.toml              # Ruff and Black configuration
```

---

## Docker & Infrastructure Structure

```
docker/
├── nginx/
│   └── nginx.conf              # Nginx config for frontend container (if self-hosting)
└── scripts/
    ├── wait-for-db.sh          # Health-wait script for compose startup ordering
    └── entrypoint.sh           # Backend container entrypoint (migrations + uvicorn)

.github/
└── workflows/
    ├── ci.yml                  # Lint + test + coverage on pull requests
    └── deploy.yml              # Build + deploy on push to main

docs/
├── 01_PRD.md
├── 02_Technical_Requirements.md
├── 03_Functional_Requirements.md
├── 04_Non_Functional_Requirements.md
├── 05_User_Stories.md
├── 06_System_Modules.md
├── 07_Development_Milestones.md
├── 08_Folder_Planning.md
├── 09_API_Planning.md
└── 10_AI_Pipeline_Planning.md
```

---

## Key Architectural Decisions in Folder Design

### Feature-First Frontend
The `src/features/` directory groups every concern of a feature — page, components, hooks, types — together. This avoids the "flat components" antipattern where a feature's files are scattered across `components/`, `pages/`, `hooks/`, and `types/` directories simultaneously. Co-location makes features easy to find, move, or delete.

### Services Layer Separation (Backend)
`app/api/` routes are intentionally thin — they validate input, call a service, and return a response. All business logic lives in `app/services/`. This keeps routes testable without spinning up the full HTTP stack and keeps AI/pipeline logic cleanly separated from HTTP concerns.

### Workers as First-Class Citizens
`app/workers/` is a sibling to `app/api/` and `app/services/`, not nested inside either. Workers are a parallel execution path, not a sub-feature of the API. They share models, schemas, and services but have their own entry points.

### AI Model Management Isolated in `app/ai/`
Model loading (`clip_model.py`, `yolo_model.py`) is isolated from task logic. Workers import model instances from `app/ai/` rather than loading models inside task functions. This enforces the "load once at worker startup" pattern and makes model swapping straightforward.

### Shared Utility Principle
`app/core/` contains only infrastructure-level utilities: security, middleware, rate limiting, exceptions, logging. No business logic lives here. This prevents `core/` from becoming a miscellaneous dumping ground.

---

## File Naming Conventions

| Context | Convention | Example |
|---|---|---|
| React components | PascalCase `.tsx` | `VideoCard.tsx` |
| React hooks | camelCase with `use` prefix | `useVideos.ts` |
| Zustand stores | camelCase with `Store` suffix | `authStore.ts` |
| Service files (FE) | camelCase with `Service` suffix | `videoService.ts` |
| Python modules | snake_case | `video_service.py` |
| Python classes | PascalCase | `VideoResponse` |
| Python functions | snake_case | `get_current_user` |
| Alembic migrations | `NNNN_description.py` | `0001_initial_schema.py` |
| Environment vars | SCREAMING_SNAKE_CASE | `DATABASE_URL` |
| Vite env vars | `VITE_` prefix | `VITE_API_BASE_URL` |
