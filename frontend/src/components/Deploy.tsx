import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Github, 
  Settings, 
  ExternalLink,
  Play,
  Pause,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  Rocket
} from 'lucide-react';
import axios from 'axios';

interface CoolifyConfig {
  id: number;
  name: string;
  api_url: string;
  team_id?: string;
  created_at: string;
}

interface Deployment {
  id: number;
  name: string;
  github_url: string;
  project_type: string;
  status: string;
  deployment_url?: string;
  coolify_config?: {
    id: number;
    name: string;
  };
  created_at: string;
}

const Deploy: React.FC = () => {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [coolifyConfigs, setCoolifyConfigs] = useState<CoolifyConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [newDeployment, setNewDeployment] = useState({
    name: '',
    github_url: '',
    coolify_config_id: '',
    environment_variables: {}
  });
  const [newConfig, setNewConfig] = useState({
    name: '',
    api_url: '',
    api_token: '',
    team_id: ''
  });

  const API_BASE_URL = (import.meta.env as any).VITE_API_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchDeployments();
    fetchCoolifyConfigs();
  }, []);

  const fetchDeployments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/deployments`);
      setDeployments(response.data);
    } catch (error) {
      console.error('Error fetching deployments:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCoolifyConfigs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/coolify-configs`);
      setCoolifyConfigs(response.data);
    } catch (error) {
      console.error('Error fetching Coolify configs:', error);
    }
  };

  const createDeployment = async () => {
    try {
      const deploymentData = {
        ...newDeployment,
        coolify_config_id: parseInt(newDeployment.coolify_config_id)
      };

      await axios.post(`${API_BASE_URL}/api/deployments`, deploymentData);
      setShowCreateModal(false);
      setNewDeployment({
        name: '',
        github_url: '',
        coolify_config_id: '',
        environment_variables: {}
      });
      fetchDeployments();
    } catch (error) {
      console.error('Error creating deployment:', error);
    }
  };

  const createCoolifyConfig = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/coolify-configs`, newConfig);
      setShowConfigModal(false);
      setNewConfig({
        name: '',
        api_url: '',
        api_token: '',
        team_id: ''
      });
      fetchCoolifyConfigs();
    } catch (error) {
      console.error('Error creating Coolify config:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { color: 'bg-gray-100 text-gray-800', icon: Clock },
      building: { color: 'bg-blue-100 text-blue-800', icon: RefreshCw },
      deploying: { color: 'bg-yellow-100 text-yellow-800', icon: Play },
      running: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      failed: { color: 'bg-red-100 text-red-800', icon: XCircle },
      stopped: { color: 'bg-gray-100 text-gray-800', icon: Pause },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${config.color}`}>
        <Icon className="h-3 w-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const extractRepoName = (githubUrl: string) => {
    try {
      const url = new URL(githubUrl);
      const pathParts = url.pathname.split('/').filter(Boolean);
      if (pathParts.length >= 2) {
        return `${pathParts[0]}/${pathParts[1]}`;
      }
      return githubUrl;
    } catch {
      return githubUrl;
    }
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
        <h2 className="text-2xl font-bold text-gray-900">Deploy</h2>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowConfigModal(true)}
            className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            <Settings className="h-4 w-4 mr-2" />
            Configure Coolify
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Deployment
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {deployments.map((deployment) => (
          <div key={deployment.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{deployment.name}</h3>
                <p className="text-sm text-gray-600 mt-1 flex items-center">
                  <Github className="h-4 w-4 mr-1" />
                  {extractRepoName(deployment.github_url)}
                </p>
              </div>
              {getStatusBadge(deployment.status)}
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex items-center text-sm text-gray-600">
                <Rocket className="h-4 w-4 mr-2" />
                {deployment.project_type}
              </div>
              {deployment.coolify_config && (
                <div className="flex items-center text-sm text-gray-600">
                  <Settings className="h-4 w-4 mr-2" />
                  {deployment.coolify_config.name}
                </div>
              )}
              {deployment.deployment_url && (
                <div className="flex items-center text-sm text-gray-600">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  <a 
                    href={deployment.deployment_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 truncate"
                  >
                    {deployment.deployment_url}
                  </a>
                </div>
              )}
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="text-sm text-gray-500">
                {new Date(deployment.created_at).toLocaleDateString()}
              </div>
              <div className="flex space-x-2">
                <button className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-800">
                  <RefreshCw className="h-4 w-4 mr-1" />
                  Refresh
                </button>
                <button className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-800">
                  <Settings className="h-4 w-4 mr-1" />
                  Manage
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {deployments.length === 0 && (
        <div className="text-center py-12">
          <Rocket className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No deployments yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by deploying your first application.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Deployment
            </button>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Deploy New Application</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Application Name</label>
                  <input
                    type="text"
                    value={newDeployment.name}
                    onChange={(e) => setNewDeployment({...newDeployment, name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="my-awesome-app"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">GitHub Repository URL</label>
                  <input
                    type="url"
                    value={newDeployment.github_url}
                    onChange={(e) => setNewDeployment({...newDeployment, github_url: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="https://github.com/username/repo"
                  />
                  <p className="mt-1 text-sm text-gray-500">Project type will be auto-detected</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Coolify Instance</label>
                  <select
                    value={newDeployment.coolify_config_id}
                    onChange={(e) => setNewDeployment({...newDeployment, coolify_config_id: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select Coolify instance</option>
                    {coolifyConfigs.map((config) => (
                      <option key={config.id} value={config.id}>
                        {config.name} ({config.api_url})
                      </option>
                    ))}
                  </select>
                  {coolifyConfigs.length === 0 && (
                    <p className="mt-1 text-sm text-red-500">No Coolify instances configured. Please add one first.</p>
                  )}
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
                  onClick={createDeployment}
                  disabled={!newDeployment.name || !newDeployment.github_url || !newDeployment.coolify_config_id}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Deploy
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showConfigModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Configure Coolify Instance</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Instance Name</label>
                  <input
                    type="text"
                    value={newConfig.name}
                    onChange={(e) => setNewConfig({...newConfig, name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="My Coolify Server"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">API URL</label>
                  <input
                    type="url"
                    value={newConfig.api_url}
                    onChange={(e) => setNewConfig({...newConfig, api_url: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="https://coolify.example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">API Token</label>
                  <input
                    type="password"
                    value={newConfig.api_token}
                    onChange={(e) => setNewConfig({...newConfig, api_token: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Your Coolify API token"
                  />
                  <p className="mt-1 text-sm text-gray-500">Generate this in your Coolify dashboard under API tokens</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Team ID (Optional)</label>
                  <input
                    type="text"
                    value={newConfig.team_id}
                    onChange={(e) => setNewConfig({...newConfig, team_id: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="team-uuid"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowConfigModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  Cancel
                </button>
                <button
                  onClick={createCoolifyConfig}
                  disabled={!newConfig.name || !newConfig.api_url || !newConfig.api_token}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Save Configuration
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Deploy;
