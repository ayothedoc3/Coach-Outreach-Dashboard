import { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Download,
  BarChart3,
  PieChart as PieChartIcon,
  Activity
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';
import axios from 'axios';

interface AnalyticsData {
  daily_messages: Array<{
    date: string;
    messages: number;
  }>;
  niche_distribution: Array<{
    niche: string;
    count: number;
  }>;
}

const Analytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');

  const API_BASE_URL = (import.meta.env as any).VITE_API_URL || '';

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/analytics/performance`);
      setAnalyticsData(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const mockConversionData = [
    { stage: 'Discovered', count: 1250, percentage: 100 },
    { stage: 'Qualified', count: 875, percentage: 70 },
    { stage: 'Messaged', count: 425, percentage: 34 },
    { stage: 'Responded', count: 85, percentage: 20 },
    { stage: 'Converted', count: 12, percentage: 14 }
  ];

  const mockResponseTimeData = [
    { hour: '0-2h', responses: 45 },
    { hour: '2-4h', responses: 32 },
    { hour: '4-8h', responses: 28 },
    { hour: '8-24h', responses: 15 },
    { hour: '1-3d', responses: 8 },
    { hour: '3d+', responses: 3 }
  ];

  const mockEngagementData = [
    { date: '2024-01-01', opens: 120, clicks: 45, responses: 12 },
    { date: '2024-01-02', opens: 135, clicks: 52, responses: 15 },
    { date: '2024-01-03', opens: 98, clicks: 38, responses: 9 },
    { date: '2024-01-04', opens: 142, clicks: 58, responses: 18 },
    { date: '2024-01-05', opens: 156, clicks: 62, responses: 22 },
    { date: '2024-01-06', opens: 128, clicks: 48, responses: 14 },
    { date: '2024-01-07', opens: 145, clicks: 55, responses: 16 }
  ];

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
        
        <div className="flex items-center space-x-3 mt-4 sm:mt-0">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          
          <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Reach</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">12,450</p>
              <p className="text-sm text-green-600 mt-1">+15.3% from last period</p>
            </div>
            <div className="p-3 rounded-full bg-blue-100">
              <TrendingUp className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Engagement Rate</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">4.2%</p>
              <p className="text-sm text-green-600 mt-1">+0.8% from last period</p>
            </div>
            <div className="p-3 rounded-full bg-green-100">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Conversion Rate</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">2.8%</p>
              <p className="text-sm text-red-600 mt-1">-0.2% from last period</p>
            </div>
            <div className="p-3 rounded-full bg-yellow-100">
              <BarChart3 className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ROI</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">340%</p>
              <p className="text-sm text-green-600 mt-1">+25% from last period</p>
            </div>
            <div className="p-3 rounded-full bg-purple-100">
              <PieChartIcon className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Message Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={analyticsData?.daily_messages || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area 
                type="monotone" 
                dataKey="messages" 
                stroke="#3B82F6" 
                fill="#3B82F6" 
                fillOpacity={0.1}
                name="Messages Sent"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Niche Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analyticsData?.niche_distribution || []}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="count"
                label={({ niche, percent }) => `${niche} ${(percent * 100).toFixed(0)}%`}
              >
                {(analyticsData?.niche_distribution || []).map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Funnel</h3>
          <div className="space-y-4">
            {mockConversionData.map((stage, _index) => (
              <div key={stage.stage} className="relative">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">{stage.stage}</span>
                  <span className="text-sm text-gray-500">{stage.count} ({stage.percentage}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                    style={{ width: `${stage.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Response Time Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mockResponseTimeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="responses" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement Trends</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={mockEngagementData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="opens" 
              stroke="#3B82F6" 
              strokeWidth={2}
              name="Opens"
            />
            <Line 
              type="monotone" 
              dataKey="clicks" 
              stroke="#10B981" 
              strokeWidth={2}
              name="Clicks"
            />
            <Line 
              type="monotone" 
              dataKey="responses" 
              stroke="#F59E0B" 
              strokeWidth={2}
              name="Responses"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h4 className="text-md font-semibold text-gray-900 mb-3">Best Performing Hashtags</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">#businesscoach</span>
              <span className="text-sm font-medium text-gray-900">8.2% CTR</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">#entrepreneur</span>
              <span className="text-sm font-medium text-gray-900">7.5% CTR</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">#lifecoach</span>
              <span className="text-sm font-medium text-gray-900">6.8% CTR</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h4 className="text-md font-semibold text-gray-900 mb-3">Peak Activity Hours</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">9:00 AM - 11:00 AM</span>
              <span className="text-sm font-medium text-gray-900">24%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">2:00 PM - 4:00 PM</span>
              <span className="text-sm font-medium text-gray-900">19%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">7:00 PM - 9:00 PM</span>
              <span className="text-sm font-medium text-gray-900">16%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h4 className="text-md font-semibold text-gray-900 mb-3">Message Templates</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Business Template A</span>
              <span className="text-sm font-medium text-gray-900">12.3%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Life Coach Template B</span>
              <span className="text-sm font-medium text-gray-900">9.8%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Fitness Template C</span>
              <span className="text-sm font-medium text-gray-900">8.5%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
