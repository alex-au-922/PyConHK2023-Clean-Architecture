import NavBar from "./navBar";
import Display from "./display";
import { useState } from "react";
import { ProductDetails } from "./types";

const App = () => {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [lambdaSearchResults, setLambdaSearchResults] = useState<
    ProductDetails[]
  >([]);

  const [ecsSearchResults, setEcsSearchResults] = useState<ProductDetails[]>(
    []
  );

  const onSearch = async () => {
    try {
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
      console.log(e);
    }
  };

  return (
    <>
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
