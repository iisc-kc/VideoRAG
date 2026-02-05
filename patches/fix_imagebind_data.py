#!/usr/bin/env python3
"""
ImageBind NDArray to Tensor Fix
Patches imagebind/data.py to convert numpy NDArray to torch.Tensor at every step
"""

import sys
import os

def find_imagebind_path():
    """Find the imagebind installation path"""
    try:
        import imagebind
        path = os.path.dirname(imagebind.__file__)
        return os.path.join(path, 'data.py')
    except ImportError:
        print("ERROR: imagebind not found. Please install it first.")
        sys.exit(1)

def apply_patch():
    data_py_path = find_imagebind_path()
    print(f"Found imagebind at: {data_py_path}")
    
    with open(data_py_path, 'r') as f:
        lines = f.readlines()
    
    # Find where to insert _ensure_tensor function (after imports)
    insert_idx = None
    for i, line in enumerate(lines):
        if 'DEFAULT_AUDIO_FRAME_SHIFT_MS' in line:
            insert_idx = i + 1
            break
    
    if insert_idx is None:
        print("ERROR: Could not find insertion point")
        sys.exit(1)
    
    # Insert _ensure_tensor function
    ensure_tensor_code = '''

def _ensure_tensor(obj):
    """Convert any array-like to tensor"""
    import torch
    import numpy as np
    if isinstance(obj, torch.Tensor):
        return obj
    elif isinstance(obj, np.ndarray):
        return torch.from_numpy(obj.copy())
    elif hasattr(obj, '__array__'):
        return torch.from_numpy(np.asarray(obj).copy())
    else:
        return torch.as_tensor(obj)

'''
    
    lines.insert(insert_idx, ensure_tensor_code)
    
    # Find and replace load_and_transform_video_data function
    start_idx = None
    for i, line in enumerate(lines):
        if 'def load_and_transform_video_data(' in line:
            start_idx = i
            break
    
    if start_idx is None:
        print("ERROR: Could not find load_and_transform_video_data function")
        sys.exit(1)
    
    # Find end of function
    end_idx = None
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith('def ') or lines[i].startswith('class '):
            end_idx = i
            break
    
    if end_idx is None:
        end_idx = len(lines)
    
    # Replace with patched version
    new_function = '''def load_and_transform_video_data(
    video_paths,
    device,
    clip_duration=2,
    clips_per_video=5,
    sample_rate=16000,
):
    if video_paths is None:
        return None

    video_outputs = []
    video_transform = transforms.Compose(
        [
            pv_transforms.ShortSideScale(224),
            NormalizeVideo(
                mean=(0.48145466, 0.4578275, 0.40821073),
                std=(0.26862954, 0.26130258, 0.27577711),
            ),
        ]
    )

    clip_sampler = ConstantClipsPerVideoSampler(
        clip_duration=clip_duration, clips_per_video=clips_per_video
    )
    frame_sampler = pv_transforms.UniformTemporalSubsample(num_samples=clip_duration)

    for video_path in video_paths:
        video = EncodedVideo.from_path(
            video_path,
            decoder="decord",
            decode_audio=False,
            **{"sample_rate": sample_rate},
        )

        all_clips_timepoints = get_clip_timepoints(clip_sampler, video.duration)

        all_video = []
        for clip_timepoints in all_clips_timepoints:
            # Read the clip, get frames
            clip = video.get_clip(clip_timepoints[0], clip_timepoints[1])
            if clip is None:
                raise ValueError("No clip found")
            video_clip = frame_sampler(clip["video"])
            # CONVERT TO TENSOR IMMEDIATELY
            video_clip = _ensure_tensor(video_clip)
            video_clip = video_clip / 255.0

            all_video.append(video_clip)

        # Transform and convert to tensor
        transformed = []
        for clip in all_video:
            t = video_transform(clip)
            t = _ensure_tensor(t)
            transformed.append(t)
        all_video = transformed
        
        # SpatialCrop and convert
        cropped = SpatialCrop(224, num_crops=3)(all_video)
        cropped = [_ensure_tensor(c) for c in cropped]

        # Stack
        all_video = torch.stack(cropped, dim=0)
        video_outputs.append(all_video)

    # Final stack
    result = torch.stack(video_outputs, dim=0)
    return result.to(device)


'''
    
    new_lines = lines[:start_idx] + [new_function] + lines[end_idx:]
    
    # Write back
    with open(data_py_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Successfully patched {data_py_path}")
    print("   Added _ensure_tensor() function")
    print("   Patched load_and_transform_video_data() to convert NDArray to Tensor")
    
    # Clear cache
    import glob
    cache_files = glob.glob(os.path.join(os.path.dirname(data_py_path), '**', '*.pyc'), recursive=True)
    for f in cache_files:
        try:
            os.remove(f)
        except:
            pass
    print("   Cleared Python cache")

if __name__ == '__main__':
    apply_patch()
