import { redirect } from "next/navigation";

export default function LegacyPaymentsPage() {
  redirect("/dashboard/inbox?status=open&reason_code=payment_receipt");
}
