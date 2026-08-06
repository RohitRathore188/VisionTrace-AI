# Production-Grade Folder Structure
## VisionTrace AI — Intelligent Video Search Platform

**Version:** 1.0  
**Date:** August 5, 2026  
**Status:** Draft — Awaiting Approval

---

## Complete Repository Structure

```
visiontrace-ai/
├── frontend/                           # React + Vite + TypeScript frontend application
├── backend/                            # FastAPI Python backend application
├── docs/                               # All planning and architecture documents
├── docker/                             # Docker configurations and scripts
├── .github/                            # GitHub Actions CI/CD workflows
├── .gitignore                          # Root .gitignore
├── .env.example                        # Example environment variables (all services)
├── docker-compose.yml                  # Local development orchestration
├── docker-compose.prod.yml             # Production-equivalent compose (staging)
├── Makefile                            # Common development commands
└── README.md                           # Project overview and setup instructions
```

---

## Frontend Structure (`/frontend`)

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── robots.txt
│   └── assets/
│       ├── logo.svg
│       └── images/
│
├── src/
│   ├── main.tsx                        # Application entry point
│   ├── App.tsx                         # Root component with Router
│   ├── vite-env.d.ts                   # Vite environment type declarations
│   │
│   ├── assets/                         # Static assets imported by components
│   │   ├── images/
│   │   │   ├── placeholder.png
│   │   │   └── empty-state.svg
│   │   └── icons/
│   │       ├── upload-icon.svg
│   │       └── search-icon.svg
│   │
│   ├── components/                     # Shared, reusable UI components
│   │   ├── ui/                         # Shadcn UI components (auto-generated)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── slider.tsx
│   │   │   └── ... (other shadcn components)
│   │   │
│   │   ├── layout/                     # Application layout components
│   │   │   ├── AppLayout.tsx           # Root layout wrapper (navbar + sidebar + main)
│   │   │   ├── Navbar.tsx              # Top navigation bar with user menu
│   │   │   ├── Sidebar.tsx             # Left sidebar navigation
│   │   │   ├── PageHeader.tsx          # Reusable page title + breadcrumb
│   │   │   └── Footer.tsx              # Footer (optional)
│   │   │
│   │   ├── common/                     # Domain-agnostic reusable components
│   │   │   ├── DisclaimerBanner.tsx    # AI disclaimer banner (mandatory on results)
│   │   │   ├── SimilarityBadge.tsx     # Color-coded similarity score badge
│   │   │   ├── StatusBadge.tsx         # Video processing status badge
│   │   │   ├── ConfirmDialog.tsx       # Reusable confirmation modal
│   │   │   ├── EmptyState.tsx          # Empty list/results placeholder
│   │   │   ├── ErrorMessage.tsx        # User-friendly error display
│   │   │   ├── LoadingSpinner.tsx      # Centered loading spinner
│   │   │   ├── SkeletonCard.tsx        # Loading skeleton for cards
│   │   │   └── Pagination.tsx          # Pagination controls
│   │   │
│   │   └── forms/                      # Reusable form components
│   │       ├── FileDropzone.tsx        # Drag-and-drop file input
│   │       ├── CharacterCounter.tsx    # Text field character counter
│   │       └── FormField.tsx           # Wrapper for form field + label + error
│   │
│   ├── features/                       # Feature modules (domain-specific)
│   │   │
│   │   ├── auth/                       # Authentication feature
│   │   │   ├── pages/
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   ├── RegisterPage.tsx
│   │   │   │   └── index.ts
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── RegisterForm.tsx
│   │   │   │   ├── AuthGuard.tsx       # Route guard for authenticated routes
│   │   │   │   ├── RoleGuard.tsx       # Route guard for role-based access
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useAuth.ts          # Auth-related hooks (login, logout, etc.)
│   │   │   │   └── index.ts
│   │   │   ├── store/
│   │   │   │   └── authStore.ts        # Zustand auth state (user, tokens)
│   │   │   ├── types/
│   │   │   │   └── auth.types.ts       # Auth TypeScript types
│   │   │   └── index.ts
│   │   │
│   │   ├── videos/                     # Video management feature
│   │   │   ├── pages/
│   │   │   │   ├── VideoLibraryPage.tsx
│   │   │   │   ├── UploadPage.tsx
│   │   │   │   └── index.ts
│   │   │   ├── components/
│   │   │   │   ├── VideoCard.tsx       # Single video card in library
│   │   │   │   ├── VideoGrid.tsx       # Grid layout for videos
│   │   │   │   ├── VideoFilterBar.tsx  # Filter and sort controls
│   │   │   │   ├── UploadForm.tsx      # Upload form with title/description
│   │   │   │   ├── UploadProgressBar.tsx  # Real-time upload progress
│   │   │   │   ├── VideoDeleteDialog.tsx  # Confirmation dialog for delete
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useVideos.ts        # TanStack Query hooks for video CRUD
│   │   │   │   ├── useUpload.ts        # Upload logic with progress
│   │   │   │   ├── useVideoStatus.ts   # Polling hook for processing status
│   │   │   │   └── index.ts
│   │   │   ├── store/
│   │   │   │   └── videoStore.ts       # Zustand video library state
│   │   │   ├── types/
│   │   │   │   └── video.types.ts      # Video TypeScript types
│   │   │   └── index.ts
│   │   │
│   │   ├── search/                     # Search feature (image + text)
│   │   │   ├── pages/
│   │   │   │   ├── SearchPage.tsx
│   │   │   │   └── index.ts
│   │   │   ├── components/
│   │   │   │   ├── SearchTabs.tsx      # Tab navigation (Image | Text)
│   │   │   │   ├── ImageSearchPanel.tsx   # Image upload + settings
│   │   │   │   ├── TextSearchPanel.tsx    # Text input + suggestions
│   │   │   │   ├── VideoSelector.tsx      # Multi-select dropdown for videos
│   │   │   │   ├── TopKSelector.tsx       # Top-K result count selector
│   │   │   │   ├── QuerySuggestions.tsx   # Example queries for text search
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useSearch.ts        # Search execution hooks
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── search.types.ts     # Search TypeScript types
│   │   │   └── index.ts
│   │   │
│   │   ├── results/                    # Search results feature
│   │   │   ├── pages/
│   │   │   │   ├── ResultsPage.tsx
│   │   │   │   └── index.ts
│   │   │   ├── components/
│   │   │   │   ├── ResultsToolbar.tsx     # Sort, filter, view toggle, export
│   │   │   │   ├── ResultGrid.tsx         # Grid view of results
│   │   │   │   ├── ResultList.tsx         # List view of results
│   │   │   │   ├── ResultCard.tsx         # Single result card
│   │   │   │   ├── BboxOverlay.tsx        # Bounding box overlay on thumbnail
│   │   │   │   ├── ScoreFilter.tsx        # Similarity score slider
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useResults.ts       # Result fetching and filtering
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── result.types.ts     # Result TypeScript types
│   │   │   └── index.ts
│   │   │
│   │   ├── player/                     # Video player feature
│   │   │   ├── components/
│   │   │   │   ├── VideoPlayerPanel.tsx   # Main video player wrapper
│   │   │   │   ├── PlayerControls.tsx     # Play/pause, seek, volume, fullscreen
│   │   │   │   ├── TimelineMarkers.tsx    # Result timestamp markers on seek bar
│   │   │   │   ├── MarkerTooltip.tsx      # Tooltip on marker hover
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── usePlayer.ts        # Video player control hooks
│   │   │   │   └── index.ts
│   │   │   ├── store/
│   │   │   │   └── playerStore.ts      # Zustand player state (video, timestamp)
│   │   │   ├── types/
│   │   │   │   └── player.types.ts     # Player TypeScript types
│   │   │   └── index.ts
│   │   │
│   │   ├── reports/                    # Report generation feature
│   │   │   ├── components/
│   │   │   │   ├── ExportCSVButton.tsx    # CSV export trigger
│   │   │   │   ├── ExportPDFModal.tsx     # PDF export modal with title input
│   │   │   │   └── index.ts
│   │   │   ├── utils/
│   │   │   │   ├── csvExporter.ts      # CSV generation logic
│   │   │   │   ├── pdfExporter.ts      # PDF generation logic (jsPDF)
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── report.types.ts     # Report TypeScript types
│   │   │   └── index.ts
│   │   │
│   │   ├── history/                    # Search history feature
│   │   │   ├── pages/
│   │   │   │   ├── SearchHistoryPage.tsx
│   │   │   │   └── index.ts
│   │   │   ├── components/
│   │   │   │   ├── HistoryList.tsx     # List of past searches
│   │   │   │   ├── HistoryItem.tsx     # Single history entry card
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useHistory.ts       # History fetching and deletion
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── history.types.ts    # History TypeScript types
│   │   │   └── index.ts
│   │   │
│   │   └── admin/                      # Admin dashboard feature
│   │       ├── pages/
│   │       │   ├── AdminDashboardPage.tsx
│   │       │   └── index.ts
│   │       ├── components/
│   │       │   ├── SystemMetricsCards.tsx  # Total videos, searches, users
│   │       │   ├── PipelineJobTable.tsx    # All processing jobs
│   │       │   ├── UserManagementTable.tsx # User CRUD table
│   │       │   ├── CreateUserModal.tsx     # Modal for creating new user
│   │       │   └── index.ts
│   │       ├── hooks/
│   │       │   ├── useAdmin.ts         # Admin-specific hooks
│   │       │   └── index.ts
│   │       ├── types/
│   │       │   └── admin.types.ts      # Admin TypeScript types
│   │       └── index.ts
│   │
│   ├── services/                       # API communication layer
│   │   ├── api.ts                      # Axios instance with interceptors
│   │   ├── authService.ts              # Auth API calls
│   │   ├── videoService.ts             # Video API calls
│   │   ├── searchService.ts            # Search API calls
│   │   ├── resultsService.ts           # Results API calls
│   │   ├── historyService.ts           # History API calls
│   │   ├── adminService.ts             # Admin API calls
│   │   └── index.ts
│   │
│   ├── router/                         # Routing configuration
│   │   ├── index.tsx                   # React Router route definitions
│   │   ├── routes.ts                   # Route path constants
│   │   └── ProtectedRoute.tsx          # Route wrapper with auth check
│   │
│   ├── hooks/                          # Global custom hooks
│   │   ├── useDebounce.ts              # Debounce hook
│   │   ├── useLocalStorage.ts          # LocalStorage hook
│   │   ├── useMediaQuery.ts            # Responsive breakpoint hook
│   │   └── index.ts
│   │
│   ├── lib/                            # Utility functions and helpers
│   │   ├── utils.ts                    # Shadcn cn() + general helpers
│   │   ├── formatters.ts               # Date, time, file size formatters
│   │   ├── validators.ts               # Shared Zod schemas
│   │   ├── constants.ts                # App-wide constants
│   │   └── index.ts
│   │
│   ├── types/                          # Global TypeScript types
│   │   ├── api.types.ts                # Generic API response types
│   │   ├── global.types.ts             # App-wide enums and shared types
│   │   └── index.ts
│   │
│   └── styles/
│       └── globals.css                 # Tailwind directives + CSS variables
│
├── index.html                          # HTML entry point
├── vite.config.ts                      # Vite configuration
├── tailwind.config.ts                  # TailwindCSS configuration
├── tsconfig.json                       # TypeScript base configuration
├── tsconfig.app.json                   # TypeScript app-specific config
├── tsconfig.node.json                  # TypeScript Node-specific config
├── eslint.config.js                    # ESLint configuration
├── .prettierrc                         # Prettier configuration
├── .env.example                        # Example environment variables
├── .gitignore
├── package.json
└── pnpm-lock.yaml (or package-lock.json/yarn.lock)
```

---

## Backend Structure (`/backend`)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                         # FastAPI application factory and startup
│   ├── config.py                       # Pydantic Settings (all environment variables)
│   ├── dependencies.py                 # Shared FastAPI dependencies (DB session, auth)
│   │
│   ├── api/                            # API route handlers (thin layer)
│   │   ├── __init__.py
│   │   ├── router.py                   # Master API router (mounts all sub-routers)
│   │   │
│   │   ├── v1/                         # API version 1 routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 # POST /auth/register, /auth/login, /auth/refresh, /auth/logout
│   │   │   ├── users.py                # GET /users/me, PUT /users/me/password
│   │   │   ├── videos.py               # POST /videos/upload, GET /videos, GET /videos/{id}, DELETE /videos/{id}
│   │   │   ├── search.py               # POST /search/image, POST /search/text
│   │   │   ├── sessions.py             # GET /search/sessions, GET /search/sessions/{id}/results, DELETE /search/sessions/{id}
│   │   │   ├── admin.py                # GET /admin/metrics, GET /admin/jobs, POST /admin/jobs/{id}/retry
│   │   │   └── system.py               # GET /system/health, GET /system/readiness
│   │   │
│   │   └── middleware/                 # Custom middleware
│   │       ├── __init__.py
│   │       ├── request_id.py           # Request ID injection
│   │       ├── logging.py              # Structured logging middleware
│   │       ├── rate_limit.py           # Rate limiting middleware
│   │       └── error_handler.py        # Global exception handler
│   │
│   ├── services/                       # Business logic layer
│   │   ├── __init__.py
│   │   │
│   │   ├── auth/                       # Authentication services
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py         # Registration, login, token generation
│   │   │   ├── token_service.py        # JWT creation, validation, refresh
│   │   │   └── password_service.py     # Password hashing and verification
│   │   │
│   │   ├── video/                      # Video management services
│   │   │   ├── __init__.py
│   │   │   ├── video_service.py        # Video CRUD operations
│   │   │   ├── upload_service.py       # File validation and upload logic
│   │   │   └── status_service.py       # Processing status tracking
│   │   │
│   │   ├── storage/                    # Storage services
│   │   │   ├── __init__.py
│   │   │   ├── storage_service.py      # Supabase Storage operations
│   │   │   └── signed_url_service.py   # Signed URL generation
│   │   │
│   │   ├── search/                     # Search services
│   │   │   ├── __init__.py
│   │   │   ├── search_service.py       # Main search orchestration
│   │   │   ├── embedding_service.py    # Query embedding generation
│   │   │   ├── index_service.py        # FAISS index loading and search
│   │   │   └── ranking_service.py      # Result ranking and merging
│   │   │
│   │   ├── result/                     # Result services
│   │   │   ├── __init__.py
│   │   │   ├── result_service.py       # Result persistence and retrieval
│   │   │   └── session_service.py      # Search session management
│   │   │
│   │   └── admin/                      # Admin services
│   │       ├── __init__.py
│   │       ├── admin_service.py        # Admin operations
│   │       ├── metrics_service.py      # System metrics aggregation
│   │       └── job_service.py          # Job management and retry logic
│   │
│   ├── repositories/                   # Data access layer (Repository pattern)
│   │   ├── __init__.py
│   │   ├── base_repository.py          # Base repository with common CRUD operations
│   │   ├── user_repository.py          # User table operations
│   │   ├── video_repository.py         # Video table operations
│   │   ├── frame_repository.py         # Frame table operations
│   │   ├── detection_repository.py     # Detection table operations
│   │   ├── track_repository.py         # Track table operations
│   │   ├── embedding_repository.py     # Embedding table operations
│   │   ├── session_repository.py       # Search session table operations
│   │   ├── result_repository.py        # Search result table operations
│   │   └── job_repository.py           # Processing job table operations
│   │
│   ├── models/                         # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py                     # DeclarativeBase, UUID mixin, timestamp mixin
│   │   ├── user.py                     # User model + UserRole enum
│   │   ├── video.py                    # Video model + VideoStatus enum
│   │   ├── processing_job.py           # ProcessingJob model + PipelineStep enum
│   │   ├── frame.py                    # Frame model
│   │   ├── detection.py                # Detection model
│   │   ├── track.py                    # Track model
│   │   ├── embedding.py                # Embedding model
│   │   ├── search_session.py           # SearchSession model + QueryType enum
│   │   └── search_result.py            # SearchResult model
│   │
│   ├── schemas/                        # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── base.py                     # Base schemas with common fields
│   │   ├── auth.py                     # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── user.py                     # UserResponse, UpdatePasswordRequest, UserAdminUpdate
│   │   ├── video.py                    # VideoCreate, VideoResponse, VideoListResponse, UploadRequest
│   │   ├── search.py                   # ImageSearchRequest, TextSearchRequest, SearchResponse
│   │   ├── result.py                   # ResultResponse, ResultListResponse
│   │   ├── session.py                  # SessionResponse, SessionListResponse
│   │   ├── admin.py                    # MetricsResponse, JobResponse, JobListResponse
│   │   └── pagination.py               # PaginatedResponse schema
│   │
│   ├── pipelines/                      # AI/ML pipeline modules
│   │   ├── __init__.py
│   │   │
│   │   ├── detection/                  # Object detection pipeline
│   │   │   ├── __init__.py
│   │   │   ├── detector.py             # YOLO model wrapper and inference
│   │   │   ├── preprocessor.py         # Image preprocessing for YOLO
│   │   │   └── postprocessor.py        # Detection result filtering and formatting
│   │   │
│   │   ├── tracking/                   # Object tracking pipeline
│   │   │   ├── __init__.py
│   │   │   ├── tracker.py              # ByteTrack wrapper
│   │   │   └── track_manager.py        # Track ID assignment and persistence
│   │   │
│   │   ├── embeddings/                 # Embedding generation pipeline
│   │   │   ├── __init__.py
│   │   │   ├── clip_encoder.py         # OpenCLIP model wrapper
│   │   │   ├── image_processor.py      # Crop extraction and preprocessing
│   │   │   └── batch_processor.py      # Batching logic for efficient inference
│   │   │
│   │   ├── search/                     # Search pipeline
│   │   │   ├── __init__.py
│   │   │   ├── faiss_index.py          # FAISS index builder and searcher
│   │   │   ├── query_processor.py      # Query embedding generation
│   │   │   └── result_mapper.py        # FAISS ID to DB record mapping
│   │   │
│   │   └── frame_extraction/           # Frame extraction pipeline
│   │       ├── __init__.py
│   │       ├── extractor.py            # OpenCV frame extraction
│   │       └── frame_processor.py      # Frame resizing and encoding
│   │
│   ├── workers/                        # Celery worker tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py               # Celery application instance
│   │   ├── pipeline.py                 # Task chain orchestration
│   │   │
│   │   ├── tasks/                      # Individual task definitions
│   │   │   ├── __init__.py
│   │   │   ├── frame_extraction.py     # Task: Extract frames from video
│   │   │   ├── object_detection.py     # Task: Detect objects in frames
│   │   │   ├── object_tracking.py      # Task: Track objects across frames
│   │   │   ├── embedding_generation.py # Task: Generate embeddings
│   │   │   └── index_building.py       # Task: Build FAISS index
│   │   │
│   │   └── utils/                      # Worker utilities
│   │       ├── __init__.py
│   │       ├── task_logger.py          # Task-specific logging
│   │       └── retry_handler.py        # Custom retry logic
│   │
│   ├── core/                           # Core infrastructure and utilities
│   │   ├── __init__.py
│   │   ├── security.py                 # JWT encoding/decoding, password hashing
│   │   ├── exceptions.py               # Custom exception classes
│   │   ├── logging.py                  # Structured logging configuration (structlog)
│   │   ├── rate_limiter.py             # Rate limiting logic (slowapi)
│   │   └── metrics.py                  # Prometheus metrics (optional)
│   │
│   ├── db/                             # Database infrastructure
│   │   ├── __init__.py
│   │   ├── session.py                  # Async SQLAlchemy engine and session factory
│   │   ├── base.py                     # Import all models for Alembic
│   │   │
│   │   └── migrations/                 # Alembic migrations
│   │       ├── env.py                  # Alembic environment configuration
│   │       ├── script.py.mako          # Migration script template
│   │       └── versions/               # Migration version files
│   │           └── 0001_initial_schema.py
│   │
│   └── utils/                          # Utility functions
│       ├── __init__.py
│       ├── file_validators.py          # File type and size validation
│       ├── image_utils.py              # Image manipulation helpers
│       ├── video_utils.py              # Video metadata extraction
│       └── time_utils.py               # Timestamp and duration helpers
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures (test DB, test client)
│   │
│   ├── unit/                           # Unit tests
│   │   ├── __init__.py
│   │   ├── test_security.py
│   │   ├── test_validators.py
│   │   ├── test_formatters.py
│   │   └── services/
│   │       ├── test_auth_service.py
│   │       ├── test_video_service.py
│   │       └── test_search_service.py
│   │
│   ├── integration/                    # Integration tests
│   │   ├── __init__.py
│   │   ├── test_auth_api.py
│   │   ├── test_videos_api.py
│   │   ├── test_search_api.py
│   │   └── test_admin_api.py
│   │
│   ├── e2e/                            # End-to-end tests
│   │   ├── __init__.py
│   │   └── test_upload_pipeline.py
│   │
│   └── fixtures/                       # Test data
│       ├── test_video.mp4
│       ├── test_query_image.jpg
│       └── mock_data.json
│
├── scripts/                            # Utility scripts
│   ├── seed_database.py                # Seed test data
│   ├── rebuild_indexes.py              # Rebuild all FAISS indexes
│   └── migrate_embeddings.py           # Data migration scripts
│
├── alembic.ini                         # Alembic configuration
├── pyproject.toml                      # Project metadata + tool configs (ruff, black, pytest)
├── requirements.txt                    # Pinned production dependencies
├── requirements-dev.txt                # Development dependencies
├── Dockerfile                          # Multi-stage Docker build
├── .dockerignore
├── .env.example
├── .gitignore
├── pytest.ini
└── README.md
```

