import { createBrowserRouter, RouterProvider } from "react-router-dom";
import SignInPage from "./pages/SignInPage";
import SignUpPage from "./pages/SignUpPage";
import { QueryClient, QueryClientProvider } from "react-query";
import Dashboard from "./pages/Dashboard";
import AuthContext from "./contexts/AuthContext";
import Authorize from "./pages/Authorize";

const router = createBrowserRouter([
  {
    path: "/sign-in",
    element: <SignInPage />,
  },
  {
    path: "/sign-up",
    element: <SignUpPage />,
  },
  {
    path: "/",
    element: (
      <AuthContext> 
        <Dashboard />
      </AuthContext>
    ),
  },
  {
    path: "/authorize",
    element: (
      <AuthContext>
        <Authorize />
      </AuthContext>
    ),
  }
]);

const queryClient = new QueryClient();

function App() {

  return (
    <>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </>
  );
}

export default App;
