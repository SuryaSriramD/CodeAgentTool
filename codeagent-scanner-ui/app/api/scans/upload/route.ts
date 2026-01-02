import { submitZipScan } from "@/lib/api-client"
import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("file") as File

    if (!file) {
      return NextResponse.json({ error: "File is required" }, { status: 400 })
    }

    if (!file.name.endsWith(".zip")) {
      return NextResponse.json({ error: "Only ZIP files are allowed" }, { status: 400 })
    }

    const result = await submitZipScan(file)

    return NextResponse.json(result)
  } catch (error) {
    console.error("[v0] ZIP upload error:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to upload file" },
      { status: 500 },
    )
  }
}
