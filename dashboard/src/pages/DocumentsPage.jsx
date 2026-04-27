import { useState, useEffect } from 'react'
import { fetchMissions, getDevisUrl } from '../lib/supabase'
import { FileText, Download, ExternalLink, User, Receipt, Search } from 'lucide-react'

export default function DocumentsPage() {
  const [missions, setMissions] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const { data } = await fetchMissions({ limit: 100 })
        setMissions((data || []).filter(m => m.status === 'proposal_ready' || m.status === 'sent' || m.status === 'won'))
      } catch (e) {
        console.error(e)
      }
      setLoading(false)
    }
    load()
  }, [])

  const filtered = search
    ? missions.filter(m => m.title?.toLowerCase().includes(search.toLowerCase()) || m.company?.toLowerCase().includes(search.toLowerCase()))
    : missions

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Documents</h2>
        <p className="text-sm text-slate-500 mt-0.5">Devis, profil et documents légaux</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <a href="https://www.malt.fr/profile/baptistethevenot1" target="_blank" rel="noopener noreferrer" className="block bg-white rounded-lg border border-slate-200 p-5 hover:border-slate-300 hover:shadow-sm transition-all group">
          <div className="flex items-start justify-between mb-3">
            <div className="w-9 h-9 rounded-md bg-slate-100 flex items-center justify-center">
              <User className="w-4 h-4 text-slate-700" strokeWidth={1.75} />
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-700" />
          </div>
          <p className="text-sm font-semibold text-slate-900">Profil Malt</p>
          <p className="text-xs text-slate-500 mt-1">CV en ligne, références et avis clients</p>
        </a>

        <div className="bg-white rounded-lg border border-slate-200 p-5">
          <div className="flex items-start justify-between mb-3">
            <div className="w-9 h-9 rounded-md bg-slate-100 flex items-center justify-center">
              <Receipt className="w-4 h-4 text-slate-700" strokeWidth={1.75} />
            </div>
          </div>
          <p className="text-sm font-semibold text-slate-900">Devis types</p>
          <p className="text-xs text-slate-500 mt-1">TJM 450 EUR/jour HT · Forfait 9 000 EUR/mois</p>
          <p className="text-[11px] text-slate-400 mt-2">Générés automatiquement par mission</p>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-5">
          <div className="flex items-start justify-between mb-3">
            <div className="w-9 h-9 rounded-md bg-slate-100 flex items-center justify-center">
              <FileText className="w-4 h-4 text-slate-700" strokeWidth={1.75} />
            </div>
          </div>
          <p className="text-sm font-semibold text-slate-900">Mentions légales</p>
          <div className="text-[11px] text-slate-500 space-y-0.5 mt-2">
            <p>Baptiste Thevenot</p>
            <p>SIRET 849 022 058</p>
            <p>10 chemin de Catala, 31100 Toulouse</p>
            <p>TVA non applicable — art. 293B du CGI</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Devis par mission</h3>
            <p className="text-xs text-slate-500 mt-0.5">{missions.length} devis disponibles</p>
          </div>
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Rechercher..."
              className="w-full pl-9 pr-3 py-1.5 rounded-md border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
            />
          </div>
        </div>
        {loading && <div className="px-5 py-12 text-center text-sm text-slate-400">Chargement...</div>}
        {!loading && filtered.length === 0 && (
          <p className="px-5 py-12 text-center text-sm text-slate-400">Aucun devis disponible. Les devis sont générés pour les missions avec proposition.</p>
        )}
        <div className="divide-y divide-slate-50">
          {filtered.map(m => (
            <div key={m.id} className="flex items-center justify-between px-5 py-3 hover:bg-slate-50 transition-colors">
              <div className="flex items-center gap-3 min-w-0">
                <Receipt className="w-4 h-4 text-slate-400 shrink-0" strokeWidth={1.75} />
                <div className="min-w-0">
                  <p className="text-sm text-slate-900 truncate">{m.title}</p>
                  <p className="text-xs text-slate-500">{m.company || 'Entreprise non précisée'} &middot; Score {m.score}/100</p>
                </div>
              </div>
              <a
                href={getDevisUrl(m.id)}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition-colors shrink-0"
              >
                <Download className="w-3.5 h-3.5" /> Ouvrir le devis
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
