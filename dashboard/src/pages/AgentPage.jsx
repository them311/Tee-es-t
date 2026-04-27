import { useState, useEffect, useMemo } from 'react'
import { fetchStats, fetchScanLogs, fetchMissions } from '../lib/supabase'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts'
import {
  Activity, Cpu, Zap, Target, TrendingUp, Database,
  CheckCircle2, AlertCircle, Clock,
} from 'lucide-react'

const TYPE_COLORS = {
  ia: '#7c3aed',
  web: '#2563eb',
  data: '#0891b2',
  consulting: '#d97706',
  design: '#db2777',
  other: '#64748b',
}

function MetricCard({ icon: Icon, label, value, sub, accent = 'slate' }) {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">{label}</p>
          <p className="text-2xl font-semibold text-slate-900 mt-1.5 tabular-nums">{value}</p>
          {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
        </div>
        <Icon className="w-4 h-4 text-slate-300" strokeWidth={1.75} />
      </div>
    </div>
  )
}

export default function AgentPage() {
  const [stats, setStats] = useState(null)
  const [logs, setLogs] = useState([])
  const [missions, setMissions] = useState([])
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    try {
      const [s, l, m] = await Promise.all([
        fetchStats(),
        fetchScanLogs(50),
        fetchMissions({ limit: 200 }),
      ])
      setStats(s)
      setLogs(l || [])
      setMissions(m.data || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 60000)
    return () => clearInterval(id)
  }, [])

  // Aggregate metrics
  const sourceStats = useMemo(() => {
    const map = {}
    logs.forEach(l => {
      const s = l.source || 'unknown'
      if (!map[s]) map[s] = { source: s, total: 0, success: 0, missions: 0 }
      map[s].total += 1
      if (l.status === 'success') map[s].success += 1
      map[s].missions += l.missions_found || 0
    })
    return Object.values(map)
      .map(s => ({ ...s, successRate: s.total ? Math.round((s.success / s.total) * 100) : 0 }))
      .sort((a, b) => b.missions - a.missions)
  }, [logs])

  const typeDistribution = useMemo(() => {
    const map = {}
    missions.forEach(m => {
      const t = m.type || 'other'
      map[t] = (map[t] || 0) + 1
    })
    return Object.entries(map).map(([name, value]) => ({ name, value, fill: TYPE_COLORS[name] || '#64748b' }))
  }, [missions])

  const scoreDistribution = useMemo(() => {
    const buckets = [
      { range: '0-20', count: 0, fill: '#cbd5e1' },
      { range: '20-40', count: 0, fill: '#94a3b8' },
      { range: '40-60', count: 0, fill: '#fbbf24' },
      { range: '60-80', count: 0, fill: '#3b82f6' },
      { range: '80-100', count: 0, fill: '#22c55e' },
    ]
    missions.forEach(m => {
      const s = m.score || 0
      if (s < 20) buckets[0].count++
      else if (s < 40) buckets[1].count++
      else if (s < 60) buckets[2].count++
      else if (s < 80) buckets[3].count++
      else buckets[4].count++
    })
    return buckets
  }, [missions])

  const dailyActivity = useMemo(() => {
    const map = {}
    missions.forEach(m => {
      const d = m.found_at?.slice(0, 10)
      if (!d) return
      if (!map[d]) map[d] = { date: d, missions: 0, proposals: 0 }
      map[d].missions++
      if (m.status === 'proposal_ready' || m.status === 'sent') map[d].proposals++
    })
    return Object.values(map).sort((a, b) => a.date.localeCompare(b.date)).slice(-14)
  }, [missions])

  const learningMetrics = useMemo(() => {
    const total = missions.length || 1
    const highScore = missions.filter(m => (m.score || 0) >= 70).length
    const proposed = missions.filter(m => m.status === 'proposal_ready' || m.status === 'sent' || m.status === 'won').length
    const won = missions.filter(m => m.status === 'won').length
    return {
      relevanceRate: Math.round((highScore / total) * 100),
      proposalRate: Math.round((proposed / total) * 100),
      conversionRate: proposed ? Math.round((won / proposed) * 100) : 0,
      avgScore: Math.round(missions.reduce((s, m) => s + (m.score || 0), 0) / total),
    }
  }, [missions])

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Agent</h2>
          <p className="text-sm text-slate-500 mt-0.5">Performance, apprentissage et activité de l'agent autonome</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium ${stats?.status === 'running' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-500 border border-slate-200'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${stats?.status === 'running' ? 'bg-emerald-500' : 'bg-slate-400'}`} />
            {stats?.status === 'running' ? 'En activité' : 'Inactif'}
          </span>
          <span className="text-xs text-slate-400">Uptime {stats?.uptime || '-'}</span>
        </div>
      </div>

      {/* Top metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard icon={Database} label="Missions analysées" value={missions.length} sub="Total en base" />
        <MetricCard icon={Target} label="Score moyen" value={learningMetrics.avgScore} sub={`${learningMetrics.relevanceRate}% pertinentes (≥70)`} />
        <MetricCard icon={Zap} label="Taux de proposition" value={`${learningMetrics.proposalRate}%`} sub={`${stats?.proposals_today ?? 0} aujourd'hui`} />
        <MetricCard icon={TrendingUp} label="Conversion" value={`${learningMetrics.conversionRate}%`} sub="Propositions gagnées" />
      </div>

      {/* Activity chart */}
      <div className="bg-white rounded-lg border border-slate-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Activité quotidienne (14 derniers jours)</h3>
            <p className="text-xs text-slate-500 mt-0.5">Missions découvertes et propositions générées</p>
          </div>
        </div>
        <div className="h-64">
          {dailyActivity.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dailyActivity}>
                <CartesianGrid stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickFormatter={d => d.slice(5)} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
                <Line type="monotone" dataKey="missions" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }} name="Missions" />
                <Line type="monotone" dataKey="proposals" stroke="#7c3aed" strokeWidth={2} dot={{ r: 3 }} name="Propositions" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-sm text-slate-400">Pas encore de données</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score distribution */}
        <div className="bg-white rounded-lg border border-slate-200 p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Distribution des scores</h3>
          <p className="text-xs text-slate-500 mb-4">Qualité du pipeline de missions</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={scoreDistribution}>
                <CartesianGrid stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="range" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {scoreDistribution.map((b, i) => <Cell key={i} fill={b.fill} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Type distribution */}
        <div className="bg-white rounded-lg border border-slate-200 p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-1">Types de missions</h3>
          <p className="text-xs text-slate-500 mb-4">Répartition par catégorie</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={typeDistribution}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={50}
                  outerRadius={85}
                  paddingAngle={2}
                  label={({ name, value }) => `${name} (${value})`}
                  labelLine={false}
                  fontSize={11}
                >
                  {typeDistribution.map((d, i) => <Cell key={i} fill={d.fill} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Sources performance */}
      <div className="bg-white rounded-lg border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-100">
          <h3 className="text-sm font-semibold text-slate-900">Performance par source</h3>
          <p className="text-xs text-slate-500 mt-0.5">Apprentissage continu — l'agent privilégie les sources les plus fiables</p>
        </div>
        <div className="divide-y divide-slate-50">
          {sourceStats.length === 0 && (
            <p className="px-5 py-8 text-center text-sm text-slate-400">Pas encore de données de scan</p>
          )}
          {sourceStats.map(s => (
            <div key={s.source} className="px-5 py-3 grid grid-cols-12 items-center gap-3 hover:bg-slate-50">
              <div className="col-span-3">
                <p className="text-sm font-medium text-slate-900">{s.source}</p>
                <p className="text-[11px] text-slate-500">{s.total} scans</p>
              </div>
              <div className="col-span-3">
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${s.successRate}%` }} />
                  </div>
                  <span className="text-xs font-medium text-slate-600 tabular-nums">{s.successRate}%</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Taux succès</p>
              </div>
              <div className="col-span-2">
                <p className="text-sm font-semibold text-slate-900 tabular-nums">{s.missions}</p>
                <p className="text-[11px] text-slate-400">missions</p>
              </div>
              <div className="col-span-4 flex items-center gap-2 justify-end">
                {s.successRate >= 90 ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                    <CheckCircle2 className="w-3 h-3" /> Excellent
                  </span>
                ) : s.successRate >= 60 ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-medium text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                    Stable
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
                    <AlertCircle className="w-3 h-3" /> À surveiller
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Learning indicators */}
      <div className="bg-white rounded-lg border border-slate-200 p-5">
        <h3 className="text-sm font-semibold text-slate-900 mb-1">Apprentissage de l'agent</h3>
        <p className="text-xs text-slate-500 mb-4">Indicateurs de progression — l'agent affine son modèle à chaque cycle</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
            <div className="flex items-center gap-2 mb-2">
              <Cpu className="w-4 h-4 text-slate-500" strokeWidth={1.75} />
              <p className="text-xs font-medium text-slate-700">Pertinence</p>
            </div>
            <p className="text-xl font-semibold text-slate-900 tabular-nums">{learningMetrics.relevanceRate}%</p>
            <p className="text-[11px] text-slate-500 mt-1">des missions scrapées matchent le profil</p>
          </div>
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-slate-500" strokeWidth={1.75} />
              <p className="text-xs font-medium text-slate-700">Activation</p>
            </div>
            <p className="text-xl font-semibold text-slate-900 tabular-nums">{learningMetrics.proposalRate}%</p>
            <p className="text-[11px] text-slate-500 mt-1">des missions déclenchent une proposition IA</p>
          </div>
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-slate-500" strokeWidth={1.75} />
              <p className="text-xs font-medium text-slate-700">Conversion</p>
            </div>
            <p className="text-xl font-semibold text-slate-900 tabular-nums">{learningMetrics.conversionRate}%</p>
            <p className="text-[11px] text-slate-500 mt-1">des propositions sont gagnées</p>
          </div>
        </div>
      </div>
    </div>
  )
}
