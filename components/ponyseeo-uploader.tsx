'use client'

import { useState } from 'react'
import { Upload, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export function PonyseeoUploader() {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
    }
  }

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    setUploading(true)
    
    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        await fetch('/api/upload', {
          method: 'POST',
          body: formData
        })
      } catch (error) {
        console.error('Upload failed:', error)
      }
    }
    
    setUploading(false)
    setFiles([])
  }

  return (
    <div className="container mx-auto p-8">
      <Card className="p-6">
        <h1 className="text-2xl font-bold mb-6">Upload Videos</h1>
        
        <div className="border-2 border-dashed border-border rounded-lg p-8 text-center mb-6">
          <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
          <input
            type="file"
            multiple
            accept="video/*"
            onChange={handleFileChange}
            className="hidden"
            id="file-input"
          />
          <label htmlFor="file-input">
            <Button asChild>
              <span>Select Videos</span>
            </Button>
          </label>
        </div>

        {files.length > 0 && (
          <div className="space-y-2 mb-6">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <span className="text-sm">{file.name}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeFile(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}

        <Button
          onClick={handleUpload}
          disabled={files.length === 0 || uploading}
          className="w-full"
        >
          {uploading ? 'Uploading...' : `Upload ${files.length} video${files.length !== 1 ? 's' : ''}`}
        </Button>
      </Card>
    </div>
  )
}
