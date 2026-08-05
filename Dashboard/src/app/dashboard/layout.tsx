"use client"
import '@/app/globals.css';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import { ReactNode, useState } from 'react';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSidebarClose = () => setSidebarOpen(false);
  const handleSidebarToggle = () => setSidebarOpen((prev) => !prev);

  return (
    <div className="flex min-h-screen bg-white dark:bg-gray-900 text-black dark:text-white">
      {/* Sidebar with responsive props */}
      <Sidebar isOpen={sidebarOpen} onClose={handleSidebarClose} />

      {/* Mobile overlay when sidebar is open */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 lg:hidden"
          onClick={handleSidebarClose}
          aria-label="Close sidebar overlay"
        />
      )}

      <div className="flex flex-col flex-1">
        {/* Header receives menu click handler for mobile */}
        <Header onMenuClick={handleSidebarToggle} />
        <main className="p-6 flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
