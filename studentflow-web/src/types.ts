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
