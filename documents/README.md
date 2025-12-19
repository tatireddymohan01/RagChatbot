# Documents Folder

This folder is used for document processing by the RAG Chatbot system with **automatic monitoring**.

## How to Use

### Automatic Processing (Recommended)

1. **Add Your Documents**: Simply place any documents in this folder
   - Supported formats: PDF (.pdf), Word (.docx, .doc), Text (.txt)

2. **Automatic Detection**: The system automatically:
   - ✅ Processes new documents on startup
   - ✅ Tracks which files have been processed
   - ✅ Only processes new or modified files
   - ✅ Skips already-processed files

### Manual Processing

If you want to manually trigger processing:

```bash
# Process only new/modified documents
curl -X POST "http://localhost:8000/ingest/folder"

# Reset tracking and reprocess all documents
curl -X POST "http://localhost:8000/ingest/folder/reset"
curl -X POST "http://localhost:8000/ingest/folder"
```

## How It Works

1. **Place documents** in this folder
2. **Restart the application** or call `/ingest/folder` endpoint
3. System automatically:
   - Scans for new/modified files
   - Processes only changed documents
   - Updates the vector database
   - Tracks processed files in `.processed_files.json`

## Supported File Types

- **PDF** (.pdf) - Portable Document Format files
- **Word** (.docx, .doc) - Microsoft Word documents
- **Text** (.txt) - Plain text files

## Tracking System

The system maintains a `.processed_files.json` file that tracks:
- Which files have been processed
- File checksums to detect modifications
- This ensures efficient processing (no duplicate work)

## Notes

- ✅ **Smart Processing**: Only new or modified files are processed
- ✅ **Automatic on Startup**: New documents are detected when server starts
- ✅ **Change Detection**: Modifying a file will trigger reprocessing
- ✅ **No Duplicates**: Previously processed files are skipped
- 🔄 **Manual Trigger**: Use `/ingest/folder` endpoint anytime
- 🔄 **Force Reprocess**: Use `/ingest/folder/reset` to clear tracking
