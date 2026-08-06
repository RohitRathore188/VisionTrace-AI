# API Planning
## VisionTrace AI — Intelligent Video Search Platform

**Version:** 1.0  
**Date:** August 5, 2026  
**Status:** Draft — Awaiting Approval

---

## Conventions

- **Base URL:** `https://api.visiontrace.ai/api/v1`
- **Protocol:** HTTPS only
- **Format:** JSON request and response bodies (except file uploads which use `multipart/form-data`)
- **Authentication:** `Authorization: Bearer <access_token>` header on all protected routes
- **Versioning:** URL path versioning (`/v1/`)
- **Errors:** Uniform error envelope on all 4xx/5xx responses
- **Request IDs:** Every request receives `X-Request-ID` header in the response
- **Rate Limiting:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers on all responses
- **Pagination:** Cursor-based using `limit` + `cursor` query params; response includes `next_cursor`

### Standard Error Envelope
```json
{
  "error": {
    "code": "VIDEO_NOT_FOUND",
    "message": "The requested video does not exist or you do not have access.",
    "request_id": "req_01j2k3..."
  }
}
```

### Standard Paginated Response Envelope
```json
{
  "data": [ ... ],
  "total": 142,
  "limit": 20,
  "next_cursor": "eyJpZCI6Ij..."
}
```

---

## Role Permissions Summary

| Role | Auth | Videos | Search | Admin |
|---|---|---|---|---|
| Unauthenticated | register, login | — | — | — |
| Viewer | all auth | read | search, history | — |
| Analyst | all auth | read + upload + delete own | search, history | — |
| Admin | all auth | read + upload + delete any | search, history | full |

---

## 1. Authentication — `/api/v1/auth`

---

### POST `/auth/register`
Register a new user account.

**Auth:** None  
**Rate Limit:** 10/hour per IP

**Request Body:**
```json
{
  "email": "analyst@example.com",
  "password": "SecurePass1",
  "confirm_password": "SecurePass1"
}
```

**Response `201 Created`:**
```json
{
  "message": "Registration successful. Please log in."
}
```

**Errors:** `400 VALIDATION_ERROR`, `409 EMAIL_ALREADY_EXISTS`

---

### POST `/auth/login`
Authenticate and receive tokens.

**Auth:** None  
**Rate Limit:** 20/hour per IP; lockout after 5 failures in 15 minutes

**Request Body:**
```json
{
  "email": "analyst@example.com",
  "password": "SecurePass1"
}
```

**Response `200 OK`:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "analyst@example.com",
    "role": "analyst",
    "created_at": "2026-08-01T10:00:00Z"
  }
}
```
> Refresh token set as `HttpOnly` cookie: `refresh_token`

**Errors:** `401 INVALID_CREDENTIALS`, `423 ACCOUNT_LOCKED`

---

### POST `/auth/refresh`
Exchange a refresh token for a new access token.

**Auth:** `refresh_token` HttpOnly cookie  
**Rate Limit:** 60/hour per user

**Response `200 OK`:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```
> Refresh token rotated — new `refresh_token` cookie set

**Errors:** `401 INVALID_REFRESH_TOKEN`, `401 REFRESH_TOKEN_EXPIRED`

---

### POST `/auth/logout`
Invalidate the current refresh token.

**Auth:** Bearer token  

**Response `204 No Content`**

---

## 2. Users — `/api/v1/users`

---

### GET `/users/me`
Get the current authenticated user's profile.

**Auth:** Bearer (all roles)

**Response `200 OK`:**
```json
{
  "id": "uuid",
  "email": "analyst@example.com",
  "role": "analyst",
  "is_active": true,
  "created_at": "2026-08-01T10:00:00Z",
  "updated_at": "2026-08-01T10:00:00Z"
}
```

---

### PUT `/users/me/password`
Change the current user's password.

**Auth:** Bearer (all roles)

**Request Body:**
```json
{
  "current_password": "OldPass1",
  "new_password": "NewSecure2",
  "confirm_new_password": "NewSecure2"
}
```

**Response `200 OK`:**
```json
{
  "message": "Password updated successfully."
}
```

