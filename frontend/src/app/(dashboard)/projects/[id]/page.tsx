"use client";

import { useEffect, useState, useRef } from "react";
import { useApi } from "@/lib/api";
import { useParams } from "next/navigation";
import { UploadCloud, FileText, CheckCircle2, Loader2, RefreshCw, LayoutTemplate } from "lucide-react";
import Link from "next/link";

export default function ProjectDashboard() {
  const { id } = useParams();
  const { request } = useApi();
  const [project, setProject] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadProject = async () => {
    try {
      const data = await request(`/projects/${id}`);
      setProject(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadProject();
    // Poll every 5s if there is a processing document
    const interval = setInterval(() => {
        setProject((prev: any) => {
            if (prev?.documents?.some((d:any) => d.status === 'PROCESSING' || d.status === 'PENDING')) {
                loadProject();
            }
            return prev;
        });
    }, 5000);
    return () => clearInterval(interval);
  }, [id, request]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await request(`/documents/upload?project_id=${id}`, {
        method: "POST",
        body: formData,
      });
      await loadProject();
    } catch (err) {
      alert("Upload failed. Make sure it's a valid document under 20MB.");
    } finally {
      setUploading(false);
    }
  };

  if (!project) return <div className="p-8 text-neutral-400">Loading workspace...</div>;

  const hasSprints = project.sprints && project.sprints.length > 0;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-12">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">{project.name}</h1>
          <p className="text-neutral-400">{project.description}</p>
        </div>
        {hasSprints && (
            <Link href={`/projects/${id}/sprints`} className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 shadow-lg shadow-purple-500/20">
                <LayoutTemplate className="w-4 h-4" />
                View Sprint Board
            </Link>
        )}
      </div>

      {/* Upload Zone */}
      <section>
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
           <FileText className="w-5 h-5 text-purple-400" />
           Requirements Documents
        </h2>
        
        <div 
            onClick={() => fileInputRef.current?.click()}
            className="w-full border-2 border-dashed border-white/10 rounded-2xl p-12 text-center bg-white/5 hover:bg-white/10 transition-colors cursor-pointer relative overflow-hidden group"
        >
            <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
                className="hidden" 
                accept=".pdf,.docx,.txt"
            />
            
            {uploading ? (
                <div className="flex flex-col items-center">
                    <Loader2 className="w-10 h-10 text-purple-500 animate-spin mb-4" />
                    <p className="text-lg font-medium">Uploading securely...</p>
                </div>
            ) : (
                <div className="flex flex-col items-center">
                    <div className="w-16 h-16 rounded-full bg-purple-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <UploadCloud className="w-8 h-8 text-purple-500" />
                    </div>
                    <p className="text-lg font-medium mb-1">Click or drag document to analyze</p>
                    <p className="text-sm text-neutral-500">Supports PDF, DOCX, TXT (Max 20MB)</p>
                </div>
            )}
        </div>
      </section>

      {/* Document Status */}
      {project.documents?.length > 0 && (
          <section>
            <h3 className="text-lg font-medium mb-4">Processing History</h3>
            <div className="space-y-3">
                {project.documents.map((doc: any) => (
                    <div key={doc.id} className="flex items-center justify-between p-4 rounded-xl border border-white/10 bg-[#111]">
                        <div className="flex items-center gap-3">
                            <FileText className="w-5 h-5 text-neutral-400" />
                            <div>
                                <p className="font-medium text-sm">{doc.fileName}</p>
                                <p className="text-xs text-neutral-500">{new Date(doc.createdAt).toLocaleString()}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            {doc.status === 'COMPLETED' ? (
                                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-green-500/10 text-green-400 text-xs font-medium">
                                    <CheckCircle2 className="w-3.5 h-3.5" />
                                    Analyzed
                                </span>
                            ) : doc.status === 'ERROR' ? (
                                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-red-500/10 text-red-400 text-xs font-medium">
                                    Failed
                                </span>
                            ) : (
                                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 text-xs font-medium">
                                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                                    Processing AI Agents...
                                </span>
                            )}
                        </div>
                    </div>
                ))}
            </div>
          </section>
      )}
    </div>
  );
}
