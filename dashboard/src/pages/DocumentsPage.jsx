import { useState, useEffect } from 'react'
import { fetchMissions, getDevisUrl } from '../lib/supabase'
import { FileText, Download, ExternalLink, File, User } from 'lucide-react'

export default function DocumentsPage() {
  const [missions, setMissions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const { data } = await fetchMissions({ limit: 50, status: 'proposal_ready' })
        setMissions(data || [])
      } catch (e) {
        console.error(e)
      }
      setLoading(false)
    }
    load()
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Documents</h2>
        <p className="text-sm text-slate-500">Devis, CV et documents téléchargeables</p>
      </div>

      {/* Static documents */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <User className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">CV Baptiste Thevenot</p>
              <p className="text-xs text-slate-400">Consultant Web & IA</p>
            </div>
          </div>
          <p className="text-xs text-slate-500 mb-4">CV professionnel — React, Shopify, Claude API, automatisation, stratégie digitale</p>
          <a
            href="https://www.malt.fr/profile/baptistethevenot1"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-600 text-white text-xs font-medium hover:bg-blue-700 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" /> Profil Malt
          </a>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <FileText className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">Modèle de devis</p>
              <p className="text-xs text-slate-400">TJM 450EUR/jour — HT</p>
            </div>
          </div>
          <p className="text-xs text-slate-500 mb-4">Devis auto-généré par l'agent pour chaque mission. TVA non applicable art. 293B du CGI.</p>
          <span className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-100 text-slate-500 text-xs font-medium">
            <File className="w-3.5 h-3.5" /> Généré par mission
          </span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
              <FileText className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">Informations légales</p>
              <p className="text-xs text-slate-400">SIRET & contact</p>
            </div>
          </div>
          <div className="text-xs text-slate-500 space-y-1">
            <p>Baptiste Thevenot</p>
            <p>SIRET : 849 022 058</p>
            <p>bp.thevenot@gmail.com</p>
            <p>06 86 50 43 79</p>
            <p>10 chemin de Catala, 31100 Toulouse</p>
          </div>
        </div>
      </div>

      {/* Devis by mission */}
      <div className="bg-white rounded-xl border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-100">
          <h3 className="font-semibold text-slate-900 text-sm">Devis par mission</h3>
          <p className="text-xs text-slate-400 mt-0.5">Cliquez pour ouvrir et imprimer le devis</p>
        </div>
        {loading && <div className="px-5 py-8 text-center text-sm text-slate-400">Chargement...</div>}
        <div className="divide-y divide-slate-100">
          {missions.map(m => (
            <div key={m.id} className="flex items-center justify-between px-5 py-3 hover:bg-slate-50 transition-colors">
              <div className="flex items-center gap-3 min-w-0">
                <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                <div className="min-w-0">
                  <p className="text-sm text-slate-700 truncate">{m.title}</p>
                  <p className="text-xs text-slate-400">{m.company || 'N/A'} — Score {m.score}/100</p>
                </div>
              </div>
              <a
                href={getDevisUrl(m.id)}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-white border border-slate-200 text-slate-600 hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 transition-colors shrink-0"
              >
                <Download className="w-3.5 h-3.5" /> Ouvrir le devis
              </a>
            </div>
          ))}
          {!loading && missions.length === 0 && (
            <p className="px-5 py-8 text-center text-sm text-slate-400">Aucun devis disponible. Les devis sont générés pour les missions avec propositions.</p>
          )}
        </div>
      </div>
    </div>
  )
}
