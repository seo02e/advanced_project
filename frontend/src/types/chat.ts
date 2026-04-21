export type Role = "user" | "assistant";

export interface ChatMessage {
  role: Role;
  raw_text: string;
}

export interface ChatResponse {
  session_id: string;
  saved_message?: ChatMessage;
  assistant_message?: ChatMessage;
  total_messages: number;
}
