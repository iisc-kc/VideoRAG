import os
import torch
import pickle
import numpy as np
import gc
from tqdm import tqdm
from imagebind import data
from imagebind.models import imagebind_model
from imagebind.models.imagebind_model import ImageBindModel, ModalityType


def encode_video_segments(video_paths, embedder: ImageBindModel):
    """Encode video segments - process one by one with memory cleanup"""
    device = next(embedder.parameters()).device
    
    all_embeddings = []
    for i, video_path in enumerate(video_paths):
        try:
            # Process each video individually
            video_data = data.load_and_transform_video_data([video_path], device)
            
            inputs = {
                ModalityType.VISION: video_data,
            }
            with torch.no_grad():
                embeddings = embedder(inputs)[ModalityType.VISION]
            
            # Move to CPU immediately and cleanup GPU memory
            all_embeddings.append(embeddings.cpu())
            
            # Explicit cleanup after each video
            del video_data, inputs, embeddings
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
        except Exception as e:
            print(f"Error processing video {i} ({video_path}): {e}")
            raise
    
    # Concatenate all embeddings
    if len(all_embeddings) == 1:
        result = all_embeddings[0]
    else:
        result = torch.cat(all_embeddings, dim=0)
    
    return result


def encode_string_query(query: str, embedder: ImageBindModel):
    """Encode text query"""
    device = next(embedder.parameters()).device
    
    text_data = data.load_and_transform_text([query], device)
    
    inputs = {
        ModalityType.TEXT: text_data,
    }
    with torch.no_grad():
        embeddings = embedder(inputs)[ModalityType.TEXT]
    
    if isinstance(embeddings, torch.Tensor):
        embeddings = embeddings.cpu()
    
    return embeddings
