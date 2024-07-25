import { SubmitHandler, useForm } from "react-hook-form";
import { getMe, signIn } from "../api/api";
import { useNavigate } from 'react-router-dom';
import { ServiceError } from "../entities";
import zod from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import useNextParam from "../hooks/useNextParam";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import ErrorMessage from "../components/ui/Error";
import LinkButton from "../components/ui/LinkButton";
import Card from "../components/Card";

const schema = zod.object({
  login: zod.string().min(1, "Login is required"),
  password: zod.string().min(1, "Password is required"),
});

type SignInSchema = zod.infer<typeof schema>;

function SignInPage() {
  const navigate = useNavigate();
  const nextLocation = useNextParam();

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
    <div className="min-h-screen flex justify-center items-center">
      <Card className="w-[30rem]">
        <Card.Title>Sign In</Card.Title>
        <form
          className="flex flex-col gap-2"
          onSubmit={handleSubmit(onSubmit)}
        >
          <Input {...register("login")} type="text" placeholder="login" />
          <ErrorMessage message={errors.login?.message} />
          <Input
            {...register("password")}
            type="password"
            placeholder="password"
          />
          <ErrorMessage message={errors.password?.message} />
          <Button disabled={isSubmitting} variant={"primary"}>Sign In</Button>
          <ErrorMessage message={errors.root?.message} />
        </form>
        <div className="text-center text-slate-300">
          Don't have an account?
          <LinkButton to={"/sign-up"}>sign up</LinkButton>
        </div>
      </Card>
    </div>
  );
}

export default SignInPage;
