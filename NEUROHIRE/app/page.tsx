import { FileUpload } from "@/components/file-upload"
import { ChatPopup } from "@/components/chat-popup"
import { Logo } from "@/components/logo"

export default function Home() {
  return (
    <main className="min-h-screen relative bg-black text-white overflow-hidden">
      {/* Enhanced space background */}
      <div className="space-bg"></div>

      {/* Stars layers */}
      <div className="stars-small absolute inset-0"></div>
      <div className="stars-medium absolute inset-0"></div>
      <div className="stars-large absolute inset-0"></div>
      <div className="stars-twinkle"></div>

      {/* Nebula effect */}
      <div className="nebula"></div>

      {/* Galaxy */}
      <div className="galaxy"></div>

      {/* Shooting stars */}
      <div className="shooting-star"></div>
      <div className="shooting-star"></div>
      <div className="shooting-star"></div>

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto p-6 md:p-24 space-y-8">
        {/* Logo */}
        <Logo />

        <section className="space-y-4">
          <h1 className="text-4xl font-bold tracking-tight text-white">Cosmic File Upload Portal</h1>
          <p className="text-gray-300 text-lg">
            Upload and manage your files in the vastness of digital space. Need help? Use the chat assistant in the
            bottom right.
          </p>
        </section>

        <FileUpload />

        <section className="mt-12 p-6 bg-slate-900/70 backdrop-blur-md rounded-lg border border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.15)]">
          <h2 className="text-2xl font-semibold mb-4 text-white">How It Works</h2>
          <div className="grid gap-6 md:grid-cols-3">
            <div className="p-4 rounded-lg bg-slate-800/80 border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.1)]">
              <div className="mb-2 text-xl font-medium text-purple-300">1. Select Files</div>
              <p className="text-gray-300">Drag and drop files or browse to select them from your device.</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-800/80 border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.1)]">
              <div className="mb-2 text-xl font-medium text-purple-300">2. Upload</div>
              <p className="text-gray-300">Click the upload button to securely transfer your files to our servers.</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-800/80 border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.1)]">
              <div className="mb-2 text-xl font-medium text-purple-300">3. Manage</div>
              <p className="text-gray-300">View, download, or delete your uploaded files as needed.</p>
            </div>
          </div>
        </section>
      </div>

      <ChatPopup />
    </main>
  )
}
