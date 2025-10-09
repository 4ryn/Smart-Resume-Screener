import React from 'react';
import { Upload, Target, ArrowRight, Briefcase, Users, Zap } from 'lucide-react';

const LandingPage = ({ onSelectMode }) => {
  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="text-center max-w-5xl mx-auto">
        <div className="mb-12">
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            SmartHireX
          </h1>
          <p className="text-2xl text-gray-300 mb-4">
            Complete AI-Powered Recruitment Solution
          </p>
          <p className="text-lg text-gray-400">
            Upload job descriptions and resumes together, let AI do the matching and screening
          </p>
        </div>

        {/* Single Main Action Card */}
        <div className="max-w-2xl mx-auto mb-12">
          <div
            onClick={() => onSelectMode('unified')}
            className="card hover:shadow-2xl hover:scale-105 transition-all cursor-pointer border-2 border-transparent hover:border-gradient-to-r hover:from-blue-500 hover:to-purple-500 group relative overflow-hidden"
          >
            {/* Animated background gradient */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            
            <div className="relative z-10 text-center py-12 px-8">
              <div className="bg-gradient-to-r from-blue-500 to-purple-500 w-32 h-32 rounded-full flex items-center justify-center mx-auto mb-8 group-hover:scale-110 transition-transform duration-300">
                <Target size={64} className="text-white" />
              </div>
              
              <h3 className="text-3xl font-bold mb-4 group-hover:text-blue-400 transition-colors">
                Start Smart Recruitment
              </h3>
              
              <p className="text-gray-400 mb-8 text-lg leading-relaxed">
                Upload both job descriptions and candidate resumes.<br/>
                Our AI will analyze, match, and create shortlists automatically.
              </p>
              
              <div className="flex items-center justify-center space-x-3 text-blue-400 group-hover:text-blue-300 text-xl font-semibold">
                <Zap size={24} />
                <span>Begin AI Screening</span>
                <ArrowRight size={24} className="group-hover:translate-x-2 transition-transform" />
              </div>
            </div>
          </div>
        </div>

        {/* Feature highlights */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
            <Upload className="text-blue-400 mb-4 mx-auto" size={48} />
            <h4 className="font-semibold mb-2">Upload Everything</h4>
            <p className="text-gray-400 text-sm">Job descriptions (CSV) and candidate resumes (PDF/DOCX) in one place</p>
          </div>
          
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
            <Target className="text-purple-400 mb-4 mx-auto" size={48} />
            <h4 className="font-semibold mb-2">AI Matching</h4>
            <p className="text-gray-400 text-sm">Advanced AI analyzes skills, experience, and requirements for perfect matches</p>
          </div>
          
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
            <Users className="text-pink-400 mb-4 mx-auto" size={48} />
            <h4 className="font-semibold mb-2">Smart Shortlisting</h4>
            <p className="text-gray-400 text-sm">Automatic candidate ranking and interview scheduling with email notifications</p>
          </div>
        </div>

        <div className="mt-12 p-6 bg-gray-800/50 rounded-lg">
          <h4 className="font-semibold mb-3">How it works:</h4>
          <div className="grid md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="bg-blue-500 rounded-full w-8 h-8 flex items-center justify-center text-white font-bold">1</div>
              <span>Upload Files</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="bg-blue-500 rounded-full w-8 h-8 flex items-center justify-center text-white font-bold">2</div>
              <span>AI Processing</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="bg-blue-500 rounded-full w-8 h-8 flex items-center justify-center text-white font-bold">3</div>
              <span>Smart Matching</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="bg-blue-500 rounded-full w-8 h-8 flex items-center justify-center text-white font-bold">4</div>
              <span>View Results</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;