import { ProductDetails } from "../types";
import { useMediaQuery } from "usehooks-ts";

interface ProductCardProps {
  product: ProductDetails;
  source: string;
}

const ProductCard = ({ product, source }: ProductCardProps) => {
  const isMobile = useMediaQuery("(max-width: 768px)");

  const roundToNearest = (decimal: number, nearest: number) => {
    return Math.round(decimal / nearest) * nearest;
  };

  return (
    <div
      className={`card card-bordered h-64 bg-white card-side my-[1rem] p-2 w-full`}
    >
      <figure>
        <img
          className="h-48 object-scale-down p-2 rounded-lg"
          src={product.image_url}
          alt={product.name}
        />
      </figure>
      <div className="card-body">
        <h2 className={`card-title text-base ${isMobile && "line-clamp-3"}`}>
          {product.name}
        </h2>
        <div className="card-subtitle">
          <div className="badge badge-primary mr-2 text-xs">
            {product.main_category}
          </div>
          <div className="badge badge-secondary mr-2 text-xs">
            {product.sub_category}
          </div>
        </div>
        <div className="flex justify-center">
          {product.discounted_price < product.actual_price ? (
            <p>
              <del>${roundToNearest(product.actual_price, 10)}</del>
              <p>${roundToNearest(product.discounted_price, 10)}</p>
            </p>
          ) : (
            <p>${roundToNearest(product.actual_price, 10)}</p>
          )}
          <div>{source}</div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
