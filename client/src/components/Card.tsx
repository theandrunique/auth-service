import { FC, HTMLAttributes } from "react";
import cn from "../utils/cn";

interface CardProps extends HTMLAttributes<HTMLDivElement> {}

const Card: FC<CardProps> = ({ children, className, ...props }) => {
  const classInner = "bg-slate-600 p-16 rounded-2xl gap-4 flex flex-col w-[40rem]"
  return (
    <div className="min-h-screen flex justify-center items-center">
      <div className={cn(classInner, className)}>
        {children}
      </div>
    </div>
  );
};

export default Card;
