import HomeFlightSearchSection from "../components/home/HomeFlightSearchSection";
import HomeNavbar from "../components/home/HomeNavbar";
import { useAuth } from "../context/AuthContext";
import { useHomeFlightSearch } from "../hooks/useHomeFlightSearch";

export default function HomePage() {
  const { user, isLoading, logout } = useAuth();
  const searchVm = useHomeFlightSearch();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <HomeNavbar user={user} onLogout={logout} />
      <HomeFlightSearchSection {...searchVm} />
    </div>
  );
}

