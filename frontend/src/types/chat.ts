export type Role = "user" | "assistant";

export interface Policy {
  policy_id?: string;
  policy_name?: string;
  title?: string;
  name?: string;
  source_layer?: "A" | "B" | string;
  short_reason?: string;
  recommend_reason?: string;
  reason?: string;
  support_type?: string;
  policy_type?: string;
  category?: string;
  field?: string;
  eligibility_status?: string;
  apply_status?: string;
  status?: string;
  missing_requirements?: string[];
  need_more_info?: string[];
  source_url?: string;
  url?: string;
  summary?: string;
}

export interface AnswerBlocks {
  summary?: string;
  recommended?: Policy[];
  need_more_info?: string[];
  sources?: string[];
  next_action?: string;
}

export interface ChatData {
  answer_text?: string;
  answer_blocks?: AnswerBlocks;
  recommended_policies?: Policy[];
  retrieved_chunks?: Policy[];
  need_more_info?: string[];
  citations?: Array<string | { title?: string; source_url?: string }>;
  [key: string]: unknown;
}

export interface ChatMessage {
  role: Role;
  raw_text: string;
  data?: ChatData;
}

export interface ChatResponse {
  session_id: string;
  saved_message?: ChatMessage;
  assistant_message?: ChatMessage;
  total_messages: number;
}
