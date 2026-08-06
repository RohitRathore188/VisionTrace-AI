# Non-Functional Requirements
## VisionTrace AI — Intelligent Video Search Platform

**Version:** 1.0  
**Date:** August 5, 2026  
**Status:** Draft — Awaiting Approval

---

## Notation

- **NFR-XXX** — Non-Functional Requirement identifier
- **Category** groups requirements by quality attribute
- **Measurement** defines the concrete acceptance criterion

---

## 1. Performance

| ID | Requirement | Measurement | Priority |
|---|---|---|---|
| NFR-001 | Search response time (image or text query) shall be fast enough for interactive use | End-to-end API response < 3 seconds at p95 under normal load | P0 |
| NFR-002 | Non-AI API endpoints (auth, video list, metadata) shall respond quickly | Response time < 200ms at p95 | P0 |
| NFR-003 | The AI processing pipeline shall complete frame extraction efficiently | ≥ 10 FPS equivalent extraction rate using OpenCV on CPU | P0 |
| NFR-004 | OpenCLIP embedding generation shall process crops in batches | ≥ 100 detection crops per minute on CPU; ≥ 500 on GPU | P1 |
| NFR-005 | FAISS vector search shall complete quickly regardless of index size | FAISS `IndexFlatIP` search < 100ms for indexes up to 100,000 vectors | P0 |
| NFR-006 | The frontend shall render initial content quickly | Largest Contentful Paint (LCP) < 2.5 seconds on a standard broadband connection | P1 |
| NFR-007 | The frontend shall remain interactive during background operations | No UI thread blocking > 50ms during search or upload | P1 |
| NFR-008 | Video file upload to Supabase Storage shall be efficient | Throughput limited only by client network bandwidth; no server-side throttling below 10 Mbps | P1 |

---

## 2. Scalability

| ID | Requirement | Measurement | Priority |
|---|---|---|---|
| NFR-009 | The API shall support concurrent users without degradation | Handle 50 concurrent users with < 10% increase in p95 response time | P0 |
| NFR-010 | The Celery worker pool shall be horizontally scalable | Adding worker replicas shall linearly increase pipeline throughput | P1 |
| NFR-011 | The FAISS index architecture shall support per-video isolation | Each video has its own FAISS index; no single monolithic index required | P0 |
| NFR-012 | The database connection pool shall handle peak load | SQLAlchemy pool_size=10, max_overflow=20; no connection exhaustion under 50 concurrent users | P0 |
| NFR-013 | The system shall support up to 10,000 videos in the video library without pagination or search degradation | Query response for video list < 500ms at 10,000 rows with proper indexing | P2 |

---

## 3. Reliability & Availability

| ID | Requirement | Measurement | Priority |
|---|---|---|---|
| NFR-014 | The platform shall maintain high availability | 99.5% monthly uptime (excludes scheduled maintenance windows) | P0 |
| NFR-015 | Failed AI pipeline jobs shall be recoverable | Celery shall retry failed tasks up to 3 times with exponential backoff before marking as Error | P0 |
| NFR-016 | Database writes shall be transactional | All multi-step database operations wrapped in SQLAlchemy transactions; no partial writes on failure | P0 |
| NFR-017 | Video files shall be durably stored | Supabase Storage provides 99.999% durability; no additional replication required for v1.0 | P0 |
| NFR-018 | FAISS index files shall be persisted to a durable volume | Railway persistent volume; index rebuilt from DB on catastrophic volume loss | P1 |
| NFR-019 | The system shall provide health check endpoints | `/health` (liveness) and `/readiness` (DB + Redis connectivity) endpoints return 200 within 1 second | P0 |

---

## 4. Security

| ID | Requirement | Measurement | Priority |
|---|---|---|---|
| NFR-020 | All data in transit shall be encrypted | HTTPS/TLS 1.2+ enforced on all API and frontend endpoints; HTTP redirected to HTTPS | P0 |
| NFR-021 | User passwords shall be stored securely | bcrypt hashing with cost factor ≥ 12; plaintext passwords never logged or stored | P0 |
| NFR-022 | JWT tokens shall have limited lifetimes | Access token: 15 minutes; Refresh token: 7 days | P0 |
| NFR-023 | The API shall protect against brute-force attacks | Rate limit: 5 failed login attempts per IP per 15 minutes trigger a 15-minute lockout | P0 |
| NFR-024 | The API shall enforce global rate limiting | 100 requests per minute per authenticated user; 20 per minute for unauthenticated | P0 |
| NFR-025 | File uploads shall be validated to prevent malicious uploads | MIME type validation + magic bytes check; reject non-video content regardless of extension | P0 |
| NFR-026 | SQL injection shall be prevented | All database queries use SQLAlchemy ORM parameterized statements; no raw string SQL | P0 |
| NFR-027 | Cross-origin requests shall be restricted | CORS policy allows only the registered frontend origin; wildcard `*` never used in production | P0 |
| NFR-028 | Secrets shall never appear in source code or logs | All secrets injected via environment variables; secret values redacted in structured logs | P0 |
| NFR-029 | User data access shall be scoped | Users can only access their own videos and search sessions; Admins can access all | P0 |
| NFR-030 | Uploaded video URLs shall not be publicly guessable | All Supabase Storage access via short-lived signed URLs (expiry ≤ 1 hour) | P0 |

