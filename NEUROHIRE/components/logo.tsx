"use client"

import { Rocket, Star } from "lucide-react"

export function Logo() {
  return (
    <div className="z-40 flex items-center space-x-3 group cursor-pointer mb-8">
      

      {/* Logo text */}
      <div className="hidden md:block">
        {/* <h2 className="text-xl font-bold text-white group-hover:text-purple-200 transition-colors duration-300">
          NeuroHire
        </h2> */}
        <img
          src="/logo.png"
          alt="CosmicCloud Logo"
        className="w-20 h-20 rounded-full object-cover group-hover:opacity-90 transition-opacity duration-300"
        />

        {/* <p className="text-xs text-gray-400 group-hover:text-gray-300 transition-colors duration-300">
         RH SOLUTION
        </p> */}
      </div>

      {/* Mobile logo text (shorter) */}
      <div className="block md:hidden">
        <h2 className="text-lg font-bold text-white group-hover:text-purple-200 transition-colors duration-300">
          CosmicCloud
        </h2>
      </div>
    </div>
  )
}
