import React, { useState } from 'react';
import { Youtube, Play, Clock, Eye, ThumbsUp, ExternalLink, Info } from 'lucide-react';
import { motion } from 'framer-motion';

interface Video {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  embedUrl: string;
  duration: string;
  viewCount: string;
  likes?: string;
  channel?: string;
  publishDate?: string;
  tags?: string[];
}

interface VideosSectionProps {
  videos: Video[];
}

const VideosSection: React.FC<VideosSectionProps> = ({ videos }) => {
  const [activeVideo, setActiveVideo] = useState<string | null>(null);
  
  const closeVideo = () => {
    setActiveVideo(null);
  };
  
  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 }
    },
    hover: {
      y: -5,
      boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
      transition: { duration: 0.3 }
    }
  };

  return (
    <section className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-100">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
          <Youtube className="w-6 h-6 text-red-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Inspiring Visual Stories
          </h2>
          <p className="text-gray-600">Immersive video content to help you explore your destination</p>
        </div>
      </div>
      
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 gap-8"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {videos.map((video, index) => (
          <motion.div 
            key={video.id} 
            className="rounded-xl overflow-hidden border border-gray-200 bg-white hover:border-red-200 transition-all"
            variants={itemVariants}
            whileHover="hover"
          >
            {activeVideo === video.id ? (
              <div className="relative pt-[56.25%] bg-black">
                <iframe
                  src={`${video.embedUrl}?autoplay=1`}
                  className="absolute inset-0 w-full h-full"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
                <button 
                  onClick={closeVideo}
                  className="absolute top-3 right-3 bg-black bg-opacity-70 text-white rounded-full p-1"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            ) : (
              <div className="relative group">
                <div className="relative h-56 overflow-hidden">
                  <img
                    src={video.thumbnail}
                    alt={video.title}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-20 group-hover:bg-opacity-30 transition-opacity"></div>
                  <button
                    onClick={() => setActiveVideo(video.id)}
                    className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-red-600 text-white rounded-full w-14 h-14 flex items-center justify-center group-hover:bg-red-700 transition-colors"
                  >
                    <Play className="w-7 h-7 ml-1" fill="white" />
                  </button>
                  <div className="absolute bottom-3 right-3 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded-md flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {video.duration}
                  </div>
                  {video.tags && video.tags.length > 0 && (
                    <div className="absolute top-3 left-3">
                      <span className="bg-red-600 text-white text-xs px-2 py-1 rounded-md">
                        {video.tags[0]}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1">{video.title}</h3>
              
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                {video.description}
              </p>
              
              <div className="flex flex-wrap justify-between items-center mb-3">
                {video.channel && (
                  <div className="flex items-center text-sm text-gray-600 mr-4">
                    <Info className="w-4 h-4 mr-1 text-gray-400" />
                    <span>{video.channel}</span>
                  </div>
                )}
                
                {video.publishDate && (
                  <div className="text-sm text-gray-500">
                    {video.publishDate}
                  </div>
                )}
              </div>
              
              <div className="flex justify-between items-center pt-3 border-t border-gray-100">
                <div className="flex space-x-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <Eye className="w-4 h-4 mr-1 text-gray-400" />
                    <span>{video.viewCount}</span>
                  </div>
                  
                  {video.likes && (
                    <div className="flex items-center text-sm text-gray-600">
                      <ThumbsUp className="w-4 h-4 mr-1 text-gray-400" />
                      <span>{video.likes}</span>
                    </div>
                  )}
                </div>
                
                <a
                  href={video.embedUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-red-600 hover:text-red-800 text-sm font-medium flex items-center transition-colors"
                >
                  Watch on YouTube
                  <ExternalLink className="w-3.5 h-3.5 ml-1" />
                </a>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>
      
      {videos.length === 0 && (
        <div className="text-center py-10 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No videos found. Curated video content will appear here.</p>
        </div>
      )}
    </section>
  );
};

export default VideosSection;
