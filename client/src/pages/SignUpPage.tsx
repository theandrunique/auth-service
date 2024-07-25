import { SubmitHandler, useForm } from "react-hook-form";
import { singUp } from "../api/api";
import zod from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { ServiceError } from "../entities";
import Input from "../components/ui/Input";
import ErrorMessage from "../components/ui/Error";
import Button from "../components/ui/Button";
import LinkButton from "../components/ui/LinkButton";
import Card from "../components/Card";

const schema = zod.object({
  email: zod.string().email(),
  username: zod
    .string()
    .regex(/^[a-zA-Z0-9]+$/, "Username must only contain letters and numbers")
    .min(3, "Username must be at least 3 characters")
    .max(32, "Username must be at most 32 characters"),
  password: zod
    .string()
    .regex(
      /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])/,
      "Password must contain at least one uppercase letter, one lowercase letter, one number and one special character"
    )
    .min(8, "Password must be at least 8 characters")
    .max(32, "Password must be at most 32 characters"),
});

type SignUpSchema = zod.infer<typeof schema>;

export default function SignUpPage() {
  const navigate = useNavigate();
  const {
    setError,
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignUpSchema>({ resolver: zodResolver(schema) });

  const onSubmit: SubmitHandler<SignUpSchema> = async (data) => {
    try {
      const response = await singUp(data.username, data.email, data.password);
      if (response === null) {
        navigate("/sign-in");
      }
    } catch (error) {
      if (error instanceof ServiceError && error.error.errors) {
        for (const [field, details] of Object.entries(error.error.errors)) {
          setError(field as keyof SignUpSchema, {
            type: "manual",
            message: details.message,
          });
        }
      } else {
        setError("root", { message: "Error: something went wrong" });
      }
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-center">
      <Card className="w-[30rem]" >
        <Card.Title>Sign Up</Card.Title>
        <form
          className="flex flex-col gap-2"
          onSubmit={handleSubmit(onSubmit)}
        >
          <Input {...register("email")} type="text" placeholder="email" />
          <ErrorMessage message={errors.email?.message} />
          <Input
            {...register("username")}
            type="text"
            placeholder="username"
          />
          <ErrorMessage message={errors.username?.message} />
          <Input
            {...register("password")}
            type="password"
            placeholder="password"
          />
          <ErrorMessage message={errors.password?.message} />
          <Button disabled={isSubmitting}>Sign Up</Button>
          <ErrorMessage message={errors.root?.message} />
        </form>
        <div className="text-center text-slate-300">
          Already have an account?
          <LinkButton to={"/sign-in"}>sign in</LinkButton>
        </div>
      </Card>
    </div>
  );
}
