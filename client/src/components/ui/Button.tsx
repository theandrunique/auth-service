import { cva, VariantProps } from "class-variance-authority";
import { ButtonHTMLAttributes, forwardRef } from "react";
import cn from "../../utils/cn";


const buttonVariants = cva(
  "px-4 py-2 rounded text-white font-bold shadow",
  {
    variants: {
      variant: {
        primary: "bg-blue-500 hover:bg-blue-600 ",
        secondary: "bg-gray-500 hover:bg-gray-600",
      },

    },
    defaultVariants: {
      variant: "primary",
    },
  }
)

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(({ variant, children, className, ...props }, ref) => {
  return (
    <button
      className={cn(buttonVariants({ variant }), className)}
      {...props}
      ref={ref}
    >
      {children}
    </button>
  );
});

export default Button;
