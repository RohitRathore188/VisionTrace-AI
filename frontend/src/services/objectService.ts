/**
 * YOLO Object Detection API Service
 */

import { api } from '@/lib/api'
import {
  YOLODetectionProgress,
  ObjectListResponse,
  DetectedObject,
} from '@/types/object_detection'

export class ObjectService {
  /**
   * Trigger YOLO object detection on video keyframes
   */
  static async triggerDetection(
    videoId: string,
    confidenceThreshold = 0.25,
    targetClasses?: string[]
  ): Promise<YOLODetectionProgress> {
    const response = await api.post<YOLODetectionProgress>(`/videos/${videoId}/detect-objects`, {
      confidence_threshold: confidenceThreshold,
      target_classes: targetClasses,
    })
    return response.data
  }

  /**
   * Poll object detection status
   */
  static async getDetectionStatus(videoId: string): Promise<YOLODetectionProgress> {
    const response = await api.get<YOLODetectionProgress>(`/videos/${videoId}/objects/status`)
    return response.data
  }

  /**
   * List detected objects for a video with optional class label and min confidence filter
   */
  static async getDetectedObjects(
    videoId: string,
    page = 1,
    pageSize = 50,
    label?: string,
    minConfidence?: number
  ): Promise<ObjectListResponse> {
    const params: Record<string, any> = { page, page_size: pageSize }
    if (label) params.label = label
    if (minConfidence) params.min_confidence = minConfidence

    const response = await api.get<ObjectListResponse>(`/videos/${videoId}/objects`, { params })
    return response.data
  }

  /**
   * List objects detected within a single keyframe
   */
  static async getFrameObjects(frameId: string): Promise<DetectedObject[]> {
    const response = await api.get<DetectedObject[]>(`/videos/frames/${frameId}/objects`)
    return response.data
  }
}
