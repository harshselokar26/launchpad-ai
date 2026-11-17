
import { useEffect, useState } from "react";
import {
  Search,
  MapPin,
  Briefcase,
  ExternalLink,
  RefreshCw,
  Sparkles
} from "lucide-react";

import "./App.css";

const API = import.meta.env.VITE_API_URL;

export default function App() {
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState({});
  const [search, setSearch] = useState("");
  const [city, setCity] = useState("");
  const [role, setRole] = useState("");
  const [fresher, setFresher] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function fetchJobs() {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams();

      if (search) params.set("search", search);
      if (city) params.set("city", city);
      if (role) params.set("role", role);
      if (fresher) params.set("fresher_only", "true");

      const response = await fetch(
        `${API}/api/jobs/?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error("Unable to load jobs");
      }

      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function fetchStats() {
    try {
      const response = await fetch(`${API}/api/jobs/stats`);
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error("Stats error:", err);
    }
  }

  useEffect(() => {
    fetchJobs();
    fetchStats();
  }, []);

  function handleSubmit(event) {
    event.preventDefault();
    fetchJobs();
  }

  return (
    <div className="app">
      <header className="navbar">
        <a className="brand" href="/">
          <span className="brand-icon">
            <Sparkles size={21} />
          </span>
          LaunchPad<span className="brand-ai">AI</span>
        </a>

        <span className="nav-label">
          India's fresher job discovery platform
        </span>
      </header>

      <main>
        <section className="hero">
          <span className="eyebrow">
            <Sparkles size={14} />
            AI-POWERED JOB DISCOVERY
          </span>

          <h1>
            Your first job starts
            <br />
            <span>with the right opportunity.</span>
          </h1>

          <p>
            Discover fresher jobs and internships
            across India in one place.
          </p>

          <form className="search-panel" onSubmit={handleSubmit}>
            <div className="search-field">
              <Search size={19} />
              <input
                placeholder="Job title, skill or company"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <div className="search-field">
              <MapPin size={19} />
              <input
                placeholder="City"
                value={city}
                onChange={(e) => setCity(e.target.value)}
              />
            </div>

            <button className="search-button">
              Search jobs
            </button>
          </form>

          <label className="fresher-toggle">
            <input
              type="checkbox"
              checked={fresher}
              onChange={(e) => setFresher(e.target.checked)}
            />
            Only show fresher-friendly opportunities
          </label>
        </section>

        <section className="stats">
          <Stat
            label="Total opportunities"
            value={stats.total_jobs ?? 0}
          />
          <Stat
            label="Fresher friendly"
            value={stats.fresher_jobs ?? 0}
          />
          <Stat
            label="Internships"
            value={stats.internships ?? 0}
          />
          <Stat
            label="Cities"
            value={stats.cities ?? 0}
          />
        </section>

        <section className="jobs-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">OPPORTUNITIES</span>
              <h2>Latest job openings</h2>
            </div>

            <button
              className="refresh-button"
              onClick={() => {
                fetchJobs();
                fetchStats();
              }}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>

          {loading && (
            <p className="message">Loading opportunities...</p>
          )}

          {error && (
            <p className="error">{error}</p>
          )}

          {!loading && !error && jobs.length === 0 && (
            <div className="empty-state">
              <Briefcase size={30} />
              <h3>No matching jobs found</h3>
              <p>Try another search or location.</p>
            </div>
          )}

          <div className="job-grid">
            {jobs.map((job) => (
              <article className="job-card" key={job.id}>
                <div className="job-top">
                  <div className="company-avatar">
                    {job.company?.charAt(0)?.toUpperCase()}
                  </div>

                  <span className="source">
                    {job.source}
                  </span>
                </div>

                <h3>{job.title}</h3>
                <p className="company">{job.company}</p>

                <div className="job-meta">
                  <span>
                    <MapPin size={14} />
                    {job.city || job.location || "Location unknown"}
                  </span>
                  <span>
                    <Briefcase size={14} />
                    {job.job_type || "Not specified"}
                  </span>
                </div>

                <div className="tags">
                  {job.role && <span>{job.role}</span>}

                  {job.experience_level && (
                    <span>{job.experience_level}</span>
                  )}

                  {job.fresher_eligible === true && (
                    <span className="eligible">Fresher friendly</span>
                  )}
                </div>

                <div className="job-bottom">
                  <span className="confidence">
                    AI confidence: {Math.round(
                      (job.confidence || 0) * 100
                    )}%
                  </span>

                  <a
                    href={job.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Apply <ExternalLink size={14} />
                  </a>
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>

      <footer>
        <strong>LaunchPad AI</strong>
        <span>Discover your next opportunity.</span>
      </footer>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="stat-card">
      <h3>{value}</h3>
      <p>{label}</p>
    </div>
  );
}