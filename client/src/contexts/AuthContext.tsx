import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getMe } from "../api/api";

const AuthContext = ({ children } : { children: JSX.Element }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const checkAuth = async () => {
    try {
      await getMe();
    } catch (error) {
      const fullPath = encodeURIComponent(location.pathname + location.search);
      navigate(`/sign-in?next=${fullPath}`);
    }
  };
  useEffect(() => {
    checkAuth();
  }, [])

  return children;
};

export default AuthContext;
