# 📦 S3 File Mover with Email Notification (SNS)

This Python script (`s3_sns_automation.py`) automates uploading files to an S3 bucket, moving files based on a prefix, and sending an email notification through AWS SNS once the operation is complete.

---

## 🚀 Features

- ✅ Creates an S3 bucket if it doesn’t exist
- ☁️ Uploads files from a local folder named `customer-details/`
- 🔄 Moves files with a prefix (e.g., `sr1_`) to a separate folder within the same bucket
- 📧 Sends an email notification using AWS SNS if files were moved

---

## 📂 Prerequisites

### ✅ Python & Dependencies

- Python 3.x
- `boto3` library:
  ```bash
  pip install -r requirements.txt
  ```

### ✅ AWS Configuration

Ensure you have AWS credentials configured on your machine:

1. Run:

   ```bash
   aws configure
   ```

2. This will populate your credentials in:

   ```
   ~/.aws/credentials
   ```

   With content similar to:

   ```ini
   [default]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY
   region = us-west-2
   ```

> The script uses these credentials automatically via `boto3`.

### ✅ Permissions Required

Make sure your IAM user or role has the following permissions:

- `s3:CreateBucket`
- `s3:ListBucket`
- `s3:GetObject`
- `s3:PutObject`
- `s3:DeleteObject`
- `sns:CreateTopic`
- `sns:Subscribe`
- `sns:Publish`
- `sns:ListSubscriptionsByTopic`

---

## 🗂 Folder Structure

```
s3_sns_project/
├── customer-details/
│   ├── sr1_file1.csv
│   ├── sr1_file2.csv
│   ├── sr2_file1.csv
│   ├── sr3_file1.csv
│   └── otherfile.txt
├── s3_sns_automation.py
├── README.md
├── requirements.txt
├── .gitignore
└── venv/
```

---

## 🧪 How to Use

1. **Activate your virtual environment (optional)**:

   ```bash
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Run the script**:

   ```bash
   python s3_sns_automation.py
   ```

3. **Enter your email address** when prompted.

4. **Check your inbox** and confirm the AWS SNS subscription.

5. ❗ **Run the script a second time** —  
   SNS will only deliver notifications _after_ the subscription has been confirmed.

---

## 📨 Notification Example

> Subject: ✅ S3 File Move Notification
>
> 3 files with prefix 'sr1\_' were successfully moved to `sr1/`  
> and deleted from `customer-details/`.
> Name of the files:['sr1_file1.csv', 'sr1_file2.csv']

---

## 🛡 Notes

- Files are moved **within the same bucket**.
- The script uses AWS SNS with the **`email` protocol**, which requires **manual confirmation** before notifications are sent.
- Notifications are skipped if the subscription is unconfirmed.

---

## 📜 License

MIT License
