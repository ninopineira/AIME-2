from huggingface_hub import snapshot_download

model_name = "MiBo/SABERT"
cache_dir = "./models_cache"

print("Téléchargement en cours...")
snapshot_download(
    repo_id=model_name,
    cache_dir=cache_dir,
    ignore_patterns=["*.msgpack", "*.h5"]  # ignore fichiers inutiles
)
print("Téléchargement terminé !")