import React from 'react';

const Layout = ({ children, tabs, activeTab, setActiveTab }) => {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-primary">SmartHireX</h1>
          <p className="text-gray-400 text-sm">AI-Powered Recruitment Platform</p>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4">
          <div className="flex space-x-1 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-3 font-medium transition-colors whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'text-primary border-b-2 border-primary'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <Icon size={20} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-gray-400">
          <p>© 2025 SmartHireX - Team TalentSage</p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;