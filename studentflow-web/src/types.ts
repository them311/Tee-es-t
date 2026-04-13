export type ContractType =
  | "internship"
  | "apprenticeship"
  | "cdd"
  | "cdi"
  | "part_time"
  | "freelance"
  | "other";

export interface StudentCreate {
  email: string;
  full_name: string;
  city: string;
  remote_ok: boolean;
  skills: string[];
  accepted_contracts: ContractType[];
  max_hours_per_week: number;
  available_from?: string | null;
  available_until?: string | null;
}

export interface Match {
  offer_id: string;
  title: string;
  company: string;
  city: string;
  score: number;
  reasons: string[];
}

export interface Stats {
  offers: number;
  students: number;
  matches: number;
  matches_unnotified: number;
  per_source: Record<string, number>;
}

export interface OfferCreate {
  title: string;
  company: string;
  description: string;
  city: string;
  remote: boolean;
  contract: ContractType;
  hours_per_week: number | null;
  skills: string[];
  url: string;
  contact_email: string;
}

export interface StudentMatch {
  student_id: string;
  full_name: string;
  email: string;
  city: string;
  skills: string[];
  score: number;
  reasons: string[];
}
