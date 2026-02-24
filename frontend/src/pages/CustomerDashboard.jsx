import CustomerDashboardView from "../components/customerDashboard/CustomerDashboardView";
import { useCustomerDashboard } from "../hooks/useCustomerDashboard";

export default function CustomerDashboard() {
  const vm = useCustomerDashboard();
  return <CustomerDashboardView {...vm} />;
}

