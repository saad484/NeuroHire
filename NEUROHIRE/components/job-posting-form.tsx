"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { API_ENDPOINTS } from "@/app/actions"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { CheckCircle, AlertCircle } from "lucide-react"

interface JobPostingFormProps {
  onJobCreated: () => void
}

export default function JobPostingForm({ onJobCreated }: JobPostingFormProps) {
  const [title, setTitle] = useState("")
  const [company, setCompany] = useState("")
  const [description, setDescription] = useState("")
  const [requiredSkills, setRequiredSkills] = useState("")
  const [requiredExperienceYears, setRequiredExperienceYears] = useState("")
  const [educationLevel, setEducationLevel] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(false)

    // Parse skills from comma-separated string to array
    const skillsArray = requiredSkills
      .split(",")
      .map(skill => skill.trim())
      .filter(skill => skill.length > 0)

    const jobData = {
      title,
      company,
      description,
      required_skills: skillsArray,
      required_experience_years: parseInt(requiredExperienceYears) || 0,
      education_level: educationLevel,
      active: true
    }

    try {
      const token = localStorage.getItem("neurohire_token")
      const response = await fetch(API_ENDPOINTS.JOBS, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Token ${token}`
        },
        body: JSON.stringify(jobData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Failed to create job posting")
      }

      // Reset form
      setTitle("")
      setCompany("")
      setDescription("")
      setRequiredSkills("")
      setRequiredExperienceYears("")
      setEducationLevel("")
      setSuccess(true)
      
      // Notify parent component
      onJobCreated()

      // Hide success message after 3 seconds
      setTimeout(() => {
        setSuccess(false)
      }, 3000)
    } catch (err: any) {
      setError(err.message || "Failed to create job posting")
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {success && (
        <Alert className="bg-green-900/20 text-green-300 border-green-500/30">
          <CheckCircle className="h-4 w-4 text-green-400" />
          <AlertDescription>Job posting created successfully!</AlertDescription>
        </Alert>
      )}
      
      {error && (
        <Alert className="bg-red-900/20 text-red-300 border-red-500/30">
          <AlertCircle className="h-4 w-4 text-red-400" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      <div className="space-y-2">
        <Label htmlFor="title" className="text-gray-200">Job Title</Label>
        <Input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Senior Software Engineer"
          required
          className="bg-slate-800/80 border-purple-500/30 text-white"
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="company" className="text-gray-200">Company</Label>
        <Input
          id="company"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          placeholder="e.g. TechCorp Inc."
          required
          className="bg-slate-800/80 border-purple-500/30 text-white"
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="description" className="text-gray-200">Job Description</Label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe the responsibilities and requirements..."
          required
          className="bg-slate-800/80 border-purple-500/30 text-white min-h-32"
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="requiredSkills" className="text-gray-200">Required Skills (comma-separated)</Label>
        <Input
          id="requiredSkills"
          value={requiredSkills}
          onChange={(e) => setRequiredSkills(e.target.value)}
          placeholder="e.g. React, TypeScript, Node.js"
          required
          className="bg-slate-800/80 border-purple-500/30 text-white"
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="requiredExperienceYears" className="text-gray-200">Required Experience (years)</Label>
          <Input
            id="requiredExperienceYears"
            type="number"
            min="0"
            value={requiredExperienceYears}
            onChange={(e) => setRequiredExperienceYears(e.target.value)}
            placeholder="e.g. 3"
            required
            className="bg-slate-800/80 border-purple-500/30 text-white"
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="educationLevel" className="text-gray-200">Education Level</Label>
          <Input
            id="educationLevel"
            value={educationLevel}
            onChange={(e) => setEducationLevel(e.target.value)}
            placeholder="e.g. Bachelor's Degree"
            required
            className="bg-slate-800/80 border-purple-500/30 text-white"
          />
        </div>
      </div>
      
      <Button 
        type="submit" 
        disabled={loading}
        className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
      >
        {loading ? "Creating..." : "Create Job Posting"}
      </Button>
    </form>
  )
}
