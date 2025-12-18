# 🎨 Web UI Guide

## Accessing the Web Interface

Once the server is running, open your browser and navigate to:
```
http://localhost:8000
```

## Features

### 📚 Document Management Sidebar

**Upload Documents:**
1. Click "Choose Files" button
2. Select PDF, DOCX, or TXT files (can select multiple)
3. Click "Upload Documents"
4. Wait for success confirmation

**Ingest from URL:**
1. Paste a URL in the input field
2. Click "Ingest URL"
3. The system will scrape and process the content

**System Status:**
- Shows real-time API health
- Displays current model being used
- Shows service version

### 💬 Chat Interface

**Asking Questions:**
1. Type your question in the input box
2. Press Enter or click "Send"
3. Wait for the AI response
4. Response includes source citations from your documents

**Chat Features:**
- **Session Memory**: Maintains conversation context
- **Source Citations**: Shows which documents were used
- **Multi-turn Dialogue**: Ask follow-up questions
- **Clear Chat**: Reset conversation and start fresh

## Usage Workflow

### Step 1: Ingest Content
Before chatting, you need to add documents:

**Option A - Upload Files:**
```
1. Click "Choose Files"
2. Select your documents
3. Click "Upload Documents"
4. Wait for "✅ Successfully ingested" message
```

**Option B - Ingest URL:**
```
1. Enter URL (e.g., https://en.wikipedia.org/wiki/Machine_learning)
2. Click "Ingest URL"
3. Wait for success confirmation
```

### Step 2: Start Chatting
Once documents are ingested:

```
1. Type: "What is machine learning?"
2. Press Enter
3. Review the answer and sources
4. Ask follow-up questions
```

### Step 3: Continue Conversation
The system remembers your conversation:

```
User: "What is machine learning?"
Bot: [Detailed answer with sources]

User: "Can you explain that in simpler terms?"
Bot: [Simplified explanation using previous context]
```

## UI Components Explained

### Message Display
- **User messages**: Blue bubbles on the right
- **Bot messages**: Gray bubbles on the left
- **Sources**: Expandable section below bot messages showing:
  - Document name
  - Page number (if applicable)
  - Relevant content excerpt

### Status Indicators
- **Green (●)**: System is healthy
- **Red (●)**: System is offline/error
- **Loading spinner**: Processing in progress

### Buttons
- **Send**: Submit your question
- **Clear Chat**: Reset conversation history
- **Upload Documents**: Process selected files
- **Ingest URL**: Scrape and process web content

## Tips for Best Results

### Document Ingestion
✅ **DO:**
- Upload relevant, well-formatted documents
- Use clear, text-based PDFs (not scanned images)
- Ingest multiple related documents for better context
- Wait for upload confirmation before chatting

❌ **DON'T:**
- Upload extremely large files (>50MB)
- Use password-protected PDFs
- Ingest unrelated content simultaneously

### Asking Questions
✅ **DO:**
- Be specific in your questions
- Reference document topics directly
- Ask follow-up questions for clarification
- Use the conversation context

❌ **DON'T:**
- Ask questions unrelated to ingested documents
- Expect knowledge outside the uploaded content
- Ask multiple unrelated questions at once

## Example Sessions

### Example 1: Research Paper Analysis
```
1. Upload: research_paper.pdf
2. Ask: "What is the main conclusion of this paper?"
3. Ask: "What methodology did they use?"
4. Ask: "What were the limitations mentioned?"
```

### Example 2: Website Documentation
```
1. Ingest URL: https://docs.python.org/3/tutorial/
2. Ask: "How do I create a function in Python?"
3. Ask: "Can you show me an example with parameters?"
4. Ask: "What about default parameters?"
```

### Example 3: Multiple Documents
```
1. Upload: doc1.pdf, doc2.pdf, doc3.docx
2. Ask: "Compare the approaches mentioned in these documents"
3. Ask: "Which document discusses X topic?"
4. Ask: "Summarize the key points from all documents"
```

## Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line in message (if needed)
- **Esc**: Clear input field

## Troubleshooting

### "I don't know" Responses
**Cause**: Question is outside the ingested document context
**Solution**: 
- Verify documents were successfully uploaded
- Rephrase question to match document content
- Ingest additional relevant documents

### Upload Failures
**Cause**: File format not supported or file corrupted
**Solution**:
- Check file format (PDF, DOCX, TXT only)
- Ensure file is not corrupted
- Try with a different file

### Slow Responses
**Cause**: Large document processing or API latency
**Solution**:
- Wait patiently for response
- Check network connection
- Verify OpenAI API is operational

### No Response
**Cause**: API connection issue
**Solution**:
1. Check system status indicator (should be green)
2. Verify `.env` file has correct `OPENAI_API_KEY`
3. Restart the server
4. Check browser console for errors (F12)

## Mobile Support

The UI is responsive and works on mobile devices:
- Touch-friendly buttons
- Adaptive layout
- Optimized for small screens

## Browser Support

Recommended browsers:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Privacy & Security

- All conversations are stored locally in your session
- Documents are processed on your server
- No data is sent to third parties except OpenAI API
- Session IDs are unique per browser session
- Clear chat removes conversation history

## Advanced Features

### Session Management
Each browser session maintains its own conversation history. Opening in a new tab/window creates a new session.

### Source Verification
Click on source citations to see:
- Exact document name
- Page number (for PDFs)
- Relevant content excerpt (200 chars)

### Real-time Status
System status updates every 30 seconds automatically.

---

**Need Help?** Check the [main README](README.md) or [API documentation](http://localhost:8000/docs)