**Errors:** `400 VALIDATION_ERROR`, `401 INCORRECT_CURRENT_PASSWORD`

---

## 3. Videos — `/api/v1/videos`

---

### POST `/videos/upload`
Upload a new video file and trigger the AI processing pipeline.

**Auth:** Bearer (Analyst, Admin)  
**Content-Type:** `multipart/form-data`  
**Rate Limit:** 10 uploads/hour per user

**Form Fields:**
| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | Video file (MP4, AVI, MOV, MKV; max 2 GB) |
| `title` | string | No | Display name (max 200 chars; defaults to filename) |
| `description` | string | No | Optional description (max 500 chars) |

**Response `202 Accepted`:**
```json
{
  "id": "uuid",
  "title": "Lobby Camera 2026-08-01",
  "filename": "lobby_cam.mp4",
  "size_bytes": 524288000,
  "status": "uploaded",
  "created_at": "2026-08-05T09:00:00Z"
}
```

**Errors:** `400 INVALID_FILE_TYPE`, `400 FILE_TOO_LARGE`, `422 VALIDATION_ERROR`

---

### GET `/videos`
List all videos accessible to the current user.

**Auth:** Bearer (all roles)

**Query Params:**
| Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 20 | Results per page (max 100) |
| `cursor` | string | — | Pagination cursor |
| `status` | string | — | Filter by status: `uploaded`, `processing`, `ready`, `error` |
| `sort` | string | `created_at_desc` | `created_at_desc`, `created_at_asc`, `title_asc` |
| `q` | string | — | Filter by title (partial match) |

