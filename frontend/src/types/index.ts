export interface Keyword {
  id: number;
  value: string;
}

export interface ResearchField {
  id: number;
  name: string;
}

export type CareerStage =
  | 'phd_student'
  | 'postdoc'
  | 'early_career'
  | 'mid_career'
  | 'senior'
  | 'emeritus';

// Public profile — email is never exposed in public responses
export interface AcademicProfile {
  id: number;
  handle: string;
  career_stage: CareerStage | null;
  research_summary: string | null;
  match_threshold: number;
  keywords: Keyword[];
  fields: ResearchField[];
  created_at: string;
  updated_at: string;
}

// Private profile — only returned to the profile owner
export interface AcademicProfilePrivate extends AcademicProfile {
  email: string;
}

export interface FundingOpportunity {
  id: number;
  title: string;
  description: string | null;
  funder: string | null;
  institution: string | null;
  deadline: string | null;
  budget_min: number | null;
  budget_max: number | null;
  currency: string;
  eligibility_criteria: string | null;
  career_stages: string | null;
  url: string;
  keywords: Keyword[];
  fields: ResearchField[];
  created_at: string;
}

export interface Match {
  id: number;
  profile_id: number;
  opportunity_id: number;
  score: number;
  match_method: string;
  match_reasons: string | null;
  is_seen: boolean;
  is_saved: boolean;
  is_dismissed: boolean;
  opportunity: FundingOpportunity;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}
