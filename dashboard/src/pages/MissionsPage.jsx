import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { fetchMissions } from '../lib/supabase'
import { Search, ChevronLeft, ChevronRight, Clock } from 'lucide-react'

function ScoreBadge({ score }) {
  const cls = score >= 80 ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
    : score >= 60 ? 'text-blue-700 bg-blue-50 border-blue-200'
    : score >= 40 ? 'text-amber-700 bg-amber-50 border-amber-200'
    : 'text-slate-600 bg-slate-50 border-slate-200'
  return <span className={`inline-flex items-center justify-center w-10 h-7 rounded text-[11px] font-bold tabular-nums border ${cls}`}>{score}</span>
}

const TYPE_LABELS = {
  ia: { label: 'IA', cls: 'bg-violet-50 text-violet-700 border-violet-200' },
  web: { label: 'Web', cls: 'bg-blue-50 text-blue-700 border-blue-200' },
  data: { label: 'Data', cls: 'bg-cyan-50 text-cyan-700 border-cyan-200' },
  consulting: { label: 'Conseil', cls: 'bg-amber-50 text-amber-700 border-amber-200' },
  design: { label: 'Design', cls: 'bg-pink-50 text-pink-700 border-pink-200' },
  other: { label: 'Autre', cls: 'bg-slate-50 text-slate-600 border-slate-200' },
}

const STATUS_LABELS = {
  new: 'Nouveau',
  proposal_ready: 'Proposition',
  sent: 'Envoyé',
  won: 'Gagné',
  lost: 'Perdu',
}

const STATUS_CLS = {
  new: 'bg-slate-50 text-slate-600 border-slate-200',
  proposal_ready: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  sent: 'bg-blue-50 text-blue-700 border-blue-200',
  won: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  lost: 'bg-red-50 text-red-600 border-red-200',
}

function timeAgo(date) {
  if (!date) return ''
  const d = new Date(date)
  const diff = (Date.now() - d.getTime()) / 1000
  if (diff < 3600) return `${Math.floor(diff / 60)}min`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`
  return `${Math.floor(diff / 86400)}j`
}

export default function MissionsPage() {
  const [missions, setMissions] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [type, setType] = useState('all')
  const [minScore, setMinScore] = useState('')
  const limit = 25

  const loadMissions = useCallback(async () => {
    setLoading(true)
    try {
      const { data, total: t } = await fetchMissions({
        limit,
        offset: page * limit,
        status: status !== 'all' ? status : undefined,
        minScore: minScore || undefined,
        search: search || undefined,
        type: type !== 'all' ? type : undefined,
      })
      setMissions(data || [])
      setTotal(t)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }, [page, status, type, minScore, search])

  useEffect(() => { loadMissions() }, [loadMissions])

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="space-y-5 max-w-6xl">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Missions</h2>
        <p className="text-sm text-slate-500 mt-0.5">{total} missions analysées par l'agent</p>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-3 flex flex-wrap gap-2 items-center">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0) }}
            placeholder="Rechercher une mission..."
            className="w-full pl-9 pr-3 py-2 rounded-md border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
          />
        </div>
        <select value={status} onChange={e => { setStatus(e.target.value); setPage(0) }} className="px-3 py-2 rounded-md border border-slate-200 text-sm bg-white">
          <option value="all">Tous statuts</option>
          <option value="new">Nouveau</option>
          <option value="proposal_ready">Proposition</option>
          <option value="sent">Envoyé</option>
          <option value="won">Gagné</option>
          <option value="lost">Perdu</option>
        </select>
        <select value={type} onChange={e => { setType(e.target.value); setPage(0) }} className="px-3 py-2 rounded-md border border-slate-200 text-sm bg-white">
          <option value="all">Tous types</option>
          <option value="ia">IA</option>
          <option value="web">Web</option>
          <option value="data">Data</option>
          <option value="consulting">Conseil</option>
          <option value="design">Design</option>
        </select>
        <select value={minScore} onChange={e => { setMinScore(e.target.value); setPage(0) }} className="px-3 py-2 rounded-md border border-slate-200 text-sm bg-white">
          <option value="">Score min</option>
          <option value="80">≥ 80</option>
          <option value="60">≥ 60</option>
          <option value="40">≥ 40</option>
          <option value="20">≥ 20</option>
        </select>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        {loading && <div className="px-5 py-12 text-center text-sm text-slate-400">Chargement...</div>}
        {!loading && missions.length === 0 && <div className="px-5 py-12 text-center text-sm text-slate-400">Aucune mission trouvée avec ces filtres</div>}
        <div className="divide-y divide-slate-50">
          {missions.map(m => {
            const t = TYPE_LABELS[m.type] || TYPE_LABELS.other
            return (
              <Link key={m.id} to={`/missions/${m.id}`} className="flex items-center gap-4 px-5 py-3.5 hover:bg-slate-50 transition-colors group">
                <ScoreBadge score={m.score || 0} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-sm font-medium text-slate-900 truncate group-hover:underline">{m.title}</p>
                    <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded border ${t.cls}`}>{t.label}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                    <span>{m.company || 'Entreprise non précisée'}</span>
                    <span className="text-slate-300">·</span>
                    <span>{m.source}</span>
                    {m.budget_raw && <>
                      <span className="text-slate-300">·</span>
                      <span className="text-slate-700 font-medium">{m.budget_raw}</span>
                    </>}
                    {m.remote && <span className="text-[10px] text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">Remote</span>}
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className={`text-[11px] font-medium px-2 py-0.5 rounded border ${STATUS_CLS[m.status] || STATUS_CLS.new}`}>
                    {STATUS_LABELS[m.status] || m.status}
                  </span>
                  <span className="text-[11px] text-slate-400 inline-flex items-center gap-1 tabular-nums w-10 justify-end">
                    <Clock className="w-3 h-3" /> {timeAgo(m.found_at || m.posted_at)}
                  </span>
                </div>
              </Link>
            )
          })}
        </div>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white rounded-lg border border-slate-200 px-4 py-3">
          <span className="text-xs text-slate-500">Page {page + 1} sur {totalPages} · {total} missions</span>
          <div className="flex gap-2">
            <button disabled={page === 0} onClick={() => setPage(p => p - 1)} className="p-1.5 rounded-md border border-slate-200 text-slate-500 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)} className="p-1.5 rounded-md border border-slate-200 text-slate-500 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