**Response `200 OK`:**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Lobby Camera 2026-08-01",
      "filename": "lobby_cam.mp4",
      "size_bytes": 524288000,
      "duration_seconds": 3600,
      "status": "ready",
      "thumbnail_url": "https://...",
      "uploaded_by": "uuid",
      "created_at": "2026-08-05T09:00:00Z"
    }
  ],
  "total": 42,
  "limit": 20,
  "next_cursor": "eyJ..."
}
```

---

### GET `/videos/{video_id}`
Get a single video with full metadata and current job status.

**Auth:** Bearer (all roles)

**Response `200 OK`:**
```json
{
  "id": "uuid",
  "title": "Lobby Camera 2026-08-01",
  "filename": "lobby_cam.mp4",
  "size_bytes": 524288000,
  "duration_seconds": 3600,
  "status": "ready",
  "thumbnail_url": "https://...",
  "uploaded_by": "uuid",
  "created_at": "2026-08-05T09:00:00Z",
  "job": {
    "id": "uuid",
    "current_step": "complete",
    "steps": {
      "frame_extraction": "complete",
      "object_detection": "complete",
      "object_tracking": "complete",
      "embedding_generation": "complete",
      "index_building": "complete"
    },
    "error_message": null,
    "started_at": "2026-08-05T09:01:00Z",
    "completed_at": "2026-08-05T09:08:43Z"
  }
}
```

**Errors:** `404 VIDEO_NOT_FOUND`

---

### DELETE `/videos/{video_id}`
Delete a video and all associated data.

**Auth:** Bearer (Analyst — own videos only; Admin — any)

**Response `204 No Content`**

**Errors:** `403 FORBIDDEN`, `404 VIDEO_NOT_FOUND`

---

### GET `/videos/{video_id}/stream-url`
Get a short-lived signed URL for streaming the video.

**Auth:** Bearer (all roles)

**Response `200 OK`:**
```json
{
  "url": "https://storage.supabase.co/...?token=...&expires=...",
  "expires_at": "2026-08-05T10:00:00Z"
}
```

**Errors:** `404 VIDEO_NOT_FOUND`, `422 VIDEO_NOT_READY`

---

### GET `/videos/{video_id}/job-status`
Get the current processing job status for a video (used for polling).

**Auth:** Bearer (all roles)

**Response `200 OK`:**
```json
{
  "video_id": "uuid",
  "status": "processing",
  "current_step": "object_detection",
  "steps": {
    "frame_extraction": "complete",
    "object_detection": "in_progress",
    "object_tracking": "pending",
    "embedding_generation": "pending",
    "index_building": "pending"
  },
  "progress_pct": 35,
  "error_message": null
}
```

---

## 4. Search — `/api/v1/search`

---

### POST `/search/image`
Perform a visual similarity search using an uploaded query image.

**Auth:** Bearer (Analyst, Viewer)  
**Content-Type:** `multipart/form-data`  
**Rate Limit:** 30/minute per user

**Form Fields:**
| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | Query image (JPEG, PNG, WebP; max 10 MB) |
| `video_ids` | string | No | Comma-separated video UUIDs to search (omit for all ready videos) |
| `top_k` | int | No | Number of results: 10, 20, or 50 (default: 20) |

**Response `200 OK`:**
```json
{
  "session_id": "uuid",
  "query_type": "image",
  "total_results": 20,
  "search_time_ms": 1240,
  "results": [
    {
      "rank": 1,
      "video_id": "uuid",
      "video_title": "Lobby Camera 2026-08-01",
      "frame_id": "uuid",
      "timestamp_seconds": 142.0,
      "timestamp_display": "00:02:22",
      "similarity_score": 0.891,
      "similarity_pct": 89,
      "confidence_band": "high",
      "thumbnail_url": "https://...",
      "bbox": {
        "x": 120,
        "y": 45,
        "width": 180,
        "height": 320
      },
      "detected_labels": ["person"]
    }
  ],
  "disclaimer": "These results are AI-generated similarity matches presented for human review. VisionTrace AI does not confirm the identity of any individual."
}
```

**Errors:** `400 INVALID_FILE_TYPE`, `400 FILE_TOO_LARGE`, `422 NO_READY_VIDEOS`

---

### POST `/search/text`
Perform a semantic similarity search using a natural language text query.

**Auth:** Bearer (Analyst, Viewer)  
**Content-Type:** `application/json`  
**Rate Limit:** 30/minute per user

**Request Body:**
```json
{
  "query": "person wearing a red jacket near the entrance",
  "video_ids": ["uuid1", "uuid2"],
  "top_k": 20
}
```

**Response `200 OK`:** Same structure as `POST /search/image` with `"query_type": "text"` and `"query_text"` field added.

**Errors:** `400 EMPTY_QUERY`, `400 QUERY_TOO_LONG`, `422 NO_READY_VIDEOS`

---

## 5. Search Sessions & Results — `/api/v1/search/sessions`

---

### GET `/search/sessions`
List all search sessions for the current user.

**Auth:** Bearer (all roles)

**Query Params:**
| Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 20 | Results per page (max 100) |
| `cursor` | string | — | Pagination cursor |
| `query_type` | string | — | Filter: `image` or `text` |

**Response `200 OK`:**
```json
{
  "data": [
    {
      "session_id": "uuid",
      "query_type": "image",
      "query_preview": "query_image.jpg",
      "top_k": 20,
      "result_count": 20,
      "searched_video_count": 3,
      "created_at": "2026-08-05T09:30:00Z"
    }
  ],
  "total": 15,
  "limit": 20,
  "next_cursor": null
}
```

---

### GET `/search/sessions/{session_id}/results`
Retrieve the saved results for a specific search session.

**Auth:** Bearer (all roles — own sessions only)

**Query Params:**
| Param | Type | Default | Description |
|---|---|---|---|
| `min_score` | float | 0.0 | Minimum similarity score filter (0.0–1.0) |
| `sort` | string | `score_desc` | `score_desc`, `timestamp_asc`, `video_title_asc` |

**Response `200 OK`:**
```json
{
  "session_id": "uuid",
  "query_type": "text",
  "query_text": "person wearing a red jacket near the entrance",
  "created_at": "2026-08-05T09:30:00Z",
  "total_results": 18,
  "results": [ ... ],
  "disclaimer": "These results are AI-generated similarity matches presented for human review. VisionTrace AI does not confirm the identity of any individual."
}
```

**Errors:** `403 FORBIDDEN`, `404 SESSION_NOT_FOUND`

---

### GET `/search/sessions/{session_id}/export`
Get structured export payload for client-side PDF/CSV generation.

**Auth:** Bearer (Analyst, Admin)

**Response `200 OK`:**
```json
{
  "session_id": "uuid",
  "generated_at": "2026-08-05T10:00:00Z",
  "generated_by": "analyst@example.com",
  "query_type": "text",
  "query_text": "person wearing a red jacket",
  "disclaimer": "...",
  "results": [
    {
      "rank": 1,
      "video_title": "Lobby Camera",
      "timestamp_seconds": 142.0,
      "timestamp_display": "00:02:22",
      "similarity_pct": 89,
      "confidence_band": "high",
      "detected_labels": ["person"],
      "thumbnail_signed_url": "https://...",
      "bbox": { "x": 120, "y": 45, "width": 180, "height": 320 }
    }
  ]
}
```

**Errors:** `403 FORBIDDEN`, `404 SESSION_NOT_FOUND`

---

### DELETE `/search/sessions/{session_id}`
Delete a search session and its results.

**Auth:** Bearer (all roles — own sessions only)

**Response `204 No Content`**

**Errors:** `403 FORBIDDEN`, `404 SESSION_NOT_FOUND`

---

## 6. Admin — `/api/v1/admin`

> All routes require Admin role. Non-admins receive `403 FORBIDDEN`.

---

### GET `/admin/metrics`
Get system-wide activity metrics.

**Auth:** Bearer (Admin)

**Response `200 OK`:**
```json
{
  "total_videos": 142,
  "total_searches_today": 38,
  "active_users_today": 12,
  "pipeline_queue_depth": 3,
  "videos_by_status": {
    "uploaded": 2,
    "processing": 3,
    "ready": 135,
    "error": 2
  },
  "generated_at": "2026-08-05T10:05:00Z"
}
```

---

### GET `/admin/jobs`
List all pipeline processing jobs across all users.

**Auth:** Bearer (Admin)

**Query Params:** `limit`, `cursor`, `status` (filter), `video_id` (filter)

**Response `200 OK`:**
```json
{
  "data": [
    {
      "job_id": "uuid",
      "video_id": "uuid",
      "video_title": "Lobby Camera",
      "status": "error",
      "current_step": "embedding_generation",
      "attempt_count": 3,
      "error_message": "CUDA out of memory",
      "started_at": "2026-08-05T08:00:00Z",
      "updated_at": "2026-08-05T08:14:22Z"
    }
  ],
  "total": 10,
  "limit": 20,
  "next_cursor": null
}
```

---

### POST `/admin/jobs/{job_id}/retry`
Requeue a failed pipeline job.

**Auth:** Bearer (Admin)

**Response `202 Accepted`:**
```json
{
  "job_id": "uuid",
  "video_id": "uuid",
  "status": "processing",
  "message": "Job requeued successfully."
}
```

**Errors:** `404 JOB_NOT_FOUND`, `422 JOB_NOT_IN_ERROR_STATE`

---

### GET `/admin/users`
List all user accounts.

**Auth:** Bearer (Admin)

**Query Params:** `limit`, `cursor`, `role` (filter), `is_active` (filter), `q` (search by email)

**Response `200 OK`:**
```json
{
  "data": [
    {
      "id": "uuid",
      "email": "analyst@example.com",
      "role": "analyst",
      "is_active": true,
      "created_at": "2026-08-01T10:00:00Z",
      "last_login_at": "2026-08-05T09:00:00Z"
    }
  ],
  "total": 24,
  "limit": 20,
  "next_cursor": null
}
```

---

### POST `/admin/users`
Create a new user account with a temporary password.

**Auth:** Bearer (Admin)

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "role": "analyst",
  "temporary_password": "TempPass99"
}
```

