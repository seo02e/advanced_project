import { api } from "./axios";
import type {
  SessionCreateResponse,
  SessionInfoResponse,
} from "../types/session";

export const createSession = async (): Promise<SessionCreateResponse> => {
  const response = await api.post("/session/");
  return response.data;
};

export const getMySession = async (): Promise<SessionInfoResponse> => {
  const response = await api.get("/session/me");
  return response.data;
};

export const deleteSession = async (): Promise<void> => {
  await api.delete("/session/");
};
