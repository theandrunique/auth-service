import { forwardRef, InputHTMLAttributes } from "react";
import cn from "../../utils/cn";


interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}


const Input = forwardRef<HTMLInputElement, InputProps>(({ className, ...props}, ref) => {
    return (
        <input 
            className={cn("p-1 rounded-lg text-lg", className)}
            {...props}
            ref={ref}
        />
    )
});

export default Input;
