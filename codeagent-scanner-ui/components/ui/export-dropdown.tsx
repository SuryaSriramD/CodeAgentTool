"use client";

import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Download, ChevronDown, Sparkles } from "lucide-react";
import { Label } from "@/components/ui/label";

interface ExportDropdownProps {
  onExport: (
    format: "html" | "csv" | "markdown" | "json",
    includeEnhanced: boolean
  ) => void;
  disabled?: boolean;
  label?: string;
  showEnhancedOption?: boolean;
}

export function ExportDropdown({
  onExport,
  disabled = false,
  label = "Export Report",
  showEnhancedOption = true,
}: ExportDropdownProps) {
  const [includeEnhanced, setIncludeEnhanced] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const handleExport = (format: "html" | "csv" | "markdown" | "json") => {
    onExport(format, includeEnhanced);
    setIsOpen(false);
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className="border-border bg-transparent"
          disabled={disabled}
        >
          <Download size={18} />
          {label}
          <ChevronDown size={16} className="ml-1" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-72">
        <DropdownMenuLabel>Export Format</DropdownMenuLabel>
        <DropdownMenuSeparator />

        {showEnhancedOption && (
          <>
            <div className="px-2 py-3 mb-2 bg-accent/30 rounded-md mx-2">
              <div className="flex items-start space-x-3">
                <Checkbox
                  id="include-enhanced"
                  checked={includeEnhanced}
                  onCheckedChange={(checked) =>
                    setIncludeEnhanced(checked === true)
                  }
                  className="mt-0.5"
                />
                <div className="flex-1">
                  <Label
                    htmlFor="include-enhanced"
                    className="text-sm font-medium cursor-pointer flex items-center gap-2"
                  >
                    <Sparkles size={14} className="text-primary" />
                    Include AI-Enhanced Analysis
                  </Label>
                  <p className="text-xs text-muted mt-1">
                    Export with AI-generated fixes and recommendations
                  </p>
                </div>
              </div>
            </div>
            <DropdownMenuSeparator />
          </>
        )}

        <DropdownMenuItem onClick={() => handleExport("html")}>
          <span className="mr-2">📄</span>
          HTML Report
          <span className="ml-auto text-xs text-muted">Recommended</span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport("csv")}>
          <span className="mr-2">📊</span>
          CSV Spreadsheet
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport("markdown")}>
          <span className="mr-2">📝</span>
          Markdown
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => handleExport("json")}>
          <span className="mr-2">🔧</span>
          JSON (Developer)
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
