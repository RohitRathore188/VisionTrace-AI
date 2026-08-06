# User Stories
## VisionTrace AI — Intelligent Video Search Platform

**Version:** 1.0  
**Date:** August 5, 2026  
**Status:** Draft — Awaiting Approval

---

## Roles

| Role | Description |
|---|---|
| **Analyst** | Primary operator — uploads videos, performs searches, generates reports |
| **Viewer** | Read-only access — views videos, runs searches, cannot upload or delete |
| **Admin** | Full access — manages users, videos, system settings, and pipeline jobs |
| **System** | Automated backend process (not a human actor) |

---

## Epic 1 — Authentication & Account Management

### US-001 · Register an account
**As a** new user,  
**I want to** register with my email and a secure password,  
**So that** I can access the VisionTrace AI platform.

**Acceptance Criteria:**
- Registration form requires: email, password, confirm password
- Password must be ≥ 8 characters, contain 1 uppercase letter and 1 number
- Duplicate email returns a clear validation error
- Successful registration redirects to the login page with a success message

---

### US-002 · Log in
**As a** registered user,  
**I want to** log in with my email and password,  
**So that** I can access my dashboard and tools.

**Acceptance Criteria:**
- Login form accepts email and password
- Successful login returns a JWT and navigates to the dashboard
- Failed login shows "Invalid email or password" (no differentiation between the two)
- After 5 consecutive failures, account is locked for 15 minutes with a clear message

---

### US-003 · Stay logged in
**As a** returning user,  
**I want** my session to persist across browser refreshes,  
**So that** I don't have to log in repeatedly during a work session.

**Acceptance Criteria:**
- Access token stored securely (httpOnly cookie or memory); refresh token used to renew silently
- Expired access token is automatically refreshed without user interaction
- After 7 days of inactivity the session expires and user is redirected to login

---

### US-004 · Log out
**As a** logged-in user,  
**I want to** log out securely,  
**So that** my session is terminated on shared or public devices.

**Acceptance Criteria:**
- Logout button visible in the navigation header
- Clicking logout clears all tokens and redirects to the login page
- Subsequent requests with the old token are rejected (refresh token invalidated)

---

### US-005 · Change my password
**As a** logged-in user,  
**I want to** change my password from my account settings,  
**So that** I can maintain account security.

**Acceptance Criteria:**
- Requires current password + new password + confirm new password
- New password must meet the same strength requirements as registration
- Success shows a confirmation message; failure shows a specific error

---

### US-006 · Manage users (Admin)
**As an** Admin,  
**I want to** create, deactivate, and assign roles to user accounts,  
**So that** I can control who has access to the system and at what level.

**Acceptance Criteria:**
- Admin user management table lists: email, role, status, created date
- Admin can create a new user with a temporary password
- Admin can change a user's role (Analyst / Viewer)
- Admin can deactivate an account (user cannot log in; data preserved)
- Deactivated accounts are visually distinct in the table

---

## Epic 2 — Video Upload & Management

### US-007 · Upload a video
**As an** Analyst,  
**I want to** upload a video file from my device,  
**So that** it can be processed and made searchable.

**Acceptance Criteria:**
- Upload accepts MP4, AVI, MOV, MKV formats
- Files over 2 GB are rejected before upload starts, with a clear size error
- Drag-and-drop and file picker both work
- Upload progress bar is visible during transfer
- After upload, the video appears in the library with status "Processing"

---

### US-008 · Add metadata to an upload
**As an** Analyst,  
**I want to** give my uploaded video a title and optional description,  
**So that** I can identify it easily in the library.

**Acceptance Criteria:**
- Title field is optional at upload (defaults to filename if empty)
- Description field is optional, max 500 characters
- Title and description appear on the video card in the library

---

### US-009 · Monitor processing status
**As an** Analyst,  
**I want to** see the real-time status of a video being processed,  
**So that** I know when it's ready to search.

**Acceptance Criteria:**
- Status badge on video card shows: Uploaded → Processing → Ready → Error
- Status updates without requiring a manual page refresh (polling or WebSocket)
- "Processing" state shows which pipeline step is in progress (e.g., "Extracting frames…")
- "Error" state shows a human-readable error message and an option to contact Admin

