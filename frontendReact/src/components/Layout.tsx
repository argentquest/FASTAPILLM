import React from 'react';
import { NavLink } from 'react-router-dom';
import { useQuery } from 'react-query';
import { Book, MessageCircle, History, DollarSign, FileText, Cpu } from 'lucide-react';
import { systemApi } from '../services/api';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { data: providerInfo } = useQuery('providerInfo', systemApi.getProviderInfo);

  const navigation = [
    { name: 'Generate Story', href: '/', icon: Book },
    { name: 'Chat', href: '/chat', icon: MessageCircle },
    { name: 'History', href: '/history', icon: History },
    { name: 'Cost Tracking', href: '/cost', icon: DollarSign },
    { name: 'Context', href: '/context', icon: FileText },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-primary-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Book className="h-8 w-8 text-white" />
                <span className="ml-2 text-xl font-bold text-white">
                  AI Story Generator
                </span>
                <span className="ml-2 text-xs bg-primary-700 text-primary-100 px-2 py-1 rounded">
                  React
                </span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      className={({ isActive }) =>
                        `inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200 ${
                          isActive
                            ? 'border-white text-white'
                            : 'border-transparent text-primary-100 hover:border-primary-300 hover:text-white'
                        }`
                      }
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.name}
                    </NavLink>
                  );
                })}
              </div>
            </div>
            
            {/* Provider Info */}
            <div className="flex items-center">
              <div className="flex items-center text-primary-100 text-sm">
                <Cpu className="h-4 w-4 mr-2" />
                <span>Provider: {providerInfo?.provider || 'Loading...'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        <div className="sm:hidden">
          <div className="pt-2 pb-3 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200 ${
                      isActive
                        ? 'bg-primary-700 border-primary-300 text-white'
                        : 'border-transparent text-primary-100 hover:bg-primary-700 hover:border-primary-300 hover:text-white'
                    }`
                  }
                >
                  <div className="flex items-center">
                    <Icon className="h-4 w-4 mr-3" />
                    {item.name}
                  </div>
                </NavLink>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;