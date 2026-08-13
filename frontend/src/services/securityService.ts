/**
 * Security Operations API Services
 * Handles Cameras, Incident Cases, Evidence Hashing, Security Alerts, and Audit Logs
 */

import { api } from '@/lib/api'

export interface CameraItem {
  id: string
  name: string
  location: string
  zone: string
  rtsp_url?: string
  status: 'online' | 'degraded' | 'offline' | 'maintenance'
  resolution: string
  fps: number
}

export interface CaseItem {
  id: string
  case_number: string
  title: string
  description?: string
  status: 'open' | 'investigating' | 'pending_review' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'critical'
  assigned_investigator_id?: string
  created_by_id: string
  notes_json: Array<{ timestamp: string; author: string; text: string }>
  created_at: string
  updated_at: string
}

export interface EvidenceItem {
  id: string
  evidence_id: string
  case_id?: string
  video_id?: string
  frame_id?: string
  title: string
  description?: string
  sha256_hash: string
  file_path: string
  file_size_bytes: number
  timestamp_seconds: number
  integrity_status: 'verified' | 'modified' | 'unknown'
  created_at: string
}

export interface AlertItem {
  id: string
  alert_id: string
  alert_type: string
  severity: 'critical' | 'warning' | 'info'
  status: 'new' | 'acknowledged' | 'resolved'
  camera_name: string
  timestamp_seconds: number
  detected_object_label?: string
  confidence?: number
  frame_image_url?: string
  created_at: string
}

export interface AuditLogItem {
  id: string
  user_email: string
  action: string
  resource_type: string
  resource_id?: string
  result_status: string
  ip_address?: string
  details_json: Record<string, any>
  created_at: string
}

export class SecurityService {
  // Camera Management
  static async getCameras(): Promise<CameraItem[]> {
    const res = await api.get<CameraItem[]>('/cameras')
    return res.data
  }

  // Incident Cases
  static async getCases(): Promise<CaseItem[]> {
    const res = await api.get<CaseItem[]>('/cases')
    return res.data
  }

  static async createCase(title: string, description?: string, priority = 'medium'): Promise<CaseItem> {
    const res = await api.post<CaseItem>('/cases', { title, description, priority })
    return res.data
  }

  static async addCaseNote(caseId: string, note: string): Promise<CaseItem> {
    const res = await api.post<CaseItem>(`/cases/${caseId}/notes`, { note })
    return res.data
  }

  // Evidence Locker
  static async getEvidence(): Promise<EvidenceItem[]> {
    const res = await api.get<EvidenceItem[]>('/evidence')
    return res.data
  }

  static async verifyEvidence(id: string): Promise<any> {
    const res = await api.post(`/evidence/${id}/verify`)
    return res.data
  }

  // Security Alerts
  static async getAlerts(): Promise<AlertItem[]> {
    const res = await api.get<AlertItem[]>('/alerts')
    return res.data
  }

  static async acknowledgeAlert(id: string): Promise<AlertItem> {
    const res = await api.post<AlertItem>(`/alerts/${id}/acknowledge`)
    return res.data
  }

  // Immutable Audit Logs
  static async getAuditLogs(): Promise<AuditLogItem[]> {
    const res = await api.get<AuditLogItem[]>('/audit-logs')
    return res.data
  }
}
