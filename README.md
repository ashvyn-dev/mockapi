# Mock API

A full-stack mock API server for creating, managing, and testing API endpoints.

## Overview

Mock API provides a complete solution for mocking REST APIs during development and testing. It features a Django backend with Django REST Framework for API management and a React frontend for intuitive endpoint configuration and testing.

## Features

- JWT-based authentication and authorization
- Collection-based API organization
- Full CRUD operations for collections and endpoints
- Multiple response configurations per endpoint
- Request logging and inspection
- Response delay simulation
- Custom headers and status codes
- Collapsible sidebar navigation
- Inline endpoint editing
- Real-time API testing

## Tech Stack

### Backend
- Django 4.2+
- Django REST Framework
- djangorestframework-simplejwt
- django-cors-headers
- django-nested-admin
- SQLite (default database)

### Frontend
- React 18
- Vite
- Axios
- CSS3

## Project Structure

```
mockapi/
├── mockapi/                 # Django project settings
├── domains/                 # Collections and endpoints app
├── logger/                  # Request logging app
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── styles/
│   │   ├── api.js
│   │   └── main.jsx
│   └── package.json
├── manage.py
└── requirements.txt
```

## Installation

### Prerequisites

- Python 3.10+
- uv (Python package manager)
- Node.js 18+
- npm or yarn

### Install uv

```
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Using pip
pip install uv
```

### Backend Setup

1. Clone the repository
```
git clone <repository-url>
cd hf-mockapi
```

2. Create virtual environment with uv
```
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install Python dependencies using uv
```
uv pip install -r requirements.txt
```

4. Run migrations
```
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser
```
python manage.py createsuperuser
```

6. Start Django server
```
python manage.py runserver 8008
```

### Frontend Setup

1. Navigate to frontend directory
```
cd frontend
```

2. Install dependencies
```
npm install
```

3. Start development server
```
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8008
- Admin Panel: http://localhost:8008/admin

## Usage

### Creating Collections

1. Log in to the application
2. Click the "+" button in the Collections sidebar
3. Enter collection slug, name, and description
4. Click "Create"

### Adding Endpoints

1. Select a collection from the sidebar
2. Click "New Endpoint" in the endpoint list
3. Configure the endpoint:
   - Display name
   - HTTP method (GET, POST, PUT, PATCH, DELETE)
   - Path
   - Response status code
   - Response body
   - Custom headers (optional)
   - Response delay (optional)
4. Click "Create"

### Testing Endpoints

1. Select an endpoint from the list
2. Add request body (for POST/PUT/PATCH)
3. Add custom headers (optional)
4. Click "Send Request"
5. View response status, headers, and body

### Managing Multiple Responses

1. Edit an endpoint
2. Scroll to "Additional Responses" section
3. Click "Add Response"
4. Configure response name, status, and body
5. Mark as default if needed

### Accessing Mock Endpoints

Mock endpoints are accessible at:
```
http://localhost:8008/{collection-slug}/{endpoint-path}
```

Example:
```
GET http://localhost:8008/api/users
POST http://localhost:8008/api/users
```

## API Endpoints

### Authentication
- POST `/api/auth/login/` - Login
- POST `/api/auth/register/` - Register
- POST `/api/auth/refresh/` - Refresh token
- GET `/api/auth/me/` - Get current user

### Collections
- GET `/api/collections/` - List collections
- POST `/api/collections/` - Create collection
- GET `/api/collections/{slug}/` - Get collection
- PUT `/api/collections/{slug}/` - Update collection
- DELETE `/api/collections/{slug}/` - Delete collection

### Endpoints
- GET `/api/endpoints/` - List endpoints
- POST `/api/endpoints/` - Create endpoint
- GET `/api/endpoints/{id}/` - Get endpoint
- PUT `/api/endpoints/{id}/` - Update endpoint
- DELETE `/api/endpoints/{id}/` - Delete endpoint

### Responses
- GET `/api/responses/` - List responses
- POST `/api/responses/` - Create response
- GET `/api/responses/{id}/` - Get response
- PUT `/api/responses/{id}/` - Update response
- DELETE `/api/responses/{id}/` - Delete response

## Development

### Adding Dependencies

Backend (using uv):
```
uv pip install package-name
uv pip freeze > requirements.txt
```

Frontend:
```
npm install package-name
```

### Running Tests

Backend:
```
python manage.py test
```

Frontend:
```
npm test
```

### Code Style

Backend follows PEP 8 guidelines.
Frontend uses standard React conventions.

## Configuration

### CORS Settings

Update `hf_mockapi/settings.py` to configure allowed origins:

```
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### JWT Token Settings

Adjust token lifetime in `hf_mockapi/settings.py`:

```
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

## Deployment

### Backend Deployment

1. Update `ALLOWED_HOSTS` in settings.py
2. Set `DEBUG = False`
3. Configure production database
4. Collect static files:
```
python manage.py collectstatic
```
5. Use gunicorn or similar WSGI server

### Frontend Deployment

1. Build production assets:
```
npm run build
```
2. Serve the `dist` folder with nginx or similar

## Useful uv Commands

```
# Create virtual environment
uv venv

# Install packages
uv pip install package-name

# Install from requirements.txt
uv pip install -r requirements.txt

# Update package
uv pip install --upgrade package-name

# Freeze dependencies
uv pip freeze > requirements.txt

# Sync environment with requirements
uv pip sync requirements.txt
```

## License

GNU GPL License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a pull request

## Support

For issues and questions, please open an issue on GitHub.
