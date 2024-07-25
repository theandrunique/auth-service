import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { OAuthRequest, ScopeInfo } from "../entities";
import { oauthRequestAccept, validateOAuthRequest } from "../api/api";
import Button from "../components/ui/Button";
import Card from "../components/Card";

export default function Authorize() {
  const [searchParams] = useSearchParams();
  const [scopes, setScopes] = useState<ScopeInfo[]>([]);
  const [request, setRequest] = useState<OAuthRequest | null>(null);
  const [error, setError] = useState(false);

  const validateRequest = async (request: OAuthRequest) => {
    try {
      const response = await validateOAuthRequest(request);
      setScopes(response.scopes);
    } catch (error) {
      setError(true);
    }
  };

  useEffect(() => {
    const response_type = searchParams.get("response_type");
    const client_id = searchParams.get("client_id");
    const redirect_uri = searchParams.get("redirect_uri");

    if (!response_type || !client_id || !redirect_uri) {
      setError(true);
      return
    }
    const request = {
      response_type: response_type,
      client_id: client_id,
      redirect_uri: redirect_uri,
      scope: searchParams.get("scope"),
      state: searchParams.get("state"),
      code_challenge: searchParams.get("code_challenge"),
      code_challenge_method: searchParams.get("code_challenge_method"),
    }
    validateRequest(request);

    setRequest(request);
  }, []);

  const submitHandler = async () => {
    if (!request) return;

    try {
      await oauthRequestAccept(request);
    } catch (error) {
      console.log(error);
      setError(true);
    }
  };

  const cancelRequest = () => {}

  if (error) {
    return <Card><div>Something goes wrong...</div></Card>
  }

  return (
    <div className="min-h-screen flex justify-center items-center">
      <Card>
        <div className="text-xl text-slate-100">
          App <strong>{request?.client_id}</strong> want to get access to your
          account with the following scopes:
        </div>
        <ul className="list-disc list-inside text-slate-100">
          {scopes.map((scope) => (
            <li>
              <strong>{scope.name}</strong> - {scope.description}
            </li>
          ))}
        </ul>
        <Button className="w-64 self-center" onClick={() => submitHandler()}>Submit</Button>
        <Button variant={"secondary"} className="w-64 self-center" onClick={() => cancelRequest()}>Cancel</Button>
      </Card>
    </div>
  );
}
