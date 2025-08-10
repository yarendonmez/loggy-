import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  BarChart3, 
  Upload, 
  Settings, 
  Bell,
  Activity,
  Shield,
  AlertTriangle,
  Sun,
  Moon,
  Globe
} from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useTheme } from '../context/ThemeContext';
import { translations } from '../translations/translations';

const Navbar = () => {
  const location = useLocation();
  const { isDark, toggleTheme, language, changeLanguage } = useTheme();
  const t = translations[language];

  const navItems = [
    { path: '/', icon: BarChart3, label: t.dashboard, color: 'text-blue-600' },
    { path: '/upload', icon: Upload, label: t.logUpload, color: 'text-green-600' },
    { path: '/analysis', icon: Activity, label: t.analysis, color: 'text-purple-600' },
    { path: '/settings', icon: Settings, label: t.settings, color: 'text-gray-600' },
  ];

  return (
    <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Shield className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900 dark:text-white">Loggy</span>
          </div>
          <Badge variant="secondary" className="ml-2">
            AI Log Analizi
          </Badge>
        </div>

        {/* Navigation Links */}
        <div className="hidden md:flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link key={item.path} to={item.path}>
                <Button
                  variant={isActive ? "default" : "ghost"}
                  className={`flex items-center space-x-2 px-4 py-2 ${
                    isActive ? 'bg-blue-600 text-white' : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Button>
              </Link>
            );
          })}
        </div>

        {/* Right Side */}
        <div className="flex items-center space-x-3">
          {/* Language Toggle */}
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => changeLanguage(language === 'tr' ? 'en' : 'tr')}
            className="text-gray-600 dark:text-gray-300"
          >
            <Globe className="h-5 w-5" />
          </Button>

          {/* Theme Toggle */}
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={toggleTheme}
            className="text-gray-600 dark:text-gray-300"
          >
            {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>

          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5 text-gray-600 dark:text-gray-300" />
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
            >
              3
            </Badge>
          </Button>

          {/* Critical Alert */}
          <Button variant="destructive" size="sm" className="flex items-center space-x-2">
            <AlertTriangle className="h-4 w-4" />
            <span>{t.critical}</span>
          </Button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
