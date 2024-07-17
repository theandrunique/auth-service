import { SubmitHandler, useForm } from "react-hook-form";
import { singUp } from "../api/api";
import zod from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { ServiceError } from "../entities";

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
      if (error instanceof ServiceError) {
        for (const [field, details] of Object.entries(error.error.errors)) {
          setError(field as keyof SignUpSchema, { type: "manual", message: details.message });
        }
      } else {
        setError("root", { message: "Error: something went wrong" });
      }
    }
  };

  return (
    <>
      <div className="min-h-screen flex justify-center items-center">
        <div className="bg-slate-600">
          <div>Sign Up</div>
          <form
            className="flex flex-col gap-2"
            onSubmit={handleSubmit(onSubmit)}
          >
            <input {...register("email")} type="text" placeholder="email" />
            {errors.email?.message && (
              <p className="text-red-500">{errors.email?.message}</p>
            )}
            <input
              {...register("username")}
              type="text"
              placeholder="username"
            />
            {errors.username?.message && (
              <p className="text-red-500">{errors.username?.message}</p>
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
            {errors.root?.message && (
              <p className="text-red-500">{errors.root?.message}</p>
            )}
          </form>
        </div>
      </div>
    </>
  );
}
