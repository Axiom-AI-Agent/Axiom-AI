"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import {
  Building2,
  ClipboardList,
  Loader2,
  Plus,
  Trash2,
  Users,
} from "lucide-react";

import {
  AuthApiError,
  registerOrganization,
} from "@/lib/auth-api";

import {
  saveAuthSession,
} from "@/lib/auth";

import type {
  OnboardingFieldType,
  StaffRegistration,
  StaffRole,
} from "@/types/auth";

type DraftOnboardingField = {
  label: string;
  field_key: string;
  field_type: OnboardingFieldType;
  required: boolean;
  optionsText: string;
  keyEdited: boolean;
};

const RESERVED_FIELD_KEYS = new Set([
  "name",
  "phone",
  "class",
  "course",
  "consent",
]);

function slugifyFieldKey(label: string): string {
  return label
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 64);
}

function emptyOnboardingField(): DraftOnboardingField {
  return {
    label: "",
    field_key: "",
    field_type: "text",
    required: true,
    optionsText: "",
    keyEdited: false,
  };
}

function defaultOnboardingFields(): DraftOnboardingField[] {
  return [
    {
      label: "School",
      field_key: "school",
      field_type: "text",
      required: true,
      optionsText: "",
      keyEdited: true,
    },
    {
      label: "District",
      field_key: "district",
      field_type: "text",
      required: true,
      optionsText: "",
      keyEdited: true,
    },
  ];
}

function emptyStaff(): StaffRegistration {
  return {
    name: "",
    email: "",
    password: "",
    role: "viewer",
  };
}

