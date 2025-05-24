"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { MessageCircle, X, Send, User, Bot } from "lucide-react"
import { cn } from "@/lib/utils"

type Message = {
  id: string
  content: string
  sender: "user" | "bot"
  timestamp: Date
}

export function ChatPopup() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! How can I assist you with file uploads today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isTyping, setIsTyping] = useState(false)

  const toggleChat = () => {
    setIsOpen(!isOpen)
  }

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault()

    if (!inputValue.trim()) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")

    // Simulate bot typing
    setIsTyping(true)

    // Simulate bot response after a delay
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: getBotResponse(inputValue),
        sender: "bot",
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, botMessage])
      setIsTyping(false)
    }, 1500)
  }

  // Simple bot response logic
  const getBotResponse = (message: string): string => {
    const lowerMessage = message.toLowerCase()

    if (lowerMessage.includes("upload") || lowerMessage.includes("file")) {
      return "You can upload files by dragging and dropping them into the upload area or by clicking 'browse' to select files from your device. We support all file types up to 10MB."
    } else if (lowerMessage.includes("delete") || lowerMessage.includes("remove")) {
      return "To remove a file before uploading, click the X button next to the file name. For files that have already been uploaded, you'll find a delete option in the uploaded files section."
    } else if (lowerMessage.includes("help") || lowerMessage.includes("support")) {
      return "I'm here to help! You can ask me questions about uploading files, managing your uploads, or any other features of our platform."
    } else if (lowerMessage.includes("hello") || lowerMessage.includes("hi")) {
      return "Hello there! How can I assist you with file management today?"
    } else {
      return "I'm not sure I understand. Could you please rephrase your question? I'm here to help with file uploads and management."
    }
  }

  return (
    <>
      {/* Chat toggle button */}
      <Button
        className="fixed bottom-6 right-6 rounded-full h-14 w-14 shadow-[0_0_15px_rgba(168,85,247,0.5)] bg-purple-900 hover:bg-purple-800 text-white pulse-glow z-50"
        onClick={toggleChat}
      >
        {isOpen ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </Button>

      {/* Chat popup */}
      <div
        className={cn(
          "fixed bottom-24 right-6 w-80 md:w-96 transition-all duration-300 transform z-50",
          isOpen ? "scale-100 opacity-100" : "scale-95 opacity-0 pointer-events-none",
        )}
      >
        <Card className="shadow-[0_0_20px_rgba(168,85,247,0.3)] border-purple-500/30 bg-slate-900/90 backdrop-blur-md text-white">
          <CardHeader className="bg-purple-900/80 text-white p-4 border-b border-purple-500/30">
            <div className="flex items-center space-x-2">
              <Bot className="h-5 w-5" />
              <h3 className="font-medium">Cosmic Assistant</h3>
            </div>
          </CardHeader>

          <CardContent className="p-4 h-80 overflow-y-auto bg-slate-900/50">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn("flex", message.sender === "user" ? "justify-end" : "justify-start")}
                >
                  <div
                    className={cn(
                      "max-w-[80%] rounded-lg p-3",
                      message.sender === "user"
                        ? "bg-purple-700 text-white"
                        : "bg-slate-800 text-gray-100 border border-purple-500/20",
                    )}
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      {message.sender === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                      <span className="text-xs font-medium">{message.sender === "user" ? "You" : "Assistant"}</span>
                    </div>
                    <p className="text-sm">{message.content}</p>
                    <div className="text-xs opacity-70 text-right mt-1">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </div>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-slate-800 rounded-lg p-3 max-w-[80%] border border-purple-500/20">
                    <div className="flex space-x-1">
                      <div
                        className="w-2 h-2 rounded-full bg-purple-400 animate-bounce"
                        style={{ animationDelay: "0ms" }}
                      ></div>
                      <div
                        className="w-2 h-2 rounded-full bg-purple-400 animate-bounce"
                        style={{ animationDelay: "150ms" }}
                      ></div>
                      <div
                        className="w-2 h-2 rounded-full bg-purple-400 animate-bounce"
                        style={{ animationDelay: "300ms" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>

          <CardFooter className="p-3 border-t border-purple-500/30 bg-slate-900/80">
            <form onSubmit={handleSendMessage} className="flex w-full space-x-2">
              <Input
                placeholder="Type your message..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                className="flex-1 bg-slate-800 border-purple-500/30 text-white placeholder:text-gray-400"
              />
              <Button
                type="submit"
                size="icon"
                disabled={!inputValue.trim()}
                className="bg-purple-700 hover:bg-purple-600 text-white"
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </CardFooter>
        </Card>
      </div>
    </>
  )
}
