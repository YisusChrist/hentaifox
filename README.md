# Hentai Fox API

<img width="824" height="498" alt="hentaifox-api" src="https://github.com/user-attachments/assets/c94beec5-6f5e-41d4-9d22-3ac1bc47b25d" />

This is an unofficial API for accessing content from the Hentai Fox website, a platform dedicated to hentai manga.

## Overview

The Hentai Fox API allows users to search and fetch manga information including titles, links, covers, and descriptions. The API is designed for developers who want to integrate Hentai Fox's manga content into their applications.

#### Response

- **200 OK**
  - Returns a JSON array of manga objects, each containing:
    - `name`: Title of the manga
    - `link`: URL to the manga
    - `cover`: URL of the cover image
    - `description`: A brief description (if available)
    - `host`: The base URL for Hentai Fox

#### Example Response

```json
{
  "manga": [
    {
      "name": "Manga Title",
      "link": "https://hentaifox.com/manga/1",
      "cover": "https://hentaifox.com/covers/1.jpg",
      "description": "A brief description of the manga.",
      "host": "https://hentaifox.com"
    },
    ...
  ],
  "next": "2"
}
```

### Error Handling

- **404 Not Found**: If no results are found for the given search key.
- **500 Internal Server Error**: If there is a problem with the server.

## Usage Example

You can use this API in your application to display manga content or build features around it, such as search functionalities or manga listings.

## Disclaimer

This API is unofficial and is not affiliated with Hentai Fox. Use it at your own risk, and be sure to respect the website's terms of service.

## Contributing

If you have any suggestions or improvements, feel free to create a pull request or open an issue on the repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

