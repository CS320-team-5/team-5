import theme from "../../styles/theme.module.css";

export function FilterList({ filterList }: { filterList: string[] }) {
  return filterList.map(filter => (
    <button className="filter-button" type="button" key={filter}>
      <span className={theme["small-text"]}>{filter}</span>
    </button>
  ));
}