---

## Folder Responsibilities — Frontend

### **Root Level (`/frontend`)**
- **`public/`**: Static assets served directly (favicon, robots.txt, images not processed by Vite)
- **`src/`**: All application source code
- **`index.html`**: HTML entry point with `<div id="root">`

### **`src/` Core Files**
- **`main.tsx`**: Application entry point; mounts React root, initializes providers (Router, TanStack Query, Auth)
- **`App.tsx`**: Root component; wraps app with `<Router>`, `<AppLayout>`, error boundary
- **`vite-env.d.ts`**: TypeScript declarations for Vite environment variables

### **`src/assets/`**
Static images and icons imported by components (not directly served; processed by Vite build)

### **`src/components/`**
Shared, reusable UI components with no feature-specific logic

- **`ui/`**: Auto-generated Shadcn UI components (Button, Input, Dialog, etc.)
- **`layout/`**: App shell components (Navbar, Sidebar, PageHeader)
- **`common/`**: Domain-agnostic reusable components (badges, empty states, loading spinners)
- **`forms/`**: Reusable form primitives (file dropzone, character counter)

### **`src/features/`**
Feature modules — each feature is self-contained with its own pages, components, hooks, types, and store

**Feature structure (applies to all features: auth, videos, search, results, player, reports, history, admin):**

