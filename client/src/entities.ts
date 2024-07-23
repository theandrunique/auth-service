
export type User = {
    id: string
    username: string
    email: string
    email_verified: boolean
    image_url: string | null
    active: boolean
    created_at: Date
}


export type FieldError = {
    code: string
    message: string
}


export type ValidationError = {
    code: number;
    message: string;
    errors: Record<string, FieldError> | null; 
};

export class ServiceError extends Error {
    error: ValidationError
    constructor(error: ValidationError) {
        super(error.message);
        this.error = error;
    }
}

export type OAuthRequest = {
    response_type: string
    client_id: string
    redirect_uri: string
    scope: string | null
    state: string | null
    code_challenge_method: string | null
    code_challenge: string | null
}

export type ScopeInfo = {
  name: string;
  description: string;
}

export type OAuthRequestInfo = {
    scopes: ScopeInfo[]
}
