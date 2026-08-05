"use client";

import { useEffect } from "react";

/**
 * Placeholder Payments page.
 */
export default function PaymentsPage() {
  useEffect(() => {
    console.log("Payments page loaded");
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white">Payments Module</h1>
      <p className="mt-4 text-gray-300">This is a placeholder page for Payments.</p>
    </div>
  );
}
