import { api } from "./axios";
import type { ChatResponse } from "../types/chat";

export const getChatHistory = async (): Promise<any> => {
  const response = await api.get("/chat/history");
  return response.data;
};

export const sendChatMessage = async (
  message: string,
): Promise<ChatResponse> => {
  const response = await api.post("/chat/", { message });
  return response.data;
};
