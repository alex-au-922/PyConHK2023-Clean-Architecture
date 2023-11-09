import NavBar from "./navBar";
import Display from "./display";
import { useState, useContext } from "react";
import { ProductDetails } from "./types";
import { IsLoadingContext } from "./contexts/isLoading";

type ErrorType = {
  title: string;
  message: string;
};

const App = () => {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [error, setError] = useState<ErrorType>({
    title: "",
    message: "",
  });
  const [lambdaSearchResults, setLambdaSearchResults] = useState<
    ProductDetails[]
  >([]);

  const [ecsSearchResults, setEcsSearchResults] = useState<ProductDetails[]>(
    []
  );

  const { setIsLoading } = useContext(IsLoadingContext);

  const onSearch = async () => {
    setIsLoading(true);
    try {
      if (!searchQuery) {
        setError({
          title: "Empty Input",
          message: "Please enter a keyword to search for similar products.",
        });
        (document.getElementById("error_modal") as any).showModal();
        return;
      }
      const [lambdaAPIGatewayResponse, ecsClusterREsponse] = await Promise.all([
        fetch(
          `${
            import.meta.env.VITE_LAMBDA_API_GATEWAY_DOMAIN
          }/api/similar_products`,
          {
            method: "POST",
            body: JSON.stringify({
              query: searchQuery,
              limit: 50,
              threshold: 0.3,
            }),
            headers: {
              "Content-Type": "application/json",
            },
          }
        ),
        fetch(
          `${import.meta.env.VITE_ECS_API_GATEWAY_DOMAIN}/api/similar_products`,
          {
            method: "POST",
            body: JSON.stringify({
              query: searchQuery,
              limit: 50,
              threshold: 0.3,
            }),
            headers: {
              "Content-Type": "application/json",
            },
          }
        ),
      ]);

      if (!lambdaAPIGatewayResponse.ok || !ecsClusterREsponse.ok) {
        throw new Error(
          `lambdaAPIGatewayResponse.ok: ${lambdaAPIGatewayResponse.ok}, ecsClusterREsponse.ok: ${ecsClusterREsponse.ok}`
        );
      }

      const lambdaAPIGatewayResponseJson =
        await lambdaAPIGatewayResponse.json();
      const ecsClusterResponseJson = await ecsClusterREsponse.json();

      setLambdaSearchResults(
        lambdaAPIGatewayResponseJson.data.similar_products as ProductDetails[]
      );
      setEcsSearchResults(
        ecsClusterResponseJson.data.similar_products as ProductDetails[]
      );
    } catch (e) {
      if (e instanceof Error) {
        setError({
          title: "Request Error",
          message: e.message,
        });
        (document.getElementById("error_modal") as any).showModal();
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <dialog id="error_modal" className="modal">
        <div className="modal-box">
          <h3 className="font-bold text-lg">{error.title}</h3>
          <p className="py-4">{error.message}</p>
          <div className="modal-action">
            <form method="dialog">
              <button className="btn">Close</button>
            </form>
          </div>
        </div>
      </dialog>
      {/* <dialog id="request_error_modal" className="modal">
        <div className="modal-box">
          <h3 className="font-bold text-lg">Empty Input</h3>
          <p className="py-4">
            Please enter a keyword to search for similar products.
          </p>
          <div className="modal-action">
            <form method="dialog">
              <button className="btn">Close</button>
            </form>
          </div>
        </div>
      </dialog> */}
      <NavBar
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onSearch={onSearch}
      />
      <Display
        lambdaSearchResults={lambdaSearchResults}
        ecsSearchResults={ecsSearchResults}
      />
    </>
  );
};

export default App;
