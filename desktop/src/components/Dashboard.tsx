import React, { useEffect, useState } from 'react';

interface DashboardStats {
  projects_count: number;
  running_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  storage_usage_bytes: number;
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = () => {
      fetch('http://localhost:8000/production/dashboard')
        .then((res) => {
          if (!res.ok) throw new Error("Failed to fetch dashboard data");
          return res.json();
        })
        .then((data) => {
          setStats(data);
          setError(null);
        })
        .catch((err) => {
          console.error("Dashboard fetch error:", err);
          setError(err.message);
        });
    };

    fetchDashboard();
    const intervalId = setInterval(fetchDashboard, 5000); // refresh every 5s

    return () => clearInterval(intervalId);
  }, []);

  if (error) {
    return <div style={{ color: 'red' }}>Error loading dashboard: {error}</div>;
  }

  if (!stats) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', padding: '20px' }}>
      <div style={cardStyle}>
        <h3>Total Projects</h3>
        <p style={numberStyle}>{stats.projects_count}</p>
      </div>
      <div style={cardStyle}>
        <h3>Running Jobs</h3>
        <p style={numberStyle}>{stats.running_jobs}</p>
      </div>
      <div style={cardStyle}>
        <h3>Completed Jobs</h3>
        <p style={numberStyle}>{stats.completed_jobs}</p>
      </div>
      <div style={cardStyle}>
        <h3>Failed Jobs</h3>
        <p style={{ ...numberStyle, color: 'red' }}>{stats.failed_jobs}</p>
      </div>
    </div>
  );
};

const cardStyle = {
  border: '1px solid #ddd',
  borderRadius: '8px',
  padding: '16px',
  backgroundColor: '#f9f9f9',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

const numberStyle = {
  fontSize: '2em',
  margin: '10px 0',
  fontWeight: 'bold'
};
