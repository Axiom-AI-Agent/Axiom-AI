"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  Check,
  CreditCard,
  Loader2,
  RefreshCw,
  X,
} from "lucide-react";

import {
  approvePayment,
  getPendingPayments,
  Payment,
  rejectPayment,
} from "@/lib/api";

export default function PaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadPayments = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setPayments(await getPendingPayments());
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Could not load pending payments. Check the backend connection.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadPayments();
  }, [loadPayments]);

  async function handleApprove(paymentId: string) {
    setActionId(paymentId);
    setError(null);
    setSuccess(null);

    try {
      await approvePayment(paymentId);
      setPayments((current) =>
        current.filter((payment) => payment.id !== paymentId),
      );
      setSuccess("Payment approved successfully.");
    } catch (requestError) {
      console.error(requestError);
      setError("The payment could not be approved.");
    } finally {
      setActionId(null);
    }
  }

  async function handleReject(paymentId: string) {
    const confirmed = window.confirm(
      "Are you sure you want to reject this payment?",
    );

    if (!confirmed) {
      return;
    }

    setActionId(paymentId);
    setError(null);
    setSuccess(null);

    try {
      await rejectPayment(paymentId);
      setPayments((current) =>
        current.filter((payment) => payment.id !== paymentId),
      );
      setSuccess("Payment rejected successfully.");
    } catch (requestError) {
      console.error(requestError);
      setError("The payment could not be rejected.");
    } finally {
      setActionId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            Pending Payments
          </h1>
          <p className="mt-1 text-sm text-gray-400">
            Review payment records requiring staff action.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadPayments()}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-200 hover:bg-gray-800 disabled:opacity-50"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-200">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4 text-emerald-200">
          <Check className="h-5 w-5" />
          {success}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-gray-400" />
        </div>
      ) : payments.length === 0 ? (
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-10 text-center">
          <CreditCard className="mx-auto h-10 w-10 text-gray-500" />
          <p className="mt-3 text-gray-300">
            There are no pending payments.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-800">
          <table className="min-w-full divide-y divide-gray-800">
            <thead className="bg-gray-900">
              <tr className="text-left text-xs uppercase tracking-wide text-gray-400">
                <th className="px-5 py-4">Student</th>
                <th className="px-5 py-4">Period</th>
                <th className="px-5 py-4">Amount</th>
                <th className="px-5 py-4">Status</th>
                <th className="px-5 py-4">Submitted</th>
                <th className="px-5 py-4 text-right">
                  Actions
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-800 bg-gray-950">
              {payments.map((payment) => {
                const processing = actionId === payment.id;

                return (
                  <tr key={payment.id}>
                    <td className="px-5 py-4">
                      <p className="text-sm font-medium text-gray-200">
                        {payment.student_name ??
                          payment.student_id}
                      </p>

                      {payment.student_name && (
                        <p className="mt-1 text-xs text-gray-500">
                          {payment.student_id}
                        </p>
                      )}
                    </td>

                    <td className="px-5 py-4 text-sm text-gray-300">
                      {payment.period}
                    </td>

                    <td className="px-5 py-4 text-sm font-medium text-white">
                      LKR{" "}
                      {Number(
                        payment.amount_due,
                      ).toLocaleString()}
                    </td>

                    <td className="px-5 py-4">
                      <span className="rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-300">
                        {payment.status}
                      </span>
                    </td>

                    <td className="px-5 py-4 text-sm text-gray-400">
                      {new Date(
                        payment.created_at,
                      ).toLocaleString()}
                    </td>

                    <td className="px-5 py-4">
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          disabled={processing}
                          onClick={() =>
                            void handleApprove(payment.id)
                          }
                          className="flex items-center gap-1 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
                        >
                          {processing ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Check className="h-4 w-4" />
                          )}
                          Approve
                        </button>

                        <button
                          type="button"
                          disabled={processing}
                          onClick={() =>
                            void handleReject(payment.id)
                          }
                          className="flex items-center gap-1 rounded-lg bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-500 disabled:opacity-50"
                        >
                          <X className="h-4 w-4" />
                          Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
