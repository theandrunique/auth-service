
const ErrorMessage = ({ message } : { message?: string }) => {
    if (!message) return null;

    return (
        <p className="text-red-500">{message}</p>
    )
}

export default ErrorMessage;
