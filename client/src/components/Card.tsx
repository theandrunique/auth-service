import { FC, HTMLAttributes, ReactNode } from "react";
import cn from "../utils/cn";

interface TitleProps {
  children: ReactNode
}

const CardTitle: FC<TitleProps> = ({ children }) => {
  return (
    <div className="text-3xl text-center font-semibold text-slate-100">
      {children}
    </div>
  )
};

interface CardProps extends HTMLAttributes<HTMLDivElement> {}

const Card: FC<CardProps> & {
  Title: FC<TitleProps>
} = ({ children, className, ...props }) => {
  const classInner = "bg-slate-600 p-16 rounded-2xl gap-4 flex flex-col w-[40rem]"

  return (
    <div className={cn(classInner, className)} {...props}>
      {children}
    </div>
  );
};


Card.Title = CardTitle;

export default Card;
