import { useQuery } from "react-query";
import { getMe, logout } from "../api/api";
import { User } from "../entities";
import { useNavigate } from "react-router-dom";
import Button from "../components/ui/Button";
import Card from "../components/Card";

export default function Dashboard() {
  const user = useQuery<User>({
    queryKey: ["user"],
    queryFn: getMe,
  });
  const navigate = useNavigate();

  const executeLogout = async () => {
    await logout();

    navigate("/sign-in");
  };

  return (
    <div className="min-h-screen flex justify-center items-center">
      <Card className="w-[40rem]">
        <Card.Title>Userinfo:</Card.Title>
        <div className="text-lg text-slate-200">
          <div><strong>Id: </strong>{user.data?.id}</div>
          <div><strong>Username: </strong>{user.data?.username}</div>
          <div><strong>Email: </strong>{user.data?.email}</div>
          <div><strong>Email verified: </strong>{user.data?.email_verified.toString()}</div>
          <div><strong>Created at: </strong>{user.data?.created_at.toString()}</div>
        </div>
        <Button onClick={() => executeLogout()}>Logout</Button>
      </Card>
    </div>
  );
}
