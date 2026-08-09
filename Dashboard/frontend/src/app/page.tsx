import Link from "next/link";

import {
  ArrowRight,
  BookOpen,
  Bot,
  LayoutDashboard,
  MessageSquare,
  ShieldCheck,
} from "lucide-react";

const features = [
  {
    icon: Bot,
    title: "AI Student Support",
    description:
      "Automate common student questions, class inquiries, and resource requests.",
  },
  {
    icon: MessageSquare,
    title: "Conversation Monitoring",
    description:
      "View student conversations and handle escalations that need human attention.",
  },
  {
    icon: BookOpen,
    title: "Class & Resource Management",
    description:
      "Manage classes and upload tutor resources for AI-powered retrieval.",
  },
  {
    icon: LayoutDashboard,
    title: "Operations Dashboard",
    description:
      "Track students, classes, payments, conversations, and activity in one place.",
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Navigation */}
      <header className="border-b border-slate-800/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link
            href="/"
            className="flex items-center gap-3"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/logo.png"
              alt="Axiom AI"
              className="h-9 w-auto"
            />

            <span className="text-xl font-bold tracking-tight">
              Axiom AI
            </span>
          </Link>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="hidden rounded-lg px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-800 hover:text-white sm:block"
            >
              Sign In
            </Link>

            <Link
              href="/login"
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500"
            >
              Open Dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute left-1/2 top-20 -z-0 h-96 w-96 -translate-x-1/2 rounded-full bg-blue-600/10 blur-3xl" />

        <div className="relative z-10 mx-auto max-w-7xl px-6 pb-24 pt-24 text-center sm:pt-32">
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-2 text-sm text-blue-300">
            <ShieldCheck className="h-4 w-4" />
            AI-powered tuition operations
          </div>

          <h1 className="mx-auto max-w-4xl text-4xl font-bold tracking-tight sm:text-6xl">
            Run your tuition classes with
            <span className="text-blue-500">
              {" "}
              intelligent automation
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg">
            Axiom AI helps tuition institutes manage
            students, conversations, classes, payments,
            learning resources, and escalations from one
            dashboard.
          </p>

          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              href="/login"
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-500 sm:w-auto"
            >
              Try the Demo
              <ArrowRight className="h-5 w-5" />
            </Link>

            <Link
              href="/register"
              className="w-full rounded-lg border border-slate-700 px-6 py-3 font-medium text-slate-200 transition hover:bg-slate-800 sm:w-auto"
            >
              Register Institution
            </Link>
          </div>

          <p className="mt-4 text-xs text-slate-500">
            Use “Proceed to Demo” on the login page for
            instant access.
          </p>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="px-6 pb-24">
        <div className="mx-auto max-w-6xl">
          <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl shadow-blue-950/20">
            <div className="flex items-center gap-2 border-b border-slate-800 px-5 py-4">
              <div className="h-3 w-3 rounded-full bg-red-400/70" />
              <div className="h-3 w-3 rounded-full bg-amber-400/70" />
              <div className="h-3 w-3 rounded-full bg-emerald-400/70" />

              <span className="ml-3 text-xs text-slate-500">
                Axiom AI Dashboard
              </span>
            </div>

            <div className="grid gap-4 p-6 sm:grid-cols-2 lg:grid-cols-4">
              <DashboardCard
                label="Students"
                value="128"
              />

              <DashboardCard
                label="Active Classes"
                value="12"
              />

              <DashboardCard
                label="Open Escalations"
                value="4"
              />

              <DashboardCard
                label="Pending Payments"
                value="7"
              />
            </div>

            <div className="grid gap-5 px-6 pb-6 md:grid-cols-5">
              <div className="rounded-xl border border-slate-800 bg-slate-950 p-5 md:col-span-3">
                <p className="text-sm font-medium">
                  Recent Activity
                </p>

                <div className="mt-5 space-y-4">
                  <ActivityRow
                    title="Student requested Physics notes"
                    detail="Resource agent • just now"
                  />

                  <ActivityRow
                    title="Payment receipt requires review"
                    detail="Escalation • 5 min ago"
                  />

                  <ActivityRow
                    title="New student registration"
                    detail="Admissions agent • 12 min ago"
                  />
                </div>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950 p-5 md:col-span-2">
                <p className="text-sm font-medium">
                  AI Operations
                </p>

                <div className="mt-5 space-y-3">
                  <StatusRow
                    label="Student support"
                    status="Active"
                  />

                  <StatusRow
                    label="Resource retrieval"
                    status="Active"
                  />

                  <StatusRow
                    label="Escalation workflow"
                    status="Active"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-y border-slate-800 bg-slate-900/40 px-6 py-24">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <p className="text-sm font-medium text-blue-400">
              Built for tuition operations
            </p>

            <h2 className="mt-2 text-3xl font-bold">
              Everything staff need in one place
            </h2>

            <p className="mt-3 text-slate-400">
              Keep the AI handling routine work while staff
              maintain visibility and control through the
              dashboard.
            </p>
          </div>

          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => {
              const Icon = feature.icon;

              return (
                <div
                  key={feature.title}
                  className="rounded-xl border border-slate-800 bg-slate-900 p-5"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400">
                    <Icon className="h-5 w-5" />
                  </div>

                  <h3 className="mt-4 font-semibold">
                    {feature.title}
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-24">
        <div className="mx-auto max-w-4xl rounded-2xl border border-blue-500/20 bg-blue-500/10 px-6 py-12 text-center">
          <h2 className="text-3xl font-bold">
            See Axiom AI in action
          </h2>

          <p className="mx-auto mt-3 max-w-xl text-slate-400">
            Explore the preconfigured Demo Physics
            institution and see the dashboard, students,
            classes, conversations, and AI workflows.
          </p>

          <Link
            href="/login"
            className="mt-7 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-medium transition hover:bg-blue-500"
          >
            Launch Demo Dashboard
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 px-6 py-7">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 text-sm text-slate-500 sm:flex-row">
          <div className="flex items-center gap-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/logo.png"
              alt="Axiom AI"
              className="h-6 w-auto"
            />

            <span>Axiom AI</span>
          </div>

          <span>
            AI-powered tuition management platform
          </span>
        </div>
      </footer>
    </main>
  );
}

function DashboardCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
      <p className="text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-3xl font-semibold text-white">
        {value}
      </p>
    </div>
  );
}

function ActivityRow({
  title,
  detail,
}: {
  title: string;
  detail: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-1.5 h-2 w-2 rounded-full bg-blue-500" />

      <div>
        <p className="text-sm text-slate-200">
          {title}
        </p>

        <p className="mt-1 text-xs text-slate-500">
          {detail}
        </p>
      </div>
    </div>
  );
}

function StatusRow({
  label,
  status,
}: {
  label: string;
  status: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-800 px-3 py-3">
      <span className="text-sm text-slate-300">
        {label}
      </span>

      <span className="flex items-center gap-2 text-xs text-emerald-400">
        <span className="h-2 w-2 rounded-full bg-emerald-400" />
        {status}
      </span>
    </div>
  );
}