# How to Upload to GitHub

## Step 1: Initialize Git Repository

```bash
cd /data1/home/kunalc/VideoRAG-Local-Setup
git init
```

## Step 2: Configure Git (if not already done)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 3: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `videorag-local` (or your preferred name)
3. Description: "VideoRAG with 100% Local Models - Ollama + Whisper ASR"
4. Keep it Public or Private (your choice)
5. **Do NOT** initialize with README (we already have one)
6. Click "Create repository"

## Step 4: Add and Commit Files

```bash
git add .
git commit -m "Initial commit: VideoRAG with local models and ImageBind fix"
```

## Step 5: Link to GitHub Repository

Replace `iisc-kc` and `videorag-local` with your actual username and repo name:

```bash
git remote add origin https://github.com/iisc-kc/videorag-local.git
```

## Step 6: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

## If You Get Authentication Error

### Option 1: Use Personal Access Token (Recommended)
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. When pushing, use token as password:
   - Username: iisc-kc
   - Password: [paste your token]

### Option 2: Use SSH
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key

# Change remote to SSH
git remote set-url origin git@github.com:iisc-kc/videorag-local.git

# Push
git push -u origin main
```

## After Successful Push

Your repository will be live at: `https://github.com/iisc-kc/videorag-local`

## Update Repository Later

```bash
# After making changes
git add .
git commit -m "Description of changes"
git push
```

## Files Included

- `README.md` - Main documentation
- `patches/fix_imagebind_data.py` - ImageBind NDArray fix script
- `patches/feature.py` - Fixed video processing module  
- `.gitignore` - Git ignore patterns
- `SETUP_GITHUB.md` - This file

## What's NOT Included (by .gitignore)

- Model files (.pth, .pt, .ckpt)
- Database and storage directories
- Python cache files
- Virtual environments
- Logs
