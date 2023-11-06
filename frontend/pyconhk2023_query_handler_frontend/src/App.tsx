import NavBar from "./navBar";
import { useState } from "react";

type ProductDetails = {
  product_id: string;
  name: string;
  main_category: string;
  sub_category: string;
  image_url: string;
  ratings: number;
  discounted_price: number;
  actual_price: number;
  modified_date: string;
  created_date: string;
  score: number;
};

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
          `${import.meta.env.VITE_API_GATEWAY_DOMAIN}/api/similar_products/`,
          {
            method: "POST",
            body: JSON.stringify({
              query: searchQuery,
              limit: 50,
              threshold: 0.3,
            }),
            headers: {
              "Content-Type": "application/json",
              "Access-Control-Allow-Origin": "*",
            },
          }
        ),
        fetch(`${import.meta.env.VITE_ECS_CLUSTER_ALB}/api/similar_products/`, {
          method: "POST",
          body: JSON.stringify({
            query: searchQuery,
            limit: 50,
            threshold: 0.3,
          }),
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        }),
      ]);

      const lambdaAPIGatewayResponseJson =
        await lambdaAPIGatewayResponse.json();
      const ecsClusterResponseJson = await ecsClusterREsponse.json();

      setLambdaSearchResults(lambdaAPIGatewayResponseJson);
      setEcsSearchResults(ecsClusterResponseJson);
    } catch (e) {
      console.log(e);
    }
  };

  return (
    <NavBar
      searchQuery={searchQuery}
      setSearchQuery={setSearchQuery}
      onSearch={onSearch}
    />
  );
};

export default App;
