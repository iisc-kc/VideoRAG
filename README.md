# VideoRAG with 100% Local Models

Complete local VideoRAG setup using Ollama and local Whisper ASR - no external API calls.

## Hardware Requirements
- 3x NVIDIA H200 NVL GPUs (or similar high-memory GPUs)
- CUDA support

## Local Models Used
- **Vision**: Ollama llava:13b
- **Embeddings**: Ollama bge-m3:latest  
- **Text Generation**: Ollama qwen2.5:72b (analysis) / qwen2.5:14b (processing)
- **ASR**: OpenAI Whisper base (local)
- **Video Embeddings**: ImageBind (local)

## Critical Fixes Included

### 1. ImageBind NDArray Fix
**Problem**: ImageBind's data loading returns numpy NDArray instead of torch.Tensor, causing `'NDArray' object has no attribute 'to'` errors.

**Solution**: Patched `imagebind/data.py` with `_ensure_tensor()` helper that converts NDArray/numpy to torch.Tensor at every step of video processing.

### 2. One-by-One Video Processing  
**Problem**: Batch video processing causes state pollution in pytorchvideo transforms.

**Solution**: Process videos individually with explicit memory cleanup between each video.

## Installation

### 1. Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Ollama Models
```bash
ollama pull llava:13b
ollama pull bge-m3
ollama pull qwen2.5:72b
ollama pull qwen2.5:14b
```

### 3. Install VideoRAG Environment
```bash
conda create -n videorag python=3.11
conda activate videorag
# Install VideoRAG dependencies
pip install -r requirements.txt
```

### 4. Apply ImageBind Fix
Run the patch script to fix the NDArray issue:
```bash
python patches/fix_imagebind_data.py
```

### 5. Copy Fixed Feature Module
```bash
cp patches/feature.py /path/to/videorag/_videoutil/feature.py
```

## Usage

### 1. Start Ollama Server
```bash
ollama serve
```

### 2. Start VideoRAG Server
```bash
cd python_backend
python videorag_api.py
```

### 3. Initialize Configuration
```bash
curl -X POST "http://localhost:PORT/api/initialize" \
  -H "Content-Type: application/json" \
  -d '{
    "base_storage_path": "/path/to/storage",
    "image_bind_model_path": "/path/to/imagebind_huge.pth",
    "embedding_func": "ollama_embedding",
    "text_func": "ollama_text_complete", 
    "caption_func": "ollama_caption_complete",
    "asr_model": "base"
  }'
```

### 4. Load ImageBind Model
```bash
curl -X POST "http://localhost:PORT/api/imagebind/load"
```

### 5. Process Videos
```bash
curl -X POST "http://localhost:PORT/api/sessions/SESSION_ID/videos/upload" \
  -H "Content-Type: application/json" \
  -d '{"video_path_list": ["/path/to/video.mp4"]}'
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   VideoRAG Server                   │
├─────────────────────────────────────────────────────┤
│  Video Processing Pipeline:                         │
│  1. Video Upload & Segmentation                     │
│  2. ASR (Local Whisper)           ✓ 100% Local     │
│  3. Video Encoding (ImageBind)     ✓ 100% Local     │
│  4. Caption Generation (Ollama)    ✓ 100% Local     │
│  5. Embeddings (Ollama bge-m3)     ✓ 100% Local     │
│  6. Storage & Indexing                               │
└─────────────────────────────────────────────────────┘
```

## Technical Details

### ImageBind NDArray Issue
The core issue is in pytorchvideo's `SpatialCrop` transform which returns numpy NDArrays instead of torch Tensors. Our fix:

1. Added `_ensure_tensor()` helper function to `imagebind/data.py`
2. Apply tensor conversion at every transform step:
   - After `frame_sampler()` 
   - After `video_transform()`
   - After `SpatialCrop()`
3. Process videos one-by-one to avoid state pollution

### Performance Optimization
- Process videos individually to prevent memory buildup
- Explicit GPU cache clearing after each video
- CPU offloading of embeddings to free GPU memory

## Troubleshooting

### NDArray Error Still Occurring
- Clear Python cache: `find /path/to/imagebind -name "*.pyc" -delete`
- Restart the server
- Verify patch was applied: `grep "_ensure_tensor" /path/to/imagebind/data.py`

### Out of Memory
- Reduce batch size in video processing
- Process fewer videos simultaneously
- Use smaller Ollama models (qwen2.5:14b instead of :72b)

## Known Issues

1. **State Pollution**: After first encoding batch succeeds, subsequent batches may fail. Solution: Process videos one-by-one (already implemented).

2. **First Request Success**: The first encoding request after server start always works. Subsequent requests may fail due to pytorchvideo caching.

## Contributing

Issues and pull requests welcome!

## License

See original VideoRAG license.
