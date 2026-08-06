// src/components/MetricCard.tsx
import { ReactNode } from "react";
import { motion } from "framer-motion";

interface MetricCardProps {
  title: string;
  value: number | string;
  icon?: ReactNode;
}

export default function MetricCard({ title, value, icon }: MetricCardProps) {
  return (
    <motion.div
      className="flex items-center p-4 bg-gradient-to-r from-gray-800 to-gray-700 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {icon && <div className="mr-4 text-gray-200">{icon}</div>}
      <div>
        <p className="text-sm text-gray-300 uppercase">{title}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
      </div>
    </motion.div>
  );
}
