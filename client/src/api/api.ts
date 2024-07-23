import axios from "axios"
import { OAuthRequest, OAuthRequestInfo, ServiceError, User, ValidationError } from '../entities';

const apiUrl = "http://localhost:8000";

const axiosInstance = axios.create({
    baseURL: apiUrl,
    withCredentials: true
})


function isValidationError(data: any): data is ValidationError {
  return (
    data &&
    typeof data === "object" &&
    typeof data.code === "number" &&
    typeof data.message === "string" &&
    typeof data.errors === "object"
  );
}

export async function signIn(login: string, password: string):Promise<null> {
    try {
        await axiosInstance.post<null>("/auth/login", {
            login: login,
            password: password
        });

        return null;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response && error.response.status === 400 && isValidationError(error.response.data)) {
            throw new ServiceError(error.response.data);
        }
        throw error;
    }

}

export async function singUp(username: string, email: string, password: string):Promise<User> {
    try {
        const response = await axiosInstance.post<User>("/auth/sign-up", {
            username: username,
            email: email,
            password: password
        });
        return response.data;

    } catch (error) {
        if (axios.isAxiosError(error) && error.response && error.response.status === 400 && isValidationError(error.response.data)) {
            throw new ServiceError(error.response.data);
        }
        throw error;
    }
}

export async function getMe():Promise<User> {
    const response = await axiosInstance.get<User>("/users/me");
    return response.data;
}

export async function logout():Promise<null> {
    const response = await axiosInstance.delete<null>("/auth/logout");
    return response.data;
}

export async function validateOAuthRequest(request: OAuthRequest) {
    const response = await axiosInstance.post<OAuthRequestInfo>("/oauth/request", {
        ...request
    });
    return response.data;
}


export async function oauthRequestAccept(request: OAuthRequest) {
    const response = await axiosInstance.postForm('/oauth/authorize/accept', request);

    if (response.status === 200) {
        const redirectUri = response.headers.location;

        if (redirectUri) {
            window.location.href = redirectUri;
        } else {
            throw new Error('Redirect URL not found');
        }

    } else {
        throw new Error(`Unexpected response status: ${response.status}`);
    }
}