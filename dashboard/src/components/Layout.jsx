import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { logout } from '../lib/auth'
import { useState, useEffect } from 'react'
import {
  LayoutDashboard, Briefcase, FileText, FolderOpen,
  Settings, LogOut, Menu, Activity, ChevronRight,
} from 'lucide-react'
import { fetchStats } from '../lib/supabase'

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Vue d\'ensemble' },
  { to: '/missions', icon: Briefcase, label: 'Missions' },
  { to: '/proposals', icon: FileText, label: 'Propositions' },
  { to: '/documents', icon: FolderOpen, label: 'Documents' },
  { to: '/agent', icon: Activity, label: 'Agent' },
  { to: '/settings', icon: Settings, label: 'Paramètres' },
]

export default function Layout({ session, onLogout }) {
  const [open, setOpen] = useState(false)
  const [agentStatus, setAgentStatus] = useState(null)
  const location = useLocation()

  useEffect(() => {
    let active = true
    async function poll() {
      const s = await fetchStats().catch(() => null)
      if (active) setAgentStatus(s)
    }
    poll()
    const id = setInterval(poll, 60000)
    return () => { active = false; clearInterval(id) }
  }, [])

  function handleLogout() {
    logout()
    onLogout()
  }

  const isOnline = agentStatus?.status === 'running'
  const currentPage = NAV.find(n => location.pathname === n.to || (n.to !== '/' && location.pathname.startsWith(n.to)))

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {open && <div className="fixed inset-0 bg-slate-900/40 z-40 lg:hidden backdrop-blur-sm" onClick={() => setOpen(false)} />}

      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 flex flex-col transition-transform duration-200 ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="px-5 py-5 border-b border-slate-100">
          <p className="text-[11px] font-semibold tracking-[0.15em] text-slate-400 uppercase">Mission Hunter</p>
          <p className="text-sm font-semibold text-slate-900 mt-1">{session.name}</p>
          <p className="text-[11px] text-slate-500 mt-0.5">{session.role === 'tech' ? 'Consultant Web & IA' : 'Support & Administration'}</p>
        </div>

        <nav className="flex-1 py-3 px-3 space-y-0.5 overflow-y-auto">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md text-[13px] font-medium transition-colors ${
                  isActive ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`
              }
            >
              <Icon className="w-4 h-4" strokeWidth={1.75} />
              <span className="flex-1">{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="px-3 py-3 border-t border-slate-100">
          <div className="flex items-center gap-2 px-3 py-2 mb-1">
            <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${isOnline ? 'bg-emerald-500' : 'bg-slate-300'}`} />
            <span className="text-[11px] font-medium text-slate-500">
              {isOnline ? 'Agent en ligne' : 'Agent hors ligne'}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-md text-[13px] text-slate-500 hover:bg-slate-50 hover:text-slate-900 w-full transition-colors"
          >
            <LogOut className="w-4 h-4" strokeWidth={1.75} />
            Déconnexion
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 bg-white border-b border-slate-200 flex items-center px-4 lg:px-8 shrink-0">
          <button onClick={() => setOpen(true)} className="lg:hidden p-1 mr-3 text-slate-500 hover:text-slate-900">
            <Menu className="w-5 h-5" strokeWidth={1.75} />
          </button>
          <div className="flex items-center gap-2 text-[13px]">
            <span className="text-slate-400">SNB</span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-300" strokeWidth={2} />
            <span className="font-medium text-slate-900">{currentPage?.label || 'Mission Hunter'}</span>
          </div>
          <div className="ml-auto flex items-center gap-3">
            {agentStatus && (
              <span className="hidden sm:inline-flex text-[11px] text-slate-500">
                {agentStatus.missions_today ?? 0} missions · {agentStatus.proposals_today ?? 0} propositions aujourd'hui
              </span>
            )}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-4 lg:px-8 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
