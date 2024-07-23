import { useQuery, UseQueryResult } from "react-query";
import { User } from "../entities";
import { getMe } from "../api/api";


export default function useUserInfo():UseQueryResult<User> {
    const user = useQuery<User>({
        queryKey: ["user"],
        queryFn: getMe
    });

    return user;
}