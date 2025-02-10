from huggingface_hub import hf_hub_download, snapshot_download


hf_hub_download(
    repo_id="KBlueLeaf/danbooru2023-metadata-database",
    filename="danbooru2023.db",
    repo_type="dataset",
    local_dir="./data",
)

snapshot_download(
    repo_id="deepghs/danbooru2024-webp-4Mpixel",
    ignore_patterns="embs/*",
    repo_type="dataset",
    local_dir="./images",
)
