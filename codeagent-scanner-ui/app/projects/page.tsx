import { ProjectsPage } from "@/components/scanner/projects";
export default async function Page({ searchParams }: { searchParams: Promise<{ project?: string }> }) { const params = await searchParams; return <ProjectsPage initialProject={params.project} />; }
