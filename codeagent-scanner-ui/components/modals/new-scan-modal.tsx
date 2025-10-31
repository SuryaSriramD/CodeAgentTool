"use client";

import type React from "react";
import { useState, useRef } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Github, Upload } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import { useCreateScan } from "@/lib/hooks/use-create-scan";
import { githubScanSchema, zipScanSchema } from "@/lib/schemas/scan";

interface NewScanModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function NewScanModal({ open, onOpenChange }: NewScanModalProps) {
  const [activeTab, setActiveTab] = useState("github");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const router = useRouter();
  const createScan = useCreateScan();

  const githubForm = useForm({
    resolver: zodResolver(githubScanSchema),
    defaultValues: {
      githubUrl: "",
      branch: "",
    },
  });

  const zipForm = useForm({
    resolver: zodResolver(zipScanSchema),
    defaultValues: {
      file: undefined,
    },
  });

  const handleGithubScan = async (data: any) => {
    try {
      console.log("[NewScanModal] Submitting GitHub scan:", data.githubUrl);
      const result = await createScan.mutateAsync({
        type: "github",
        githubUrl: data.githubUrl,
        branch: data.branch || undefined, // Only send if provided
      });

      console.log("[NewScanModal] Scan submitted successfully:", result);
      console.log("[NewScanModal] Job ID:", result.job_id);

      githubForm.reset();
      onOpenChange(false);

      toast({
        title: "✅ Scan Started",
        description: "Redirecting to job details...",
      });

      const jobUrl = `/jobs/${result.job_id}`;
      console.log("[NewScanModal] Navigating to:", jobUrl);
      router.push(jobUrl);
    } catch (error) {
      console.error("[Scan Error] GitHub scan failed:", error);
      // Error toast is already handled by the hook
    }
  };

  const handleZipUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const file = fileInputRef.current?.files?.[0];

    if (!file) {
      toast({
        title: "❌ No File Selected",
        description: "Please select a ZIP file to upload",
        variant: "destructive",
      });
      return;
    }

    // Validate file type
    if (!file.name.endsWith(".zip")) {
      toast({
        title: "❌ Invalid File Type",
        description: "Please upload a ZIP file (.zip extension)",
        variant: "destructive",
      });
      return;
    }

    try {
      const result = await createScan.mutateAsync({
        type: "zip",
        file,
      });

      zipForm.reset();
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      onOpenChange(false);

      toast({
        title: "✅ Upload Successful",
        description: "Redirecting to job details...",
      });

      router.push(`/jobs/${result.job_id}`);
    } catch (error) {
      console.error("[Scan Error] ZIP upload failed:", error);
      // Error toast is already handled by the hook
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-card border-border">
        <DialogHeader>
          <DialogTitle>Start New Scan</DialogTitle>
          <DialogDescription>
            Choose how you want to scan your code for vulnerabilities
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-background gap-2 p-1">
            <TabsTrigger
              value="github"
              className={`cursor-pointer transition-all ${
                activeTab === "github"
                  ? "glow-active bg-primary/10 text-primary"
                  : "text-muted-foreground"
              }`}
            >
              <Github size={16} className="mr-2" />
              GitHub URL
            </TabsTrigger>
            <TabsTrigger
              value="zip"
              className={`cursor-pointer transition-all ${
                activeTab === "zip"
                  ? "glow-active bg-primary/10 text-primary"
                  : "text-muted-foreground"
              }`}
            >
              <Upload size={16} className="mr-2" />
              Upload ZIP
            </TabsTrigger>
          </TabsList>

          <TabsContent value="github" className="space-y-4">
            <div className="border-2 border-border rounded-lg p-6">
              <form
                onSubmit={githubForm.handleSubmit(handleGithubScan)}
                className="space-y-4"
              >
                <div>
                  <Label htmlFor="github-url">Repository URL</Label>
                  <Input
                    id="github-url"
                    placeholder="https://github.com/owner/repo"
                    className="bg-background border-border mt-2"
                    {...githubForm.register("githubUrl")}
                  />
                  {githubForm.formState.errors.githubUrl && (
                    <p className="text-error text-sm mt-1">
                      {githubForm.formState.errors.githubUrl.message}
                    </p>
                  )}
                </div>
                <div>
                  <Label htmlFor="branch">Branch (optional)</Label>
                  <Input
                    id="branch"
                    placeholder="main"
                    className="bg-background border-border mt-2"
                    {...githubForm.register("branch")}
                  />
                </div>
                <Button
                  type="submit"
                  disabled={createScan.isPending}
                  className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary-dark hover:to-accent text-white cursor-pointer"
                >
                  <Github size={18} />
                  {createScan.isPending ? "Starting..." : "Scan Repository"}
                </Button>
              </form>
            </div>
          </TabsContent>

          <TabsContent value="zip" className="space-y-4">
            <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
              <form onSubmit={handleZipUpload} className="space-y-4">
                <div
                  className="hover:border-primary/50 transition-colors cursor-pointer"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload size={32} className="mx-auto mb-2 text-muted" />
                  <p className="font-medium">
                    {fileInputRef.current?.files?.[0]?.name ||
                      "Drop your ZIP file here"}
                  </p>
                  <p className="text-sm text-muted">
                    {fileInputRef.current?.files?.[0]
                      ? "Click to change"
                      : "or click to browse"}
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".zip"
                    className="hidden"
                  />
                </div>
                <Button
                  type="submit"
                  disabled={
                    createScan.isPending || !fileInputRef.current?.files?.[0]
                  }
                  className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary-dark hover:to-accent text-white cursor-pointer"
                >
                  {createScan.isPending ? "Uploading..." : "Upload & Scan"}
                </Button>
              </form>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
