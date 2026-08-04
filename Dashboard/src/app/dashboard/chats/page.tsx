"use client";

import { useEffect } from "react";

/**
 * Placeholder Chats page.
 */
export default function ChatsPage() {
  useEffect(() => {
    console.log("Chats page loaded");
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white">Chats Module</h1>
      <p className="mt-4 text-gray-300">This is a placeholder page for Chats.</p>
    </div>
  );
}
