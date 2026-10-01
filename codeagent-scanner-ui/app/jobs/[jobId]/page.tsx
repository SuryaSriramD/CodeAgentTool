import { RunDetail } from "@/components/scanner/runs";
export default async function JobPage({ params }: { params: Promise<{ jobId: string }> }) { const { jobId } = await params; return <RunDetail id={jobId} />; }
