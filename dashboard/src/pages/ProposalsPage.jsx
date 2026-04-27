import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { fetchProposals } from '../lib/supabase'
import {
  FileText, Copy, Check, ExternalLink, Search,
  Calendar, Package, ChevronRight, ChevronDown,
} from 'lucide-react'

function parsePackage(text) {
  if (!text) return null
  const match = text.match(/<!--PACKAGE_JSON:(.+?)-->/s)
  if (!match) return null
  try {
    return JSON.parse(match[1])
  } catch {
    return null
  }
}

function PackagingView({ pkg }) {
  return (
    <div className="space-y-5">
      {pkg.intro && (
        <p className="text-[15px] leading-relaxed text-slate-800">{pkg.intro}</p>
      )}

      {pkg.comprehension && (
        <div>
          <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-1.5">Votre besoin</p>
          <p className="text-sm leading-relaxed text-slate-700">{pkg.comprehension}</p>
        </div>
      )}

      {pkg.approach && (
        <div>
          <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-1.5">Approche</p>
          <p className="text-sm leading-relaxed text-slate-700">{pkg.approach}</p>
        </div>
      )}

      {pkg.phases && pkg.phases.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-2">Phases</p>
          <div className="space-y-2">
            {pkg.phases.map((p, i) => (
              <div key={i} className="border border-slate-200 rounded-md p-3">
                <div className="flex items-center justify-between mb-1.5 flex-wrap gap-2">
                  <p className="text-sm font-semibold text-slate-900">{p.name}</p>
                  {p.duration && (
                    <span className="inline-flex items-center gap-1 text-[11px] text-slate-500 bg-slate-50 px-2 py-0.5 rounded">
                      <Calendar className="w-3 h-3" /> {p.duration}
                    </span>
                  )}
                </div>
                {p.tasks && p.tasks.length > 0 && (
                  <ul className="text-xs text-slate-600 space-y-0.5 mt-1">
                    {p.tasks.map((t, j) => (
                      <li key={j} className="flex gap-2"><span className="text-slate-300">·</span><span>{t}</span></li>
                    ))}
                  </ul>
                )}
                {p.deliverable && (
                  <p className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100">
                    <span className="font-medium text-slate-700">Livrable :</span> {p.deliverable}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {pkg.timeline && (
          <div className="bg-slate-50 border border-slate-100 rounded-md p-3">
            <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">Durée totale</p>
            <p className="text-sm font-medium text-slate-900 mt-1">{pkg.timeline}</p>
          </div>
        )}
        {pkg.pricing && (
          <div className="bg-slate-50 border border-slate-100 rounded-md p-3">
            <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">Tarification</p>
            <p className="text-sm font-medium text-slate-900 mt-1">{pkg.pricing.amount}</p>
            <p className="text-[11px] text-slate-500">{pkg.pricing.model} · {pkg.pricing.payment}</p>
          </div>
        )}
      </div>

      {pkg.deliverables && pkg.deliverables.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-2">Livrables finaux</p>
          <ul className="space-y-1">
            {pkg.deliverables.map((d, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                <Check className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" strokeWidth={2.5} />
                <span>{d}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {pkg.expected_outcome && (
        <div className="border-l-2 border-blue-500 pl-4 py-1">
          <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-1">Résultat attendu</p>
          <p className="text-sm text-slate-800 leading-relaxed">{pkg.expected_outcome}</p>
        </div>
      )}

      {pkg.next_step && (
        <div>
          <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-1.5">Prochaine étape</p>
          <p className="text-sm text-slate-700">{pkg.next_step}</p>
        </div>
      )}

      {pkg.signature && (
        <p className="text-sm text-slate-500 italic pt-3 border-t border-slate-100">{pkg.signature}</p>
      )}
    </div>
  )
}

export default function ProposalsPage() {
  const [proposals, setProposals] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [copiedId, setCopiedId] = useState(null)
  const [expanded, setExpanded] = useState({})

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
    const cleanText = text.replace(/<!--PACKAGE_JSON:.+?-->/s, '').trim()
    navigator.clipboard.writeText(cleanText)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  function toggle(id) {
    setExpanded(e => ({ ...e, [id]: !e[id] }))
  }

  const filtered = useMemo(() => {
    if (!search) return proposals
    const q = search.toLowerCase()
    return proposals.filter(p => {
      const m = p.missions
      return m?.title?.toLowerCase().includes(q) ||
             m?.company?.toLowerCase().includes(q) ||
             p.text?.toLowerCase().includes(q)
    })
  }, [proposals, search])

  return (
    <div className="space-y-5 max-w-5xl">
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Propositions</h2>
          <p className="text-sm text-slate-500 mt-0.5">{proposals.length} packages générés par l'agent</p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Rechercher dans les propositions..."
            className="w-full pl-9 pr-3 py-2 rounded-md border border-slate-200 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {loading && <div className="text-center py-12 text-sm text-slate-400">Chargement...</div>}

      <div className="space-y-3">
        {filtered.map(p => {
          const mission = p.missions
          const pkg = parsePackage(p.text)
          const isOpen = expanded[p.id]
          return (
            <div key={p.id} className="bg-white rounded-lg border border-slate-200">
              <button
                onClick={() => toggle(p.id)}
                className="w-full flex items-center gap-4 px-5 py-4 text-left hover:bg-slate-50 transition-colors"
              >
                <Package className="w-4 h-4 text-slate-400 shrink-0" strokeWidth={1.75} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-900 truncate">{mission?.title || 'Mission'}</p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {mission?.company || 'Entreprise non précisée'} · {mission?.source || ''}
                    {mission?.score && ` · Score ${mission.score}/100`}
                  </p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className={`text-[11px] font-medium px-2 py-0.5 rounded ${p.status === 'ready' ? 'bg-emerald-50 text-emerald-700' : p.status === 'sent' ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-500'}`}>
                    {p.status === 'ready' ? 'Prête' : p.status === 'sent' ? 'Envoyée' : 'Brouillon'}
                  </span>
                  <span className="text-[11px] text-slate-400 hidden sm:inline">{p.language?.toUpperCase()}</span>
                  {isOpen ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                </div>
              </button>

              {isOpen && (
                <div className="px-5 pb-5 border-t border-slate-100 pt-5">
                  {pkg ? (
                    <PackagingView pkg={pkg} />
                  ) : (
                    <pre className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap font-sans">
                      {p.text?.replace(/<!--PACKAGE_JSON:.+?-->/s, '').trim()}
                    </pre>
                  )}

                  <div className="flex items-center gap-2 mt-5 pt-4 border-t border-slate-100">
                    <button
                      onClick={(e) => { e.stopPropagation(); copyText(p.text, p.id) }}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-white border border-slate-200 text-slate-700 hover:bg-slate-50"
                    >
                      {copiedId === p.id ? <><Check className="w-3.5 h-3.5 text-emerald-600" /> Copié</> : <><Copy className="w-3.5 h-3.5" /> Copier le texte</>}
                    </button>
                    {p.mission_id && (
                      <Link
                        to={`/missions/${p.mission_id}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-white border border-slate-200 text-slate-700 hover:bg-slate-50"
                      >
                        <ExternalLink className="w-3.5 h-3.5" /> Voir la mission
                      </Link>
                    )}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {!loading && filtered.length === 0 && (
        <div className="bg-white rounded-lg border border-slate-200 p-12 text-center">
          <Package className="w-10 h-10 text-slate-300 mx-auto mb-3" strokeWidth={1.5} />
          <p className="text-sm text-slate-500">Aucune proposition pour le moment</p>
          <p className="text-xs text-slate-400 mt-1">L'agent génère des packages structurés pour les missions à fort score</p>
        </div>
      )}
    </div>
  )
}
