import { useState } from 'react'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setError('')
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query.trim() }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Search failed')
      }

      const data = await response.json()
      setResults(data.results || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>🧠 AI Video Search</h1>
        <p>Search through Microsoft AI Show episodes using semantic similarity (Gemini Embeddings).</p>
      </header>

      <main className="main-content">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-bar">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything — e.g. 'What are Jupyter Notebooks?'"
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !query.trim()}>
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && <div className="error-message">Error: {error}</div>}

        <div className="results-container">
          {results.length > 0 && !isLoading && (
            <h2>Found Top-{results.length} results</h2>
          )}

          {results.map((result, idx) => (
            <div key={result.id || idx} className="result-card">
              <div className="card-header">
                <h3><span className="rank-badge">#{idx + 1}</span> {result.title}</h3>
                <div className="similarity-score">
                  <span className="score-label">Similarity</span>
                  <span className="score-value">{result.similarity}%</span>
                </div>
              </div>
              
              <div className="card-meta">
                <span className="meta-item">🗣️ <strong>Speaker:</strong> {result.speaker}</span>
                <span className="meta-item">⏱️ <strong>Time:</strong> {result.start || '00:00:00'}</span>
              </div>
              
              <p className="card-summary">{result.summary}</p>
              
              <div className="card-footer">
                <a 
                  href={`https://www.youtube.com/watch?v=${result.videoId}&t=${Math.floor(result.seconds)}s`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="youtube-btn"
                >
                  ▶️ Watch on YouTube
                </a>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}

export default App
