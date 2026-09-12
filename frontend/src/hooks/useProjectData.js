import { useCallback, useEffect, useState } from 'react'
import * as api from '../lib/api'

const STORAGE_KEY = 'followup:activeProjectId'

export function getStoredProjectId() {
  return localStorage.getItem(STORAGE_KEY)
}

export function setStoredProjectId(id) {
  if (id) localStorage.setItem(STORAGE_KEY, id)
  else localStorage.removeItem(STORAGE_KEY)
}

export function useProjectData(projectId) {
  const [project, setProject] = useState(null)
  const [commitments, setCommitments] = useState([])
  const [waiting, setWaiting] = useState([])
  const [stats, setStats] = useState(null)
  const [forgotten, setForgotten] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = useCallback(async () => {
    if (!projectId) {
      setProject(null)
      setCommitments([])
      setWaiting([])
      setStats(null)
      setForgotten([])
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const [p, c, w, s, f] = await Promise.all([
        api.getProject(projectId),
        api.getCommitments(projectId),
        api.getWaiting(projectId),
        api.getStats(projectId),
        api.getForgotten(projectId),
      ])
      setProject(p)
      setCommitments(c)
      setWaiting(w)
      setStats(s)
      setForgotten(f)
    } catch (e) {
      setError(e.message || 'Could not load this project.')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    refresh()
  }, [refresh])

  return { project, commitments, waiting, stats, forgotten, loading, error, refresh }
}
