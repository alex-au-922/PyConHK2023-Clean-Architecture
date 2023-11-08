import { ProductDetails } from "../types";
import { useMediaQuery } from "usehooks-ts";
import ProductCard from "./productCard";
import { useState } from "react";

interface DisplayProps {
  lambdaSearchResults: ProductDetails[];
  ecsSearchResults: ProductDetails[];
}

const MobileDisplay = ({
  lambdaSearchResults,
  ecsSearchResults,
}: DisplayProps) => {
  const allAvailableTabs = ["Lambda Search Results", "ECS Search Results"];

  const [activeTab, setActiveTab] = useState(allAvailableTabs[0]);

  const isVerySmallMobile = useMediaQuery("(max-width: 320px)");

  return (
    <div className="mt-[1rem] w-full">
      <div className="flex justify-center">
        <div className="tabs">
          {allAvailableTabs.map((tabName) => (
            <a
              key={tabName}
              className={`tab tab-bordered  ${
                activeTab === tabName && "tab-active"
              }`}
              data-target={`#${tabName}`}
              data-toggle="tabName"
              onClick={() => setActiveTab(tabName)}
            >
              {isVerySmallMobile ? tabName.split(" ").slice(0, 1) : tabName}
            </a>
          ))}
        </div>
      </div>
      {activeTab === "Lambda Search Results" && (
        <div>
          {lambdaSearchResults.map((product) => (
            <ProductCard
              key={product.product_id}
              product={product}
              source={"lambda"}
            />
          ))}
        </div>
      )}
      {activeTab === "ECS Search Results" && (
        <div>
          {ecsSearchResults.map((product) => (
            <ProductCard
              key={product.product_id}
              product={product}
              source={"ecs"}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const ComputerDisplay = ({
  lambdaSearchResults,
  ecsSearchResults,
}: DisplayProps) => {
  return (
    <div className="grid grid-cols-2 w-full gap-x-[2rem] px-[2rem] mt-[1rem]">
      <div>
        <h2 className="text-center underline underline-offset-8 text-2xl">
          Lambda Search Result
        </h2>
        <div>
          {lambdaSearchResults.map((product) => (
            <ProductCard
              key={product.product_id}
              product={product}
              source={"lambda"}
            />
          ))}
        </div>
      </div>
      <div>
        <h2 className="text-center underline underline-offset-8 text-2xl">
          ECS Search Result
        </h2>
        <div>
          {ecsSearchResults.map((product) => (
            <ProductCard
              key={product.product_id}
              product={product}
              source={"ecs"}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const Display = ({ lambdaSearchResults, ecsSearchResults }: DisplayProps) => {
  const isMobile = useMediaQuery("(max-width: 768px)");

  return isMobile ? (
    <MobileDisplay
      lambdaSearchResults={lambdaSearchResults}
      ecsSearchResults={ecsSearchResults}
    />
  ) : (
    <ComputerDisplay
      lambdaSearchResults={lambdaSearchResults}
      ecsSearchResults={ecsSearchResults}
    />
  );
};

export default Display;
