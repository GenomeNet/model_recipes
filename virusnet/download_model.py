import os
import urllib.request

def download_model(target_path):
    url = "https://f000.backblazeb2.com/file/genomenet/models/virus_genus_2023-01-23.hdf5"
    print(f"Downloading model from {url} to {target_path} ...")
    urllib.request.urlretrieve(url, target_path)
    print("Download complete.")

if __name__ == "__main__":
    output_dir = os.environ.get('PREFIX', '') + '/lib/virusnet'
    os.makedirs(output_dir, exist_ok=True)
    download_model(os.path.join(output_dir, 'virus_genus_2023-01-23.hdf5'))
