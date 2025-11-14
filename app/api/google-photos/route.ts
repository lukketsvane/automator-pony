import { NextResponse } from 'next/server'

const SHARED_ALBUM_URL = 'https://photos.app.goo.gl/ZMeEZxpuzC1Sj8uH8'

export async function GET() {
  try {
    console.log('[v0] Fetching videos from Google Photos shared album')
    
    const response = await fetch(SHARED_ALBUM_URL, {
      redirect: 'follow', // Explicitly follow redirects
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
      }
    })
    
    console.log('[v0] Response status:', response.status)
    console.log('[v0] Final URL after redirect:', response.url)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch album: ${response.status}`)
    }
    
    const html = await response.text()
    console.log('[v0] Album page fetched, length:', html.length)
    
    // Extract video data from the page
    // Google Photos embeds data in JSON within the HTML
    const videos: any[] = []
    
    // Pattern 1: Look for media URLs in the HTML
    const urlPattern = /https:\/\/lh3\.googleusercontent\.com\/[^"'\s]+/g
    const urls = html.match(urlPattern) || []
    
    // Pattern 2: Extract video metadata from AF_initDataCallback
    const dataCallbackPattern = /AF_initDataCallback\({[^}]*key:\s*'ds:(\d+)'[^}]*data:(\[[^\]]*\[[^\]]*\])/g
    let match
    
    const videoDataMap = new Map<string, any>()
    
    while ((match = dataCallbackPattern.exec(html)) !== null) {
      try {
        const dataStr = match[2]
        // Basic extraction without full JSON parsing due to complex nested structure
        if (dataStr.includes('video/') || dataStr.includes('.mp4') || dataStr.includes('.mov')) {
          // Find video URLs
          const videoUrlMatch = dataStr.match(/https:\/\/[^"'\s,\]]+\.(mp4|mov|avi|webm)/gi)
          if (videoUrlMatch) {
            videoUrlMatch.forEach(url => {
              if (!videoDataMap.has(url)) {
                videoDataMap.set(url, { url })
              }
            })
          }
        }
      } catch (e) {
        console.log('[v0] Skipping data chunk due to parse error')
      }
    }
    
    // Pattern 3: Look for base64 encoded data that contains video info
    const base64Pattern = /"(https:\/\/lh3\.googleusercontent\.com\/[^"]+)"/g
    const imageUrls: string[] = []
    
    while ((match = base64Pattern.exec(html)) !== null) {
      const url = match[1]
      if (url.includes('lh3.googleusercontent.com')) {
        imageUrls.push(url)
      }
    }
    
    console.log(`[v0] Found ${imageUrls.length} potential media URLs`)
    
    // Create video objects from the extracted data
    // Since direct video URLs are protected, we'll use thumbnail URLs and transform them
    const uniqueUrls = [...new Set(imageUrls)]
    
    uniqueUrls.forEach((url, index) => {
      // Google Photos URLs can be transformed for video playback
      // Remove size parameters and add video parameter
      const baseUrl = url.split('=')[0]
      
      videos.push({
        id: `video-${index}`,
        title: `Video ${index + 1}`,
        thumbnail: `${baseUrl}=w640-h360-c`,
        videoUrl: `${baseUrl}=dv`, // =dv parameter attempts to get video download
        width: 1280,
        height: 720,
        mimeType: 'video/mp4'
      })
    })
    
    // Limit to first 20 videos to avoid overwhelming the player
    const limitedVideos = videos.slice(0, 20)
    
    console.log(`[v0] Returning ${limitedVideos.length} videos`)
    
    if (limitedVideos.length === 0) {
      return NextResponse.json({
        videos: [],
        error: 'No videos found. Google Photos API requires OAuth authentication for programmatic access. Consider adding OAuth or manually embedding video URLs.',
        requiresOAuth: true
      })
    }
    
    return NextResponse.json({ videos: limitedVideos })
    
  } catch (error) {
    console.error('[v0] Error fetching Google Photos:', error)
    
    return NextResponse.json({
      videos: [],
      error: error instanceof Error ? error.message : 'Failed to fetch videos from Google Photos',
      requiresOAuth: true
    })
  }
}
