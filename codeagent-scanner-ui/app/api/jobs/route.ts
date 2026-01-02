import { NextResponse } from "next/server"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function GET() {
  try {
    // Note: The backend doesn't have a /jobs endpoint that lists all jobs
    // This is a placeholder - you may need to implement this in the backend
    // For now, we'll return an empty list
    return NextResponse.json({ jobs: [] })
  } catch (error) {
    console.error("[v0] Failed to fetch jobs:", error)
    return NextResponse.json({ error: "Failed to fetch jobs" }, { status: 500 })
  }
}
