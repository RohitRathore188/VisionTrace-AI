import React, { useState, useEffect } from 'react'
import { SecurityService, EvidenceItem } from '@/services/securityService'
import {
  Lock,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  ShieldCheck,
} from 'lucide-react'

export const EvidenceLibraryPage: React.FC = () => {
  const [evidence, setEvidence] = useState<EvidenceItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [verifyingId, setVerifyingId] = useState<string | null>(null)

  const fetchEvidence = async () => {
    try {
      const data = await SecurityService.getEvidence()
      setEvidence(data)
    } catch (err) {
      console.error('Failed to load evidence locker:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchEvidence()
  }, [])

  const handleVerify = async (item: EvidenceItem) => {
    setVerifyingId(item.id)
    try {
      const result = await SecurityService.verifyEvidence(item.id)
      setEvidence(
        evidence.map((e) => (e.id === item.id ? { ...e, integrity_status: result.integrity_status } : e))
      )
    } catch (err) {
      console.error('Evidence verification failed:', err)
    } finally {
      setVerifyingId(null)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-2">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <Lock className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-100 uppercase tracking-tight flex items-center space-x-2">
              <span>Forensic Evidence Locker (SHA-256 Integrity Verified)</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Cryptographically hashed video clips and keyframe evidence records with verification auditing
            </p>
          </div>
        </div>
      </div>

      {/* Evidence Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
        {isLoading ? (
          <div className="py-16 text-center text-xs text-slate-400">Loading forensic evidence items...</div>
        ) : evidence.length === 0 ? (
          <div className="py-16 text-center text-xs text-slate-500">No evidence items logged in locker.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 border-b border-slate-800 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="p-4">Evidence Tag</th>
                  <th className="p-4">Title & Source</th>
                  <th className="p-4">SHA-256 Hash</th>
                  <th className="p-4">File Size</th>
                  <th className="p-4">Timestamp</th>
                  <th className="p-4">Integrity Status</th>
                  <th className="p-4 text-right">Verification Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80 font-mono text-slate-300">
                {evidence.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-950/60 transition">
                    <td className="p-4 font-bold text-indigo-400">{item.evidence_id}</td>
                    <td className="p-4">
                      <div className="font-sans font-bold text-slate-100 text-xs">{item.title}</div>
                      <div className="text-[10px] text-slate-400 truncate max-w-xs">{item.file_path}</div>
                    </td>
                    <td className="p-4 text-[10px] text-purple-300 max-w-xs truncate" title={item.sha256_hash}>
                      {item.sha256_hash}
                    </td>
                    <td className="p-4 text-slate-400">{(item.file_size_bytes / 1024).toFixed(1)} KB</td>
                    <td className="p-4 text-slate-400">{item.timestamp_seconds}s</td>
                    <td className="p-4">
                      {item.integrity_status === 'verified' ? (
                        <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold px-2 py-0.5 rounded-md flex items-center space-x-1 w-fit">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>VERIFIED</span>
                        </span>
                      ) : (
                        <span className="bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[10px] font-bold px-2 py-0.5 rounded-md flex items-center space-x-1 w-fit">
                          <AlertTriangle className="w-3 h-3" />
                          <span>{item.integrity_status.toUpperCase()}</span>
                        </span>
                      )}
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => handleVerify(item)}
                        disabled={verifyingId === item.id}
                        className="px-3 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border border-indigo-500/30 text-xs font-sans font-bold transition flex items-center space-x-1.5 ml-auto"
                      >
                        {verifyingId === item.id ? (
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <ShieldCheck className="w-3.5 h-3.5" />
                        )}
                        <span>Re-Verify SHA-256</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
