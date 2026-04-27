import { api } from "./axios";

export const getChatHistory = async (): Promise<any> => {
  const response = await api.get("/chat/history");
  return response.data;
};

export const sendChatMessage = async (message: string): Promise<any> => {
  const response = await api.post("/api/ask", {
    raw_text: message,
  });

  return response.data;
};