- **`pages/`**: Top-level page components rendered by routes
- **`components/`**: Feature-specific components (not shared outside the feature)
- **`hooks/`**: Feature-specific custom hooks (e.g., `useVideos`, `useSearch`)
- **`store/`**: Zustand state management (if feature needs global state)
- **`types/`**: TypeScript type definitions for the feature
- **`utils/`** (optional): Feature-specific utility functions

**Why feature-first?**
- **Co-location**: Everything related to a feature lives together
- **Easy refactoring**: Move or delete a feature by moving/deleting one folder
- **Clear boundaries**: Avoids feature logic bleeding into shared components

### **`src/services/`**
API communication layer — Axios-based service functions for each domain

- **`api.ts`**: Axios instance with interceptors (token refresh, request ID, error handling)
- **`authService.ts`**: Auth API calls (`login`, `register`, `refresh`, `logout`)
- **`videoService.ts`**: Video API calls (`upload`, `getVideos`, `deleteVideo`)
- **`searchService.ts`**: Search API calls (`imageSearch`, `textSearch`)
- **`resultsService.ts`**: Results API calls (`getResults`, `getSession`)
- **`historyService.ts`**: History API calls (`getSessions`, `deleteSession`)
- **`adminService.ts`**: Admin API calls (`getMetrics`, `retryJob`)

