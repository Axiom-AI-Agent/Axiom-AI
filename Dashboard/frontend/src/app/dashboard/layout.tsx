"use client";

import '@/app/globals.css';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import ToastContainer from '@/components/ToastContainer';
import { TenantProvider } from '@/context/TenantContext';
import { ToastProvider } from '@/context/ToastContext';
import { ReactNode, useState } from 'react';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSidebarClose = () => setSidebarOpen(false);
  const handleSidebarToggle = () => setSidebarOpen((prev) => !prev);

  return (
    <TenantProvider>
      <ToastProvider>
        <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50">
          <Sidebar isOpen={sidebarOpen} onClose={handleSidebarClose} />

          {sidebarOpen && (
            <div
              className="fixed inset-0 bg-black/50 lg:hidden"
              onClick={handleSidebarClose}
              aria-label="Close sidebar overlay"
            />
          )}

          <div className="flex flex-col flex-1">
            <Header onMenuClick={handleSidebarToggle} />
            <main className="p-6 flex-1 overflow-auto">
              {children}
            </main>
          </div>
        </div>

        <ToastContainer />
      </ToastProvider>
    </TenantProvider>
  );
}
