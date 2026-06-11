import axios from "axios";

const API_BASE = "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export function setApiBase(url: string) {
  api.defaults.baseURL = url;
}

export { API_BASE };
