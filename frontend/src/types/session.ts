export interface SessionCreateResponse {
  session_id: string;
  expires_in?: number;
  message?: string;
}

export interface SessionInfoResponse {
  session_id: string;
  created_at?: string;
  last_accessed_at?: string;
}
