import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchMission, fetchProposals, updateMission, getDevisUrl } from '../lib/supabase'
import { ArrowLeft, ExternalLink, FileText, Download, Send, CheckCircle, XCircle, Clock, Tag } from 'lucide-react'

function ScoreBadge({ score }) {
  const bg = score >= 80 ? 'bg-green-100 text-green-700' : score >= 60 ? 'bg-blue-100 text-blue-700' : score >= 40 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'
  return <span className={`inline-flex items-center px-3 py-1 rounded-lg text-sm font-bold ${bg}`}>{score}/100</span>
}

const STATUS_FLOW = [
  { key: 'new', label: 'Nouveau', icon: Clock, color: 'text-slate-500' },
  { key: 'proposal_ready', label: 'Proposition', icon: FileText, color: 'text-blue-600' },
  { key: 'sent', label: 'Envoyé', icon: Send, color: 'text-purple-600' },
  { key: 'won', label: 'Gagné', icon: CheckCircle, color: 'text-green-600' },
]

export default function MissionDetailPage() {
  const { id } = useParams()
  const [mission, setMission] = useState(null)
  const [proposals, setProposals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      setLoading(true)
      const [m, p] = await Promise.all([
        fetchMission(id),
        fetchProposals({ missionId: id }),
      ])
      setMission(m)
      setProposals(p || [])
      setLoading(false)
    }
    load()
  }, [id])

  async function setStatus(status) {
    await updateMission(id, { status })
    setMission(prev => ({ ...prev, status }))
  }

  if (loading) return <div className="text-center py-12 text-sm text-slate-400">Chargement...</div>
  if (!mission) return <div className="text-center py-12 text-sm text-slate-400">Mission introuvable</div>

  const currentStep = STATUS_FLOW.findIndex(s => s.key === mission.status)

  return (
    <div className="space-y-6 max-w-4xl">
      <Link to="/missions" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700">
        <ArrowLeft className="w-4 h-4" /> Retour aux missions
      </Link>

      {/* Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              <ScoreBadge score={mission.score} />
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${mission.type === 'ia' ? 'bg-purple-100 text-purple-700' : mission.type === 'web' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>{mission.type}</span>
              {mission.remote && <span className="text-xs text-emerald-600 font-medium bg-emerald-50 px-2 py-0.5 rounded">Remote</span>}
            </div>
            <h2 className="text-lg font-bold text-slate-900">{mission.title}</h2>
            <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-slate-500">
              <span>{mission.company || 'Entreprise non precisée'}</span>
              <span>{mission.source}</span>
              {mission.budget_raw && <span className="font-medium text-slate-700">{mission.budget_raw}</span>}
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {mission.source_url && (
              <a href={mission.source_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors">
                <ExternalLink className="w-4 h-4" /> Voir l'offre
              </a>
            )}
            <a href={getDevisUrl(mission.id)} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-white border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">
              <Download className="w-4 h-4" /> Devis
            </a>
          </div>
        </div>

        {/* Pipeline */}
        <div className="mt-6 pt-6 border-t border-slate-100">
          <div className="flex items-center gap-2">
            {STATUS_FLOW.map((step, i) => {
              const Icon = step.icon
              const isActive = step.key === mission.status
              const isPast = i <= currentStep
              return (
                <button
                  key={step.key}
                  onClick={() => setStatus(step.key)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive ? 'bg-blue-50 text-blue-700 ring-2 ring-blue-200' :
                    isPast ? 'bg-slate-50 text-slate-600' :
                    'bg-white text-slate-400 border border-slate-200'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" /> {step.label}
                </button>
              )
            })}
            <button onClick={() => setStatus('lost')} className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-white text-red-400 border border-slate-200 hover:bg-red-50 hover:text-red-600 transition-all ml-auto">
              <XCircle className="w-3.5 h-3.5" /> Perdu
            </button>
          </div>
        </div>
      </div>

      {/* Description */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="font-semibold text-slate-900 text-sm mb-3">Description</h3>
        <div className="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap max-h-[400px] overflow-y-auto">
          {mission.description || 'Pas de description disponible.'}
        </div>
        {mission.tags && mission.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-100">
            {mission.tags.map((tag, i) => (
              <span key={i} className="inline-flex items-center gap-1 px-2 py-1 rounded bg-slate-100 text-xs text-slate-600">
                <Tag className="w-3 h-3" /> {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Proposals */}
      {proposals.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-900 text-sm mb-4">Propositions générées</h3>
          <div className="space-y-4">
            {proposals.map((p, i) => (
              <div key={i} className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-slate-500">Proposition {i + 1} — {p.language?.toUpperCase()}</span>
                  <span className="text-xs text-slate-400">{p.created_at ? new Date(p.created_at).toLocaleDateString('fr-FR') : ''}</span>
                </div>
                <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">{p.text}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
