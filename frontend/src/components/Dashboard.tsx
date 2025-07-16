import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './Sidebar';
import Overview from './Overview';
import Prospects from './Prospects';
import Campaigns from './Campaigns';
import Analytics from './Analytics';
import InstagramAccounts from './InstagramAccounts';
import { LogOut, Menu, X } from 'lucide-react';

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { logout } = useAuth();

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <Overview />;
      case 'prospects':
        return <Prospects />;
      case 'campaigns':
        return <Campaigns />;
      case 'accounts':
        return <InstagramAccounts />;
      case 'analytics':
        return <Analytics />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              >
                {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
              <h1 className="ml-2 lg:ml-0 text-2xl font-semibold text-gray-900 capitalize">
                {activeTab}
              </h1>
            </div>
            
            <button
              onClick={logout}
              className="flex items-center px-4 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </button>
          </div>
        </header>
        
        <main className="flex-1 overflow-y-auto p-6">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