### **`src/router/`**
React Router configuration

- **`index.tsx`**: Route definitions with `createBrowserRouter`
- **`routes.ts`**: Route path constants (e.g., `ROUTES.LOGIN = '/login'`)
- **`ProtectedRoute.tsx`**: Route wrapper that redirects unauthenticated users to login

### **`src/hooks/`**
Global custom hooks (not feature-specific)

- **`useDebounce.ts`**: Debounce value changes (e.g., search input)
- **`useLocalStorage.ts`**: Persist state to localStorage
- **`useMediaQuery.ts`**: Responsive breakpoint detection

### **`src/lib/`**
Utility functions and helpers

- **`utils.ts`**: Shadcn's `cn()` function + general helpers
- **`formatters.ts`**: Format dates, timestamps, file sizes, similarity scores
- **`validators.ts`**: Shared Zod schemas for form validation
- **`constants.ts`**: App-wide constants (API base URL, max file size, etc.)

### **`src/types/`**
Global TypeScript types (used across multiple features)

- **`api.types.ts`**: Generic API response types (`ApiResponse<T>`, `PaginatedResponse<T>`)
- **`global.types.ts`**: App-wide enums and shared types

### **`src/styles/`**
Global CSS and Tailwind configuration

- **`globals.css`**: Tailwind directives (`@tailwind base; @tailwind components; @tailwind utilities;`) + CSS custom properties

