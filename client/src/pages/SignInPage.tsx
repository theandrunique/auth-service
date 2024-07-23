import { SubmitHandler, useForm } from "react-hook-form";
import { getMe, signIn } from "../api/api";
import { useNavigate } from 'react-router-dom';
import { ServiceError } from "../entities";
import zod from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import useNextParameter from "../hooks/useNextParameter";

const schema = zod.object({
  login: zod.string().min(1, "Login is required"),
  password: zod.string().min(1, "Password is required"),
});

type SignInSchema = zod.infer<typeof schema>;

function SignInPage() {
  const navigate = useNavigate();
  const nextLocation = useNextParameter();

  const {
    setError,
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignInSchema>({ resolver: zodResolver(schema) });

  const onSubmit: SubmitHandler<SignInSchema> = async (data) => {
    try {
      const response = await signIn(data.login, data.password);
      if (response === null) {
        navigate(nextLocation || "/");
      }
    } catch (error) {
      if (error instanceof ServiceError && error.error.errors) {
        for (const [field, details] of Object.entries(error.error.errors)) {
          setError(field as keyof SignInSchema, { type: "manual", message: details.message });
        }
      } else {
        setError("root", { message: "Error: something went wrong" });
      }
    }
  };

  useEffect(() => {
    const checkSession = async () => {
      try {
        await getMe();
        navigate(nextLocation || "/");
      } catch (error) {}
    }
    checkSession();
  }, []);

  return (
    <>
      <div className="min-h-screen flex justify-center items-center">
        <div className="bg-slate-600">
          <div>Sign In</div>
          <form
            className="flex flex-col gap-2"
            onSubmit={handleSubmit(onSubmit)}
          >
            <input {...register("login")} type="text" placeholder="login" />
            {errors.login?.message && (
              <p className="text-red-500">{errors.login?.message}</p>
            )}
            <input
              {...register("password")}
              type="password"
              placeholder="password"
            />
            {errors.password?.message && (
              <p className="text-red-500">{errors.password?.message}</p>
            )}
            <button disabled={isSubmitting} type="submit">
              Sign In
            </button>
            {errors.root?.message && <p>{errors.root?.message}</p>}
          </form>
        </div>
      </div>
    </>
  );
}

export default SignInPage;