export default function RegisterPage() {
  const router = useRouter();

  const [
    institutionName,
    setInstitutionName,
  ] = useState("");

  const [
    whatsappNumber,
    setWhatsappNumber,
  ] = useState("");

  const [
    driveFolderId,
    setDriveFolderId,
  ] = useState("");

  const [
    adminName,
    setAdminName,
  ] = useState("");

  const [
    adminEmail,
    setAdminEmail,
  ] = useState("");

  const [
    adminPassword,
    setAdminPassword,
  ] = useState("");

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("");

  const [
    staffMembers,
    setStaffMembers,
  ] = useState<StaffRegistration[]>([]);

  const [
    onboardingFields,
    setOnboardingFields,
  ] = useState<DraftOnboardingField[]>(
    defaultOnboardingFields,
  );

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(null);

  function addStaff() {
    if (staffMembers.length >= 5) {
      setError(
        "You can add up to five staff members during onboarding.",
      );
      return;
    }

    setStaffMembers((current) => [
      ...current,
      emptyStaff(),
    ]);
  }

  function updateStaff(
    index: number,
    field: keyof StaffRegistration,
    value: string,
  ) {
    setStaffMembers((current) =>
      current.map((staff, staffIndex) =>
        staffIndex === index
          ? {
              ...staff,
              [field]:
                field === "role"
                  ? (value as StaffRole)
                  : value,
            }
          : staff,
      ),
    );
  }

  function removeStaff(index: number) {
    setStaffMembers((current) =>
      current.filter(
        (_, staffIndex) =>
          staffIndex !== index,
      ),
    );
  }

  function addOnboardingField() {
    if (onboardingFields.length >= 15) {
      setError("You can add up to 15 custom onboarding fields.");
      return;
    }
    setOnboardingFields((current) => [
      ...current,
      emptyOnboardingField(),
    ]);
  }

  function updateOnboardingField(
    index: number,
    patch: Partial<DraftOnboardingField>,
  ) {
    setOnboardingFields((current) =>
      current.map((field, fieldIndex) => {
        if (fieldIndex !== index) {
          return field;
        }
        const next = { ...field, ...patch };
        if (
          patch.label !== undefined &&
          !next.keyEdited
        ) {
          next.field_key = slugifyFieldKey(patch.label);
        }
        return next;
      }),
    );
  }

  function removeOnboardingField(index: number) {
    setOnboardingFields((current) =>
      current.filter((_, fieldIndex) => fieldIndex !== index),
    );
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError(null);

    if (
      !institutionName.trim() ||
      !adminName.trim() ||
      !adminEmail.trim() ||
      !adminPassword
    ) {
      setError(
        "Complete all required organization and administrator fields.",
      );
      return;
    }

    if (adminPassword.length < 8) {
      setError(
        "Administrator password must be at least 8 characters.",
      );
      return;
    }

    if (adminPassword !== confirmPassword) {
      setError(
        "Administrator passwords do not match.",
      );
      return;
    }

    const incompleteStaff =
      staffMembers.some(
        (staff) =>
          !staff.name.trim() ||
          !staff.email.trim() ||
          staff.password.length < 8,
      );

    if (incompleteStaff) {
      setError(
        "Complete every added staff member. Passwords must be at least 8 characters.",
      );
      return;
    }

    const incompleteFields = onboardingFields.some(
      (field) => !field.label.trim() || !field.field_key.trim(),
    );
    if (incompleteFields) {
      setError("Each onboarding field needs a label and key.");
      return;
    }

    const fieldKeys = onboardingFields.map((field) =>
      field.field_key.trim().toLowerCase(),
    );
    if (fieldKeys.some((key) => RESERVED_FIELD_KEYS.has(key))) {
      setError(
        "Name, phone, class, and consent are always collected — do not add them as custom fields.",
      );
      return;
    }
    if (new Set(fieldKeys).size !== fieldKeys.length) {
      setError("Onboarding field keys must be unique.");
      return;
    }

    const invalidSelect = onboardingFields.some((field) => {
      if (field.field_type !== "select") {
        return false;
      }
      const options = field.optionsText
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
      return options.length < 2;
    });
    if (invalidSelect) {
      setError("Select fields need at least two comma-separated options.");
      return;
    }

    setLoading(true);

    try {
      const response =
        await registerOrganization({
          institution_name:
            institutionName.trim(),

          whatsapp_number:
            whatsappNumber.trim() ||
            null,

          drive_folder_id:
            driveFolderId.trim() ||
            null,

          admin: {
            name:
              adminName.trim(),

            email:
              adminEmail
                .trim()
                .toLowerCase(),

            password:
              adminPassword,
          },

          staff_members:
            staffMembers.map(
              (staff) => ({
                ...staff,

                name:
                  staff.name.trim(),

                email:
                  staff.email
                    .trim()
                    .toLowerCase(),
              }),
            ),

          onboarding_fields:
            onboardingFields.map(
              (field, index) => ({
                field_key:
                  field.field_key
                    .trim()
                    .toLowerCase(),
                label: field.label.trim(),
                field_type: field.field_type,
                required: field.required,
                sort_order: index,
                options:
                  field.field_type ===
                  "select"
                    ? field.optionsText
                        .split(",")
                        .map((item) =>
                          item.trim(),
                        )
                        .filter(Boolean)
                    : null,
              }),
            ),
        });

      saveAuthSession(response);

      router.replace(
        "/dashboard/overview",
      );
    } catch (requestError: unknown) {
      console.error(requestError);

      if (
        requestError instanceof
        AuthApiError
      ) {
        let message =
          "Organization registration failed.";

        if (
          typeof requestError.details ===
            "object" &&
          requestError.details !== null &&
          "detail" in
            requestError.details
        ) {
          const detail = (
            requestError.details as {
              detail?: unknown;
            }
          ).detail;

          if (
            typeof detail ===
            "string"
          ) {
            message = detail;
          }
        }

        setError(message);
      } else {
        setError(
          "Could not connect to the authentication server.",
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-ink px-4 py-10 text-white">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-ember">
            <Building2 className="h-6 w-6" />
          </div>

          <h1 className="mt-4 text-3xl font-semibold">
            Create your institution
          </h1>

          <p className="mt-2 text-sm text-muted">
            Set up your organization,
            administrator, student onboarding
            questions, and initial staff
            accounts.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-6"
        >
          {error && (
            <div className="rounded-lg border border-border bg-surface p-4 text-sm text-fg">
              {error}
            </div>
          )}

          <section className="rounded-xl border border-border bg-indigo p-6">
            <h2 className="text-lg font-semibold">
              Institution
            </h2>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="space-y-2 sm:col-span-2">
                <span className="text-sm text-muted">
                  Institution name *
                </span>

                <input
                  required
                  value={institutionName}
                  onChange={(event) =>
                    setInstitutionName(
                      event.target.value,
                    )
                  }
                  placeholder="Apex Physics Academy"
                  className="w-full rounded-lg border border-border bg-ink px-3 py-2.5 outline-none focus:border-indigo-soft"
                />
              </label>

              <label className="space-y-2 sm:col-span-2">
                <span className="text-sm text-muted">
                  WhatsApp number
                </span>

                <input
                  value={whatsappNumber}
                  onChange={(event) =>
                    setWhatsappNumber(
                      event.target.value,
                    )
                  }
                  placeholder="94771234567"
                  className="w-full rounded-lg border border-border bg-ink px-3 py-2.5 outline-none focus:border-indigo-soft"
                />
              </label>

              <label className="space-y-2 sm:col-span-2">
                <span className="text-sm text-muted">
                  Google Drive Folder ID
                </span>

                <input
                  value={driveFolderId}
                  onChange={(event) =>
                    setDriveFolderId(
                      event.target.value,
                    )
                  }
                  placeholder="1AbC..."
                  className="w-full rounded-lg border border-border bg-ink px-3 py-2.5 outline-none focus:border-indigo-soft"
                />
              </label>
            </div>
          </section>

          <section className="rounded-xl border border-border bg-indigo p-6">
            <h2 className="text-lg font-semibold">
              Administrator
            </h2>

            <p className="mt-1 text-sm text-muted">
              This account receives full
              organization access.
            </p>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="space-y-2">
                <span className="text-sm text-muted">
                  Full name *
                </span>

                <input
                  required
                  value={adminName}
                  onChange={(event) =>
                    setAdminName(
                      event.target.value,
                    )
                  }
                  className="w-full rounded-lg border border-border bg-ink px-3 py-2.5 outline-none focus:border-indigo-soft"
                />
              </label>

              <label className="space-y-2">
                <span className="text-sm text-muted">
                  Email *
                </span>

                <input
                  type="email"
                  required
                  value={adminEmail}
                  onChange={(event) =>
                    setAdminEmail(
                      event.target.value,
                    )
                  }
                  className="w-full rounded-lg border border-border bg-ink px-3 py-2.5 outline-none focus:border-indigo-soft"
                />
              </label>

              <label className="space-y-2">
                <span className="text-sm text-muted">
                  Password *
                </span>

                <input
                  type="password"
                  minLength={8}
                  required
                  value={adminPassword}
                  onChange={(event) =>
                    setAdminPassword(
                      event.target.value,
                    )
                  }
                  className="w-full rounded-lg border border-border bg-ink px-3 py-2.5 outline-none focus:border-indigo-soft"
                />
              </label>

              <label className="space-y-2">
                <span className="text-sm text-muted">
                  Confirm password *
                </span>

                <input
                  type="password"
                  minLength={8}
                  required
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(
                      event.target.value,
                    )
                  }
                  className="w-full rounded-lg border border-border bg-ink px-3 py-2.5 outline-none focus:border-indigo-soft"
                />
              </label>
            </div>
          </section>

          <section className="rounded-xl border border-border bg-indigo p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-muted" />

                  <h2 className="text-lg font-semibold">
                    Initial staff
                  </h2>
                </div>

                <p className="mt-1 text-sm text-muted">
                  Optional — add up to five
                  staff accounts.
                </p>
              </div>

              <button
                type="button"
                onClick={addStaff}
                disabled={
                  staffMembers.length >=
                  5
                }
                className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm hover:bg-surface disabled:opacity-50"
              >
                <Plus className="h-4 w-4" />
                Add staff
              </button>
            </div>

            {staffMembers.length === 0 ? (
              <div className="mt-5 rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted">
                You can skip this and add
                staff later.
              </div>
            ) : (
              <div className="mt-5 space-y-4">
                {staffMembers.map(
                  (staff, index) => (
                    <div
                      key={index}
                      className="rounded-xl border border-border bg-ink p-4"
                    >
                      <div className="mb-4 flex items-center justify-between">
                        <h3 className="font-medium">
                          Staff member{" "}
                          {index + 1}
                        </h3>

                        <button
                          type="button"
                          onClick={() =>
                            removeStaff(
                              index,
                            )
                          }
                          className="rounded-lg p-2 text-muted hover:bg-hover"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>

                      <div className="grid gap-4 sm:grid-cols-2">
                        <input
                          required
                          placeholder="Full name"
                          value={staff.name}
                          onChange={(event) =>
                            updateStaff(
                              index,
                              "name",
                              event.target
                                .value,
                            )
                          }
                          className="rounded-lg border border-border bg-indigo px-3 py-2.5 outline-none focus:border-indigo-soft"
                        />

                        <input
                          required
                          type="email"
                          placeholder="Email"
                          value={staff.email}
                          onChange={(event) =>
                            updateStaff(
                              index,
                              "email",
                              event.target
                                .value,
                            )
                          }
                          className="rounded-lg border border-border bg-indigo px-3 py-2.5 outline-none focus:border-indigo-soft"
                        />

                        <input
                          required
                          type="password"
                          minLength={8}
                          placeholder="Temporary password"
                          value={staff.password}
                          onChange={(event) =>
                            updateStaff(
                              index,
                              "password",
                              event.target
                                .value,
                            )
                          }
                          className="rounded-lg border border-border bg-indigo px-3 py-2.5 outline-none focus:border-indigo-soft"
                        />

                        <select
                          value={staff.role}
                          onChange={(event) =>
                            updateStaff(
                              index,
                              "role",
                              event.target
                                .value,
                            )
                          }
                          className="rounded-lg border border-border bg-indigo px-3 py-2.5 outline-none focus:border-indigo-soft"
                        >
                          <option value="admin">
                            Admin
                          </option>

                          <option value="tutor">
                            Tutor
                          </option>

                          <option value="marker">
                            Marker
                          </option>

                          <option value="viewer">
                            Viewer
                          </option>
                        </select>
                      </div>
                    </div>
                  ),
                )}
              </div>
            )}
          </section>

          <section className="rounded-xl border border-border bg-indigo p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <ClipboardList className="h-5 w-5 text-muted" />
                  <h2 className="text-lg font-semibold">
                    Student onboarding fields
                  </h2>
                </div>
                <p className="mt-1 text-sm text-muted">
                  Name, phone, class, and
                  consent are always collected.
                  Add extra questions here.
                  This is locked after you
                  create the institution.
                </p>
              </div>
              <button
                type="button"
                onClick={addOnboardingField}
                disabled={onboardingFields.length >= 15}
                className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm hover:bg-surface disabled:opacity-50"
              >
                <Plus className="h-4 w-4" />
                Add field
              </button>
            </div>

            {onboardingFields.length === 0 ? (
              <div className="mt-5 rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted">
                No extra fields — students will
                only be asked for name, then
                class.
              </div>
            ) : (
              <div className="mt-5 space-y-4">
                {onboardingFields.map((field, index) => (
                  <div
                    key={index}
                    className="rounded-xl border border-border bg-ink p-4"
                  >
                    <div className="mb-4 flex items-center justify-between">
                      <h3 className="font-medium">
                        Field {index + 1}
                      </h3>
                      <button
                        type="button"
                        onClick={() =>
                          removeOnboardingField(index)
                        }
                        className="rounded-lg p-2 text-muted hover:bg-hover"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-2">
                      <label className="space-y-2">
                        <span className="text-sm text-muted">
                          Label *
                        </span>
                        <input
                          required
                          placeholder="School"
                          value={field.label}
                          onChange={(event) =>
                            updateOnboardingField(
                              index,
                              { label: event.target.value },
                            )
                          }
                          className="w-full rounded-lg border border-border bg-indigo px-3 py-2.5 outline-none focus:border-indigo-soft"
                        />
                      </label>

                      <label className="space-y-2">
                        <span className="text-sm text-muted">
                          Key *
                        </span>
                        <input
                          required
                          placeholder="school"
                          value={field.field_key}
                          onChange={(event) =>
                            updateOnboardingField(
                              index,
                              {
                                field_key: event.target.value,
                                keyEdited: true,
                              },
                            )
                          }
                          className="w-full rounded-lg border border-border bg-indigo px-3 py-2.5 outline-none focus:border-indigo-soft"
                        />
                      </label>

                      <label className="space-y-2">
                        <span className="text-sm text-muted">
                          Type
                        </span>
                        <select
                          value={field.field_type}
                          onChange={(event) =>
                            updateOnboardingField(
                              index,
                              {
                                field_type: event.target
                                  .value as OnboardingFieldType,
                              },
                            )
                          }
                          className="w-full rounded-lg border border-border bg-indigo px-3 py-2.5 outline-none focus:border-indigo-soft"
                        >
                          <option value="text">Text</option>
                          <option value="number">Number</option>
                          <option value="select">Select</option>
                          <option value="boolean">Yes / no</option>
                          <option value="date">Date</option>
                        </select>
                      </label>

                      <label className="flex items-center gap-3 pt-7 text-sm text-muted">
                        <input
                          type="checkbox"
                          checked={field.required}
                          onChange={(event) =>
                            updateOnboardingField(
                              index,
                              { required: event.target.checked },
                            )
                          }
                          className="h-4 w-4 rounded border-border"
                        />
                        Required
                      </label>

                      {field.field_type === "select" && (
                        <label className="space-y-2 sm:col-span-2">
                          <span className="text-sm text-muted">
                            Options (comma-separated) *
                          </span>
                          <input
                            required
                            placeholder="Physical, Biological"
                            value={field.optionsText}
                            onChange={(event) =>
                              updateOnboardingField(
                                index,
                                { optionsText: event.target.value },
                              )
                            }
                            className="w-full rounded-lg border border-border bg-indigo px-3 py-2.5 outline-none focus:border-indigo-soft"
                          />
                        </label>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-ember px-4 py-3 font-medium hover:bg-ember/90 disabled:opacity-50"
          >
            {loading && (
              <Loader2 className="h-5 w-5 animate-spin" />
            )}

            Create institution
          </button>

          <p className="text-center text-sm text-muted">
            Already registered?{" "}
            <Link
              href="/login"
              className="font-medium text-muted hover:text-muted"
            >
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </main>
  );
}