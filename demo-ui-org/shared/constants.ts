/** Demo Physics Academy — fixed tenant + presenter copy. */

export const TENANT_ID = "tenant-demo-physics";
export const TENANT_NAME = "Demo Physics Academy";
export const TENANT_SHORT = "DPA";

/** Seeded enrolled student from sql/02_seed_demo.sql (Amaya Perera). */
export const ENROLLED_DEMO_PHONE = "94771234567";
export const ENROLLED_DEMO_NAME = "Amaya Perera";

export const SESSION_STORAGE_KEY = "axiom-demo-ui-session";

/** Preset payment slip served by Vite (absolute URL built at runtime). */
export const PAYMENT_SLIP_PATH = "/assets/payment-slip-demo.svg";

export const QUICK_ACTIONS = [
  { id: "enrolled", label: "Enrolled student", text: "Who am I?" },
  { id: "join", label: "Join A/L Physics", text: "Hi, I want to join A/L Physics" },
  { id: "name", label: "My details", text: "My name is Kasun Perera, I study at Royal College, Colombo" },
  { id: "class", label: "Pick class", text: "A/L Physics" },
  { id: "consent", label: "Consent YES", text: "YES" },
  { id: "velocity", label: "Explain velocity", text: "Explain velocity from the tutor notes" },
  { id: "tutor", label: "Speak to sir", text: "Can I speak to sir?" },
  { id: "oos", label: "OOS weather", text: "What's the weather in Colombo?" },
] as const;

export const WELCOME_HINT =
  "New student demo — tap a quick action or type a message. Use Enrolled student for Amaya (seed data), or Reset Demo for a fresh phone.";
