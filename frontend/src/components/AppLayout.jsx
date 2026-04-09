import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import { useTheme } from '../context/ThemeContext'

export default function AppLayout() {
  const { darkMode } = useTheme()

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-dark-950 text-white' : 'bg-gray-50 text-gray-900'}`}>
      <Sidebar />
      <main className="ml-64 min-h-screen">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
