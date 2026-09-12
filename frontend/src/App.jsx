import { Routes, Route } from 'react-router-dom'
import AppShell from './components/AppShell'
import Overview from './pages/Overview'
import Analyze from './pages/Analyze'
import FollowUps from './pages/FollowUps'
import Completed from './pages/Completed'

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Overview />} />
        <Route path="/analyze" element={<Analyze />} />
        <Route path="/follow-ups" element={<FollowUps />} />
        <Route path="/completed" element={<Completed />} />
      </Routes>
    </AppShell>
  )
}
