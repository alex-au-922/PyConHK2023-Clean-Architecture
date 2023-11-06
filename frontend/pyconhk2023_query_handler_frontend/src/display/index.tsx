import { ProductDetails } from "../types";
import ProductCard from "./productCard";

interface DisplayProps {
  lambdaSearchResults: ProductDetails[];
  ecsSearchResults: ProductDetails[];
}

const Display = ({ lambdaSearchResults, ecsSearchResults }: DisplayProps) => {
  return (
    <div className="flex justify-between">
      <div className="flex-1">
        <h3 className="text-center">Lambda Search Results</h3>
        {lambdaSearchResults.map((product) => (
          <ProductCard key={product.product_id} product={product} />
        ))}
      </div>
      <div className="flex-1">
        <h3 className="text-center">ECS Search Results</h3>
        {ecsSearchResults.map((product) => (
          <ProductCard key={product.product_id} product={product} />
        ))}
      </div>
    </div>
  );
};

export default Display;
