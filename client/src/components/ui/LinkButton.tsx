import { Link, LinkProps } from "react-router-dom";
import cn from "../../utils/cn";


const LinkButton: React.FC<LinkProps> = ({ to, children, className, ...props}) => {

    return (
        <Link
            to={to}
            className={cn("hover:underline ml-1 font-semibold", className)}
            {...props}
        >
            {children}
        </Link>
    )
}

export default LinkButton;
