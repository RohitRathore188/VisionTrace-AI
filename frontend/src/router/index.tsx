import { Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { DashboardPage } from '@/pages/DashboardPage'
import { UploadPage } from '@/pages/UploadPage'
import { SearchPage } from '@/pages/SearchPage'
import { VideosPage } from '@/pages/VideosPage'
import { HistoryPage } from '@/pages/HistoryPage'
import { SettingsPage } from '@/pages/SettingsPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { AdminPage } from '@/pages/AdminPage'
import { LoginPage } from '@/pages/auth/LoginPage'
import { SignupPage } from '@/pages/auth/SignupPage'
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage'
import { ProtectedRoute } from '@/components/auth'
import { RequireAdmin } from '@/components/auth'

import { CaseManagementPage } from '@/pages/CaseManagementPage'
import { EvidenceLibraryPage } from '@/pages/EvidenceLibraryPage'
import { AlertCenterPage } from '@/pages/AlertCenterPage'
import { LiveMonitoringPage } from '@/pages/LiveMonitoringPage'
import { AuditLogsPage } from '@/pages/AuditLogsPage'
import { SystemHealthPage } from '@/pages/SystemHealthPage'
import { PersonSearchPage } from '@/pages/PersonSearchPage'
import { VehicleSearchPage } from '@/pages/VehicleSearchPage'

export function AppRoutes() {
  return (
    <Routes>
      {/* Root redirect to dashboard */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Authentication routes */}
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/signup" element={<SignupPage />} />
      <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />

      {/* Main app routes with layout and protection */}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/command-center" element={<DashboardPage />} />
        <Route path="/monitoring" element={<LiveMonitoringPage />} />
        <Route path="/videos" element={<VideosPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/investigate" element={<SearchPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/cases" element={<CaseManagementPage />} />
        <Route path="/alerts" element={<AlertCenterPage />} />

        {/* Intelligence Routes */}
        <Route path="/intelligence/person" element={<PersonSearchPage />} />
        <Route path="/intelligence/vehicle" element={<VehicleSearchPage />} />
        <Route path="/intelligence/objects" element={<SearchPage />} />
        <Route path="/intelligence/tracking" element={<SearchPage />} />
        <Route path="/analytics" element={<DashboardPage />} />

        {/* Evidence & System Routes */}
        <Route path="/evidence-locker" element={<EvidenceLibraryPage />} />
        <Route path="/reports" element={<CaseManagementPage />} />
        <Route path="/export-center" element={<EvidenceLibraryPage />} />
        <Route path="/audit-logs" element={<AuditLogsPage />} />
        <Route path="/system-health" element={<SystemHealthPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/settings" element={<SettingsPage />} />

        <Route
          path="/admin"
          element={
            <RequireAdmin>
              <AdminPage />
            </RequireAdmin>
          }
        />
      </Route>

      {/* Error pages */}
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  AUTH_LOGIN: '/auth/login',
  AUTH_SIGNUP: '/auth/signup',
  AUTH_FORGOT_PASSWORD: '/auth/forgot-password',
  VIDEOS: '/videos',
  UPLOAD: '/upload',
  SEARCH: '/search',
  RESULTS: '/results/:sessionId',
  HISTORY: '/history',
  ADMIN: '/admin',
  NOT_FOUND: '/404',
} as const
