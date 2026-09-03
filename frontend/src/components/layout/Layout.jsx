import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import WatchlistAlertToast from '../WatchlistAlertToast';

const Layout = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen bg-dark-bg text-gray-200 overflow-hidden font-sans relative">
      <Sidebar isOpen={isMobileMenuOpen} setIsOpen={setIsMobileMenuOpen} />
      <div className="flex flex-col flex-1 overflow-hidden min-w-0">
        <Topbar onMenuClick={() => setIsMobileMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 custom-scrollbar">
          {children}
        </main>
      </div>
      <WatchlistAlertToast />
    </div>
  );
};

export default Layout;
