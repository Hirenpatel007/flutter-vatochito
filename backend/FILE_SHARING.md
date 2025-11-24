# File Sharing Feature Documentation

## Overview
Vatochito now supports comprehensive file sharing capabilities, allowing users to send and receive images, videos, audio files, and documents in real-time chat conversations.

## Supported File Types

### Images
- **Formats**: JPEG, PNG, GIF, WebP
- **MIME Types**: `image/jpeg`, `image/png`, `image/gif`, `image/webp`
- **Display**: Inline preview with download option
- **Max Size**: 50MB (configurable)

### Videos
- **Formats**: MP4, WebM, QuickTime
- **MIME Types**: `video/mp4`, `video/webm`, `video/quicktime`
- **Display**: Inline video player with controls
- **Max Size**: 50MB (configurable)

### Audio
- **Formats**: MP3, WAV, OGG, M4A
- **MIME Types**: `audio/mpeg`, `audio/wav`, `audio/ogg`, `audio/mp4`
- **Display**: Inline audio player
- **Max Size**: 50MB (configurable)

### Documents
- **Formats**: PDF, Word (DOC/DOCX), Excel (XLS/XLSX), Text
- **MIME Types**: 
  - `application/pdf`
  - `application/msword`
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - `application/vnd.ms-excel`
  - `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - `text/plain`
- **Display**: Download link with file icon and size
- **Max Size**: 50MB (configurable)

## Backend Implementation

### Models

#### Message Model
```python
class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('file', 'File'),
    ]
    
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
```

#### Attachment Model
```python
class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=generate_upload_path)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
```

### API Endpoints

#### Send Message with Files
```
POST /chat/conversations/{conversation_id}/messages/
Content-Type: multipart/form-data

Fields:
- content: string (optional) - Text message content
- message_type: string - One of: text, image, video, audio, file
- uploaded_files: file[] - Array of files to upload
```

**Example using cURL**:
```bash
curl -X POST \
  http://localhost:8000/api/chat/conversations/1/messages/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "content=Check out this image!" \
  -F "message_type=image" \
  -F "uploaded_files=@/path/to/image.jpg"
```

**Example Response**:
```json
{
  "id": 123,
  "sender": {
    "id": 1,
    "username": "alice",
    "avatar": null
  },
  "message_type": "image",
  "content": "Check out this image!",
  "created_at": "2024-01-15T10:30:00Z",
  "attachments": [
    {
      "id": 45,
      "file": "http://localhost:8000/media/attachments/2024/01/15/image.jpg",
      "file_name": "image.jpg",
      "file_size": 524288,
      "mime_type": "image/jpeg"
    }
  ]
}
```

## Frontend Implementation

### Components

#### FileUpload Component
Location: `frontend/src/components/FileUpload.js`

**Props**:
- `onFilesSelected(files)`: Callback when files are selected
- `maxSize`: Maximum file size in bytes (default: 50MB)

**Features**:
- Five upload buttons for specific file types:
  - 🖼️ Images
  - 🎥 Videos
  - 🎵 Audio
  - 📄 Documents
  - ⬆️ All files
- Drag-and-drop zone
- File validation (type and size)
- Multi-file selection support

**Usage**:
```javascript
<FileUpload 
  onFilesSelected={(files) => setSelectedFiles(files)}
  maxSize={50 * 1024 * 1024}
/>
```

#### FilePreview Component
Location: `frontend/src/components/FilePreview.js`

**Props**:
- `files`: Array of File objects to preview
- `onRemove(index)`: Callback to remove a file

**Features**:
- Image thumbnails for image files
- File icons for other types
- File name and size display
- Remove button for each file
- Mobile-responsive layout

**Usage**:
```javascript
<FilePreview 
  files={selectedFiles}
  onRemove={(index) => removeFile(index)}
/>
```

#### MessageBubble Component (Enhanced)
Location: `frontend/src/components/MessageBubble.js`

**New Features**:
- Image attachments with inline preview
- Video attachments with video player
- Audio attachments with audio player
- Document attachments with download link
- File size formatting
- Download buttons
- Mobile-responsive media

### User Flow

1. **Opening File Upload**
   - User clicks the attachment button (📎) in MessageInput
   - File upload modal appears

2. **Selecting Files**
   - Click specific type button (Images, Videos, etc.)
   - OR click "Upload Any File" button
   - OR drag and drop files onto the drop zone

3. **File Preview**
   - Selected files appear in FilePreview component
   - Image thumbnails shown for images
   - File icons shown for other types
   - User can remove files before sending

4. **Sending Files**
   - User clicks send button (➤)
   - Files upload via multipart/form-data
   - Progress indicator (optional enhancement)
   - Message appears in chat with attachments

5. **Receiving Files**
   - Files appear in MessageBubble
   - Images: Inline preview with download button
   - Videos: Video player with controls
   - Audio: Audio player
   - Documents: Download link with file info

## File Upload Process

### Frontend (ChatContext)
```javascript
// Text only - WebSocket (real-time)
if (content.trim() && !files.length) {
  wsService.sendMessage(content, 'text', null);
}