---

## Folder Responsibilities — Backend

### **Root Level (`/backend`)**
- **`app/`**: All application code
- **`tests/`**: Test suite (unit, integration, e2e)
- **`scripts/`**: Utility scripts (seed data, rebuild indexes)
- **`alembic.ini`**: Alembic configuration for database migrations
- **`requirements.txt`**: Pinned production dependencies
- **`requirements-dev.txt`**: Development/test dependencies
- **`Dockerfile`**: Multi-stage build for API + worker containers

### **`app/` Core Files**
- **`main.py`**: FastAPI app factory; registers routers, middleware, startup/shutdown events
- **`config.py`**: Pydantic `Settings` class; loads all environment variables
- **`dependencies.py`**: Shared FastAPI dependencies (`get_db`, `get_current_user`, `require_role`)

### **`app/api/`**
HTTP route handlers — thin layer that validates input, calls services, returns responses

- **`router.py`**: Master API router that mounts all versioned sub-routers
- **`v1/`**: API version 1 routes (auth, users, videos, search, sessions, admin, system)
- **`middleware/`**: Custom middleware (request ID, logging, rate limiting, error handling)

**Responsibilities:**
- Validate request body/query params using Pydantic schemas
- Call service layer functions
- Serialize response using Pydantic schemas
- Return appropriate HTTP status codes
- **No business logic** should live in route handlers

