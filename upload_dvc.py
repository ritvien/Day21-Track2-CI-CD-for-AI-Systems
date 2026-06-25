import hashlib
import os
import yaml
import boto3

# 1. Create .dvc/config
os.makedirs(".dvc", exist_ok=True)
with open(".dvc/config", "w") as f:
    f.write("[core]\n    remote = myremote\n['remote \"myremote\"']\n    url = s3://lab-941141114915-us-east-1-an/dvc\n")

# 2. Hash and upload files
def hash_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest(), os.path.getsize(path)

s3 = boto3.client('s3')
bucket = 'lab-941141114915-us-east-1-an'

prefix = 'dvc/files/md5'

for file_name in ['train_phase1.csv', 'eval.csv', 'train_phase2.csv']:
    path = f"data/{file_name}"
    if not os.path.exists(path): continue
    md5, size = hash_file(path)
    
    # Upload to S3
    s3_key = f"{prefix}/{md5[:2]}/{md5[2:]}"
    print(f"Uploading {path} to s3://{bucket}/{s3_key}...")
    s3.upload_file(path, bucket, s3_key)
    
    # Write .dvc file
    dvc_path = f"{path}.dvc"
    dvc_content = {
        "outs": [{
            "md5": md5,
            "size": size,
            "hash": "md5",
            "path": file_name
        }]
    }
    with open(dvc_path, 'w') as f:
        yaml.dump(dvc_content, f, sort_keys=False)

print("Xong! Đã tạo file .dvc và đẩy lên AWS S3 thành công.")
