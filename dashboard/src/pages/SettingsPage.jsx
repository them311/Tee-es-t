import { useState, useEffect } from 'react'
import { fetchStats } from '../lib/supabase'
import { Settings, Server, Database, Mail, Bot, Shield, RefreshCw, CheckCircle, XCircle } from 'lucide-react'

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
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Paramètres</h2>
        <p className="text-sm text-slate-500">Configuration de l'agent et services</p>
      </div>

      {/* Agent status */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-900 text-sm flex items-center gap-2"><Server className="w-4 h-4" /> Statut de l'agent Railway</h3>
          <button onClick={refresh} disabled={loading} className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1">
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Rafraîchir
          </button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
            {isOnline ? <CheckCircle className="w-5 h-5 text-green-500" /> : <XCircle className="w-5 h-5 text-red-500" />}
            <div>
              <p className="text-sm font-medium text-slate-700">Statut</p>
              <p className="text-xs text-slate-500">{isOnline ? 'En ligne' : 'Hors ligne'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
            <Database className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-sm font-medium text-slate-700">Uptime</p>
              <p className="text-xs text-slate-500">{health?.uptime || 'N/A'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
            <Bot className="w-5 h-5 text-purple-500" />
            <div>
              <p className="text-sm font-medium text-slate-700">Scans aujourd'hui</p>
              <p className="text-xs text-slate-500">{health?.scans_total ?? 'N/A'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
            <Mail className="w-5 h-5 text-amber-500" />
            <div>
              <p className="text-sm font-medium text-slate-700">Dernier scan</p>
              <p className="text-xs text-slate-500">{health?.last_scan ? new Date(health.last_scan).toLocaleString('fr-FR') : 'N/A'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sources status */}
      {health?.sources && Object.keys(health.sources).length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-900 text-sm mb-4">Sources actives</h3>
          <div className="space-y-2">
            {Object.entries(health.sources).map(([name, info]) => (
              <div key={name} className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-50">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${info.status === 'success' ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-sm text-slate-700 font-medium">{name}</span>
                </div>
                <span className="text-xs text-slate-400">{info.missions_found || 0} missions</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User info */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="font-semibold text-slate-900 text-sm flex items-center gap-2 mb-4"><Shield className="w-4 h-4" /> Session</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between py-2 border-b border-slate-100">
            <span className="text-slate-500">Utilisateur</span>
            <span className="text-slate-700 font-medium">{session.name}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-100">
            <span className="text-slate-500">Rôle</span>
            <span className="text-slate-700 font-medium capitalize">{session.role}</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-slate-500">Profil</span>
            <span className="text-slate-700 font-medium">{session.role === 'tech' ? 'Missions tech & IA' : 'Missions admin & support'}</span>
          </div>
        </div>
      </div>

      {/* Config */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="font-semibold text-slate-900 text-sm flex items-center gap-2 mb-4"><Settings className="w-4 h-4" /> Configuration agent</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between py-2 border-b border-slate-100">
            <span className="text-slate-500">Score minimum proposition</span>
            <span className="text-slate-700 font-medium">70/100</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-100">
            <span className="text-slate-500">Intervalle scan Tier 1</span>
            <span className="text-slate-700 font-medium">5 minutes</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-100">
            <span className="text-slate-500">Intervalle scan Tier 2</span>
            <span className="text-slate-700 font-medium">30 minutes</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-100">
            <span className="text-slate-500">Sources actives</span>
            <span className="text-slate-700 font-medium">14 scrapers</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-slate-500">IA Propositions</span>
            <span className="text-slate-700 font-medium">Claude Sonnet 4</span>
          </div>
        </div>
      </div>
    </div>
  )
}
