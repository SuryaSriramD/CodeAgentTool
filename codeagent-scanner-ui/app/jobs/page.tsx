import { Shell } from "@/components/scanner/shared";
import { RunList } from "@/components/scanner/runs";
export default function JobsPage() { return <Shell title="Runs" description="Track every scan and review, including queued, interrupted, and partial runs."><RunList /></Shell>; }
