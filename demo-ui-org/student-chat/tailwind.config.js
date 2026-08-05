/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}", "../shared/**/*.{js,ts}"],
  theme: {
    extend: {
      colors: {
        wa: {
          header: "#075E54",
          headerDark: "#054C44",
          user: "#DCF8C6",
          bot: "#FFFFFF",
          bg: "#E5DDD5",
          input: "#F0F2F5",
          accent: "#25D366",
          tick: "#34B7F1",
        },
      },
      fontFamily: {
        sans: [
          "Segoe UI",
          "Helvetica Neue",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
      },
      boxShadow: {
        bubble: "0 1px 0.5px rgba(0,0,0,0.13)",
      },
    },
  },
  plugins: [],
};