**Response `201 Created`:**
```json
{
  "id": "uuid",
  "email": "newuser@example.com",
  "role": "analyst",
  "is_active": true,
  "created_at": "2026-08-05T10:00:00Z"
}
```

**Errors:** `409 EMAIL_ALREADY_EXISTS`, `400 VALIDATION_ERROR`

---

### PUT `/admin/users/{user_id}`
Update a user's role or active status.

**Auth:** Bearer (Admin)

**Request Body:**
```json
{
  "role": "viewer",
  "is_active": false
}
```

**Response `200 OK`:** Updated user object (same schema as GET `/admin/users` data item)

**Errors:** `404 USER_NOT_FOUND`, `422 CANNOT_DEACTIVATE_SELF`

---

## 7. System — `/api/v1/system`

---

### GET `/system/health`
Liveness check — confirms the API process is running.

**Auth:** None

**Response `200 OK`:**
```json
{
  "status": "ok",
  "timestamp": "2026-08-05T10:00:00Z"
}
```

---

### GET `/system/readiness`
Readiness check — confirms DB and Redis are reachable.

**Auth:** None

**Response `200 OK`:**
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok"
  },
  "timestamp": "2026-08-05T10:00:00Z"
}
```

**Response `503 Service Unavailable`:**
```json
{
  "status": "not_ready",
  "checks": {
    "database": "ok",
    "redis": "error"
  }
}
```

---

## 8. Complete Endpoint Index

| Method | Path | Auth | Milestone |
|---|---|---|---|
| POST | `/auth/register` | None | M1 |
| POST | `/auth/login` | None | M1 |
| POST | `/auth/refresh` | Cookie | M1 |
| POST | `/auth/logout` | Bearer | M1 |
| GET | `/users/me` | Bearer | M1 |
| PUT | `/users/me/password` | Bearer | M1 |
| POST | `/videos/upload` | Bearer | M1 |
| GET | `/videos` | Bearer | M1 |
| GET | `/videos/{id}` | Bearer | M1 |
| DELETE | `/videos/{id}` | Bearer | M1 |
| GET | `/videos/{id}/stream-url` | Bearer | M4 |
| GET | `/videos/{id}/job-status` | Bearer | M2 |
| POST | `/search/image` | Bearer | M3 |
| POST | `/search/text` | Bearer | M3 |
| GET | `/search/sessions` | Bearer | M3 |
| GET | `/search/sessions/{id}/results` | Bearer | M3 |
| GET | `/search/sessions/{id}/export` | Bearer | M4 |
| DELETE | `/search/sessions/{id}` | Bearer | M3 |
| GET | `/admin/metrics` | Bearer (Admin) | M5 |
| GET | `/admin/jobs` | Bearer (Admin) | M5 |
| POST | `/admin/jobs/{id}/retry` | Bearer (Admin) | M5 |
| GET | `/admin/users` | Bearer (Admin) | M5 |
| POST | `/admin/users` | Bearer (Admin) | M5 |
| PUT | `/admin/users/{id}` | Bearer (Admin) | M5 |
| GET | `/system/health` | None | M0 |
| GET | `/system/readiness` | None | M0 |

---

## 9. WebSocket Events (Optional — M3 Enhancement)

If polling is replaced or supplemented with WebSocket push:

**Connection:** `wss://api.visiontrace.ai/ws?token=<access_token>`

| Event | Direction | Payload |
|---|---|---|
| `video.status_changed` | Server → Client | `{ video_id, status, current_step, progress_pct }` |
| `pipeline.step_complete` | Server → Client | `{ video_id, step, completed_at }` |
| `pipeline.error` | Server → Client | `{ video_id, step, error_message }` |

---

## 10. HTTP Status Code Usage

| Code | Usage |
|---|---|
| 200 | Successful GET, PUT |
| 201 | Successful POST creating a resource |
| 202 | Accepted (async operation triggered, e.g., upload, retry) |
| 204 | Successful DELETE (no body) |
| 400 | Bad request — client validation error |
| 401 | Unauthenticated — missing or invalid token |
| 403 | Forbidden — authenticated but insufficient role |
| 404 | Resource not found |
| 409 | Conflict — duplicate resource |
| 422 | Unprocessable — request is valid but business logic prevents it |
| 423 | Locked — account locked after too many failed attempts |
| 429 | Too many requests — rate limit exceeded |
| 500 | Internal server error — unexpected failure |
| 503 | Service unavailable — dependency (DB/Redis) unreachable |
