export function FilterList({ filterList }: { filterList: string[] }) {
  return filterList.map(filter => (
    <button className="filter-button" type="button" key={filter}>
      <span className="filter-text">{filter}</span>
    </button>
  ));
}
