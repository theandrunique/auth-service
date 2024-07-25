import { oauthRequestAccept } from "../api/api";
import Button from "../components/ui/Button";
import Card from "../components/Card";
import useOAuthParams from "../hooks/useOAuthParams";

export default function Authorize() {
  const { isError, request, scopesInfo } = useOAuthParams();

  const submitHandler = async () => {
    if (!request) return;

    try {
      await oauthRequestAccept(request);
    } catch (error) {
      console.log(error);
    }
  };

  const cancelRequest = () => {}

  if (isError) {
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
          {scopesInfo.map((scope) => (
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
