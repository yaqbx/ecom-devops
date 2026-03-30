terraform {
  # -----------------------------------------------------------------
  # Remote backend – S3 bucket created in the bootstrap step
  # -----------------------------------------------------------------
  backend "s3" {
    # 👉 Replace <YOUR_BUCKET_NAME> with the name printed by the
    #    bootstrap output (you can get it with
    #    `terraform -chdir=infra/bootstrap output -raw bucket_name`).
    bucket         = "ecom-devops-tf-state-c4b0e445"
    key            = "terraform.tfstate"   # object path inside the bucket
    region         = "eu-central-1"
    encrypt        = true                 # SSE‑AES256 (default)
    use_lockfile   = true                 # native S3 lockfile (no DynamoDB)
  }
}