---

### US-010 · Browse my video library
**As a** user,  
**I want to** see all uploaded videos in a library view,  
**So that** I can find and select the right video for my search.

**Acceptance Criteria:**
- Library displays videos as cards with: thumbnail, title, duration, upload date, status badge
- Library is paginated or supports infinite scroll (> 20 videos)
- Library supports sorting by upload date (newest first default) and title
- Library supports text search/filter by video title

---

### US-011 · Delete a video
**As an** Analyst,  
**I want to** delete a video and all its associated data,  
**So that** I can manage storage and remove unnecessary files.

**Acceptance Criteria:**
- Delete action requires a confirmation dialog ("Are you sure? This cannot be undone.")
- Deletion removes: video file from storage, frames, detections, embeddings, FAISS index, and DB records
- Deleted video disappears from the library immediately
- Viewers cannot delete videos; button is hidden for Viewer role

---

## Epic 3 — Image-Based Search

### US-012 · Search by uploading an image
**As an** Analyst,  
**I want to** upload a photo of a person or object and search for similar appearances in a video,  
**So that** I can locate matching frames quickly without watching the entire footage.

**Acceptance Criteria:**
- Image upload accepts JPEG, PNG, WebP up to 10 MB
- User can select which video(s) to search or choose "All Videos"
- Query executes within 3 seconds and displays ranked results
- Results show: thumbnail, video name, timestamp, similarity score badge
- Mandatory disclaimer is visible above the results: "Similarity matches only — not confirmed identifications"

---

### US-013 · Adjust the number of results
**As an** Analyst,  
**I want to** control how many results are returned for my search,  
**So that** I can broaden or narrow my review based on the investigation's needs.

**Acceptance Criteria:**
- Top-K selector allows values: 10, 20, 50 (default: 20)
- Changing Top-K and re-running search refreshes results immediately
- Selected Top-K value is preserved across image and text searches within the session

---

## Epic 4 — Text-Based Search

### US-014 · Search using a natural language description
**As an** Analyst,  
**I want to** type a description like "person in a blue hoodie carrying a bag" and find matching frames,  
**So that** I can search when I don't have a reference image.

**Acceptance Criteria:**
- Text input field is prominently placed on the search page
- Query is limited to 512 characters with a visible character counter
- Results are displayed in the same format as image search results
- Empty query submission is blocked with a validation message

---

### US-015 · Use query suggestions
**As a** new user,  
**I want to** see example search queries,  
**So that** I understand how to write effective text descriptions.

**Acceptance Criteria:**
- 5–8 example queries displayed below or near the text input (e.g., "person wearing red jacket", "black backpack near entrance")
- Clicking a suggestion populates the text field with that query
- Suggestions are dismissible

---

## Epic 5 — Search Results & Navigation

### US-016 · View and interpret search results
**As a** user,  
**I want to** see clearly presented search results with scores and timestamps,  
**So that** I can quickly assess which matches are most relevant.

**Acceptance Criteria:**
- Results displayed in a responsive card grid (default) or list view
- Each card shows: thumbnail, video name, timestamp (HH:MM:SS), similarity score with color badge
- Color coding: green = High (≥75%), yellow = Medium (50–74%), red = Low (<50%)
- Total result count displayed ("Showing 20 of 47 matches")
- Results sorted by similarity score descending by default

---

### US-017 · Filter and sort results
**As an** Analyst,  
**I want to** filter results by a minimum similarity score and sort them in different ways,  
**So that** I can focus on the most relevant matches.

**Acceptance Criteria:**
- Minimum score filter slider (0–100%) filters results in real time
- Sort options: Similarity (default), Timestamp, Video Name
- Applied filters and sort order are clearly indicated in the UI
- Filters reset when a new search is started

---

### US-018 · Jump to a video timestamp
**As a** user,  
**I want to** click a result and have the video player seek to that exact moment,  
**So that** I can instantly review the original footage at the matched timestamp.

