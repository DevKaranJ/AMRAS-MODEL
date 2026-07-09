import React, { useEffect, useState } from 'react';
import { Dashboard } from './components/Dashboard';

const App: React.FC = () => {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/production/system/resources')
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch((err) => console.error("Error fetching resources:", err));
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>AMRAS Control Panel</h1>
      <p>Welcome to the AI Manga Recap Automation System desktop app.</p>

      <h2>Dashboard Overview</h2>
      <Dashboard />

      <div style={{ marginTop: '40px' }}>
        <h2>System Resources</h2>
        <pre>{JSON.stringify(health, null, 2)}</pre>
      </div>
    </div>
  );
};

export default App;
