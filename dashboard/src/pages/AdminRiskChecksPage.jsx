import SiteRiskTable from "../components/SiteRiskTable";

export default function AdminRiskChecksPage() {
  return (
    <div className="max-w-3xl mx-auto p-6">
      <h2 className="text-xl font-semibold text-slate-800 mb-4">Site Risk Checks</h2>
      <SiteRiskTable />
    </div>
  );
}
