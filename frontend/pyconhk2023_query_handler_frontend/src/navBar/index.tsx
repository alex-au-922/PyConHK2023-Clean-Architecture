import { useMediaQuery } from "usehooks-ts";
import { useState } from "react";
import mahjongIcon from "/single_mahjong.png";

type NavBarProps = {
  searchQuery: string;
  setSearchQuery: (searchQuery: string) => void;
  searchLimit: number;
  setSearchLimit: (searchLimit: number) => void;
  searchThreshold: number;
  setSearchThreshold: (searchThreshold: number) => void;
  onSearch: () => Promise<void>;
};

const MobileNavBar = ({
  searchQuery,
  setSearchQuery,
  searchLimit,
  setSearchLimit,
  searchThreshold,
  setSearchThreshold,
  onSearch,
}: NavBarProps) => {
  const [openCollapse, setOpenCollapse] = useState(false);
  const isVerySmallMobile = useMediaQuery("(max-width: 320px)");

  const limitScale = 10;
  const limitRanges = Array.from(Array(6).keys()).map((i) => i * limitScale);
  const thresholdScale = 0.05;
  const thresholdRanges = Array.from(Array(6).keys())
    .map((i) => i * thresholdScale * 4)
    .map((i) => i.toFixed(1));

  const approxEqual = (v1: number, v2: number, epsilon: number = 0.001) =>
    Math.abs(v1 - v2) <= epsilon;

  return (
    <div className="w-full bg-white">
      <input
        id="expand-navbar-collapse"
        checked={openCollapse}
        type="checkbox"
        className="peer sr-only"
        onChange={() => {}}
      />
      <div className="w-full flex items-center bg-white rounded-none">
        <label
          htmlFor="expand-navbar-collapse"
          className="duration-200 ease-in-out cursor-pointer select-none"
          onClick={() => setOpenCollapse(!openCollapse)}
        >
          <div className="flex-none mr-2">
            <div className="btn btn-square btn-ghost">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                className="inline-block w-5 h-5 stroke-current"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4 6h16M4 12h16M4 18h16"
                ></path>
              </svg>
            </div>
          </div>
        </label>
        <div className="flex-1">
          <div className="flex items-center">
            <img src={mahjongIcon} className="h-8 mr-2" />
            <div className="text-base md:text-ms break-normal text-center">
              PyConHK 2023 Clean Architecture
            </div>
          </div>
        </div>
      </div>
      <div className="overflow-hidden h-0 bg-white peer-checked:p-4 peer-checked:h-full peer-checked:overflow-scroll transition duration-500 ease-in">
        <div className="flex items-center w-full mb-4">
          <div className="input-group w-full">
            <input
              type="text"
              placeholder={isVerySmallMobile ? "Keywords" : "Enter keywords"}
              className="input w-full"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button className="btn btn-square" onClick={() => onSearch()}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </button>
          </div>
        </div>
        <div className="w-full mb-4">
          <label className="text-sm">Search Limit</label>
          <input
            type="range"
            min={limitRanges[0]}
            max={limitRanges[limitRanges.length - 1]}
            value={searchLimit}
            className="range"
            step={limitScale}
            onChange={(e) => setSearchLimit(parseInt(e.target.value))}
          />
          <div className="w-full flex justify-between text-xs px-2">
            {limitRanges.map((limitRange) => (
              <div
                key={limitRange}
                className={`${limitRange === searchLimit && "text-gray-600"}`}
              >
                {limitRange}
              </div>
            ))}
          </div>
        </div>
        <div className="w-full">
          <label className="text-sm">Search Threshold</label>
          <input
            type="range"
            min={thresholdRanges[0]}
            max={thresholdRanges[thresholdRanges.length - 1]}
            value={searchThreshold}
            className="range"
            step={thresholdScale}
            onChange={(e) => {
              console.log(e.target.value);
              setSearchThreshold(parseFloat(e.target.value));
            }}
          />
          <div className="w-full flex justify-between text-xs px-2">
            {thresholdRanges.map((thresholdRange) => (
              <div
                key={thresholdRange}
                className={`${
                  approxEqual(parseFloat(thresholdRange), searchThreshold) &&
                  "text-gray-600"
                }`}
              >
                {thresholdRange}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const ComputerNavBar = ({
  searchQuery,
  setSearchQuery,
  searchLimit,
  setSearchLimit,
  searchThreshold,
  setSearchThreshold,
  onSearch,
}: NavBarProps) => {
  const [openCollapse, setOpenCollapse] = useState(false);

  const limitScale = 10;
  const limitRanges = Array.from(Array(6).keys()).map((i) => i * limitScale);
  const thresholdScale = 0.05;
  const thresholdRanges = Array.from(Array(6).keys())
    .map((i) => i * thresholdScale * 4)
    .map((i) => i.toFixed(1));

  const approxEqual = (v1: number, v2: number, epsilon: number = 0.001) =>
    Math.abs(v1 - v2) <= epsilon;

  return (
    <div className="w-full">
      <input
        id="expand-navbar-collapse"
        checked={openCollapse}
        type="checkbox"
        className="peer sr-only"
        onChange={() => {}}
      />
      <div className="w-full navbar flex items-center bg-white rounded-none">
        <div className="flex-none">
          <label
            htmlFor="expand-navbar-collapse"
            className="duration-200 ease-in-out cursor-pointer select-none"
            onClick={() => setOpenCollapse(!openCollapse)}
          >
            <div className="flex-none mr-2">
              <div className="btn btn-square btn-ghost">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  className="inline-block w-5 h-5 stroke-current"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4 6h16M4 12h16M4 18h16"
                  ></path>
                </svg>
              </div>
            </div>
          </label>
        </div>
        <div className="flex-1">
          <div className="flex items-center">
            <img src={mahjongIcon} className="h-8 mr-2" />
            <div className="text-base md:text-ms break-normal text-center">
              PyConHK 2023 Clean Architecture
            </div>
          </div>
        </div>
        <div className="input-group flex-1">
          <input
            type="text"
            placeholder="Enter keywords"
            className="input w-full dark:bg-slate-800"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button className="btn btn-square" onClick={() => onSearch()}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </button>
        </div>
        <div className="flex-1" />
      </div>
      <div
        className="overflow-hidden h-0 flex items-center justify-between bg-white peer-checked:p-4 peer-checked:h-full peer-checked:overflow-scroll transition duration-500 ease-in"
        style={{ overflow: "hidden" }}
      >
        <div className="mb-4 flex-1 mx-8">
          <label className="text-sm">Search Limit</label>
          <input
            type="range"
            min={limitRanges[0]}
            max={limitRanges[limitRanges.length - 1]}
            value={searchLimit}
            className="range"
            step={limitScale}
            onChange={(e) => setSearchLimit(parseInt(e.target.value))}
          />
          <div className="w-full flex justify-between text-xs px-2">
            {limitRanges.map((limitRange) => (
              <div
                key={limitRange}
                className={`${limitRange === searchLimit && "text-gray-600"}`}
              >
                {limitRange}
              </div>
            ))}
          </div>
        </div>
        <div className="mb-4 flex-1 mx-8">
          <label className="text-sm">Search Threshold</label>
          <input
            type="range"
            min={thresholdRanges[0]}
            max={thresholdRanges[thresholdRanges.length - 1]}
            value={searchThreshold}
            className="range"
            step={thresholdScale}
            onChange={(e) => {
              console.log(e.target.value);
              setSearchThreshold(parseFloat(e.target.value));
            }}
          />
          <div className="w-full flex justify-between text-xs px-2">
            {thresholdRanges.map((thresholdRange) => (
              <div
                key={thresholdRange}
                className={`${
                  approxEqual(parseFloat(thresholdRange), searchThreshold) &&
                  "text-gray-600"
                }`}
              >
                {thresholdRange}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
    // <div className="navbar bg-white flex gap-2">
    //   <div className="flex-1">
    //     <img src={mahjongIcon} className="h-12 mr-2" />
    //     <div className="normal-case text-xl">
    //       PyConHK 2023 Clean Architecture
    //     </div>
    //   </div>
    //   <div className="input-group flex-1">
    //     <input
    //       type="text"
    //       placeholder="Enter keywords"
    //       className="input w-full dark:bg-slate-800"
    //       value={searchQuery}
    //       onChange={(e) => setSearchQuery(e.target.value)}
    //     />
    //     <button className="btn btn-square" onClick={() => onSearch()}>
    //       <svg
    //         xmlns="http://www.w3.org/2000/svg"
    //         className="h-6 w-6"
    //         fill="none"
    //         viewBox="0 0 24 24"
    //         stroke="currentColor"
    //       >
    //         <path
    //           strokeLinecap="round"
    //           strokeLinejoin="round"
    //           strokeWidth="2"
    //           d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
    //         />
    //       </svg>
    //     </button>
    //   </div>
    //   <div className="flex-1" />
    // </div>
  );
};

const NavBar = ({
  searchQuery,
  setSearchQuery,
  searchLimit,
  setSearchLimit,
  searchThreshold,
  setSearchThreshold,
  onSearch,
}: NavBarProps) => {
  const isMobile = useMediaQuery("(max-width: 768px)");

  return isMobile ? (
    <MobileNavBar
      searchQuery={searchQuery}
      setSearchQuery={setSearchQuery}
      searchLimit={searchLimit}
      setSearchLimit={setSearchLimit}
      searchThreshold={searchThreshold}
      setSearchThreshold={setSearchThreshold}
      onSearch={onSearch}
    />
  ) : (
    <ComputerNavBar
      searchQuery={searchQuery}
      setSearchQuery={setSearchQuery}
      searchLimit={searchLimit}
      setSearchLimit={setSearchLimit}
      searchThreshold={searchThreshold}
      setSearchThreshold={setSearchThreshold}
      onSearch={onSearch}
    />
  );
};

export default NavBar;
