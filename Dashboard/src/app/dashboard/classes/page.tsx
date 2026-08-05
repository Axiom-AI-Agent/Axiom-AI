"use client";

import { useEffect } from "react";

/**
 * Simple placeholder for Classes module.
 */
export default function ClassesPage() {
  // Placeholder effect to demonstrate client component
  useEffect(() => {
    console.log("Classes page loaded");
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white">Classes Module</h1>
      <p className="mt-4 text-gray-300">This is a placeholder page for the Classes view.</p>
    </div>
  );
}