**Acceptance Criteria:**
- Clicking any result card opens the video player (inline panel or modal) and seeks to the result's timestamp
- Video pauses at that timestamp; user must press play to continue
- The selected result card is visually highlighted in the results list
- Player supports: play, pause, seek scrubber, volume control, fullscreen

---

### US-019 · See timestamp markers on the video timeline
**As a** user,  
**I want to** see all matching timestamps marked on the video scrubber,  
**So that** I can get an at-a-glance view of where matches appear in the footage.

**Acceptance Criteria:**
- Result timestamps rendered as small markers on the video seek bar
- Hovering a marker shows the similarity score in a tooltip
- Clicking a marker seeks the video to that timestamp

---

### US-020 · See bounding box on matched frame
**As an** Analyst,  
**I want to** see the exact region that matched my query highlighted in the thumbnail,  
**So that** I know which object or person in the frame triggered the match.

**Acceptance Criteria:**
- Bounding box overlay drawn on result thumbnail at the detection region coordinates
- Box is colored according to the similarity score band (green/yellow/red)
- Overlay is drawn without distorting the underlying thumbnail

---

## Epic 6 — Report Generation

### US-021 · Export results as CSV
**As an** Analyst,  
**I want to** download my search results as a CSV file,  
**So that** I can share findings with colleagues or import them into other tools.

**Acceptance Criteria:**
- "Export CSV" button visible in the results toolbar
- CSV columns: Rank, Video Name, Timestamp (seconds), Timestamp (HH:MM:SS), Similarity Score (%), Object Labels, Frame URL
- First row includes the AI disclaimer as a comment or header note
- File downloads immediately via browser download

---

### US-022 · Export results as a PDF report
**As an** Analyst,  
**I want to** generate a formatted PDF report of my search results,  
**So that** I can present findings in a professional, shareable document.

**Acceptance Criteria:**
- "Export PDF" button in the results toolbar
- PDF includes: report title, generation date/time, user name, query type, query details, results table with thumbnails and scores
- AI disclaimer printed prominently on the first page
- User can set a custom report title before generating
- PDF opens in a new browser tab or triggers a download

---

## Epic 7 — Search History

### US-023 · Review past searches
**As a** user,  
**I want to** see a history of my previous searches,  
**So that** I can revisit past investigations without re-running the query.

**Acceptance Criteria:**
- Search history page lists: query type icon (image/text), query preview, date/time, result count
- Clicking a history entry reopens the saved results view
- History is scoped to the current user (other users' history is not visible)

---

### US-024 · Delete a search history entry
**As a** user,  
**I want to** remove entries from my search history,  
**So that** I can keep my history clean and relevant.

**Acceptance Criteria:**
- Each history entry has a delete (trash) icon
- Deletion requires a single click (no confirmation needed for history entries)
- Deleted entry disappears immediately from the list
- Deleting history does not delete the video or its processing data

---

## Epic 8 — Admin Operations

### US-025 · View system dashboard
**As an** Admin,  
**I want to** see an overview of system health and activity,  
**So that** I can monitor usage and identify issues proactively.

**Acceptance Criteria:**
- Dashboard shows: total videos, total searches today, active users, pipeline queue depth
- Pipeline job table shows all jobs with status, video name, step, start time, and duration
- Dashboard data refreshes every 30 seconds or on manual refresh

---

### US-026 · Requeue a failed processing job
**As an** Admin,  
**I want to** retry a failed AI processing pipeline job,  
**So that** a video that failed due to a transient error can be made searchable.

**Acceptance Criteria:**
- Failed jobs have a "Retry" button in the Admin job table
- Clicking Retry resets the video status to "Processing" and re-enqueues the Celery task
- Retry history (attempt count) is visible on the job record

---

### US-027 · Ethical use — understand AI limitations
**As any** user,  
**I want to** be clearly informed that search results are similarity matches and not definitive identifications,  
**So that** I understand the limitations of the system and do not misuse its output.

**Acceptance Criteria:**
- Disclaimer displayed on every search results page, every export, and every report
- Disclaimer text: *"These results are AI-generated similarity matches presented for human review. VisionTrace AI does not confirm the identity of any individual."*
- Disclaimer cannot be hidden or disabled by any user role
- Disclaimer is included in all PDF and CSV exports
