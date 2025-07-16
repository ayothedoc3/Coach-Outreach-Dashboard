import { useState, useEffect } from 'react';
import { 
  Plus, 
  Play, 
  Pause, 
  Settings, 
  Hash,
  Users,
  MessageSquare,
  TrendingUp,
  Target,
  Instagram
} from 'lucide-react';
import axios from 'axios';

interface Campaign {
  id: number;
  name: string;
  description: string;
  hashtags: string[];
  target_accounts: string[];
  instagram_account_id?: number;
  instagram_account?: {
    id: number;
    username: string;
    is_active: boolean;
  };
  status: string;
  messages_sent: number;
  responses_received: number;
  conversions: number;
  daily_limit: number;
  created_at: string;
}

interface InstagramAccount {
  id: number;
  username: string;
  is_active: boolean;
  daily_messages_sent: number;
  daily_limit: number;
  account_status: string;
}

const Campaigns: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [instagramAccounts, setInstagramAccounts] = useState<InstagramAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newCampaign, setNewCampaign] = useState({
    name: '',
    description: '',
    hashtags: '',
    target_accounts: '',
    instagram_account_id: '',
    daily_limit: 50
  });

  const API_BASE_URL = (import.meta.env as any).VITE_API_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchCampaigns();
    fetchInstagramAccounts();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/campaigns`);
      setCampaigns(response.data);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInstagramAccounts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/instagram-accounts`);
      setInstagramAccounts(response.data);
    } catch (error) {
      console.error('Error fetching Instagram accounts:', error);
    }
  };

  const createCampaign = async () => {
    try {
      const campaignData = {
        ...newCampaign,
        hashtags: newCampaign.hashtags.split(',').map(h => h.trim()).filter(h => h),
        target_accounts: newCampaign.target_accounts.split(',').map(a => a.trim()).filter(a => a),
        instagram_account_id: newCampaign.instagram_account_id ? parseInt(newCampaign.instagram_account_id) : null
      };

      await axios.post(`${API_BASE_URL}/api/campaigns`, campaignData);
      setShowCreateModal(false);
      setNewCampaign({
        name: '',
        description: '',
        hashtags: '',
        target_accounts: '',
        instagram_account_id: '',
        daily_limit: 50
      });
      fetchCampaigns();
    } catch (error) {
      console.error('Error creating campaign:', error);
    }
  };

  const startCampaign = async (campaignId: number) => {
    try {
      await axios.post(`${API_BASE_URL}/api/campaigns/${campaignId}/start`);
      fetchCampaigns();
    } catch (error) {
      console.error('Error starting campaign:', error);
    }
  };

  const pauseCampaign = async (campaignId: number) => {
    try {
      await axios.post(`${API_BASE_URL}/api/campaigns/${campaignId}/pause`);
      fetchCampaigns();
    } catch (error) {
      console.error('Error pausing campaign:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      active: 'bg-green-100 text-green-800',
      paused: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-blue-100 text-blue-800',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[status as keyof typeof statusColors] || statusColors.paused}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Campaigns</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Campaign
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {campaigns.map((campaign) => (
          <div key={campaign.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{campaign.description}</p>
              </div>
              {getStatusBadge(campaign.status)}
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex items-center text-sm text-gray-600">
                <Hash className="h-4 w-4 mr-2" />
                {campaign.hashtags.length} hashtags
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Users className="h-4 w-4 mr-2" />
                {campaign.target_accounts.length} target accounts
              </div>
              {campaign.instagram_account && (
                <div className="flex items-center text-sm text-gray-600">
                  <Instagram className="h-4 w-4 mr-2" />
                  @{campaign.instagram_account.username}
                </div>
              )}
              <div className="flex items-center text-sm text-gray-600">
                <MessageSquare className="h-4 w-4 mr-2" />
                {campaign.messages_sent} messages sent
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <TrendingUp className="h-4 w-4 mr-2" />
                {campaign.responses_received} responses
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="text-sm text-gray-500">
                Daily limit: {campaign.daily_limit}
              </div>
              <div className="flex space-x-2">
                {campaign.status === 'active' ? (
                  <button
                    onClick={() => pauseCampaign(campaign.id)}
                    className="flex items-center px-3 py-1 text-sm text-yellow-600 hover:text-yellow-800"
                  >
                    <Pause className="h-4 w-4 mr-1" />
                    Pause
                  </button>
                ) : (
                  <button
                    onClick={() => startCampaign(campaign.id)}
                    className="flex items-center px-3 py-1 text-sm text-green-600 hover:text-green-800"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Start
                  </button>
                )}
                <button className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-800">
                  <Settings className="h-4 w-4 mr-1" />
                  Settings
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {campaigns.length === 0 && (
        <div className="text-center py-12">
          <Target className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No campaigns yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your first campaign.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Campaign
            </button>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Campaign</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Campaign Name</label>
                  <input
                    type="text"
                    value={newCampaign.name}
                    onChange={(e) => setNewCampaign({...newCampaign, name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter campaign name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    value={newCampaign.description}
                    onChange={(e) => setNewCampaign({...newCampaign, description: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    rows={3}
                    placeholder="Campaign description"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Hashtags</label>
                  <input
                    type="text"
                    value={newCampaign.hashtags}
                    onChange={(e) => setNewCampaign({...newCampaign, hashtags: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="businesscoach, lifecoach, entrepreneur"
                  />
                  <p className="mt-1 text-sm text-gray-500">Separate hashtags with commas</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Target Accounts</label>
                  <input
                    type="text"
                    value={newCampaign.target_accounts}
                    onChange={(e) => setNewCampaign({...newCampaign, target_accounts: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="competitor1, competitor2"
                  />
                  <p className="mt-1 text-sm text-gray-500">Separate usernames with commas</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Instagram Account</label>
                  <select
                    value={newCampaign.instagram_account_id}
                    onChange={(e) => setNewCampaign({...newCampaign, instagram_account_id: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Auto-select best account</option>
                    {instagramAccounts.filter(acc => acc.is_active).map((account) => (
                      <option key={account.id} value={account.id}>
                        @{account.username} ({account.daily_messages_sent}/{account.daily_limit} today)
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-sm text-gray-500">Leave empty to automatically select the best available account</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Daily Message Limit</label>
                  <input
                    type="number"
                    value={newCampaign.daily_limit}
                    onChange={(e) => setNewCampaign({...newCampaign, daily_limit: parseInt(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    min="1"
                    max="50"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  Cancel
                </button>
                <button
                  onClick={createCampaign}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
                >
                  Create Campaign
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Campaigns;
