import { redirect } from "next/navigation";

/**
 * Root page – redirects to the dashboard overview.
 */
export default function Home() {
  redirect("/dashboard/overview");
  return null;
}
