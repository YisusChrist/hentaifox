import random
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

app = Flask(__name__)

PORT = 3000
BASE_URL = "https://hentaifox.com/gallery"
MAX_RETRIES = 20
MAX_ID = 999999

def generate_random_id():
    return random.randint(1, MAX_ID)

def construct_url(id):
    return f"{BASE_URL}/{id}/"

def extract_id_from_url(url):
    matches = url.split("gallery/")
    if len(matches) > 1:
        return matches[1].split('/')[0]
    return None

def scrape_content(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, 'html.parser')

        id_tag = soup.select_one("a.g_button")
        id_ = int(id_tag['href'].split("/")[2]) if id_tag else None

        category = [tag.text.replace('[0-9]', '').strip() for tag in soup.select("a.tag_btn")]

        img_src = [img['data-src'] for img in soup.find_all("img") if img.get('data-src')]
        if not img_src:
            raise ValueError("Content not found")

        parameter_img2 = '/'.join(img_src[0].split("/")[:5])
        extension_img = f".{img_src[0].split('.')[-1]}"

        info = [span.text for span in soup.select("span.i_text.pages")]
        page_count = int(''.join(filter(str.isdigit, info[0]))) if info else 0

        image_urls = [f"{parameter_img2}/{i+1}{extension_img}" for i in range(page_count)]

        title_info = soup.select_one("div.info h1").text if soup.select_one("div.info h1") else "No title"

        object_data = {
            'title': title_info,
            'id': id_,
            'tags': category,
            'type': extension_img,
            'total': page_count,
            'image': image_urls,
        }

        return {
            'success': True,
            'data': object_data,
            'source': f"{BASE_URL}/{id_}/"
        }

    except requests.HTTPError as http_err:
        if http_err.response.status_code == 404:
            raise ValueError("404")
        raise http_err
    except Exception as err:
        raise ValueError(f"Scraping error: {err}")

def scrape_with_retries(initial_id):
    current_id = initial_id
    attempts = 0

    while attempts < MAX_RETRIES:
        try:
            print(f"Attempt {attempts + 1}/{MAX_RETRIES} with ID: {current_id}")
            url = construct_url(current_id)
            result = scrape_content(url)
            return result
        except ValueError as e:
            if str(e) == "404":
                attempts += 1
                if attempts < MAX_RETRIES:
                    current_id = generate_random_id()
                    continue
            raise e

@app.route("/hentaifox/<path:input_data>", methods=['GET'])
def scrape(input_data):
    try:
        if input_data == "random":
            random_id = generate_random_id()
            data = scrape_with_retries(random_id)
            return jsonify(data)

        if "hentaifox.com" in input_data:
            id_ = extract_id_from_url(input_data)
            if id_:
                data = scrape_with_retries(int(id_))
                return jsonify(data)

        if input_data.isdigit():
            data = scrape_with_retries(int(input_data))
            return jsonify(data)

        return    jsonify({'success': False, 'message': "Invalid input. Please provide a valid ID, URL, or 'random'"}), 400

    except Exception as error:
        print(f"Error processing request: {error}")
        return jsonify({'success': False, 'message': str(error)}), 500



