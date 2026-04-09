import { NavLink, useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'
import { useAuth } from '../context/AuthContext'
import {
  HiOutlineChartBar,
  HiOutlineChatBubbleLeftRight,
  HiOutlineSquares2X2,
  HiOutlineArrowRightOnRectangle,
  HiOutlineSun,
  HiOutlineMoon,
} from 'react-icons/hi2'

export default function Sidebar() {
  const { darkMode, toggleTheme } = useTheme()
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const navItems = [
    { to: '/app/analysis', label: 'Analysis', icon: HiOutlineChartBar },
    { to: '/app/chat', label: 'AI Chat', icon: HiOutlineChatBubbleLeftRight },
    { to: '/app/dashboard', label: 'Dashboard', icon: HiOutlineSquares2X2 },
  ]

  return (
    <aside className={`w-64 h-screen fixed left-0 top-0 flex flex-col border-r z-40
      ${darkMode 
        ? 'bg-dark-900 border-dark-700/50' 
        : 'bg-white border-gray-200'}`}
    >
      {/* Logo */}
      <div className="p-6 pb-4">
        <h1 className="font-display text-2xl font-bold">
          <span className="gradient-text">Trendify</span>
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 space-y-1">
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `${darkMode ? 'sidebar-link' : 'sidebar-link-light'} ${isActive ? 'active' : ''}`
            }
          >
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom actions */}
      <div className="p-4 space-y-2">
        <button
          onClick={handleLogout}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl w-full transition-all duration-200 font-medium
            ${darkMode 
              ? 'text-red-400 hover:bg-red-500/10' 
              : 'text-red-500 hover:bg-red-50'}`}
        >
          <HiOutlineArrowRightOnRectangle className="w-5 h-5" />
          <span>Logout</span>
        </button>

        <button
          onClick={toggleTheme}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl w-full transition-all duration-200 font-medium
            ${darkMode 
              ? 'text-dark-300 hover:bg-dark-700/50' 
              : 'text-gray-500 hover:bg-gray-100'}`}
        >
          {darkMode ? (
            <>
              <HiOutlineSun className="w-5 h-5" />
              <span>Light Mode</span>
            </>
          ) : (
            <>
              <HiOutlineMoon className="w-5 h-5" />
              <span>Dark Mode</span>
            </>
          )}
        </button>
      </div>
    </aside>
  )
}
