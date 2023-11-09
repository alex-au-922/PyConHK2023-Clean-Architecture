import { ProductDetails } from "../types";
import { useMediaQuery } from "usehooks-ts";

interface ProductCardProps {
  order: number;
  product: ProductDetails;
  source: string;
}

const ProductCard = ({ product, source, order }: ProductCardProps) => {
  const isMobile = useMediaQuery("(max-width: 768px)");
  const isVerySmallMobile = useMediaQuery("(max-width: 320px)");

  const roundToNearest = (decimal: number, nearest: number) => {
    return Math.round(decimal / nearest) * nearest;
  };

  return (
    <div
      className={`card card-bordered bg-white card-side my-[1rem] p-2 w-full grid grid-cols-4 ${
        isMobile ? (isVerySmallMobile ? "h-120" : "h-80") : "h-72"
      }`}
    >
      <figure
        className={`card-image ${
          isMobile
            ? isVerySmallMobile
              ? "col-span-4"
              : "col-span-1"
            : "col-span-1"
        }`}
      >
        <img
          className="h-48 object-scale-down p-2 rounded-lg"
          src={product.image_url}
          alt={product.name}
        />
      </figure>
      <div
        className={`card-body ${
          isMobile
            ? isVerySmallMobile
              ? "col-span-4"
              : "col-span-3"
            : "col-span-3"
        }`}
      >
        <h2 className={`card-title text-base ${isMobile && "line-clamp-3"}`}>
          {order}. {product.name}
        </h2>
        <div>
          <label className="text-sm">Categories</label>
          <div className="card-subtitle">
            <div className="badge badge-primary mr-2 text-xs">
              {product.main_category}
            </div>
            <div className="badge badge-secondary mr-2 text-xs">
              {product.sub_category}
            </div>
          </div>
        </div>
        <div>
          <label className="text-sm">Relevancy</label>
          <div className="card-subtitle">
            <div className="badge badge-neutral mr-2 text-xs">
              {product.score.toFixed(2)}
            </div>
            <div className="badge badge-neutral mr-2 text-xs">{source}</div>
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
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
