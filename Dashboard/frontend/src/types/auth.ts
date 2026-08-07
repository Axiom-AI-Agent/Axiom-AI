export type StaffRole =
  | "admin"
  | "marker"
  | "viewer";

export interface AuthUser {
  id: string;
  tenant_id: string;
  institution_name: string;
  name: string;
  email: string;
  role: StaffRole;
}

export interface CreatedStaff {
  id: string;
  name: string;
  email: string;
  role: StaffRole;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
  created_staff?: CreatedStaff[];
}

export interface StaffRegistration {
  name: string;
  email: string;
  password: string;
  role: StaffRole;
}

export interface RegisterOrganizationPayload {
  institution_name: string;
  whatsapp_number?: string | null;

  admin: {
    name: string;
    email: string;
    password: string;
  };

  staff_members: StaffRegistration[];
}

export interface LoginPayload {
  email: string;
  password: string;
}