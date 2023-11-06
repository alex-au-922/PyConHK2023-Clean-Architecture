import { ProductDetails } from "../types";

interface ProductCardProps {
  product: ProductDetails;
}

const ProductCard = ({ product }: ProductCardProps) => {
  return (
    <div className="card">
      <div className="card-body">
        <div className="flex justify-between">
          <div className="flex-1">
            <h5 className="card-title">{product.name}</h5>
            <h6 className="card-subtitle mb-2 text-muted">
              {product.main_category} - {product.sub_category}
            </h6>
            {product.discounted_price < product.actual_price ? (
              <p className="card-text">
                <del>${product.actual_price}</del>
                <span className="text-red-500">
                  ${product.discounted_price}
                </span>
              </p>
            ) : (
              <p className="card-text">${product.actual_price}</p>
            )}
          </div>
          <div className="flex-1">
            <img
              src={product.image_url}
              alt={product.name}
              className="rounded-lg"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
