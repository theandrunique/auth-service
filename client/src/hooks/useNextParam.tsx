import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

const useNextParam = (): string | null => {
  const [searchParams] = useSearchParams();
  const [nextParam, setNextParam] = useState<string | null>(null);

  useEffect(() => {
    setNextParam(searchParams.get("next"));
  }, [searchParams]);

  return nextParam;
};

export default useNextParam;
