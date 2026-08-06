# Functional Requirements
## VisionTrace AI — Intelligent Video Search Platform

**Version:** 1.0  
**Date:** August 5, 2026  
**Status:** Draft — Awaiting Approval

---

## Notation

- **FR-XXX** — Functional Requirement identifier
- **Priority:** P0 = Must Have (v1.0) · P1 = Should Have (v1.0) · P2 = Nice to Have (future)
- **Actor:** The user role that triggers or benefits from the requirement

---

## 1. Authentication & User Management

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-001 | The system shall allow users to register with email and password | P0 | All |
| FR-002 | The system shall validate email format and enforce minimum password strength (8+ chars, 1 uppercase, 1 number) | P0 | All |
| FR-003 | The system shall authenticate users and return a JWT access token and refresh token upon successful login | P0 | All |
| FR-004 | The system shall refresh access tokens using a valid refresh token without requiring re-login | P0 | All |
| FR-005 | The system shall allow users to log out and invalidate their refresh token | P0 | All |
| FR-006 | The system shall enforce role-based access control with three roles: Admin, Analyst, Viewer | P0 | Admin |
| FR-007 | The system shall allow Admins to create, deactivate, and assign roles to user accounts | P0 | Admin |
| FR-008 | The system shall display the current user's name and role in the navigation header | P1 | All |
| FR-009 | The system shall allow users to update their own password | P1 | All |
| FR-010 | The system shall soft-delete user accounts (preserve audit trail) | P1 | Admin |

---

## 2. Video Upload & Management

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-011 | The system shall accept video uploads in MP4, AVI, MOV, and MKV formats | P0 | Analyst, Admin |
| FR-012 | The system shall reject video files exceeding 2 GB with a clear error message | P0 | Analyst, Admin |
| FR-013 | The system shall validate uploaded file MIME type and magic bytes to prevent spoofed uploads | P0 | Analyst, Admin |
| FR-014 | The system shall display a real-time upload progress bar during file transfer | P0 | Analyst, Admin |
| FR-015 | The system shall store the raw uploaded video file in Supabase Storage under the `videos` bucket | P0 | System |
| FR-016 | The system shall persist video metadata (filename, size, duration, uploader, upload time) to PostgreSQL | P0 | System |
| FR-017 | The system shall automatically trigger the AI processing pipeline immediately after a successful upload | P0 | System |
| FR-018 | The system shall track and display the processing status for each video: Uploaded → Processing → Ready → Error | P0 | All |
| FR-019 | The system shall display a video library page listing all uploaded videos with thumbnail, name, duration, status, and upload date | P0 | All |
| FR-020 | The system shall allow Analysts and Admins to delete a video and all its associated data (frames, detections, embeddings, index) | P1 | Analyst, Admin |
| FR-021 | The system shall allow users to add an optional title and description to a video at upload time | P1 | Analyst, Admin |
| FR-022 | The system shall support drag-and-drop video upload in addition to file picker selection | P1 | Analyst, Admin |
| FR-023 | The system shall display a processing error message and log when the AI pipeline fails | P0 | All |

---

## 3. AI Processing Pipeline

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-024 | The system shall extract video frames at a configurable rate (default: 1 frame per second) using OpenCV | P0 | System |
| FR-025 | The system shall store extracted frame images as JPEG files in Supabase Storage under the `frames` bucket | P0 | System |
| FR-026 | The system shall persist frame metadata (video_id, frame_number, timestamp_seconds, storage_path) to PostgreSQL | P0 | System |
| FR-027 | The system shall run YOLOv8 object detection on each extracted frame and record bounding boxes, class labels, and confidence scores | P0 | System |
| FR-028 | The system shall filter detections below a configurable confidence threshold (default: 0.4) | P0 | System |
| FR-029 | The system shall run ByteTrack multi-object tracking across the frame sequence and assign persistent track IDs to detections | P0 | System |
| FR-030 | The system shall crop each detected object region from its frame using the bounding box coordinates | P0 | System |
| FR-031 | The system shall generate a 512-dimensional L2-normalized OpenCLIP embedding for each cropped detection region | P0 | System |
| FR-032 | The system shall also generate a whole-frame embedding for frames where no detections are found, to preserve context | P1 | System |
| FR-033 | The system shall persist embedding metadata (frame_id, detection_id, faiss_vector_id) to PostgreSQL | P0 | System |
| FR-034 | The system shall build and serialize a per-video FAISS `IndexFlatIP` index from all generated embeddings | P0 | System |
| FR-035 | The system shall update the video's processing status in PostgreSQL after each pipeline step completes or fails | P0 | System |
| FR-036 | The system shall log the start time, end time, and outcome of each pipeline step to the `processing_jobs` table | P0 | System |
| FR-037 | The system shall notify the frontend via polling or WebSocket when a video's processing status changes to Ready or Error | P1 | System |

---

