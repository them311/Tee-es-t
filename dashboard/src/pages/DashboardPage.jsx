import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { fetchMissions, fetchStats, fetchScanLogs } from '../lib/supabase'
import { Crosshair, FileText, Activity, Clock, TrendingUp, ArrowRight, RefreshCw } from 'lucide-react'

function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
          {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
        </div>
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  )
}

function ScoreBadge({ score }) {
  const bg = score >= 80 ? 'bg-green-100 text-green-700' : score >= 60 ? 'bg-blue-100 text-blue-700' : score >= 40 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'
  return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-bold ${bg}`}>{score}</span>
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
      console.error('Dashboard load error:', e)
    }
    setLoading(false)
  }

  useEffect(() => { loadData() }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Dashboard</h2>
          <p className="text-sm text-slate-500">Vue d'ensemble de l'agent de chasse</p>
        </div>
        <button onClick={loadData} disabled={loading} className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-white border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors disabled:opacity-50">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Activity} label="Statut Agent" value={stats?.status === 'running' ? 'En ligne' : 'Hors ligne'} sub={stats?.uptime || ''} color="bg-green-100 text-green-600" />
        <StatCard icon={Crosshair} label="Missions aujourd'hui" value={stats?.missions_today ?? '...'} sub={`${Object.keys(stats?.sources || {}).length} sources actives`} color="bg-blue-100 text-blue-600" />
        <StatCard icon={FileText} label="Propositions" value={stats?.proposals_today ?? '...'} sub="Générées aujourd'hui" color="bg-purple-100 text-purple-600" />
        <StatCard icon={TrendingUp} label="Scans total" value={stats?.scans_total ?? '...'} sub={stats?.last_scan ? `Dernier: ${new Date(stats.last_scan).toLocaleTimeString('fr-FR')}` : ''} color="bg-amber-100 text-amber-600" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top missions */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200">
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <h3 className="font-semibold text-slate-900 text-sm">Missions prioritaires</h3>
            <Link to="/missions" className="text-xs text-blue-600 hover:text-blue-700 font-medium inline-flex items-center gap-1">
              Tout voir <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="divide-y divide-slate-50">
            {missions.length === 0 && !loading && (
              <p className="px-5 py-8 text-center text-sm text-slate-400">Aucune mission trouvée</p>
            )}
            {missions.slice(0, 8).map(m => (
              <Link key={m.id} to={`/missions/${m.id}`} className="flex items-center gap-4 px-5 py-3 hover:bg-slate-50 transition-colors">
                <ScoreBadge score={m.score} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800 truncate">{m.title}</p>
                  <p className="text-xs text-slate-400">{m.company || 'N/A'} — {m.source}</p>
                </div>
                <span className={`text-xs font-medium px-2 py-0.5 rounded ${m.status === 'proposal_ready' ? 'bg-green-50 text-green-600' : m.status === 'sent' ? 'bg-blue-50 text-blue-600' : 'bg-slate-50 text-slate-500'}`}>
                  {m.status === 'proposal_ready' ? 'Proposition' : m.status === 'new' ? 'Nouveau' : m.status}
                </span>
              </Link>
            ))}
          </div>
        </div>

        {/* Scan activity */}
        <div className="bg-white rounded-xl border border-slate-200">
          <div className="px-5 py-4 border-b border-slate-100">
            <h3 className="font-semibold text-slate-900 text-sm">Activité des scans</h3>
          </div>
          <div className="divide-y divide-slate-50 max-h-[400px] overflow-y-auto">
            {logs.length === 0 && !loading && (
              <p className="px-5 py-8 text-center text-sm text-slate-400">Aucun scan récent</p>
            )}
            {logs.slice(0, 12).map((l, i) => (
              <div key={i} className="flex items-center gap-3 px-5 py-2.5">
                <span className={`w-2 h-2 rounded-full shrink-0 ${l.status === 'success' ? 'bg-green-500' : l.status === 'running' ? 'bg-amber-500 animate-pulse' : 'bg-red-500'}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-slate-700 truncate">{l.source}</p>
                  <p className="text-[11px] text-slate-400">
                    {l.missions_found ?? 0} trouvées, {l.missions_new ?? 0} nouvelles
                  </p>
                </div>
                <span className="text-[11px] text-slate-400 shrink-0">
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