// With files - HTTP API (reliable upload)
if (files.length > 0) {
  const formData = new FormData();
  formData.append('content', content);
  formData.append('message_type', determineType(files[0]));
  files.forEach(file => formData.append('uploaded_files', file));
  
  await chatService.sendMessageWithFiles(conversationId, formData);
  await loadMessages(conversationId);
}
```

### Backend (MessageSerializer)
```python
def create(self, validated_data):
    uploaded_files = validated_data.pop('uploaded_files', [])
    message = super().create(validated_data)
    
    # Create attachments
    for file in uploaded_files:
        Attachment.objects.create(
            message=message,
            file=file,
            file_name=file.name,
            file_size=file.size,
            mime_type=file.content_type
        )
    
    return message
```

## Security Considerations

### File Validation
- **Type Checking**: Only allowed MIME types accepted
- **Size Limiting**: 50MB default limit (configurable)
- **Extension Validation**: Cross-check extension with MIME type
- **Virus Scanning**: Optional - integrate ClamAV for production

### Storage
- **Development**: Local filesystem (`MEDIA_ROOT`)
- **Production**: AWS S3 (configured in `production.py`)
- **Access Control**: Files served through Django authentication
- **URL Signing**: Use signed URLs for S3 (optional)

### Upload Protection
- **Rate Limiting**: Prevent upload spam
- **Authentication**: Require valid JWT token
- **Conversation Membership**: Verify user is member before upload

## Configuration

### Backend Settings

#### File Size Limit
```python
# settings/base.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
```

#### Media Files
```python
# Development
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Production (AWS S3)
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

### Frontend Configuration

#### Maximum File Size
```javascript
// components/FileUpload.js
<FileUpload maxSize={50 * 1024 * 1024} />
```

#### Allowed Types
```javascript
const allowedTypes = {
  image: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  video: ['video/mp4', 'video/webm', 'video/quicktime'],
  audio: ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4'],
  document: [/* ... */]
};
```

## Mobile Responsiveness

### Breakpoints
- **Desktop**: > 768px - Full size media (300px max)
- **Tablet**: 481px - 768px - Medium media (250px max)
- **Mobile**: ≤ 480px - Compact media (200px max)

### Touch Optimizations
- Minimum touch target: 44x44px for buttons
- Larger file upload buttons on mobile
- Responsive media players
- Touch-friendly file preview tiles

## Testing

### Manual Testing Checklist

1. **Image Upload**
   - [ ] Upload single image
   - [ ] Upload multiple images
   - [ ] Preview shows correctly
   - [ ] Download works
   - [ ] Mobile display is correct

2. **Video Upload**
   - [ ] Upload video file
   - [ ] Video player loads
   - [ ] Controls work properly
   - [ ] Download works

3. **Audio Upload**
   - [ ] Upload audio file
   - [ ] Audio player loads
   - [ ] Playback controls work
   - [ ] Mobile player works

4. **Document Upload**
   - [ ] Upload PDF
   - [ ] Upload Word document
   - [ ] Download link works
   - [ ] File size displays correctly

5. **Validation**
   - [ ] Reject files over size limit
   - [ ] Reject unsupported file types
   - [ ] Show error messages

6. **Mobile Testing**
   - [ ] Upload buttons are touch-friendly
   - [ ] Media displays correctly
   - [ ] Download works on mobile
   - [ ] Drag-and-drop (if supported)

### Example Test Cases

```python
# backend/chat/tests/test_file_upload.py
def test_upload_image():
    conversation = create_test_conversation()
    with open('test_image.jpg', 'rb') as img:
        response = client.post(
            f'/api/chat/conversations/{conversation.id}/messages/',
            {
                'content': 'Test image',
                'message_type': 'image',
                'uploaded_files': img
            },
            format='multipart'
        )
    assert response.status_code == 201
    assert Message.objects.last().attachments.count() == 1
```

## Future Enhancements

1. **Progress Indicators**
   - Show upload progress percentage
   - Cancel upload in progress

2. **Image Optimization**
   - Compress images on upload
   - Generate thumbnails
   - Lazy loading for galleries

3. **Video Processing**
   - Generate video thumbnails
   - Compress videos
   - Multiple quality options

4. **Advanced Features**
   - Voice message recording
   - Screen recording
   - File galleries
   - Image editing before send
   - File expiration dates
   - Batch download

5. **Performance**
   - Resume interrupted uploads
   - Chunked upload for large files
   - CDN integration
   - Image lazy loading

## Troubleshooting

### Files Not Uploading
- Check `DATA_UPLOAD_MAX_MEMORY_SIZE` setting
- Verify CSRF token is present
- Check network tab for error responses
- Ensure `multipart/form-data` content type

### Files Not Displaying
- Verify `MEDIA_URL` is configured
- Check file permissions on server
- Ensure CORS allows media domain
- Verify attachment URLs are absolute

### Performance Issues
- Enable file compression
- Use CDN for media files
- Implement lazy loading
- Optimize database queries

## Support

For issues or questions:
- Check console logs (browser and server)
- Review API_DOCUMENTATION.md
- Check Django logs in `logs/` directory
- Test with `create_test_conversation.py`

---

**Version**: 1.0  
**Last Updated**: January 2024  
**Tested**: ✅ Development environment
