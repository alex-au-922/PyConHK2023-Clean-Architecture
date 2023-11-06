import { ProductDetails } from "../types";

interface ProductCardProps {
  product: ProductDetails;
}

const ProductCard = ({ product }: ProductCardProps) => {
  return (
    // <div className="card h-56 bg-white m-2">
    //   <div className="card-body">
    //     <div className="flex justify-between">
    //       <h5 className="card-title">{product.name}</h5>
    //       <div className="flex-1">
    //         <h6 className="card-subtitle mb-2 text-muted">
    //           <div className="badge badge-primary">{product.main_category}</div>
    //           -
    //           <div className="badge badge-secondary">
    //             {product.sub_category}
    //           </div>
    //         </h6>
    //         {product.discounted_price < product.actual_price ? (
    //           <p className="card-text">
    //             <del>${product.actual_price}</del>
    //             <p className="card-text">${product.discounted_price}</p>
    //           </p>
    //         ) : (
    //           <p className="card-text">${product.actual_price}</p>
    //         )}
    //       </div>
    //       <div className="flex-1">
    //         <div className="flex justify-center align-items-center">
    //           <img
    //             src={product.image_url}
    //             alt={product.name}
    //             className="h-48 object-scale-down"
    //           />
    //         </div>
    //       </div>
    //     </div>
    //   </div>
    // </div>
    <div className="card h-56 bg-white card-side m-2 p-2">
      <figure>
        <img
          className="h-48 object-scale-down w-full p-2 rounded-lg"
          src={product.image_url}
          alt={product.name}
        />
      </figure>
      <div className="card-body">
        <h2 className="card-title">{product.name}</h2>
        <div className="card-subtitle">
          <div className="badge badge-primary mr-2">
            {product.main_category}
          </div>
          <div className="badge badge-secondary mr-2">
            {product.sub_category}
          </div>
        </div>
        <div className="card-actions justify-end">
          <button className="btn btn-primary">Buy Now</button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