### **`app/services/`**
Business logic layer — orchestrates repositories, pipelines, and external services

**Organized by domain:**

- **`auth/`**: Authentication logic (registration, login, token generation/refresh, password hashing)
- **`video/`**: Video management (CRUD, upload validation, status tracking)
- **`storage/`**: Supabase Storage operations (upload, download, signed URL generation)
- **`search/`**: Search orchestration (query embedding, FAISS search, result ranking)
- **`result/`**: Result persistence and retrieval
- **`admin/`**: Admin operations (metrics, job management)

**Responsibilities:**
- Implement business rules and workflows
- Coordinate multiple repositories and pipelines
- Handle transactions (start/commit/rollback)
- Call external APIs (Supabase, Sentry)
- **No direct database access** — delegates to repositories
- **No HTTP concerns** — returns domain objects, not HTTP responses

### **`app/repositories/`**
Data access layer — Repository pattern for database operations

**One repository per table:**

- **`base_repository.py`**: Base class with common CRUD methods (`get`, `create`, `update`, `delete`, `list`)
- **`user_repository.py`**: User table operations
- **`video_repository.py`**: Video table operations
- **`frame_repository.py`**: Frame table operations
- **`detection_repository.py`**: Detection table operations
- **`track_repository.py`**: Track table operations
- **`embedding_repository.py`**: Embedding table operations
- **`session_repository.py`**: Search session table operations
- **`result_repository.py`**: Search result table operations
- **`job_repository.py`**: Processing job table operations

**Responsibilities:**
- Execute database queries using SQLAlchemy ORM
- Abstract database logic from services
- Return ORM model instances (not Pydantic schemas)
- Handle query optimization (joins, eager loading, pagination)

**Why repositories?**
- **Testability**: Repositories can be mocked in service tests
- **Separation of Concerns**: Services focus on business logic, repositories on data access
- **Reusability**: Same query logic can be reused across multiple services

### **`app/models/`**
SQLAlchemy ORM models — define database schema

- **`base.py`**: `DeclarativeBase`, UUID primary key mixin, timestamp mixin
- **One file per table**: `user.py`, `video.py`, `frame.py`, `detection.py`, etc.
- **Enums**: Define Python enums for status fields (e.g., `UserRole`, `VideoStatus`, `PipelineStep`)

**Responsibilities:**
- Define table structure (columns, types, constraints, indexes)
- Define relationships (`relationship()`, `ForeignKey`)
- **No business logic** — models are data containers

### **`app/schemas/`**
Pydantic request/response schemas — API input/output validation and serialization

- **`base.py`**: Base schemas with common fields (`id`, `created_at`, `updated_at`)
- **One file per domain**: `auth.py`, `user.py`, `video.py`, `search.py`, etc.
- **`pagination.py`**: Generic paginated response schema

**Responsibilities:**
- Validate request bodies and query parameters
- Serialize ORM models to JSON-serializable dicts
- Define API contracts (what fields are required, optional, read-only)

**Naming convention:**
- Request schemas: `{Entity}Create`, `{Entity}Update` (e.g., `VideoCreate`, `UserUpdate`)
- Response schemas: `{Entity}Response`, `{Entity}ListResponse` (e.g., `VideoResponse`, `VideoListResponse`)

