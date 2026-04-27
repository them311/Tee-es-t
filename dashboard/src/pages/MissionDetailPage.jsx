import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchMission, fetchProposals, updateMission, getDevisUrl } from '../lib/supabase'
import {
  ArrowLeft, ExternalLink, Download, Send,
  CheckCircle2, XCircle, Clock, FileText,
  Building2, MapPin, Tag,
} from 'lucide-react'

function parsePackage(text) {
  if (!text) return null
  const match = text.match(/<!--PACKAGE_JSON:(.+?)-->/s)
  if (!match) return null
  try { return JSON.parse(match[1]) } catch { return null }
}

const STATUS_FLOW = [
  { key: 'new', label: 'Nouveau', icon: Clock },
  { key: 'proposal_ready', label: 'Proposition', icon: FileText },
  { key: 'sent', label: 'Envoyé', icon: Send },
  { key: 'won', label: 'Gagné', icon: CheckCircle2 },
]

export default function MissionDetailPage() {
  const { id } = useParams()
  const [mission, setMission] = useState(null)
  const [proposals, setProposals] = useState([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)

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
    if (updating) return
    setUpdating(true)
    try {
      await updateMission(id, { status })
      setMission(prev => ({ ...prev, status }))
    } finally {
      setUpdating(false)
    }
  }

  if (loading) return <div className="text-center py-12 text-sm text-slate-400">Chargement...</div>
  if (!mission) return <div className="text-center py-12 text-sm text-slate-400">Mission introuvable</div>

  const currentStep = STATUS_FLOW.findIndex(s => s.key === mission.status)
  const score = mission.score || 0
  const scoreCls = score >= 80 ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
    : score >= 60 ? 'text-blue-700 bg-blue-50 border-blue-200'
    : score >= 40 ? 'text-amber-700 bg-amber-50 border-amber-200'
    : 'text-slate-600 bg-slate-50 border-slate-200'

  const proposal = proposals[0]
  const pkg = proposal ? parsePackage(proposal.text) : null

  return (
    <div className="space-y-5 max-w-5xl">
      <Link to="/missions" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-900 transition-colors">
        <ArrowLeft className="w-3.5 h-3.5" /> Retour aux missions
      </Link>

      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <div className="flex flex-wrap items-start justify-between gap-4 mb-5">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className={`inline-flex items-center px-2.5 py-1 rounded text-xs font-bold border tabular-nums ${scoreCls}`}>
                Score {score}/100
              </span>
              {mission.type && <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-50 border border-slate-200 text-slate-600 capitalize">{mission.type}</span>}
              {mission.remote && <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-700">Remote</span>}
            </div>
            <h2 className="text-lg font-semibold text-slate-900 leading-tight">{mission.title}</h2>
            <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-500">
              <span className="inline-flex items-center gap-1"><Building2 className="w-3 h-3" /> {mission.company || 'Entreprise non précisée'}</span>
              <span className="inline-flex items-center gap-1"><MapPin className="w-3 h-3" /> {mission.source}</span>
              {mission.budget_raw && <span className="font-medium text-slate-700">{mission.budget_raw}</span>}
            </div>
          </div>
          <div className="flex flex-wrap gap-2 shrink-0">
            {mission.source_url && (
              <a href={mission.source_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md bg-slate-900 text-white text-xs font-medium hover:bg-slate-800 transition-colors">
                <ExternalLink className="w-3.5 h-3.5" /> Voir l'offre
              </a>
            )}
            <a href={getDevisUrl(mission.id)} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md bg-white border border-slate-200 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors">
              <Download className="w-3.5 h-3.5" /> Devis
            </a>
          </div>
        </div>

        <div className="pt-5 border-t border-slate-100">
          <p className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase mb-3">Pipeline</p>
          <div className="flex items-center gap-1.5 flex-wrap">
            {STATUS_FLOW.map((step, i) => {
              const Icon = step.icon
              const isActive = step.key === mission.status
              const isPast = i <= currentStep
              return (
                <button
                  key={step.key}
                  onClick={() => setStatus(step.key)}
                  disabled={updating}
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all disabled:opacity-50 ${
                    isActive ? 'bg-slate-900 text-white border border-slate-900' :
                    isPast ? 'bg-slate-100 text-slate-700 border border-slate-200' :
                    'bg-white text-slate-500 border border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <Icon className="w-3 h-3" strokeWidth={2} /> {step.label}
                </button>
              )
            })}
            <button
              onClick={() => setStatus('lost')}
              disabled={updating}
              className={`ml-auto flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all disabled:opacity-50 ${
                mission.status === 'lost' ? 'bg-red-600 text-white border border-red-600' :
                'bg-white text-slate-400 border border-slate-200 hover:bg-red-50 hover:text-red-600 hover:border-red-200'
              }`}
            >
              <XCircle className="w-3 h-3" /> Perdu
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h3 className="text-sm font-semibold text-slate-900 mb-3">Description du besoin</h3>
        <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap max-h-[400px] overflow-y-auto">
          {mission.description || 'Pas de description disponible.'}
        </div>
        {mission.tags && mission.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-4 pt-4 border-t border-slate-100">
            {mission.tags.map((tag, i) => (
              <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-50 border border-slate-200 text-[11px] text-slate-600">
                <Tag className="w-2.5 h-2.5" /> {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {proposal && (
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-900">Package de proposition</h3>
            <Link to="/proposals" className="text-xs text-slate-500 hover:text-slate-900 inline-flex items-center gap-1">
              Toutes les propositions <ExternalLink className="w-3 h-3" />
            </Link>
          </div>
          {pkg ? (
            <div className="space-y-4">
              {pkg.intro && <p className="text-sm text-slate-800 leading-relaxed">{pkg.intro}</p>}
              {pkg.phases && pkg.phases.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  {pkg.phases.map((p, i) => (
                    <div key={i} className="border border-slate-200 rounded-md p-3">
                      <p className="text-xs font-semibold text-slate-900">{p.name}</p>
                      <p className="text-[11px] text-slate-500 mt-0.5">{p.duration}</p>
                    </div>
                  ))}
                </div>
              )}
              {pkg.expected_outcome && (
                <div className="border-l-2 border-blue-500 pl-3 py-1">
                  <p className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase mb-1">Résultat attendu</p>
                  <p className="text-sm text-slate-800">{pkg.expected_outcome}</p>
                </div>
              )}
              <Link to="/proposals" className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700 hover:text-slate-900">
                Voir le package complet <ExternalLink className="w-3 h-3" />
              </Link>
            </div>
          ) : (
            <pre className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap font-sans max-h-[300px] overflow-y-auto">
              {proposal.text?.replace(/<!--PACKAGE_JSON:.+?-->/s, '').trim()}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}
