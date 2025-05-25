"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Upload, X, FileText, Check } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { API_ENDPOINTS } from "@/app/actions"

interface ResumeUploaderProps {
  onResumeUploaded: () => void
}

export default function ResumeUploader({ onResumeUploaded }: ResumeUploaderProps) {
  const [files, setFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [processingInfo, setProcessingInfo] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    if (e.dataTransfer.files) {
      const newFiles = Array.from(e.dataTransfer.files)
      setFiles((prev) => [...prev, ...newFiles])
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files)
      setFiles((prev) => [...prev, ...newFiles])
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setUploading(true)
    setProgress(0)
    setError(null)
    setProcessingInfo("Preparing to upload resumes...")

    // Simulate initial upload progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 40) {
          clearInterval(interval)
          return 40
        }
        return prev + 5
      })
    }, 200)

    try {
      // Process each file
      for (const file of files) {
        setProcessingInfo(`Uploading resume: ${file.name}`)
        const formData = new FormData()
        formData.append("file", file)

        // Get auth token if available
        const token = localStorage.getItem("neurohire_token")

        // Upload to our Django backend
        const response = await fetch(API_ENDPOINTS.UPLOAD_RESUME, {
          method: "POST",
          body: formData,
          headers: token ? {
            "Authorization": `Token ${token}`
          } : undefined
        })

        if (!response.ok) {
          throw new Error(`Upload failed with status: ${response.status}`)
        }

        const result = await response.json()
        
        if (result.success) {
          setProgress(70)
          setProcessingInfo(`Processing resume with AI: extracting information...`)
          
          // Simulate AI processing time
          await new Promise(resolve => setTimeout(resolve, 1500))
          
          setProgress(90)
          setProcessingInfo(`Analyzing skills and experience...`)
          
          // Simulate final processing
          await new Promise(resolve => setTimeout(resolve, 1000))
          
          setUploadedFiles((prev) => [...prev, file.name])
        } else {
          throw new Error(result.error || "Upload failed")
        }
      }

      // Complete the progress
      setProgress(100)
      setProcessingInfo("Resume processing complete!")
      
      // Notify parent that resumes have been uploaded and processed
      onResumeUploaded()
      
      setTimeout(() => {
        setFiles([])
        setUploading(false)
        setProgress(0)
        setProcessingInfo(null)
      }, 2000)
    } catch (error: any) {
      console.error("Upload failed:", error)
      setError(error.message || "Failed to upload resume")
      setUploading(false)
    } finally {
      clearInterval(interval)
    }
  }

  return (
    <div className="space-y-6">
      {processingInfo && (
        <Alert className="bg-blue-900/20 text-blue-300 border-blue-500/30">
          <FileText className="h-4 w-4 text-blue-400" />
          <AlertDescription>{processingInfo}</AlertDescription>
        </Alert>
      )}
      
      {error && (
        <Alert className="bg-red-900/20 text-red-300 border-red-500/30">
          <X className="h-4 w-4 text-red-400" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {!uploading && (
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center backdrop-blur-md pulse-glow ${
            isDragging ? "border-purple-400 bg-purple-900/30" : "border-purple-500/30 bg-slate-900/50"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center justify-center space-y-4">
            <Upload className="w-12 h-12 text-purple-400" />
            <h3 className="text-xl font-medium text-white">Drag & Drop Resumes</h3>
            <p className="text-gray-400 max-w-md">
              Upload PDF, DOCX, or TXT resume files. Our AI will analyze them and extract key information.
            </p>
            <Button
              onClick={() => fileInputRef.current?.click()}
              variant="outline"
              className="mt-2 border-purple-500/30 text-purple-300 hover:bg-purple-900/30"
            >
              Browse Files
            </Button>
            <input
              type="file"
              className="hidden"
              multiple
              accept=".pdf,.docx,.doc,.txt"
              onChange={handleFileChange}
              ref={fileInputRef}
            />
          </div>
        </div>
      )}

      {files.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-white">Selected Files</h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 rounded-lg bg-slate-800/80 border border-purple-500/20"
              >
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-purple-400" />
                  <span className="text-gray-200 truncate max-w-xs">{file.name}</span>
                  <span className="text-xs text-gray-400">
                    {(file.size / 1024).toFixed(0)} KB
                  </span>
                </div>
                {!uploading && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-red-400 hover:bg-transparent"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {uploading && (
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-400">
              <span>Processing resumes...</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="h-2 bg-slate-700">
              <div className="h-full bg-gradient-to-r from-purple-600 to-blue-600 rounded-full" />
            </Progress>
          </div>
        </div>
      )}

      {files.length > 0 && !uploading && (
        <Button
          onClick={handleUpload}
          className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
        >
          Upload & Process {files.length} {files.length === 1 ? "Resume" : "Resumes"}
        </Button>
      )}

      {uploadedFiles.length > 0 && (
        <div className="mt-6 p-4 rounded-lg bg-green-900/20 border border-green-500/30">
          <div className="flex items-center space-x-2 mb-2">
            <Check className="w-5 h-5 text-green-400" />
            <h3 className="text-lg font-medium text-green-300">Successfully Processed</h3>
          </div>
          <ul className="space-y-1 text-gray-300">
            {uploadedFiles.map((fileName, index) => (
              <li key={index} className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-green-400" />
                <span>{fileName}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
