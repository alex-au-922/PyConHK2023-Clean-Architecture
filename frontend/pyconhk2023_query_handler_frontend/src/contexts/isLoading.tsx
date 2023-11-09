import { createContext, useState, SetStateAction, Dispatch } from "react";

type IsLoadingContextType = {
  isLoading: boolean;
  setIsLoading: Dispatch<SetStateAction<boolean>>;
};

const isLoadingContextState = {
  isLoading: false,
  setIsLoading: () => {},
};

export const IsLoadingContext = createContext<IsLoadingContextType>(
  isLoadingContextState
);

export const IsLoadingProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [isLoading, setIsLoading] = useState<boolean>(false);

  return (
    <IsLoadingContext.Provider
      value={{
        isLoading,
        setIsLoading,
      }}
    >
      {isLoading && (
        <div className="w-screen h-screen flex justify-center items-center fixed z-[10000] bg-black/[.834]">
          <div className="w-28 h-28 border-solid border-8 rounded-full animate-spin border-indigo-100/20 border-x-purple-700"></div>
        </div>
      )}
      {children}
    </IsLoadingContext.Provider>
  );
};
