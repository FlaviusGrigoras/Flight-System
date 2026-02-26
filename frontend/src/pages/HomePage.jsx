import HomeFlightSearchSection from "../components/home/HomeFlightSearchSection";
import { useAuth } from "../context/AuthContext";
import { useHomeFlightSearch } from "../hooks/useHomeFlightSearch";

export default function HomePage() {
  const { isLoading } = useAuth();
  const searchVm = useHomeFlightSearch();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <HomeFlightSearchSection {...searchVm} />
    </div>
  );
}
