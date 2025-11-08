# Serverless News Summarizer

A cloud-powered news summarizer application:  
Paste any news/article URL and get a quick summary instantly via a **beautiful web frontend**, powered by a **serverless Python backend** on AWS.

---

## Project Overview
This project is a **full-stack serverless news summarizer** built using **AWS Lambda** and **API Gateway** for the backend, with a static **HTML/CSS/JS frontend** deployed on **Vercel**.  

The app extracts the main content of any public article and generates a **concise, readable summary** using custom Python logic, **without relying on ML/AI APIs**.  

---

## Tech Stack
- **Backend:** AWS Lambda (Python 3.11)  
- **API:** AWS API Gateway (REST API)  
- **Python Libraries:** `requests`, `BeautifulSoup4`  
- **Frontend:** HTML, CSS, JavaScript  
- **Hosting:** Vercel (frontend deployment)  

---

## Architecture
```

[User Browser] --> [Frontend Web App (HTML/JS on Vercel)]
|
v
[AWS API Gateway POST /summarize]
|
v
[AWS Lambda -> requests, BeautifulSoup -> Summarizer]
|
v
[Summary Returned!]

````

---

## Step-by-Step Implementation

### Backend: AWS Lambda
1. Code is in `lambda_function.py`.
2. The function extracts the main content of a URL using `requests` and `BeautifulSoup`.
3. Key sentences are selected based on length and punctuation, limited to **15 sentences**.
4. **Lambda Packaging (Windows / PowerShell)**
```powershell
# Create a folder for Lambda
mkdir lambda_function
cd lambda_function

# Install required libraries locally
pip install requests bs4 -t .

# Place lambda_function.py in the folder

# Zip all files for Lambda deployment
Compress-Archive -Path * -DestinationPath ..\lambda_deploy.zip

# Upload lambda_deploy.zip to AWS Lambda console
````

---

### AWS API Gateway Setup (Detailed)

AWS API Gateway acts as the **bridge between the frontend and Lambda**. Here’s a detailed explanation of what was done:

1. **Create REST API**

   * Go to **AWS Console → API Gateway → REST API → Build**.
   * Name: `NewsSummarizerAPI`.
   * Endpoint Type: **Regional**.

2. **Create Resource**

   * A resource defines a **path** in the API.
   * Actions → Create Resource

     * Resource Name: `summarize`
     * Resource Path: `/summarize`
   * This creates the endpoint:

     ```
     https://<YOUR_API_ID>.execute-api.<REGION>.amazonaws.com/prod/summarize
     ```

3. **Create POST Method**

   * Select `/summarize` → Actions → Create Method → POST.
   * Integration Type: **Lambda Function**.
   * Lambda Function: `NewsSummarizerLambda`.
   * API Gateway is now authorized to invoke Lambda.

4. **Enable CORS**

   * Actions → Enable CORS on `/summarize`.
   * Allowed Origins: `*`
   * Allowed Methods: `POST, OPTIONS`
   * Allowed Headers: `Content-Type`
   * This ensures browser requests from frontend or local files are not blocked.
   * Lambda responses include:

```python
"headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
}
```

5. **Deploy API**

   * Actions → Deploy API → Stage Name: `prod`
   * Final Invoke URL:

     ```
     https://<YOUR_API_ID>.execute-api.<REGION>.amazonaws.com/prod
     ```

6. **Testing**

```bash
curl -X POST "https://<YOUR_API_ID>.execute-api.<REGION>.amazonaws.com/prod/summarize" \
-H "Content-Type: application/json" \
-d '{"url":"https://en.wikipedia.org/wiki/Serverless_computing"}'
```

> **Explanation:**
>
> * API Gateway resource `/summarize` defines the endpoint path.
> * POST method triggers the Lambda function.
> * CORS allows browser-origin requests.
> * Deployment stage `prod` provides a public endpoint.

---

### Frontend: HTML/CSS/JS

* Built `frontend/index.html` with:

  * URL input box
  * Summarize button
  * Summary output card
* Responsive design for mobile and desktop.
* Fetch API example:

```javascript
fetch("https://<YOUR_API_ID>.execute-api.<REGION>.amazonaws.com/prod/summarize", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({url: articleUrl})
})
.then(response => response.json())
.then(data => displaySummary(data.summary));
```

---

## Usage Instructions

1. Open `frontend/index.html` in a browser.
2. Paste any public article URL.
3. Click **Summarize** to see the summary instantly.

---

## Challenges & Solutions

* **CORS Errors:** Browser blocked requests; solved with CORS in API Gateway and Lambda headers.
* **Paywalled / JS-heavy Sites:** Dynamic content couldn’t be scraped; used static, open articles.
* **Windows Lambda Packaging:** Missing dependencies caused errors; installed locally in folder and zipped correctly.
* **Browser “Failed to Fetch”:** Fixed by ensuring POST & OPTIONS methods existed with correct headers.
* **Long Articles & Performance:** Slower Lambda execution; limited summaries to 15 sentences.
* **Frontend Responsiveness:** UI layout issues on mobile; solved with responsive CSS and media queries.

```
