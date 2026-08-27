import { Student } from "@/lib/api";

export function studentNeedsAttention(student: Student) {
  if (student.human_mode) {
    return true;
  }
  return (student.enrollments ?? []).some(
    (enrollment) => enrollment.status === "pending",
  );
}
