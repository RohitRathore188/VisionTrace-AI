/**
 * OpenCLIP Embedding Types & Interfaces
 */

export interface CLIPEmbeddingProgress {
  video_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  total_items: number
  processed_items: number
  frame_embeddings_count: number
  object_embeddings_count: number
  progress_percent: number
  error_message?: string
  started_at?: string
  updated_at?: string
}

export interface TextEmbeddingRequest {
  query_text: string
}

export interface TextEmbeddingResponse {
  query_text: string
  model_name: string
  dimension: number
  embedding: number[]
}
