import React, { useState, useEffect } from 'react';

const DebugPanel = () => {
  const [backendStatus, setBackendStatus] = useState('checking...');
  const [apiResults, setApiResults] = useState({});

  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      // Test health endpoint
      const response = await fetch('/api/health');
      if (response.ok) {
        setBackendStatus('✅ Connected');
        testAllEndpoints();
      } else {
        setBackendStatus('❌ Backend responding but unhealthy');
      }
    } catch (error) {
      setBackendStatus('❌ Cannot connect to backend');
      console.error('Backend connection error:', error);
    }
  };

  const testAllEndpoints = async () => {
    const endpoints = [
      { name: 'Dashboard Stats', url: '/api/dashboard/stats' },
      { name: 'Match Results', url: '/api/matching/results' },
      { name: 'Shortlist', url: '/api/matching/shortlist' },
      { name: 'Jobs', url: '/api/jobs' },
      { name: 'Candidates', url: '/api/candidates' }
    ];

    const results = {};

    for (const endpoint of endpoints) {
      try {
        const response = await fetch(endpoint.url);
        const data = await response.json();
        
        results[endpoint.name] = {
          status: response.status,
          success: response.ok,
          data: Array.isArray(data) ? `${data.length} items` : JSON.stringify(data).substring(0, 100) + '...'
        };
      } catch (error) {
        results[endpoint.name] = {
          status: 'ERROR',
          success: false,
          data: error.message
        };
      }
    }

    setApiResults(results);
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-xl font-bold mb-4">🔧 Debug Panel</h2>
      
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Backend Status:</h3>
        <p className={`p-2 rounded ${backendStatus.includes('✅') ? 'bg-green-900' : 'bg-red-900'}`}>
          {backendStatus}
        </p>
      </div>

      <div>
        <h3 className="font-semibold mb-2">API Endpoints:</h3>
        <div className="space-y-2">
          {Object.entries(apiResults).map(([name, result]) => (
            <div key={name} className={`p-2 rounded text-sm ${result.success ? 'bg-green-900' : 'bg-red-900'}`}>
              <div className="font-medium">{name}: {result.status}</div>
              <div className="text-xs text-gray-300">{result.data}</div>
            </div>
          ))}
        </div>
      </div>

      <button 
        onClick={() => { checkBackendConnection(); testAllEndpoints(); }}
        className="mt-4 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
      >
        🔄 Refresh Tests
      </button>
    </div>
  );
};

export default DebugPanel;