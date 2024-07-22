import { useSearchParams } from "react-router-dom";


const useNextParameter = (): string | null => {
  const [searchParams] = useSearchParams();
  return searchParams.get('next');
};


export default useNextParameter;
