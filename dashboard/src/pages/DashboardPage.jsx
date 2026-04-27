import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { fetchMissions, fetchStats, fetchScanLogs } from '../lib/supabase'
import {
  ArrowUpRight, RefreshCw,
} from 'lucide-react'

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-5">
      <p className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase">{label}</p>
      <p className="text-2xl font-semibold text-slate-900 mt-2 tabular-nums">{value}</p>
      {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
    </div>
  )
}

function ScoreBadge({ score }) {
  const cls = score >= 80 ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
    : score >= 60 ? 'text-blue-700 bg-blue-50 border-blue-200'
    : score >= 40 ? 'text-amber-700 bg-amber-50 border-amber-200'
    : 'text-slate-600 bg-slate-50 border-slate-200'
  return <span className={`inline-flex items-center justify-center w-9 h-6 rounded text-[11px] font-bold tabular-nums border ${cls}`}>{score}</span>
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [missions, setMissions] = useState([])
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  async function loadData() {
    setLoading(true)
    try {
      const [s, m, l] = await Promise.all([
        fetchStats(),
        fetchMissions({ limit: 10, minScore: 50 }),
        fetchScanLogs(15),
      ])
      setStats(s)
      setMissions(m.data || [])
      setLogs(l || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => { loadData() }, [])

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Vue d'ensemble</h2>
          <p className="text-sm text-slate-500 mt-0.5">Activité de l'agent et missions prioritaires</p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-white border border-slate-200 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} strokeWidth={1.75} />
          Actualiser
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard label="Statut" value={stats?.status === 'running' ? 'Actif' : 'Inactif'} sub={stats?.uptime || '—'} />
        <StatCard label="Missions du jour" value={stats?.missions_today ?? '—'} sub={`${Object.keys(stats?.sources || {}).length} sources actives`} />
        <StatCard label="Propositions" value={stats?.proposals_today ?? '—'} sub="Générées aujourd'hui" />
        <StatCard label="Scans réalisés" value={stats?.scans_total ?? '—'} sub={stats?.last_scan ? `Dernier ${new Date(stats.last_scan).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}` : '—'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 bg-white rounded-lg border border-slate-200">
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Missions prioritaires</h3>
              <p className="text-xs text-slate-500 mt-0.5">Score &ge; 50, triées par fraîcheur</p>
            </div>
            <Link to="/missions" className="text-xs text-slate-700 hover:text-slate-900 font-medium inline-flex items-center gap-1">
              Tout voir <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="divide-y divide-slate-50">
            {!loading && missions.length === 0 && (
              <p className="px-5 py-12 text-center text-sm text-slate-400">Aucune mission prioritaire pour le moment</p>
            )}
            {missions.slice(0, 8).map(m => (
              <Link key={m.id} to={`/missions/${m.id}`} className="flex items-center gap-4 px-5 py-3 hover:bg-slate-50 transition-colors group">
                <ScoreBadge score={m.score || 0} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 truncate group-hover:underline">{m.title}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{m.company || 'Entreprise non précisée'} &middot; {m.source}</p>
                </div>
                <span className={`text-[11px] font-medium px-2 py-0.5 rounded shrink-0 ${
                  m.status === 'proposal_ready' ? 'bg-emerald-50 text-emerald-700' :
                  m.status === 'sent' ? 'bg-blue-50 text-blue-700' :
                  m.status === 'won' ? 'bg-emerald-100 text-emerald-800' :
                  'bg-slate-100 text-slate-500'
                }`}>
                  {m.status === 'proposal_ready' ? 'Proposition' :
                   m.status === 'sent' ? 'Envoyé' :
                   m.status === 'won' ? 'Gagné' :
                   m.status === 'lost' ? 'Perdu' : 'Nouveau'}
                </span>
              </Link>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200">
          <div className="px-5 py-4 border-b border-slate-100">
            <h3 className="text-sm font-semibold text-slate-900">Activité des scans</h3>
            <p className="text-xs text-slate-500 mt-0.5">Derniers cycles de chasse</p>
          </div>
          <div className="divide-y divide-slate-50 max-h-[460px] overflow-y-auto">
            {!loading && logs.length === 0 && (
              <p className="px-5 py-12 text-center text-sm text-slate-400">Aucun scan récent</p>
            )}
            {logs.slice(0, 14).map((l, i) => (
              <div key={i} className="flex items-center gap-3 px-5 py-2.5">
                <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${l.status === 'success' ? 'bg-emerald-500' : l.status === 'running' ? 'bg-amber-400 animate-pulse' : 'bg-red-500'}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-slate-800 truncate">{l.source}</p>
                  <p className="text-[11px] text-slate-500">{l.missions_found ?? 0} trouvées &middot; {l.missions_new ?? 0} nouvelles</p>
                </div>
                <span className="text-[11px] text-slate-400 shrink-0 tabular-nums">
                  {l.started_at ? new Date(l.started_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) : ''}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
