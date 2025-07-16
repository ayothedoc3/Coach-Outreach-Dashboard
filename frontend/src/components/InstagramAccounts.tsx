import { useState, useEffect } from 'react';
import { Plus, Settings, Trash2, TestTube, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface InstagramAccount {
  id: number;
  username: string;
  is_active: boolean;
  daily_messages_sent: number;
  daily_limit: number;
  account_status: string;
  last_activity: string | null;
  remaining_today: number;
  created_at: string;
}

const InstagramAccounts: React.FC = () => {
  const [accounts, setAccounts] = useState<InstagramAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newAccount, setNewAccount] = useState({
    username: '',
    session_id: '',
    daily_limit: 40
  });

  const API_BASE_URL = (import.meta.env as any).VITE_API_URL || 'http://localhost:8001';

  const fetchAccounts = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_BASE_URL}/api/instagram-accounts`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAccounts(data);
      }
    } catch (error) {
      console.error('Error fetching accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_BASE_URL}/api/instagram-accounts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newAccount)
      });
      
      if (response.ok) {
        setNewAccount({ username: '', session_id: '', daily_limit: 40 });
        setShowAddForm(false);
        fetchAccounts();
      } else {
        const error = await response.json();
        alert(error.error || 'Failed to add account');
      }
    } catch (error) {
      console.error('Error adding account:', error);
      alert('Failed to add account');
    }
  };

  const handleDeleteAccount = async (accountId: number, username: string) => {
    if (!confirm(`Are you sure you want to delete account ${username}?`)) {
      return;
    }
    
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_BASE_URL}/api/instagram-accounts/${accountId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        fetchAccounts();
      } else {
        const error = await response.json();
        alert(error.error || 'Failed to delete account');
      }
    } catch (error) {
      console.error('Error deleting account:', error);
      alert('Failed to delete account');
    }
  };

  const handleTestAccount = async (accountId: number, _username: string) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_BASE_URL}/api/instagram-accounts/${accountId}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = await response.json();
      alert(result.message);
      
      if (response.ok) {
        fetchAccounts(); // Refresh to update last_activity
      }
    } catch (error) {
      console.error('Error testing account:', error);
      alert('Failed to test account');
    }
  };

  const toggleAccountStatus = async (accountId: number, currentStatus: boolean) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_BASE_URL}/api/instagram-accounts/${accountId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ is_active: !currentStatus })
      });
      
      if (response.ok) {
        fetchAccounts();
      }
    } catch (error) {
      console.error('Error updating account:', error);
    }
  };

  const getStatusIcon = (account: InstagramAccount) => {
    if (!account.is_active) {
      return <XCircle className="w-5 h-5 text-gray-400" />;
    }
    
    switch (account.account_status) {
      case 'active':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'limited':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'suspended':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getUsageColor = (sent: number, limit: number) => {
    const percentage = (sent / limit) * 100;
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Instagram Accounts</h2>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Account
        </button>
      </div>

      {showAddForm && (
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <h3 className="text-lg font-semibold mb-4">Add Instagram Account</h3>
          <form onSubmit={handleAddAccount} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Instagram Username
              </label>
              <input
                type="text"
                value={newAccount.username}
                onChange={(e) => setNewAccount({ ...newAccount, username: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="@username"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Session ID
              </label>
              <textarea
                value={newAccount.session_id}
                onChange={(e) => setNewAccount({ ...newAccount, session_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Instagram session ID from browser cookies"
                rows={3}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Daily Limit
              </label>
              <input
                type="number"
                value={newAccount.daily_limit}
                onChange={(e) => setNewAccount({ ...newAccount, daily_limit: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
                max="50"
                required
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Add Account
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid gap-4">
        {accounts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No Instagram accounts configured. Add your first account to get started.
          </div>
        ) : (
          accounts.map((account) => (
            <div key={account.id} className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getStatusIcon(account)}
                  <div>
                    <h3 className="font-semibold text-lg">@{account.username}</h3>
                    <p className="text-sm text-gray-600 capitalize">
                      Status: {account.account_status}
                      {!account.is_active && ' (Inactive)'}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleTestAccount(account.id, account.username)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-md"
                    title="Test Account"
                  >
                    <TestTube className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => toggleAccountStatus(account.id, account.is_active)}
                    className={`p-2 rounded-md ${
                      account.is_active 
                        ? 'text-gray-600 hover:bg-gray-50' 
                        : 'text-green-600 hover:bg-green-50'
                    }`}
                    title={account.is_active ? 'Deactivate' : 'Activate'}
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteAccount(account.id, account.username)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-md"
                    title="Delete Account"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Daily Usage</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getUsageColor(account.daily_messages_sent, account.daily_limit)}`}
                        style={{ width: `${Math.min((account.daily_messages_sent / account.daily_limit) * 100, 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">
                      {account.daily_messages_sent}/{account.daily_limit}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {account.remaining_today} remaining today
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Last Activity</p>
                  <p className="text-sm font-medium">
                    {account.last_activity 
                      ? new Date(account.last_activity).toLocaleString()
                      : 'Never'
                    }
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default InstagramAccounts;
