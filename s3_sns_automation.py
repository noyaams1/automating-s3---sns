import boto3
import os
from botocore.exceptions import ClientError

# -------- AWS SETUP --------
region = "us-west-2"
bucket_name = "my-dct-sales-bucket"
topic_name = "file-move-notification"
# Setting AWS clients
s3_client = boto3.client("s3", region_name=region)
sns_client = boto3.client("sns", region_name=region)


# ----------------Creating Bucket----------------
def create_bucket(bucket_name):
    """Creates an S3 bucket if it doesn't exist."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' already exists.")
    except ClientError:
        s3_client.create_bucket(
            Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": region}
        )
        print(f"✅ Bucket '{bucket_name}' created in region {region}")


# -------- Creating SNS topic and subscribe --------
def create_sns_topic_and_subscribe(topic_name, email):
    """Creates an SNS topic and subscribes an email address."""
    response = sns_client.create_topic(Name=topic_name)
    topic_arn = response["TopicArn"]
    print(f"✅ SNS topic created: {topic_arn}")
    # Subscribe the email
    subscription = sns_client.subscribe(
        TopicArn=topic_arn, Protocol="email", Endpoint=email
    )
    print("📧 Subscription initiated. Please confirm the subscription via your email.")
    return topic_arn


# ---Uploading files to a folder named customer-details under the bucket---
def upload_files_to_s3(bucket_name):
    """Uploads all files from a local folder to S3."""
    folder_path = "customer-details"
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        try:
            s3_client.upload_file(file_path, bucket_name, f"customer-details/{file}")
            print(f"📤 Uploaded: customer-details/{file}")
        except Exception as e:
            print(f"❌ Failed to upload {file}: {e}")


# -------- List and move S3 objects --------
def move_files_with_prefix(bucket_name):
    """Moves files starting with the given prefix to a destination folder."""
    source_prefix = "customer-details/sr1_"
    destination_prefix = "sr1/"

    moved_files = []
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=source_prefix)

    if "Contents" in response:
        for obj in response["Contents"]:
            source_key = obj["Key"]
            file_name = source_key.split("/")[
                -1
            ]  # Extracting name of the file from source key
            destination_key = f"{destination_prefix}{file_name}"

            try:
                # Copy to destination
                copy_source = {"Bucket": bucket_name, "Key": source_key}
                s3_client.copy_object(
                    CopySource=copy_source, Bucket=bucket_name, Key=destination_key
                )
                # Delete from source
                s3_client.delete_object(Bucket=bucket_name, Key=source_key)
                moved_files.append(file_name)
                print(f"📁 Moved: {source_key} to {destination_key}")
            except Exception as e:
                print(f"❌ Error moving {source_key}: {e}")
    else:
        print("No matching files found.")

    return moved_files


# -------- Send notification if any file was moved --------
def is_subscription_confirmed(topic_arn, email):
    """Checks whether the SNS subscription is confirmed."""
    try:
        subs = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)

        for sub in subs["Subscriptions"]:
            if sub["Endpoint"] == email:
                if "PendingConfirmation" not in sub["SubscriptionArn"]:
                    print(f"✅ Found confirmed subscription for {email}")
                    return True
                else:
                    print(f"⏳ Subscription for {email} still pending confirmation")
                    return False

        print(f"❓ No subscription found for {email}")
        return False

    except Exception as e:
        # Skip sending in case of error
        print(f"❌ Error checking subscription status: {e}")
        return True


def send_sns_notification(topic_arn, email, moved_files):
    """Sends SNS notification with list of moved files."""
    if not is_subscription_confirmed(topic_arn, email):
        print("⚠️ Subscription not confirmed. Notification skipped.")
        return

    message = f"{len(moved_files)} files with prefix sr1_ were successfuly moved to {bucket_name}/sr1/ and deleted from {bucket_name}/customer-details/ \n\nName of the files:{moved_files}"
    response = sns_client.publish(
        TopicArn=topic_arn, Subject="✅ S3 File Move Notification", Message=message
    )
    print(f"📬 Notification sent! Message ID: {response['MessageId']}")


# --------- MAIN EXECUTION ---------
if __name__ == "__main__":
    print("🔧 Starting S3 file move automation...")
    email = input("📨 Enter your email address to receive notifications: ")

    create_bucket(bucket_name)
    topic_arn = create_sns_topic_and_subscribe(topic_name, email)

    upload_files_to_s3(bucket_name)

    moved_files = move_files_with_prefix(bucket_name)

    if moved_files:
        send_sns_notification(topic_arn, email, moved_files)
    else:
        print("ℹ️ No files with prefix found. Nothing was moved.")
