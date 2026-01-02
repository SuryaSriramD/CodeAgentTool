import { submitGithubScan } from "@/lib/api-client"
import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { githubUrl, branch, analyzers, timeout } = body

    if (!githubUrl) {
      return NextResponse.json({ error: "GitHub URL is required" }, { status: 400 })
    }

    const result = await submitGithubScan(githubUrl, branch, analyzers, timeout)

    return NextResponse.json(result)
  } catch (error) {
    console.error("[v0] GitHub scan error:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to submit scan" },
      { status: 500 },
    )
  }
}
