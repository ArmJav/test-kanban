import axios, { type AxiosRequestConfig } from "axios";
import { API_URL } from "./config";
import router from "@/router";

interface HeaderKey {
    [key: string]: string;
}

interface Client {
    data?: unknown;
    method?: string;
    url: string;
    params?: string;
    headers?: HeaderKey;
}

const REQUEST_TIMEOUT = 5000;
const HEADER_DIST = {
    Accept: "application/json",
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true",
};

const API = axios.create({
    baseURL: API_URL,
    timeout: REQUEST_TIMEOUT,
    headers: HEADER_DIST,
});

export const ApiClient = async ({
                                    data,
                                    method = "GET",
                                    url,
                                    params,
                                    headers = {},
                                }: Client) => {
    const token = localStorage.getItem("token")
        ? { Authorization: `Bearer ${localStorage.getItem("token")}` }
        : {};

    const requestParams: AxiosRequestConfig = {
        method,
        url,
        params,
        data,
        responseType: "json",
        headers: {
            ...HEADER_DIST, // Базовые заголовки
            ...token,       // Если есть токен, добавляем
            ...headers,     // Заголовки только для текущего запроса
        },
    };

    return API(requestParams)
        .then((res) => {
            return { data: res.data, status: res.status };
        })
        .catch((err) => {
            if (err.response?.data?.message === "handler: no authorization header") {
                router.push("/auth");
            }

            if (
                err.response?.data?.message ===
                "handler: jwt parse with claims: token has invalid claims: token is expired"
            ) {
                localStorage.clear();
                router.push("/auth");
            }

            return {
                data: err.response?.data,
                status: err.response?.status,
                message: err.response?.message,
            };
        });
};
