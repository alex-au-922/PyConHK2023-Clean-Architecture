import { useMediaQuery } from "usehooks-ts";
import mahjongIcon from "/single_mahjong.png";

type NavBarProps = {
  searchQuery: string;
  setSearchQuery: (searchQuery: string) => void;
  onSearch: () => Promise<void>;
};

const MobileNavBar = ({
  searchQuery,
  setSearchQuery,
  onSearch,
}: NavBarProps) => {
  const isVerySmallMobile = useMediaQuery("(max-width: 320px)");
  return (
    <div>
      <div tabIndex={0} className="collapse bg-white rounded-none">
        <input type="checkbox" />
        <div className="collapse-title text-xl font-medium flex items-center">
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
          <div className="flex-1" onClick={(e) => e.preventDefault()}>
            <div className="flex justify-center items-center">
              <img src={mahjongIcon} className="h-8 mr-2" />
              <div className="text-base md:text-ms break-normal text-center">
                PyConHK 2023 Clean Architecture
              </div>
            </div>
          </div>
        </div>
        <div className="collapse-content">
          <div className="flex justify-center items-center w-full">
            <div className="input-group w-full">
              <input
                type="text"
                placeholder={
                  isVerySmallMobile ? "Keywords" : "Enter keywords"
                }
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
        </div>
      </div>
    </div>
  );
};

const ComputerNavBar = ({
  searchQuery,
  setSearchQuery,
  onSearch,
}: NavBarProps) => {
  return (
    <div className="navbar bg-white flex gap-2">
      <div className="flex-1">
        <img src={mahjongIcon} className="h-12 mr-2" />
        <div className="normal-case text-xl">
          PyConHK 2023 Clean Architecture
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
  );
};

const NavBar = ({ searchQuery, setSearchQuery, onSearch }: NavBarProps) => {
  const isMobile = useMediaQuery("(max-width: 768px)");
  
  return isMobile ? (
    <MobileNavBar
      searchQuery={searchQuery}
      setSearchQuery={setSearchQuery}
      onSearch={onSearch}
    />
  ) : (
    <ComputerNavBar
      searchQuery={searchQuery}
      setSearchQuery={setSearchQuery}
      onSearch={onSearch}
    />
  );
};

export default NavBar;
