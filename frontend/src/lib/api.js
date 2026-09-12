const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function handleResponse(res) {
  if (!res.ok) {
    let detail = 'Something went wrong. Please try again.'
    try {
      const body = await res.json()
      if (body && body.detail) detail = body.detail
    } catch {
      // response wasn't JSON, keep the default message
    }
    throw new ApiError(detail, res.status)
  }
  if (res.status === 204) return null
  return res.json()
}

export async function getHealth() {
  const res = await fetch(`${API_BASE}/api/health`)
  return handleResponse(res)
}

export async function listProjects() {
  const res = await fetch(`${API_BASE}/api/projects`)
  return handleResponse(res)
}

export async function getProject(id) {
  const res = await fetch(`${API_BASE}/api/projects/${id}`)
  return handleResponse(res)
}

export async function deleteProject(id) {
  const res = await fetch(`${API_BASE}/api/projects/${id}`, { method: 'DELETE' })
  return handleResponse(res)
}

export async function getCommitments(projectId) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/commitments`)
  return handleResponse(res)
}

export async function getWaiting(projectId) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/waiting`)
  return handleResponse(res)
}

export async function getStats(projectId) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/stats`)
  return handleResponse(res)
}

export async function getForgotten(projectId) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/forgotten`)
  return handleResponse(res)
}

export async function analyzeText(text, projectName) {
  const form = new FormData()
  form.append('text', text)
  if (projectName) form.append('project_name', projectName)
  const res = await fetch(`${API_BASE}/api/analyze`, { method: 'POST', body: form })
  return handleResponse(res)
}

export async function analyzeFile(file, projectName) {
  const form = new FormData()
  form.append('file', file)
  if (projectName) form.append('project_name', projectName)
  const res = await fetch(`${API_BASE}/api/analyze`, { method: 'POST', body: form })
  return handleResponse(res)
}

export async function runDemo() {
  const res = await fetch(`${API_BASE}/api/demo`, { method: 'POST' })
  return handleResponse(res)
}

export async function updateCommitment(id, patch) {
  const res = await fetch(`${API_BASE}/api/commitments/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  })
  return handleResponse(res)
}

export async function deleteCommitment(id) {
  const res = await fetch(`${API_BASE}/api/commitments/${id}`, { method: 'DELETE' })
  return handleResponse(res)
}

export async function updateWaiting(id, patch) {
  const res = await fetch(`${API_BASE}/api/waiting/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  })
  return handleResponse(res)
}

export async function deleteWaiting(id) {
  const res = await fetch(`${API_BASE}/api/waiting/${id}`, { method: 'DELETE' })
  return handleResponse(res)
}

export { ApiError }
