const API_BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error ${response.status}: ${error}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const api = {
  // Profiles
  getProfiles: () => request<import('../types').AcademicProfile[]>('/profiles'),
  getProfile: (id: number) => request<import('../types').AcademicProfile>(`/profiles/${id}`),
  createProfile: (data: Record<string, unknown>) =>
    request<import('../types').AcademicProfile>('/profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateProfile: (id: number, data: Record<string, unknown>) =>
    request<import('../types').AcademicProfile>(`/profiles/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  // Opportunities
  getOpportunities: (page = 1, perPage = 20) =>
    request<import('../types').PaginatedResponse<import('../types').FundingOpportunity>>(
      `/opportunities?page=${page}&per_page=${perPage}`
    ),

  // Matches
  getMatches: (profileId: number, page = 1) =>
    request<import('../types').PaginatedResponse<import('../types').Match>>(
      `/profiles/${profileId}/matches?page=${page}`
    ),
  refreshMatches: (profileId: number) =>
    request<{ new_matches: number }>(`/profiles/${profileId}/matches/refresh`, {
      method: 'POST',
    }),
  updateMatch: (profileId: number, matchId: number, action: Record<string, boolean>) =>
    request<import('../types').Match>(`/profiles/${profileId}/matches/${matchId}`, {
      method: 'PATCH',
      body: JSON.stringify(action),
    }),
};
