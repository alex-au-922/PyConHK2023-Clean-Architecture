type NavBarProps = {
  searchQuery: string;
  setSearchQuery: (searchQuery: string) => void;
  onSearch: () => Promise<void>;
};

const NavBar = ({ searchQuery, setSearchQuery, onSearch }: NavBarProps) => {
  return (
    <div className="navbar bg-white flex">
      <div className="flex-1">
        <div className="normal-case text-xl">
          PyConHK 2023 Clean Architecture
        </div>
      </div>
      <div className="flex-1 gap-2">
        <div className="form-control">
          <input
            type="text"
            placeholder="Search"
            className="input input-bordered w-60 md:w-auto"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>
      <div className="flex-1">
        <button className="btn btn-neutral" onClick={() => onSearch()}>
          Search
        </button>
      </div>
    </div>
  );
};

export default NavBar;
