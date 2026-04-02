import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { logout } from '../lib/auth'
import {
  LayoutDashboard, Crosshair, FileText, FolderOpen,
  Settings, LogOut, Menu, X, Zap
} from 'lucide-react'
import { useState } from 'react'

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/missions', icon: Crosshair, label: 'Missions' },
  { to: '/proposals', icon: FileText, label: 'Propositions' },
  { to: '/documents', icon: FolderOpen, label: 'Documents' },
  { to: '/settings', icon: Settings, label: 'Paramètres' },
]

export default function Layout({ session, onLogout }) {
  const [open, setOpen] = useState(false)
  const location = useLocation()

  function handleLogout() {
    logout()
    onLogout()
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile overlay */}
      {open && <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setOpen(false)} />}

      {/* Sidebar */}
      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-[#0f172a] text-white flex flex-col transition-transform duration-200 ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="flex items-center gap-3 px-5 py-5 border-b border-white/10">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <p className="font-semibold text-sm leading-tight">SNB Mission Hunter</p>
            <p className="text-[11px] text-slate-400">{session.name}</p>
          </div>
        </div>

        <nav className="flex-1 py-4 px-3 space-y-1">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-white/5 hover:text-white'
                }`
              }
            >
              <Icon className="w-[18px] h-[18px]" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 py-4 border-t border-white/10">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-white/5 w-full transition-colors"
          >
            <LogOut className="w-[18px] h-[18px]" />
            Déconnexion
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-14 bg-white border-b border-slate-200 flex items-center px-4 lg:px-6 shrink-0">
          <button onClick={() => setOpen(true)} className="lg:hidden p-1 mr-3 text-slate-500 hover:text-slate-700">
            <Menu className="w-5 h-5" />
          </button>
          <h1 className="text-sm font-semibold text-slate-700 capitalize">
            {NAV.find(n => n.to === location.pathname)?.label || 'Mission Hunter'}
          </h1>
          <div className="ml-auto flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-50 text-green-700 text-xs font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              Agent actif
            </span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
