import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { OAuthRequest, ScopeInfo } from '../entities';
import { oauthRequestAccept, validateOAuthRequest } from '../api/api';


export default function Authorize() {
    const [searchParams] = useSearchParams();
    const [scopes, setScopes] = useState<ScopeInfo[]>([]);
    const [request, setRequest] = useState<OAuthRequest | null>(null);
    const [error, setError] = useState(false);

    const validateRequest = async () => {
        try {
            const response = await validateOAuthRequest(request!);
            setScopes(response.scopes);
        } catch (error) {
            setError(true);
        }
    };

    useEffect(() => {
        if (request) {
            validateRequest();
        }

    }, [request]);

    useEffect(() => {
        const response_type = searchParams.get("response_type");
        if (!response_type) {
            setError(true);
            return;
        }

        const client_id = searchParams.get("client_id");
        if (!client_id) {
            setError(true);
            return;
        }

        const redirect_uri = searchParams.get("redirect_uri");
        if (!redirect_uri) {
            setError(true);
            return;
        }

        if (!error) {
            setRequest({
                response_type: response_type,
                client_id: client_id,
                redirect_uri: redirect_uri,
                scope: searchParams.get("scope"),
                state: searchParams.get("state"),
                code_challenge: searchParams.get("code_challenge"),
                code_challenge_method: searchParams.get("code_challenge_method"),
            })
        }
    }, []);

    const submitHandler = async () => {
        if (!request) {
            return;
        }

        try {
            await oauthRequestAccept(request!);

        } catch (error) {
            console.log(error);
            setError(true);
        }
    }

    return (
        <div>
            {
                error ?
                <div>
                    Something goes wrong...
                </div>
                : 
                <div>
                    <div>App {request?.client_id} want to get access to your account with the following scopes:</div>
                    {
                        scopes.map((scope) => {
                            return (
                                <div>
                                    <div>{scope.name} - {scope.description}</div>
                                </div>
                            )
                        })
                    }
                </div>
            }
            <button onClick={() => submitHandler()} className=''>
                Submit
            </button>
        </div>
    )
}