### **`app/pipelines/`**
AI/ML pipeline modules — wrappers around AI models and processing logic

**Organized by pipeline step:**

- **`detection/`**: YOLO object detection (model loading, inference, post-processing)
- **`tracking/`**: ByteTrack multi-object tracking
- **`embeddings/`**: OpenCLIP embedding generation (image + text encoders)
- **`search/`**: FAISS index building and searching
- **`frame_extraction/`**: OpenCV frame extraction and processing

**Responsibilities:**
- Load AI models once (singleton pattern)
- Encapsulate model inference logic
- Batch processing for efficiency
- Preprocessing and postprocessing
- **No database access** — receives inputs from workers, returns outputs

**Why separate pipelines?**
- **Modularity**: Each pipeline step is independently testable
- **Reusability**: Pipeline modules can be used by both workers and API (e.g., search uses embeddings pipeline)
- **Model management**: Centralized model loading and version control

### **`app/workers/`**
Celery worker tasks — background job execution

- **`celery_app.py`**: Celery application instance with Redis broker configuration
- **`pipeline.py`**: Task chain definition (chains Tasks 1–5 together)
- **`tasks/`**: Individual task definitions (one file per pipeline step)
- **`utils/`**: Worker-specific utilities (logging, retry handling)

**Responsibilities:**
- Define Celery tasks that execute pipeline steps
- Update `processing_jobs` table with status after each step
- Enqueue next task in chain on success
- Requeue task on transient failure (retry logic)
- Call pipeline modules for AI/ML operations
- Call repositories for database operations

### **`app/core/`**
Core infrastructure and cross-cutting concerns

- **`security.py`**: JWT encoding/decoding, password hashing (bcrypt)
- **`exceptions.py`**: Custom exception classes (`VideoNotFoundException`, `UnauthorizedException`)
- **`logging.py`**: Structured logging configuration (structlog with JSON output)
- **`rate_limiter.py`**: Rate limiting logic (slowapi wrapper)
- **`metrics.py`**: Prometheus metrics (optional, for monitoring)

**Responsibilities:**
- Provide reusable infrastructure utilities
- No business logic or feature-specific code

### **`app/db/`**
Database infrastructure

- **`session.py`**: Async SQLAlchemy engine and session factory
- **`base.py`**: Import all ORM models (required for Alembic auto-generation)
- **`migrations/`**: Alembic migration environment and version files

**Responsibilities:**
- Configure database connection
- Provide async session dependency for FastAPI routes
- Manage schema migrations via Alembic

### **`app/utils/`**
General utility functions (not core infrastructure)

- **`file_validators.py`**: File type (MIME + magic bytes) and size validation
- **`image_utils.py`**: Image manipulation (resize, crop, encode)
- **`video_utils.py`**: Video metadata extraction (duration, codec, FPS)
- **`time_utils.py`**: Timestamp formatting and duration calculations

---

## Key Architectural Patterns

### 1. **Feature-First Frontend** (vs. Type-First)

**❌ Type-First (Flat) Structure:**
```
src/
├── components/          # All components together
│   ├── LoginForm.tsx
│   ├── VideoCard.tsx
│   ├── SearchPanel.tsx
│   └── ... (100+ files)
├── hooks/               # All hooks together
│   ├── useAuth.ts
│   ├── useVideos.ts
│   └── ...
└── types/               # All types together
    ├── auth.types.ts
    ├── video.types.ts
    └── ...
```

**✅ Feature-First Structure:**
```
src/
├── features/
│   ├── auth/                 # Everything auth-related
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── types/
│   ├── videos/               # Everything video-related
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── types/
│   └── ...
```

**Benefits:**
- **Co-location**: Related code lives together
- **Easy refactoring**: Move or delete features by moving/deleting one folder
- **Scalability**: Adding features doesn't pollute shared folders
- **Clear boundaries**: Feature logic stays contained

---

### 2. **Repository Pattern** (Backend Data Access)

**Service Layer depends on Repository Layer (not directly on ORM)**

```python
# ❌ Service directly accessing ORM (tight coupling)
class VideoService:
    def get_video(self, video_id: UUID):
        video = db.query(Video).filter(Video.id == video_id).first()
        return video

# ✅ Service using Repository (loose coupling, testable)
class VideoService:
    def __init__(self, video_repo: VideoRepository):
        self.video_repo = video_repo
    
    def get_video(self, video_id: UUID):
        return self.video_repo.get(video_id)
```

**Benefits:**
- **Testability**: Services can be tested with mocked repositories
- **Separation of Concerns**: Services focus on business logic, repositories on data access
- **Reusability**: Same query logic reused across multiple services
- **Query optimization**: Repositories handle joins, eager loading, pagination in one place

---

### 3. **Pipeline Modules** (vs. Inline Worker Logic)

**AI/ML logic is extracted into reusable pipeline modules**

