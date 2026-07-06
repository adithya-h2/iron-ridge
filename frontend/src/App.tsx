import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { Dashboard } from './pages/Dashboard'
import { Pipeline } from './pages/Pipeline'
import { DealDetail } from './pages/DealDetail'
import { Approvals } from './pages/Approvals'
import { SystemHealth } from './pages/SystemHealth'
import { Settings } from './pages/Settings'
import { ThemeProvider } from './context/ThemeContext'

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="h-screen w-screen flex bg-base overflow-hidden">
          <Sidebar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/deals/:id" element={<DealDetail />} />
            <Route path="/approvals" element={<Approvals />} />
            <Route path="/system-health" element={<SystemHealth />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  )
}
