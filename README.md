# Working Tracker

## What does this project do and why was it built?
Working Tracker is a lightweight, mobile-first Progressive Web App (PWA) designed specifically for field workers, medical representatives, and sales professionals. It provides a simple, fast interface to log daily activities, including:
- Date of work
- Who you are working with
- Working locations/places
- Number of Doctor calls
- Number of Chemist visits
- Custom notes and remarks

**Why this project?** 
Keeping track of daily field metrics using pen-and-paper or clunky spreadsheets is tedious and prone to data loss. This project solves that by offering an installable web app that works beautifully on mobile phones. It features a robust MongoDB backend to store your data and an automated Vercel Cron Job that securely zips and backs up your monthly data directly into your personal Google Drive on the 1st of every month.

---

## 🚀 How to Set Up Your Own Instance
If you want to run this application for yourself (or someone else) **without conflicting with an existing deployment**, you must create a separate database and a separate Google Cloud project. 

Follow this step-by-step tutorial to get a fresh instance running from scratch:

### Step 1: Database Setup (MongoDB)
1. Go to [MongoDB Atlas](https://cloud.mongodb.com/) and create a free account.
2. Create a **new Project** and a **new free Cluster**. *(Creating a new project ensures your data is 100% isolated from any other app).*
3. On the left sidebar, go to **Database Access** and create a new database user with a secure password.
4. Go to **Network Access**, click "Add IP Address", and select **Allow Access from Anywhere** (`0.0.0.0/0`). This is required for Vercel to communicate with the database.
5. Go back to your Cluster, click **Connect**, select **Drivers**, and copy your Connection String. It will look like `mongodb+srv://<username>:<password>@cluster0...`
6. Save this string; this is your `MONGO_URI`.

### Step 2: Google Drive Backup Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a **new Project**.
2. Go to **APIs & Services > Library**, search for **Google Drive API**, and click Enable.
3. Go to **OAuth consent screen**:
   - Choose **External** and click Create.
   - Fill in the App name and your email. **Leave the Logo blank.**
   - For Homepage and Privacy Policy links, you can enter `https://localhost` for now.
   - Click Save and Continue.
4. Under **Scopes**, click "Add or Remove Scopes", manually paste `https://www.googleapis.com/auth/drive`, and add it.
5. Under **Test Users**, add your personal `@gmail.com` address.
6. Once back on the main OAuth consent screen dashboard, click **PUBLISH APP** and hit **Confirm**. *(Note: Google will warn you about verification. Because you left the logo blank and are only using this yourself, you do not actually need to verify it. Publishing it simply prevents the token from expiring every 7 days).*
7. Go to **Credentials > Create Credentials > OAuth client ID**.
   - Application type: **Desktop app**.
   - Name it "Tracker Backup Bot".
8. Click the download icon to download your JSON file. Rename it to **`credentials.json`**.

### Step 3: Local Setup & Initial Authentication
You must run the app locally one time to generate the Google Drive token and inject it into your new database.
1. Clone this repository to your computer.
2. Create a file named `.env` in the root folder and add your MongoDB connection string:
   ```env
   MONGO_URI="your_mongodb_connection_string_here"
   ```
3. Place your downloaded `credentials.json` file in the root folder of the project.
4. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the OAuth setup script to authorize the app:
   ```bash
   python setup_oauth.py
   ```
6. A browser window will open. Select your Google account. You will see a warning saying "Google hasn't verified this app". Click **Advanced -> Go to app (unsafe)** and click Continue.
7. The terminal will print `"Done! The token is now saved in MongoDB."` 

### Step 4: Deployment (Vercel)
1. Push your code to your own GitHub repository.
2. Log in to [Vercel](https://vercel.com/) and click **Add New > Project**.
3. Import your GitHub repository.
4. Open your `credentials.json` file in a text editor and copy all the text inside it.
5. Before clicking Deploy, expand the **Environment Variables** section and add two variables:
   - Name: `MONGO_URI`, Value: Your MongoDB connection string.
   - Name: `GCP_OAUTH_CREDENTIALS_JSON`, Value: The text you copied from `credentials.json`.
6. Click **Deploy**.

### Step 5: Automated Backups
You're done! The `vercel.json` file included in this repository already contains the Cron Job configuration. Vercel will automatically hit the `/backup` endpoint on the 1st of every month at midnight, securely zipping your previous month's data and uploading it to a folder called `WorkingTrackerBackups` in your Google Drive.
