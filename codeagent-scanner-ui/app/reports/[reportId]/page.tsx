import { ReportDetail } from "@/components/scanner/reports";
export default async function ReportPage({ params, searchParams }: { params: Promise<{ reportId: string }>; searchParams: Promise<{ review?: string }> }) {
  const { reportId } = await params; const { review } = await searchParams;
  return <ReportDetail id={reportId} selectedReviewId={review} />;
}
