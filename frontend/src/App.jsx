import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import UnifiedUploadFlow from './components/UnifiedUploadFlow';
import ResultsDashboard from './components/ResultsDashboard';
import DebugPanel from './components/DebugPanel';

function App() {
  const [stage, setStage] = useState('landing'); // 'landing', 'upload', 'results'

  const handleSelectMode = (selectedMode) => {
    // All modes now use unified flow
    setStage('upload');
  };

  const handleUploadComplete = () => {
    // After unified upload, go to results
    setStage('results');
  };

  const handleReset = () => {
    setStage('landing');
  };

  const renderContent = () => {
    switch (stage) {
      case 'landing':
        return <LandingPage onSelectMode={handleSelectMode} />;
      case 'upload':
        return <UnifiedUploadFlow onComplete={handleUploadComplete} />;
      case 'results':
        return <ResultsDashboard />;
      default:
        return <LandingPage onSelectMode={handleSelectMode} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 shadow-lg sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-primary cursor-pointer" onClick={handleReset}>
              SmartHireX
            </h1>
            <p className="text-gray-400 text-xs">AI-Powered Recruitment</p>
          </div>
          {stage !== 'landing' && (
            <button onClick={handleReset} className="btn-secondary text-sm">
              Start Over
            </button>
          )}
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {renderContent()}
      </main>

      <footer className="bg-gray-800 border-t border-gray-700 mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-gray-400">
          <p>© 2025 SmartHireX - Team TalentSage | Accenture Gen AI Hackathon</p>
        </div>
      </footer>
    </div>
  );
}

export default App;