import { 
  BarChart3, 
  Users, 
  Target, 
  TrendingUp, 
  Instagram,
  Rocket
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  activeTab, 
  setActiveTab, 
  sidebarOpen, 
  setSidebarOpen 
}) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'prospects', label: 'Prospects', icon: Users },
    { id: 'campaigns', label: 'Campaigns', icon: Target },
    { id: 'deploy', label: 'Deploy', icon: Rocket },
    { id: 'accounts', label: 'Accounts', icon: Instagram },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
  ];

  return (
    <>
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden bg-gray-600 bg-opacity-75"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        lg:translate-x-0 lg:static lg:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-center h-16 px-4 bg-blue-600">
          <div className="flex items-center">
            <Instagram className="h-8 w-8 text-white" />
            <span className="ml-2 text-xl font-semibold text-white">Coach Outreach</span>
          </div>
        </div>
        
        <nav className="mt-8">
          <div className="px-4 space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setSidebarOpen(false);
                  }}
                  className={`
                    w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                    ${activeTab === item.id
                      ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  {item.label}
                </button>
              );
            })}
          </div>
        </nav>
      </div>
    </>
  );
};

export default Sidebar;
