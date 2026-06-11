import axios from "axios";

const API_BASE = "https://youtube-video-downloader-t343.onrender.com";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});

export function setApiBase(url: string) {
  api.defaults.baseURL = url;
}

export { API_BASE };
