# Content Upload And Review System

## Setup and Execution Instructions (Mac OS X - 14.5) (Should work on unix-like systems)

1. **Create Virtual Environment**
    ```bash
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    ```

2. **Install Requirements**
    ```bash
    $ pip install -r requirements.txt
    ```

3. **Configure Environment Variables**
   - `ContentSystem/src/.env`
   - Create a `.env` file in the `ContentSystem` folder with the following content:
    ```
    DATABASE_URL=postgresql+asyncpg://postgres:@localhost/content_system
    ```
   - Create a folder called `versions` inside the alembic folder.
    ```bash
    $ mkdir alembic/versions
    ```

4. **Setup Database**
    - Docker should be installed and running.
    ```bash
    $ docker run --name content_system -e POSTGRES_HOST_AUTH_METHOD='trust' -e POSTGRES_PASSWORD='' -e POSTGRES_USER='postgres' -e POSTGRES_DB='content_system' -p 5432:5432  -d postgres:14
    ```

5. **Run Migrations**
    - Open shell and cd into `ContentSystem` folder.
    ```bash
    $ make migrate_db
    ```
   - Enter a migration message when prompted.
   - Example: "Initial migration"

6. **Run the Application**
    ```bash
    # ensure the virutal env is active in the shell.
    $ python main.py
    ```

# Postman Collection
[<img src="https://run.pstmn.io/button.svg" alt="Run In Postman" style="width: 128px; height: 32px;">](https://app.getpostman.com/run-collection/24968573-38b3f333-7237-44aa-8cc3-eacc638a0ef4?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D24968573-38b3f333-7237-44aa-8cc3-eacc638a0ef4%26entityType%3Dcollection%26workspaceId%3Ddc0fcf15-45e7-4afb-b7a7-e6db7fe2c000#?env%5Bdev%5D=W3sia2V5IjoiaG9zdCIsInZhbHVlIjoibG9jYWxob3N0OjgwMDAiLCJlbmFibGVkIjp0cnVlLCJ0eXBlIjoiZGVmYXVsdCJ9XQ==)

# CSV Upload API

## Upload Content CSV

Uploads a CSV file containing content data to the database.

### Endpoint

```
POST /content/upload
```

### Request

#### Headers

| Name           | Required | Description                              |
|----------------|----------|------------------------------------------|
| Content-Type   | Yes      | Must be `multipart/form-data`           |

#### Form Data Parameters

| Name        | Type   | Required | Description                    |
|-------------|--------|----------|--------------------------------|
| file        | File   | Yes      | CSV file to upload             |

### Example Request

### cURL
```bash
curl -X POST \
  'localhost:8000/content/upload' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/file.csv' \
```

### Response

#### Success Response

**Code**: 200 OK

```json
{
    "message": "File uploaded successfully"
}
```

#### Error Responses

**Code**: 400 Bad Request

```json
{
  "error": "Invalid file format",
  "detail": "File must be a CSV"
}
```

# Get Content API

Retrieves a paginated list of content items with filtering and sorting options, as described in the specification.

## Endpoint

```
GET /content
```

## Parameters

### Pagination
- `page`: Integer (default: 1)
- `page_size`: Integer (default: 20, max: 100)

### Filtering
- `year`: exact year (YYYY) or range (YYYY-YYYY)

```
Single year: year=2024
Range: year=2020-2024
```
- `language`: String (comma-separated for multiple) (case insensitive)
```
Single: language=english
Multiple: language=english,广州话 / 廣州話,Français
```

### Sorting
- `sort`: String with optional direction. Combine using comma `,`
- Format: `field:direction`
- Direction: `asc` (default) or `desc`
- Available fields: `release_date`, `rating`

Examples:
```
sort=release_date:asc
sort=rating:desc,release_date:desc
sort=rating:asc
```

### Example Requests

### cURL
```bash
curl -X GET 'localhost:8000/content?page=1&page_size=20&year=2015&language=english&sort=rating:desc'
```

## Response

### Success Response

**Code**: 200 OK

```json
{
    "data": [
        {
            "budget": 15000000,
            "revenue": 8235661,
            "runtime": 124,
            "status": "Released",
            "homepage": "NA",
            "original_language": "en",
            "original_title": "Trumbo",
            "title": "Trumbo",
            "overview": "The career of screenwriter Dalton Trumbo is halted by a witch hunt in the late 1940s when he defies the anti-communist HUAC committee and is blacklisted.",
            "release_date": "2015-10-27",
            "vote_average": 7.3,
            "vote_count": 507,
            "production_company_id": 4205,
            "genre_id": 18
        },
    ],
    "pagination": {
        "current_page": 15,
        "per_page": 20,
        "total_items": 1904,
        "total_pages": 96
    }
}
```
