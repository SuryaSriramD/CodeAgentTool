"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { NewScanModal } from "@/components/modals/new-scan-modal"

export function NewScanButton() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button
        onClick={() => setOpen(true)}
        className="cursor-pointer bg-gradient-to-r from-primary to-accent hover:from-primary-dark hover:to-accent text-white"
      >
        <Plus size={20} />
        New Scan
      </Button>
      <NewScanModal open={open} onOpenChange={setOpen} />
    </>
  )
}
