import { api } from "./axios";

export const getChatHistory = async (): Promise<any> => {
  const response = await api.get("/chat/history");
  return response.data;
};

export const sendChatMessage = async (message: string): Promise<any> => {
  const response = await api.post("/chat/", {
    message: message, // 🔥 핵심: message로 맞추기
  });

  return response.data;
};
