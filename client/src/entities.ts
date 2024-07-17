
export type User = {
    id: string
    username: string
    email: string
    email_verified: boolean
    image_url: string | null
    active: boolean
    created_at: Date
}


export type ValidationError = {
    code: number;
    message: string;
    errors: {
        [key: string]: {
            code: string;
            message: string;
        }
    }
};

export class ServiceError extends Error {
    error: ValidationError
    constructor(error: ValidationError) {
        super(error.message);
        this.error = error;
    }
}
