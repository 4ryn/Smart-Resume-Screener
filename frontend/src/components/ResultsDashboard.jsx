import React, { useState, useEffect } from 'react';
import { getDashboardStats, getMatchResults, getShortlist, triggerShortlisting, triggerScheduling } from '../services/api';
import { TrendingUp, Users, Award, Target, Mail, RefreshCw, Loader } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const ResultsDashboard = () => {
  const [stats, setStats] = useState(null);
  const [matches, setMatches] = useState([]);
  const [shortlist, setShortlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds to catch new data
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      console.log('🔄 Fetching dashboard data...');
      
      const [statsRes, matchesRes, shortlistRes] = await Promise.all([
        getDashboardStats().catch(err => {
          console.error('Stats API error:', err);
          return { data: { total_jobs: 0, total_candidates: 0, total_shortlisted: 0, avg_match_score: 0, emails_sent: 0 } };
        }),
        getMatchResults().catch(err => {
          console.error('Matches API error:', err);
          return { data: [] };
        }),
        getShortlist().catch(err => {
          console.error('Shortlist API error:', err);
          return { data: [] };
        })
      ]);
      
      console.log('📊 API Responses:', {
        stats: statsRes.data,
        matches: matchesRes.data?.length || 0,
        matchesData: matchesRes.data,
        shortlist: shortlistRes.data?.length || 0
      });
      
      setStats(statsRes.data);
      setMatches(matchesRes.data || []);
      setShortlist(shortlistRes.data || []);
    } catch (err) {
      console.error('❌ Error fetching data:', err);
      // Set default values on error
      setStats({ total_jobs: 0, total_candidates: 0, total_shortlisted: 0, avg_match_score: 0, emails_sent: 0 });
      setMatches([]);
      setShortlist([]);
    } finally {
      setLoading(false);
    }
  };

  const handleShortlist = async () => {
    try {
      setProcessing(true);
      await triggerShortlisting();
      await fetchData();
    } catch (err) {
      console.error('Shortlisting error:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handleScheduleEmails = async () => {
    try {
      setProcessing(true);
      await triggerScheduling();
      await fetchData();
    } catch (err) {
      console.error('Scheduling error:', err);
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <Loader className="animate-spin mx-auto mb-4" size={48} />
        <p>Loading results...</p>
      </div>
    );
  }

  const topMatches = matches.slice(0, 5);
  
  // Score distribution
  const scoreRanges = [
    { range: '90-100%', count: matches.filter(m => m.match_score >= 90).length, color: '#10B981' },
    { range: '80-89%', count: matches.filter(m => m.match_score >= 80 && m.match_score < 90).length, color: '#3B82F6' },
    { range: '70-79%', count: matches.filter(m => m.match_score >= 70 && m.match_score < 80).length, color: '#F59E0B' },
    { range: '<70%', count: matches.filter(m => m.match_score < 70).length, color: '#EF4444' }
  ];

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold mb-2">Match Results</h2>
          <p className="text-gray-400">
            AI-powered candidate-job matching results with compatibility scores
          </p>
        </div>
        <div className="flex space-x-4">
          <button 
            onClick={handleShortlist}
            disabled={processing}
            className="btn-primary flex items-center space-x-2"
          >
            <Award size={20} />
            <span>Create Shortlist</span>
          </button>
          <button 
            onClick={handleScheduleEmails}
            disabled={processing || shortlist.length === 0}
            className="btn-secondary flex items-center space-x-2"
          >
            <Mail size={20} />
            <span>Send Emails</span>
          </button>
          <button 
            onClick={() => {
              console.log('🔄 Manual refresh triggered');
              fetchData();
            }} 
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw size={20} />
            <span>Refresh Data</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Matches</p>
              <p className="text-3xl font-bold">{matches.length}</p>
            </div>
            <Target className="text-blue-400" size={32} />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Avg Score</p>
              <p className="text-3xl font-bold">{stats?.avg_match_score || 0}%</p>
            </div>
            <TrendingUp className="text-green-400" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Shortlisted</p>
              <p className="text-3xl font-bold">{stats?.total_shortlisted || 0}</p>
            </div>
            <Award className="text-purple-400" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Emails Sent</p>
              <p className="text-3xl font-bold">{stats?.emails_sent || 0}</p>
            </div>
            <Mail className="text-pink-400" size={32} />
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* Score Distribution Pie Chart */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Score Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={scoreRanges}
                dataKey="count"
                nameKey="range"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
              >
                {scoreRanges.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Matches Bar Chart */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Top 5 Matches</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={topMatches}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }} />
              <Bar dataKey="match_score" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Matches Table */}
      <div className="card">
        <h3 className="text-xl font-semibold mb-4">Top Matches Details</h3>
        <div className="space-y-3">
          {topMatches.length > 0 ? topMatches.map((match, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-4 flex items-center justify-between hover:bg-gray-600 transition-colors">
              <div className="flex items-center space-x-4">
                <div className="bg-blue-500 rounded-full w-10 h-10 flex items-center justify-center text-white font-bold">
                  #{index + 1}
                </div>
                <div>
                  <p className="font-semibold">{match.name}</p>
                  <p className="text-sm text-gray-400">{match.job_title || 'No job assigned'}</p>
                  <p className="text-xs text-gray-500">{match.email}</p>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-2xl font-bold ${
                  match.match_score >= 80 ? 'text-green-400' :
                  match.match_score >= 70 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {match.match_score}%
                </p>
                <p className="text-xs text-gray-400">Match Score</p>
              </div>
            </div>
          )) : (
            <div className="text-center py-8 text-gray-400">
              <p>No matches found yet. Upload some files to get started!</p>
            </div>
          )}
        </div>
      </div>

      {shortlist.length > 0 && (
        <div className="card mt-8">
          <h3 className="text-xl font-semibold mb-4">Shortlisted Candidates</h3>
          <div className="space-y-3">
            {shortlist.map((candidate, index) => (
              <div key={index} className="bg-gray-700 rounded-lg p-4 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="bg-purple-500 rounded-full w-10 h-10 flex items-center justify-center text-white font-bold">
                    S{index + 1}
                  </div>
                  <div>
                    <p className="font-semibold">{candidate.name}</p>
                    <p className="text-sm text-gray-400">{candidate.job_title}</p>
                    <p className="text-xs text-gray-500">{candidate.email}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-purple-400">{candidate.match_score}%</p>
                  <p className={`text-xs ${candidate.email_sent ? 'text-green-400' : 'text-gray-400'}`}>
                    {candidate.email_sent ? 'Email Sent' : 'Pending'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsDashboard;