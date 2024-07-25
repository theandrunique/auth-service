import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { OAuthRequest, ScopeInfo } from "../entities";
import { validateOAuthRequest } from "../api/api";

interface UseOAuthParamsReturn {
  request: OAuthRequest | null;
  isError: boolean;
  scopesInfo: ScopeInfo[];
}

const useOAuthParams = (): UseOAuthParamsReturn => {
  const [searchParams] = useSearchParams();
  const [isError, setIsError] = useState(false);
  const [request, setRequest] = useState<OAuthRequest | null>(null);
  const [scopesInfo, setScopesInfo] = useState<ScopeInfo[]>([]);

  const validateRequest = async (request: OAuthRequest) => {
    try {
      const response = await validateOAuthRequest(request);
      setScopesInfo(response.scopes);
    } catch (error) {
      setIsError(true);
    }
  };

  useEffect(() => {
    const response_type = searchParams.get("response_type");
    const client_id = searchParams.get("client_id");
    const redirect_uri = searchParams.get("redirect_uri");

    if (!response_type || !client_id || !redirect_uri) {
      setIsError(true);
      return;
    }
    const requestParams = {
      response_type: response_type,
      client_id: client_id,
      redirect_uri: redirect_uri,
      scope: searchParams.get("scope"),
      state: searchParams.get("state"),
      code_challenge: searchParams.get("code_challenge"),
      code_challenge_method: searchParams.get("code_challenge_method"),
    };
    validateRequest(requestParams);

    setRequest(requestParams);
  }, [searchParams]);

  return { request, isError, scopesInfo };
};

export default useOAuthParams;
