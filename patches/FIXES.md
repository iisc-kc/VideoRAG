# VideoRAG Local Setup Fixes

This patch contains critical bug fixes for running VideoRAG with Ollama and local models.

## Fixed Issues

1. **Embedding Model Integration** (videorag/_videoutil/feature.py)
   - Fixed embedding dimension handling for mxbai-embed-large (1024-dim) vs bge-m3 (1536-dim)
   - Added model_name parameter passing to ollama_embedding function
   - Properly handles Ollama embedding model format

2. **Text Completion Parameter Order** (videorag/_llm.py)
   - Fixed ollama_complete function to accept (model_name, prompt) parameter order
   - Added proper kwargs handling for model_name
   - Ensures compatibility with VideoRAG API calls

3. **Entity Extraction Return Value** (videorag/_op.py)
   - Fixed extract_entities to return tuple instead of dict
   - Changed line 598: `return sorted_nodes[:top_k], context_df` to match expected return type

4. **ASR Integration** (videorag/_videoutil/asr.py)
   - Enhanced Whisper model error handling
   - Fixed local ASR model path resolution

5. **ImageBind Auto-Loading** (videorag_api.py)
   - Added auto-initialization from ~/.videorag-bootstrap.json
   - Added ensure_imagebind_loaded() call during startup
   - Fixed config key normalization (camelCase → snake_case)
   - Proper embedding dimension calculation based on model type

6. **VideoRAG Core** (videorag/videorag.py)
   - Enhanced error handling and logging
   - Fixed parameter passing to underlying functions

## Files Modified
- Vimo-desktop/python_backend/videorag/_llm.py (+132 lines)
- Vimo-desktop/python_backend/videorag/_op.py (1 line)
- Vimo-desktop/python_backend/videorag/_videoutil/asr.py (+91 lines)
- Vimo-desktop/python_backend/videorag/_videoutil/feature.py (+110 lines)
- Vimo-desktop/python_backend/videorag/videorag.py (+22 lines)
- Vimo-desktop/python_backend/videorag_api.py (+215 lines)

Total: 510 insertions, 62 deletions

## How to Apply

```bash
cd VideoRAG
git apply patches/local-setup-fixes.patch
```

## Testing Status
✅ Video indexing: 220 segments processed successfully
✅ ASR transcription: Whisper local model working
✅ ImageBind loading: Auto-loads on API startup
✅ Ollama integration: mxbai-embed-large, gemma2:27b, llava:13b working
⚠️  Known issue: Text chunks KV store not populating (upstream bug in nano-graphrag)
