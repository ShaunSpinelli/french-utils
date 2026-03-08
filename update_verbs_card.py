import os
import subprocess
import hashlib

def get_image_hash(img_path):
    """Generate a short hash of the image content."""
    if not os.path.exists(img_path):
        return None
    with open(img_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]

def clean_old_hashed_images(dest_path):
    """Delete hashed versions of the image that don't match the current source."""
    if not os.path.exists(dest_path):
        return
        
    directory = os.path.dirname(dest_path)
    base_name = os.path.splitext(os.path.basename(dest_path))[0]
    current_hash = get_image_hash(dest_path)
    
    if not current_hash:
        return

    for f in os.listdir(directory):
        if f.startswith(f"{base_name}_") and f.endswith(".jpg"):
            if f != f"{base_name}_{current_hash}.jpg":
                try:
                    os.remove(os.path.join(directory, f))
                    print(f"Cleaned up old hashed version: {f}")
                except Exception as e:
                    print(f"Error cleaning up {f}: {e}")

def download_images(links_file):
    if not os.path.exists(links_file):
        print(f"File {links_file} not found.")
        return

    with open(links_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                # Expected format: path, keyword URL
                parts = line.split(',')
                if len(parts) < 2:
                    continue
                
                dest_path = parts[0].strip()
                # Split the second part to extract the URL
                metadata = parts[1].strip().split(' ')
                url = metadata[-1] # Assume the URL is the last element
                
                print(f"Downloading {url} to {dest_path}...")
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Use curl to download
                subprocess.run(['curl', '-L', '-o', dest_path, url], check=True)
                print(f"✅ Successfully downloaded {dest_path}")
                
                # Clean up old hashed versions now that the source is updated
                clean_old_hashed_images(dest_path)
                
            except Exception as e:
                print(f"❌ Failed to download {line}: {e}")

if __name__ == "__main__":
    download_images('image_links.txt')
