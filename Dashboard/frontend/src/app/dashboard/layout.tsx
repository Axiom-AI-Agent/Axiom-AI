"use client";


import {
  ReactNode,
  useEffect,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  Loader2,
} from "lucide-react";

import Sidebar
  from "@/components/Sidebar";

import Header
  from "@/components/Header";

import FloatingChat
  from "@/components/FloatingChat";

import ToastContainer
  from "@/components/ToastContainer";

import {
  AuthProvider,
  useAuth,
} from "@/context/AuthContext";

import {
  TenantProvider,
} from "@/context/TenantContext";

import {
  ToastProvider,
} from "@/context/ToastContext";


interface DashboardLayoutProps {
  children: ReactNode;
}


function ProtectedDashboard({
  children,
}: DashboardLayoutProps) {
  const router =
    useRouter();

  const {
    user,
    loading,
  } = useAuth();

  const [
    sidebarOpen,
    setSidebarOpen,
  ] = useState(false);


  useEffect(() => {
    if (
      !loading
      && !user
    ) {
      router.replace(
        "/login",
      );
    }
  }, [
    loading,
    user,
    router,
  ]);


  if (
    loading
    || !user
  ) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }


  return (
    <TenantProvider>

      <ToastProvider>

        <div className="flex min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-50">

          <Sidebar
            isOpen={
              sidebarOpen
            }
            onClose={() =>
              setSidebarOpen(
                false,
              )
            }
          />


          {sidebarOpen && (
            <div
              className="fixed inset-0 bg-black/50 lg:hidden"
              onClick={() =>
                setSidebarOpen(
                  false,
                )
              }
            />
          )}


          <div className="flex flex-1 flex-col">

            <Header
              onMenuClick={() =>
                setSidebarOpen(
                  (current) =>
                    !current,
                )
              }
            />


            <main className="flex-1 overflow-auto p-6">
              {children}
            </main>

          </div>

        </div>


        <ToastContainer />

        <FloatingChat />

      </ToastProvider>

    </TenantProvider>
  );
}


export default function DashboardLayout({
  children,
}: DashboardLayoutProps) {
  return (
    <AuthProvider>

      <ProtectedDashboard>
        {children}
      </ProtectedDashboard>

    </AuthProvider>
  );
}