@app.route("/", methods=['GET'])
def documentation():
    doc = """
   <html lang="en">
  <head>
    <meta charSet="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>API Documentation</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;700&family=VT323&display=swap" rel="stylesheet" />
    <style>
      :root {
        --primary-color: #FF69B4;
        --secondary-color: #7B68EE;
        --accent-color: #00FFFF;
        --background-color: #1a1a2e;
        --text-color: #ffffff;
        --code-background: #2d2d44;
        --pre-background: #252538;
        --border-color: #4a4a6a;
      }

      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }

      body {
        font-family: 'Quicksand', sans-serif;
        background-color: var(--background-color);
        background-image: 
          linear-gradient(rgba(26, 26, 46, 0.97), rgba(26, 26, 46, 0.97)),
          url('/api/placeholder/400/400');
        background-attachment: fixed;
        color: var(--text-color);
        line-height: 1.6;
        overflow-x: hidden;
        width: 100%;
      }

      .container {
        width: min(90%, 1000px);
        margin: 0 auto;
        padding: 20px;
      }

      .header {
        background: linear-gradient(45deg, #FF69B4, #7B68EE, #00FFFF);
        background-size: 300% 300%;
        animation: kawaii-gradient 10s ease infinite;
        padding: 40px 0;
        text-align: center;
        position: relative;
        overflow: hidden;
        width: 100%;
      }

      .header::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('/api/placeholder/100/100') repeat;
        opacity: 0.1;
        animation: slide 20s linear infinite;
      }

      @keyframes kawaii-gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }

      @keyframes slide {
        from { transform: translateX(0); }
        to { transform: translateX(100%); }
      }

      .header h1 {
        font-size: clamp(2rem, 5vw, 4rem);
        font-family: 'VT323', monospace;
        text-shadow: 3px 3px 0px var(--secondary-color),
                     6px 6px 0px rgba(0,0,0,0.2);
        letter-spacing: 2px;
        transform: skew(-5deg);
        margin: 0;
        padding: 0 20px;
        position: relative;
        z-index: 1;
      }

      .header p {
        font-size: clamp(1rem, 2vw, 1.3rem);
        opacity: 0.9;
        font-weight: 300;
        margin-top: 15px;
        padding: 0 20px;
        position: relative;
        z-index: 1;
      }

      .content {
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        box-shadow: 0 0 30px rgba(123, 104, 238, 0.15);
        margin: 30px auto;
        padding: clamp(20px, 5vw, 40px);
        border: 2px solid rgba(255, 105, 180, 0.3);
        backdrop-filter: blur(10px);
      }

      h2 {
        color: var(--primary-color);
        font-family: 'VT323', monospace;
        font-size: clamp(1.8rem, 4vw, 2.5rem);
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px var(--secondary-color);
      }

      h3 {
        color: var(--accent-color);
        font-family: 'VT323', monospace;
        font-size: clamp(1.4rem, 3vw, 1.8rem);
        margin-top: 30px;
      }

      h4 {
        font-size: clamp(1.1rem, 2vw, 1.3rem);
        color: var(--primary-color);
        margin: 20px 0 10px 0;
      }

      .endpoint {
        background-color: rgba(255, 255, 255, 0.05);
        border: 2px solid var(--border-color);
        border-radius: 15px;
        padding: clamp(15px, 3vw, 30px);
        margin-bottom: 30px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
      }

      .endpoint:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(123, 104, 238, 0.2);
      }

      code {
        background-color: var(--code-background);
        padding: 3px 8px;
        border-radius: 6px;
        font-family: 'VT323', monospace;
        font-size: 1.1em;
        color: var(--accent-color);
      }

      pre {
        background-color: var(--pre-background);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        font-family: 'VT323', monospace;
        font-size: 1.1em;
        white-space: pre-wrap;
        word-wrap: break-word;
        overflow-x: auto;
      }

      .try-it-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 20px 0;
        justify-content: center;
        align-items: center;
      }

      #input-data {
        background-color: var(--code-background);
        border: 2px solid var(--border-color);
        color: var(--text-color);
        padding: 12px 20px;
        border-radius: 25px;
        font-size: clamp(0.9rem, 2vw, 1rem);
        font-family: 'Quicksand', sans-serif;
        transition: all 0.3s ease;
        width: 100%;
        max-width: 300px;
      }

      #input-data:focus {
        border-color: var(--primary-color);
        outline: none;
        box-shadow: 0 0 10px rgba(255, 105, 180, 0.3);
      }

      .try-it {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 25px;
        cursor: pointer;
        font-size: clamp(0.9rem, 2vw, 1.1rem);
        font-family: 'Quicksand', sans-serif;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(255, 105, 180, 0.3);
        min-width: 120px;
      }

      .try-it:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 105, 180, 0.4);
      }

      #result {
        display: none;
        margin: 20px 0;
        animation: fadeIn 0.3s ease;
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
      }

      .response-container {
        margin: 20px 0;
      }

      .response-success {
        border: 2px solid var(--accent-color);
      }

      .response-error {
        border: 2px solid var(--primary-color);
      }

      ul {
        list-style-type: none;
        padding-left: 20px;
        margin: 10px 0;
      }

      ul li {
        margin: 10px 0;
        padding-left: 25px;
        position: relative;
      }

      ul li::before {
        content: "★";
        color: var(--primary-color);
        position: absolute;
        left: 0;
      }

      @media (max-width: 480px) {
        .container {
          width: 95%;
          padding: 10px;
        }

        .content {
          padding: 15px;
        }

        .endpoint {
          padding: 15px;
        }

        pre {
          padding: 10px;
          font-size: 0.9em;
        }
      }

      @media (max-width: 768px) {
        .try-it-container {
          flex-direction: column;
          align-items: stretch;
        }

        #input-data {
          max-width: 100%;
        }

        .try-it {
          width: 100%;
        }
      }
    </style>
  </head>
  <body>
    <div class="header">
      <div class="container">
        <h1>API Docs</h1>
        <p>✧･ﾟ Welcome to the HentaiFox unofficial API Documentation ･ﾟ✧</p>
      </div>
    </div>

    <div class="container">
      <div class="content">
        <h2>✧ Endpoints ✧</h2>
        <div class="endpoint">
          <h3>⋆｡°✩ <code>/hentaifox/&lt;input_data&gt;</code></h3>
          <p>This endpoint scrapes content from galleries.</p>

          <h4>Parameters:</h4>
          <ul>
            <li><code>input_data</code> (string) - This can be one of the following:
              <ul>
                <li><strong>random</strong>: Scrapes a random gallery</li>
                <li><strong>URL</strong>: Provide a valid gallery URL</li>
                <li><strong>ID</strong>: Provide a valid numeric ID</li>
              </ul>
            </li>
          </ul>

          <h4>Example Usage:</h4>
          <ul>
            <li><code>/hentaifox/random</code> - Scrapes a random gallery</li>
            <li><code>/hentaifox/123456</code> - Scrapes gallery ID 123456</li>
            <li><code>/hentaifox/https://hentaifox.\ncom/gallery/1</code> - Scrapes by URL</li>
          </ul>

          <h4>Try it out:</h4>
          <div class="try-it-container">
            <input type="text" id="input-data" placeholder="Enter random, ID, or URL" aria-label="Enter input data" />
            <button class="try-it" onclick="tryScrape()">Try it ✨</button>
          </div>
          <pre id="result"></pre>

          <h4>Response Format:</h4>
          <pre>
{
  "success": true,
  "data": {
    "title": "Gallery Title",
    "id": 123456,
    "tags": ["tag1", "tag2"],
    "type": ".jpg",
    "total": 20,
    "image": [
      "image_url_1",
      "image_url_2"
    ]
  },
  "source": "https://example.com/gallery/123456/"
}</pre>
        </div>
      </div>
    </div>

    <script>
      function tryScrape() {
        const input = document.getElementById('input-data').value.trim();
        const resultElement = document.getElementById('result');
        
        if (!input) {
          showResult({ error: 'Please enter input data (｡•́︿•̀｡)' }, false);
          return;
        }

        let endpoint = '';
        if (input.toLowerCase() === 'random') {
          endpoint = '/hentaifox/random';
        } else if (input.startsWith('http')) {
          endpoint = `/hentaifox?url=${encodeURIComponent(input)}`;
        } else {
          endpoint = `/hentaifox/${input}`;
        }

        resultElement.style.display = 'block';
        resultElement.textContent = 'Loading... (〜￣▽￣)〜';
        
        fetch(endpoint)
          .then(response => response.json())
          .then(data => showResult(data, true))
          .catch(error => showResult({ error: `${error.message} (╥﹏╥)` }, false));
      }

      function showResult(data, success) {
        const resultElement = document.getElementById('result');
        resultElement.style.display = 'block';
        resultElement.className = success ? 'response-success' : 'response-error';
        resultElement.textContent = JSON.stringify(data, null, 2);
      }

      document.getElementById('input-data').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          tryScrape();
        }
      });
    </script>
  </body>
</html>
    """
    return doc



if __name__ == "__main__":
  app.run(host="0.0.0.0", port=PORT, debug=True)
