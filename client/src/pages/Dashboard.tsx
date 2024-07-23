import { useQuery } from "react-query"
import { getMe, logout } from "../api/api"
import { User } from "../entities"
import { useNavigate } from "react-router-dom"


export default function Dashboard() {
    const user = useQuery<User>({
        queryKey: ["user"],
        queryFn: getMe
    })
    const navigate = useNavigate();

    const executeLogout = async () => {
        await logout();

        navigate("/sign-in");
    }

    return (
        <>
            <div>
                <div>Id: {user.data?.id}</div>
                <div>Username: {user.data?.username}</div>
                <div>Email: {user.data?.email}</div>
                <div>Email verified: {user.data?.email_verified}</div>
                <div>Created at: {user.data?.created_at.toString()}</div>
            </div>
            <button onClick={() => executeLogout()}>Logout</button>
        </>
    )
}
