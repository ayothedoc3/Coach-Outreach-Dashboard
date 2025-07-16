import React, { useState, useEffect } from 'react';
import { 
  Users, 
  MessageSquare, 
  TrendingUp, 
  Target,
  Clock,
  CheckCircle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

interface DashboardStats {
  total_prospects: number;
  qualified_prospects: number;
  messages_sent: number;
  responses_received: number;
  messages_today: number;
  recent_prospects: number;
  response_rate: number;
}

const Overview: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = (import.meta.env as any).VITE_API_URL || '';

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const mockChartData = [
    { name: 'Mon', messages: 12, responses: 2 },
    { name: 'Tue', messages: 19, responses: 4 },
    { name: 'Wed', messages: 25, responses: 6 },
    { name: 'Thu', messages: 22, responses: 5 },
    { name: 'Fri', messages: 28, responses: 8 },
    { name: 'Sat', messages: 15, responses: 3 },
    { name: 'Sun', messages: 18, responses: 4 },
  ];

  const mockPieData = [
    { name: 'Business', value: 45, color: '#3B82F6' },
    { name: 'Life', value: 25, color: '#10B981' },
    { name: 'Fitness', value: 20, color: '#F59E0B' },
    { name: 'Mindset', value: 10, color: '#EF4444' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Prospects',
      value: stats?.total_prospects || 0,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%',
    },
    {
      title: 'Messages Sent',
      value: stats?.messages_sent || 0,
      icon: MessageSquare,
      color: 'bg-green-500',
      change: '+8%',
    },
    {
      title: 'Response Rate',
      value: `${stats?.response_rate || 0}%`,
      icon: TrendingUp,
      color: 'bg-yellow-500',
      change: '+2.1%',
    },
    {
      title: 'Qualified Leads',
      value: stats?.qualified_prospects || 0,
      icon: Target,
      color: 'bg-purple-500',
      change: '+15%',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{card.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{card.value}</p>
                  <p className="text-sm text-green-600 mt-1">{card.change} from last week</p>
                </div>
                <div className={`p-3 rounded-full ${card.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="messages" 
                stroke="#3B82F6" 
                strokeWidth={2}
                name="Messages Sent"
              />
              <Line 
                type="monotone" 
                dataKey="responses" 
                stroke="#10B981" 
                strokeWidth={2}
                name="Responses"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Niche Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={mockPieData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {mockPieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Today's Progress</h3>
            <Clock className="h-5 w-5 text-gray-400" />
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Messages Sent</span>
              <span className="text-sm font-medium">{stats?.messages_today || 0}/50</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full" 
                style={{ width: `${((stats?.messages_today || 0) / 50) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
            <CheckCircle className="h-5 w-5 text-green-500" />
          </div>
          <div className="space-y-2">
            <p className="text-sm text-gray-600">New prospects this week</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.recent_prospects || 0}</p>
            <p className="text-sm text-green-600">+25% from last week</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Conversion Rate</h3>
            <TrendingUp className="h-5 w-5 text-green-500" />
          </div>
          <div className="space-y-2">
            <p className="text-sm text-gray-600">Messages to responses</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.response_rate || 0}%</p>
            <p className="text-sm text-green-600">Above industry average</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Overview;