```python
# ❌ Worker task with inline model logic (hard to test, not reusable)
@celery_app.task
def detect_objects(video_id: UUID):
    model = YOLO("yolov8n.pt")  # Loads model every time
    frames = get_frames(video_id)
    for frame in frames:
        results = model(frame)  # Inline inference
        save_detections(results)

# ✅ Worker task using Pipeline module (testable, reusable)
@celery_app.task
def detect_objects(video_id: UUID):
    detector = YOLODetector()  # Singleton, loaded once
    frames = get_frames(video_id)
    detections = detector.detect_batch(frames)
    save_detections(detections)
```

**Benefits:**
- **Model reuse**: Pipeline modules loaded once, used by both workers and API
- **Testability**: Pipeline modules can be unit tested independently
- **Modularity**: Each pipeline step is independently swappable (e.g., switch YOLO → EfficientDet)

---

### 4. **API Versioning** (v1, v2, ...)

**Routes are versioned to allow non-breaking changes**

```
/api/v1/videos        # Current API
/api/v2/videos        # New API (breaking changes)
```

**Migration strategy:**
- v1 and v2 coexist during deprecation period
- Frontend upgrades to v2 incrementally
- v1 is deprecated after 6 months

---

### 5. **Dependency Injection** (FastAPI Depends)

**Dependencies injected via `Depends()` instead of global imports**

```python
# ❌ Global database session (tight coupling, hard to test)
from app.db.session import SessionLocal
db = SessionLocal()

@app.get("/videos")
def get_videos():
    return db.query(Video).all()

# ✅ Injected database session (loose coupling, testable)
from app.dependencies import get_db

@app.get("/videos")
def get_videos(db: Session = Depends(get_db)):
    return db.query(Video).all()
```

**Benefits:**
- **Testability**: Dependencies can be overridden in tests
- **Lifecycle management**: FastAPI handles session creation/cleanup
- **Type safety**: IDE autocomplete and type checking

---

## Folder Naming Conventions

| Context | Convention | Example |
|---|---|---|
| Frontend components | PascalCase `.tsx` | `VideoCard.tsx` |
| Frontend hooks | camelCase with `use` prefix | `useVideos.ts` |
| Frontend stores | camelCase with `Store` suffix | `authStore.ts` |
| Frontend services | camelCase with `Service` suffix | `videoService.ts` |
| Backend modules | snake_case `.py` | `video_service.py` |
| Backend classes | PascalCase | `VideoService`, `VideoRepository` |
| Backend functions | snake_case | `get_current_user`, `upload_video` |
| Backend models (ORM) | PascalCase singular | `Video`, `User`, `SearchSession` |
| Backend tables (DB) | snake_case plural | `videos`, `users`, `search_sessions` |
| Alembic migrations | `NNNN_description.py` | `0001_initial_schema.py` |
| Test files | `test_` prefix | `test_auth_service.py` |
| Environment variables | SCREAMING_SNAKE_CASE | `DATABASE_URL`, `SECRET_KEY` |
| Vite env vars | `VITE_` prefix | `VITE_API_BASE_URL` |

---

## Import Patterns

### Frontend (TypeScript)

```typescript
// ✅ Feature imports use relative paths within feature
import { useVideos } from './hooks/useVideos';
import { VideoCard } from './components/VideoCard';

// ✅ Cross-feature imports use absolute paths
import { useAuth } from '@/features/auth/hooks/useAuth';
import { DisclaimerBanner } from '@/components/common/DisclaimerBanner';

// ✅ Shared utilities use absolute paths
import { cn } from '@/lib/utils';
import { formatTimestamp } from '@/lib/formatters';
```

### Backend (Python)

```python
# ✅ Absolute imports from app root
from app.services.video.video_service import VideoService
from app.repositories.video_repository import VideoRepository
from app.models.video import Video
from app.schemas.video import VideoResponse

# ✅ Relative imports within same package
from .video_service import VideoService
from ..repositories.video_repository import VideoRepository
```

---

## Configuration Files Overview

### Frontend

- **`vite.config.ts`**: Vite build configuration, path aliases, plugins
- **`tailwind.config.ts`**: TailwindCSS theme, colors, plugins
- **`tsconfig.json`**: TypeScript compiler options
- **`eslint.config.js`**: Linting rules
- **`.prettierrc`**: Code formatting rules
- **`.env.example`**: Example environment variables

### Backend

- **`pyproject.toml`**: Project metadata, Ruff/Black/Pytest configuration
- **`requirements.txt`**: Production dependencies (pinned versions)
- **`requirements-dev.txt`**: Development dependencies (pytest, ruff, black)
- **`alembic.ini`**: Alembic migration tool configuration
- **`pytest.ini`**: Pytest configuration (coverage, markers)
- **`.env.example`**: Example environment variables

---

## Summary

This folder structure is designed for:

1. **Scalability**: Supports millions of frames and hundreds of concurrent users
2. **Maintainability**: Clear separation of concerns at every layer
3. **Testability**: Services, repositories, and pipelines are independently testable
4. **Developer Experience**: Intuitive organization, consistent naming, clear boundaries
5. **Team Collaboration**: Multiple developers can work on different features without conflicts

**Next Steps:**
- Approve folder structure
- Generate actual folder skeleton (empty files with comments)
- Begin M0 implementation (Foundation & Infrastructure)

---

**End of Folder Structure Documentation**
