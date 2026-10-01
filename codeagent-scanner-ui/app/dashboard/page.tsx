import { Shell } from "@/components/scanner/shared";
import { NewScan } from "@/components/scanner/new-scan";
import { ReadinessSummary } from "@/components/scanner/readiness";
import { RunList } from "@/components/scanner/runs";
export default function Dashboard() {
  return <Shell title="Overview" description="Understand your code’s security, then review the proposed changes."><div className="stack"><ReadinessSummary /><NewScan /><RunList compact /></div></Shell>;
}
