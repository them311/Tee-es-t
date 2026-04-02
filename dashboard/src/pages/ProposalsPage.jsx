import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { fetchProposals } from '../lib/supabase'
import { FileText, Copy, Check, ExternalLink } from 'lucide-react'

export default function ProposalsPage() {
  const [proposals, setProposals] = useState([])
  const [loading, setLoading] = useState(true)
  const [copiedId, setCopiedId] = useState(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const data = await fetchProposals({ limit: 50 })
        setProposals(data || [])
      } catch (e) {
        console.error(e)
      }
      setLoading(false)
    }
    load()
  }, [])

  function copyText(text, id) {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Propositions</h2>
        <p className="text-sm text-slate-500">{proposals.length} propositions générées par l'IA</p>
      </div>

      {loading && <div className="text-center py-12 text-sm text-slate-400">Chargement...</div>}

      <div className="grid gap-4">
        {proposals.map(p => {
          const mission = p.missions
          return (
            <div key={p.id} className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100 bg-slate-50/50">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center shrink-0">
                    <FileText className="w-4 h-4 text-purple-600" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-800 truncate">{mission?.title || 'Mission'}</p>
                    <p className="text-xs text-slate-400">{mission?.company || ''} — {mission?.source || ''} — Score {mission?.score || '?'}/100</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${p.status === 'ready' ? 'bg-green-100 text-green-700' : p.status === 'sent' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>
                    {p.status === 'ready' ? 'Prête' : p.status === 'sent' ? 'Envoyée' : p.status || 'Brouillon'}
                  </span>
                  <span className="text-xs text-slate-400">{p.language?.toUpperCase()}</span>
                </div>
              </div>
              {/* Body */}
              <div className="px-5 py-4">
                <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap max-h-[200px] overflow-y-auto">
                  {p.text}
                </div>
              </div>
              {/* Actions */}
              <div className="flex items-center gap-2 px-5 py-3 border-t border-slate-100 bg-slate-50/30">
                <button
                  onClick={() => copyText(p.text, p.id)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
                >
                  {copiedId === p.id ? <><Check className="w-3.5 h-3.5 text-green-600" /> Copié</> : <><Copy className="w-3.5 h-3.5" /> Copier</>}
                </button>
                {p.mission_id && (
                  <Link
                    to={`/missions/${p.mission_id}`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" /> Voir la mission
                  </Link>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {!loading && proposals.length === 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-sm text-slate-500">Aucune proposition générée pour le moment</p>
          <p className="text-xs text-slate-400 mt-1">L'agent génère automatiquement des propositions pour les missions à fort score</p>
        </div>
      )}
    </div>
  )
}
