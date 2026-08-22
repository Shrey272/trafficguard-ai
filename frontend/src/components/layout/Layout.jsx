import React from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

const Layout = ({ children }) => {
  return (
    <div className="flex h-screen bg-dark-bg text-gray-200 overflow-hidden font-sans">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 custom-scrollbar">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
