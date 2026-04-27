import { useState, useEffect } from 'react'
import { fetchStats } from '../lib/supabase'
import { RefreshCw, CheckCircle2, XCircle } from 'lucide-react'

function Field({ label, value, mono = false }) {
  return (
    <div className="flex justify-between items-center py-2.5 border-b border-slate-100 last:border-0">
      <span className="text-xs text-slate-500">{label}</span>
      <span className={`text-sm text-slate-900 font-medium ${mono ? 'font-mono text-xs' : ''}`}>{value}</span>
    </div>
  )
}

export default function SettingsPage({ session }) {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats().then(d => { setHealth(d); setLoading(false) })
  }, [])

  async function refresh() {
    setLoading(true)
    const d = await fetchStats()
    setHealth(d)
    setLoading(false)
  }

  const isOnline = health?.status === 'running'

  return (
    <div className="space-y-5 max-w-3xl">
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Paramètres</h2>
          <p className="text-sm text-slate-500 mt-0.5">Configuration de l'agent et services connectés</p>
        </div>
        <button onClick={refresh} disabled={loading} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-white border border-slate-200 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50">
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Actualiser
        </button>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-5">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-slate-900">Infrastructure</h3>
          <span className={`inline-flex items-center gap-1.5 text-[11px] font-medium px-2 py-0.5 rounded ${isOnline ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
            {isOnline ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
            {isOnline ? 'Tous services actifs' : 'Hors ligne'}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-x-6">
          <Field label="Statut agent" value={isOnline ? 'En ligne' : 'Hors ligne'} />
          <Field label="Uptime" value={health?.uptime || '—'} />
          <Field label="Scans réalisés" value={health?.scans_total ?? '—'} />
          <Field label="Dernier scan" value={health?.last_scan ? new Date(health.last_scan).toLocaleString('fr-FR') : '—'} />
        </div>
      </div>

      {health?.sources && Object.keys(health.sources).length > 0 && (
        <div className="bg-white rounded-lg border border-slate-200 p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-3">Sources actives</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {Object.entries(health.sources).map(([name, info]) => (
              <div key={name} className="flex items-center justify-between py-2 px-3 rounded-md bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-2">
                  <span className={`w-1.5 h-1.5 rounded-full ${info.status === 'success' ? 'bg-emerald-500' : 'bg-red-500'}`} />
                  <span className="text-sm text-slate-700 font-medium">{name}</span>
                </div>
                <span className="text-[11px] text-slate-500 tabular-nums">{info.missions_found || 0}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-slate-200 p-5">
        <h3 className="text-sm font-semibold text-slate-900 mb-3">Session</h3>
        <Field label="Utilisateur" value={session.name} />
        <Field label="Rôle" value={session.role === 'tech' ? 'Consultant' : 'Administration'} />
        <Field label="Profil de chasse" value={session.role === 'tech' ? 'Missions tech & IA' : 'Missions admin & support'} />
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-5">
        <h3 className="text-sm font-semibold text-slate-900 mb-3">Configuration de l'agent</h3>
        <Field label="Score minimum proposition" value="70 / 100" />
        <Field label="Intervalle scan rapide (Tier 1)" value="5 minutes" />
        <Field label="Intervalle scan lent (Tier 2)" value="30 minutes" />
        <Field label="Sources surveillées" value="14 scrapers" />
        <Field label="Modèle de génération" value="Claude Sonnet 4" />
        <Field label="TJM consultant" value="450 EUR/jour HT" />
        <Field label="Pénalité CDI" value="-15 points" />
      </div>
    </div>
  )
}
