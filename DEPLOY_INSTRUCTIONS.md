# How to Deploy HearSee for Free

The easiest way to publish this app for free is **Streamlit Community Cloud**. It connects directly to your GitHub and hosts the app on a public URL.

## Step 1: Push to GitHub
1.  Verify all files are committed (I have done this for you locally).
2.  Push this code to a new GitHub repository or your existing one.

## Step 2: Deploy on Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Sign in with GitHub.
3.  Click **"New app"**.
4.  Select your repository (`hearsee`) and the branch (`main`).
5.  Expected Main file path: `streamlit_app.py`.
6.  Click **"Deploy!"**.

## Step 3: Add your API Key securely
Since we did not commit your API Key (for security), you must add it to the Streamlit Cloud **Secrets**.
1.  Once the app is deploying/deployed, on your app dashboard, click the **Settings menu** (three dots/lines).
2.  Click **Settings** -> **Secrets**.
3.  Paste the following into the secrets box:

OPENAI_API_KEY = "sk-proj-..."

4.  Click **Save**. The app will restart and work instantly!

## Running Locally
To test it on your machine right now:
```bash
streamlit run streamlit_app.py
```
