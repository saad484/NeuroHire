"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Upload, X, FileText, Check } from "lucide-react"
import { API_ENDPOINTS } from "@/app/actions"

export function FileUpload() {
  const [files, setFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
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

    // Simulate upload progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95) {
          clearInterval(interval)
          return 95
        }
        return prev + 5
      })
    }, 200)

    try {
      // Process each file
      for (const file of files) {
        const formData = new FormData()
        formData.append("file", file)

        // Use fetch directly to upload the file to our Django backend
        const response = await fetch(API_ENDPOINTS.UPLOAD_RESUME, {
          method: "POST",
          body: formData,
          // No credentials needed since we've configured AllowAny permission
        })

        if (!response.ok) {
          throw new Error(`Upload failed with status: ${response.status}`)
        }

        const result = await response.json()
        console.log("Upload result:", result)

        if (result.success) {
          setUploadedFiles((prev) => [...prev, file.name])
        }
      }

      // Complete the progress
      setProgress(100)
      setTimeout(() => {
        setFiles([])
        setUploading(false)
        setProgress(0)
      }, 1000)
    } catch (error) {
      console.error("Upload failed:", error)
      setUploading(false)
    } finally {
      clearInterval(interval)
    }
  }

  return (
    <div className="space-y-6">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center backdrop-blur-md pulse-glow ${
          isDragging ? "border-purple-400 bg-purple-900/30" : "border-purple-500/30 bg-slate-900/50"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className="mx-auto h-12 w-12 text-purple-300" />
        <h3 className="mt-2 text-lg font-medium text-white">Drag and drop your files here</h3>
        <p className="mt-1 text-sm text-gray-300">
          or{" "}
          <button
            className="text-purple-300 hover:text-purple-200 hover:underline"
            onClick={() => fileInputRef.current?.click()}
          >
            browse
          </button>{" "}
          to select files
        </p>
        <p className="mt-2 text-xs text-gray-400">Supports all file types up to 10MB</p>
        <input type="file" multiple className="hidden" onChange={handleFileChange} ref={fileInputRef} />
      </div>

      {files.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-white">Selected Files ({files.length})</h3>
          <ul className="space-y-2">
            {files.map((file, index) => (
              <li
                key={index}
                className="flex items-center justify-between p-3 bg-slate-800/70 backdrop-blur-md rounded-md border border-purple-500/20"
              >
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-purple-300" />
                  <span className="text-sm font-medium text-white">{file.name}</span>
                  <span className="text-xs text-gray-400">{(file.size / 1024).toFixed(1)} KB</span>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeFile(index)}
                  className="text-gray-300 hover:text-white hover:bg-purple-900/50"
                >
                  <X className="h-4 w-4" />
                </Button>
              </li>
            ))}
          </ul>

          <div className="flex items-center justify-between">
            <Button
              onClick={handleUpload}
              disabled={uploading}
              className="flex items-center space-x-2 bg-purple-700 hover:bg-purple-600 text-white"
            >
              <Upload className="h-4 w-4" />
              <span>Upload {files.length} files</span>
            </Button>
            <Button
              variant="outline"
              onClick={() => setFiles([])}
              disabled={uploading}
              className="border-purple-500/30 text-purple-300 hover:bg-purple-900/30"
            >
              Clear All
            </Button>
          </div>

          {uploading && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-300">
                <span>Uploading...</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div className="mt-8 space-y-4">
          <h3 className="text-lg font-medium text-white">Uploaded Files</h3>
          <ul className="space-y-2">
            {uploadedFiles.map((fileName, index) => (
              <li
                key={index}
                className="flex items-center justify-between p-3 bg-purple-900/30 backdrop-blur-md rounded-md border border-purple-500/30 pulse-glow"
              >
                <div className="flex items-center space-x-3">
                  <Check className="h-5 w-5 text-purple-300" />
                  <span className="text-sm font-medium text-white">{fileName}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
