/**
 * FAISS Search Types & Interfaces
 */

export interface TextSearchRequest {
  query_text: string
  top_k?: number
  video_id?: string
  video_ids?: string[]
  min_score?: number
}

export interface SearchResultItem {
  type: 'frame' | 'object'
  similarity_score: number
  vector_id?: number
  video_id: string
  video_title?: string
  camera_name?: string
  frame_id: string
  object_id?: string
  track_id?: number
  frame_number: number
  timestamp_seconds: number
  video_playback_url?: string
  image_url?: string
  crop_url?: string
  label?: string
  confidence?: number
  bounding_box?: {
    xmin: number
    ymin: number
    xmax: number
    ymax: number
  }
}

export interface SearchResponse {
  query_text: string
  total_matches: number
  execution_time_ms: number
  results: SearchResultItem[]
}