---

## 5. Maintainability

| ID | Requirement | Measurement | Priority |
|---|---|---|---|
| NFR-031 | The codebase shall follow consistent style conventions | ESLint (frontend) and Ruff/Black (backend) enforced in CI; zero lint errors on merge to main | P0 |
| NFR-032 | The backend shall have meaningful test coverage | ≥ 70% line coverage on API routes and service layer via Pytest | P1 |
| NFR-033 | Database schema changes shall be managed through migrations | All schema changes via Alembic migration files; no manual DDL in production | P0 |
| NFR-034 | The system shall produce structured logs | All backend log entries in JSON format with: timestamp, level, request_id, user_id, message | P0 |
| NFR-035 | Third-party AI model versions shall be pinned | YOLO, OpenCLIP, and FAISS versions pinned in `requirements.txt`; no floating dependencies | P0 |
| NFR-036 | The frontend shall have meaningful component coverage | ≥ 60% coverage on critical UI components via Vitest + React Testing Library | P2 |

---

## 6. Usability & Accessibility

| ID | Requirement | Measurement | Priority |
|---|---|---|---|
| NFR-037 | The UI shall be responsive across screen sizes | Fully functional on viewport widths from 375px (mobile) to 1920px (desktop) | P0 |
| NFR-038 | The UI shall meet baseline web accessibility standards | WCAG 2.1 Level AA for all primary user flows; validated with automated tooling (axe-core) | P1 |
| NFR-039 | All interactive elements shall be keyboard navigable | Full keyboard navigation without mouse for: login, video list, search, results, video player | P1 |
| NFR-040 | Color shall not be the sole indicator of information | Similarity score badges use both color and text label (e.g., "High", "Medium", "Low") | P0 |
| NFR-041 | Error messages shall be human-readable | No raw error codes or stack traces exposed to end users; all errors map to user-friendly messages | P0 |
| NFR-042 | Loading states shall provide feedback | Skeleton loaders or spinners displayed for all async operations > 300ms | P0 |

---

## 7. Portability & Compatibility

| ID | Requirement | Measurement | Priority |
|---|---|---|---|
| NFR-043 | The backend shall be fully containerized | All backend services runnable via `docker compose up` with no host-level dependencies | P0 |
| NFR-044 | The AI pipeline shall run on CPU without GPU dependencies | All AI libraries (YOLO, OpenCLIP, FAISS) use CPU-only builds by default | P0 |
| NFR-045 | The backend shall be portable across cloud providers | No hard dependency on Railway-specific APIs; deployable on any Docker-compatible host | P1 |
| NFR-046 | The frontend shall work on modern browsers | Chrome 110+, Firefox 110+, Edge 110+, Safari 16+ without polyfills | P0 |

---

## 8. Ethical & Legal Compliance

| ID | Requirement | Measurement | Priority |
|---|---|---|---|
| NFR-047 | The system shall never claim to identify a person with certainty | All result pages, exports, and reports include the mandatory AI disclaimer; reviewed in QA | P0 |
| NFR-048 | The system shall not store biometric identifiers in v1.0 | No face embeddings or biometric templates generated or stored in v1.0 (InsightFace deferred) | P0 |
| NFR-049 | The system shall allow data deletion on request | Video deletion removes all associated frames, detections, embeddings, FAISS index, and storage files | P1 |
| NFR-050 | Audit trails shall be maintained | User actions (login, upload, delete, search, export) logged with user_id, timestamp, and action type | P1 |

---

## 9. Observability

| ID | Requirement | Measurement | Priority |
|---|---|---|---|
| NFR-051 | Every API request shall carry a traceable ID | `X-Request-ID` header injected by middleware; propagated through logs and Celery tasks | P0 |
| NFR-052 | Application errors shall be tracked | Sentry integration captures unhandled exceptions in both backend and frontend | P1 |
| NFR-053 | Celery task metrics shall be visible | Flower dashboard accessible at `/flower` (admin-only, authenticated) | P1 |
| NFR-054 | System metrics shall be collectable | Prometheus-compatible `/metrics` endpoint exposed on backend (future integration) | P2 |
