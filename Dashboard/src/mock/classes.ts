// src/mock/classes.ts
export interface ClassItem {
  id: number;
  subject: string;
  fee: number;
  cycle: string;
}

export const classList: ClassItem[] = [
  { id: 1, subject: "Mathematics", fee: 5000, cycle: "Monthly" },
  { id: 2, subject: "Physics", fee: 6000, cycle: "Quarterly" },
  { id: 3, subject: "Chemistry", fee: 5500, cycle: "Monthly" },
];
