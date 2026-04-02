import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { fetchMissions } from '../lib/supabase'
import { Search, Filter, ChevronLeft, ChevronRight, ExternalLink, MapPin, Clock } from 'lucide-react'

function ScoreBadge({ score }) {
  const bg = score >= 80 ? 'bg-green-100 text-green-700' : score >= 60 ? 'bg-blue-100 text-blue-700' : score >= 40 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'
  return <span className={`inline-flex items-center justify-center w-10 h-7 rounded-md text-xs font-bold ${bg}`}>{score}</span>
}

function TypeBadge({ type }) {
  const colors = { ia: 'bg-purple-100 text-purple-700', web: 'bg-blue-100 text-blue-700', data: 'bg-cyan-100 text-cyan-700', consulting: 'bg-amber-100 text-amber-700', design: 'bg-pink-100 text-pink-700' }
  return <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${colors[type] || 'bg-slate-100 text-slate-600'}`}>{type || 'autre'}</span>
}

function StatusBadge({ status }) {
  const colors = { new: 'bg-slate-100 text-slate-600', proposal_ready: 'bg-green-100 text-green-700', sent: 'bg-blue-100 text-blue-700', won: 'bg-emerald-100 text-emerald-700', lost: 'bg-red-100 text-red-600' }
  const labels = { new: 'Nouveau', proposal_ready: 'Proposition', sent: 'Envoyé', won: 'Gagné', lost: 'Perdu' }
  return <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${colors[status] || 'bg-slate-100 text-slate-600'}`}>{labels[status] || status}</span>
}

function timeAgo(date) {
  if (!date) return ''
  const d = new Date(date)
  const diff = (Date.now() - d.getTime()) / 1000
  if (diff < 3600) return `${Math.floor(diff / 60)}min`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`
  return `${Math.floor(diff / 86400)}j`
}

export default function MissionsPage({ session }) {
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
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Missions</h2>
        <p className="text-sm text-slate-500">{total} missions en base</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center bg-white rounded-xl border border-slate-200 p-4">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0) }}
            placeholder="Rechercher une mission..."
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select value={status} onChange={e => { setStatus(e.target.value); setPage(0) }} className="px-3 py-2 rounded-lg border border-slate-200 text-sm bg-white">
          <option value="all">Tous statuts</option>
          <option value="new">Nouveau</option>
          <option value="proposal_ready">Proposition</option>
          <option value="sent">Envoyé</option>
          <option value="won">Gagné</option>
          <option value="lost">Perdu</option>
        </select>
        <select value={type} onChange={e => { setType(e.target.value); setPage(0) }} className="px-3 py-2 rounded-lg border border-slate-200 text-sm bg-white">
          <option value="all">Tous types</option>
          <option value="ia">IA</option>
          <option value="web">Web</option>
          <option value="data">Data</option>
          <option value="consulting">Consulting</option>
          <option value="design">Design</option>
        </select>
        <select value={minScore} onChange={e => { setMinScore(e.target.value); setPage(0) }} className="px-3 py-2 rounded-lg border border-slate-200 text-sm bg-white">
          <option value="">Score min</option>
          <option value="80">80+</option>
          <option value="60">60+</option>
          <option value="40">40+</option>
          <option value="20">20+</option>
        </select>
      </div>

      {/* Missions list */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        {loading && <div className="px-5 py-8 text-center text-sm text-slate-400">Chargement...</div>}
        {!loading && missions.length === 0 && <div className="px-5 py-8 text-center text-sm text-slate-400">Aucune mission trouvée</div>}
        <div className="divide-y divide-slate-100">
          {missions.map(m => (
            <Link key={m.id} to={`/missions/${m.id}`} className="flex items-center gap-4 px-5 py-3.5 hover:bg-slate-50 transition-colors group">
              <ScoreBadge score={m.score} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-slate-800 truncate group-hover:text-blue-600 transition-colors">{m.title}</p>
                  <TypeBadge type={m.type} />
                </div>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-xs text-slate-400">{m.company || 'N/A'}</span>
                  <span className="text-xs text-slate-300">|</span>
                  <span className="text-xs text-slate-400">{m.source}</span>
                  {m.budget_raw && <>
                    <span className="text-xs text-slate-300">|</span>
                    <span className="text-xs text-slate-500 font-medium">{m.budget_raw}</span>
                  </>}
                  {m.remote && <span className="text-[10px] text-emerald-600 font-medium bg-emerald-50 px-1.5 py-0.5 rounded">Remote</span>}
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <StatusBadge status={m.status} />
                <span className="text-xs text-slate-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {timeAgo(m.found_at || m.posted_at)}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white rounded-xl border border-slate-200 px-4 py-3">
          <span className="text-xs text-slate-500">Page {page + 1} / {totalPages}</span>
          <div className="flex gap-2">
            <button disabled={page === 0} onClick={() => setPage(p => p - 1)} className="p-2 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 disabled:opacity-40">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)} className="p-2 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 disabled:opacity-40">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