## 4. Image-Based Search

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-038 | The system shall allow users to upload a query image (JPEG, PNG, WebP) to perform a visual similarity search | P0 | Analyst, Viewer |
| FR-039 | The system shall accept query images up to 10 MB in size | P0 | Analyst, Viewer |
| FR-040 | The system shall generate a 512-dimensional L2-normalized OpenCLIP embedding for the uploaded query image | P0 | System |
| FR-041 | The system shall search the FAISS index of a selected video (or all videos) using the query embedding | P0 | System |
| FR-042 | The system shall return the top-K most similar frames ranked by cosine similarity score (default K=20, configurable up to 50) | P0 | System |
| FR-043 | The system shall persist the search session (query type, parameters, user, timestamp) to PostgreSQL | P0 | System |
| FR-044 | The system shall persist all search results (frame_id, similarity_score, rank) linked to the search session | P0 | System |
| FR-045 | The system shall allow users to select which video(s) to search against, or search across all ready videos | P1 | Analyst, Viewer |

---

## 5. Text-Based Search

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-046 | The system shall provide a text input field for natural language search queries | P0 | Analyst, Viewer |
| FR-047 | The system shall enforce a maximum query length of 512 characters | P0 | Analyst, Viewer |
| FR-048 | The system shall sanitize and strip potentially harmful input from text queries | P0 | System |
| FR-049 | The system shall encode the text query into a 512-dimensional L2-normalized OpenCLIP text embedding | P0 | System |
| FR-050 | The system shall search the FAISS index using the text embedding and return top-K results | P0 | System |
| FR-051 | The system shall display text search results in the same result format as image search results | P0 | Analyst, Viewer |
| FR-052 | The system shall provide example query suggestions to help users construct effective text queries | P2 | Analyst, Viewer |

---

## 6. Search Results Display

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-053 | The system shall display search results as a responsive grid of result cards | P0 | All |
| FR-054 | Each result card shall display: frame thumbnail, video name, timestamp (HH:MM:SS), similarity score, and detected object labels | P0 | All |
| FR-055 | The system shall display similarity scores as a percentage (0–100%) and as a color-coded badge (green ≥ 75%, yellow 50–74%, red < 50%) | P0 | All |
| FR-056 | The system shall display a prominent disclaimer on all result pages: "These are similarity matches for human review. This system does not confirm identity." | P0 | All |
| FR-057 | The system shall allow users to sort results by similarity score (default), timestamp, or video name | P1 | All |
| FR-058 | The system shall allow users to filter results by minimum similarity score threshold | P1 | All |
| FR-059 | The system shall allow users to switch between grid view and list view for results | P1 | All |
| FR-060 | The system shall support pagination or infinite scroll for large result sets | P1 | All |
| FR-061 | The system shall show the total count of results returned for a query | P0 | All |
| FR-062 | The system shall display a bounding box overlay on the result thumbnail indicating the matched detection region | P1 | All |

---

## 7. Video Playback & Timestamp Navigation

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-063 | The system shall provide an in-browser video player for uploaded videos | P0 | All |
| FR-064 | The system shall allow users to click a result card to open the video player and seek directly to the result's timestamp | P0 | All |
| FR-065 | The system shall highlight the selected result in the results panel while the video is playing at that timestamp | P1 | All |
| FR-066 | The system shall support standard video playback controls: play, pause, seek, volume, fullscreen | P0 | All |
| FR-067 | The system shall display the current playback timestamp in HH:MM:SS format | P0 | All |
| FR-068 | The system shall display a timeline markers overlay on the video scrubber indicating all result timestamps | P1 | All |
| FR-069 | The system shall stream video from Supabase Storage using signed URLs with short expiry times | P0 | System |

---

## 8. Report Generation

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-070 | The system shall allow users to export search results as a CSV file | P0 | Analyst, Admin |
| FR-071 | The CSV export shall include: rank, video name, timestamp, similarity score, detected object labels, and frame storage URL | P0 | Analyst, Admin |
| FR-072 | The system shall allow users to export search results as a PDF report | P1 | Analyst, Admin |
| FR-073 | The PDF report shall include: report title, generation date/time, user name, query details, and a table of results with thumbnails | P1 | Analyst, Admin |
| FR-074 | The system shall include the AI disclaimer in all exported reports | P0 | System |
| FR-075 | The system shall allow users to name the report before exporting | P1 | Analyst, Admin |

---

## 9. Search History

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-076 | The system shall maintain a history of all searches performed by the current user | P1 | All |
| FR-077 | The system shall display the search history list with: query type (image/text), query preview, date/time, and result count | P1 | All |
| FR-078 | The system shall allow users to re-open a previous search and view its saved results | P1 | All |
| FR-079 | The system shall allow users to delete individual search history entries | P1 | All |

---

## 10. Admin Dashboard

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-080 | The system shall provide an Admin-only dashboard showing: total videos, total searches, active users, and system processing queue depth | P1 | Admin |
| FR-081 | The system shall display pipeline job statuses for all videos in the Admin dashboard | P1 | Admin |
| FR-082 | The system shall allow Admins to requeue a failed processing job | P1 | Admin |
| FR-083 | The system shall allow Admins to configure system-wide settings: frame extraction FPS, YOLO confidence threshold, top-K default | P2 | Admin |
