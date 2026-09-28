# 🚀 Deploying HazWaste Sorter to Google Cloud

The recommended way to deploy HazWaste Sorter on Google Cloud is **Google Cloud Run**.

### Why Google Cloud Run?
* **Generous Free Tier**: 2 million requests per month are completely free (practically $0 cost for schools, students, and clubs).
* **Automatic HTTPS**: Provides a secure `https://...a.run.app` domain automatically. (HTTPS is strictly required by iPhone/Android for camera access).
* **Scales to Zero**: If no one is using the app overnight or during holidays, it scales down to 0 instances and incurs \$0 in server fees.
* **Mobile Ready**: PWA service worker and mobile camera capture work right out of the box.

---

## ⚡ Quickest Method: Using Google Cloud Shell (No local install needed)

Google Cloud Shell gives you a free Linux terminal in your web browser with `gcloud`, `git`, and `docker` pre-installed.

### Step 1: Open Google Cloud Shell
Go to **[shell.cloud.google.com](https://shell.cloud.google.com)** and log in with your Google account.

### Step 2: Upload or Clone the Code
You can zip the `hazwaste-sorter` folder and upload it using the Cloud Shell menu (`⋮` &rarr; **Upload**), or push it to GitHub and clone it:
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd hazwaste-sorter
```

### Step 3: Deploy with One Command
Run this command in Cloud Shell:
```bash
gcloud run deploy hazwaste-sorter \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Step 4: What Happens Next
1. Google Cloud will automatically build your container using the included `Dockerfile`.
2. It deploys the service and prints your live public URL:
   ```text
   Service [hazwaste-sorter] revision [hazwaste-sorter-00001] has been deployed and is serving 100 percent of traffic.
   Service URL: https://hazwaste-sorter-abcdef123-uc.a.run.app
   ```
3. Copy this URL, send it to students, or generate a QR code!

---

## 🖥️ Method 2: Deploying via the Google Cloud Console (GUI / Browser)

If you have your code pushed to **GitHub**:

1. Go to the **Google Cloud Console**: [console.cloud.google.com/run](https://console.cloud.google.com/run).
2. Select or create your Google Cloud project.
3. Click **Create Service**.
4. Choose **Continuously deploy from a repository** and click **Set Up with Cloud Build**.
5. Select **GitHub**, authenticate, and select your `hazwaste-sorter` repository.
6. Build Configuration:
   - Branch: `^main$`
   - Build Type: **Dockerfile** (Source location: `/Dockerfile`)
7. Under **Authentication**, select **"Allow unauthenticated invocations"** (so students can access it without a Google Cloud login).
8. Click **Create**.
9. In 1–2 minutes, your service will be live with a secure HTTPS URL.

---

## 💻 Method 3: Deploying from your Local Computer with `gcloud` CLI

If you want to deploy directly from your local Windows terminal:

1. **Install the Google Cloud SDK**:
   Download and install from: [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install).
2. **Log in and set your project**:
   ```powershell
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
3. **Enable Cloud Run & Cloud Build APIs**:
   ```powershell
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com
   ```
4. **Deploy**:
   ```powershell
   cd C:\Users\ajmea\.gemini\antigravity\scratch\hazwaste-sorter
   gcloud run deploy hazwaste-sorter --source . --region us-central1 --allow-unauthenticated
   ```

---

## 🔑 (Optional) Adding Gemini Vision API Key to Cloud Run

If you want the app to use real multimodal Gemini Vision for image analysis:

```bash
gcloud run services update hazwaste-sorter \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

*(Note: Even without a Gemini key, the built-in aviation heuristics engine will classify all hangar waste items instantly!)*
