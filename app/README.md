# FirstStreet Backend Application

This is the backend application for FirstStreet, organized with a clear separation of concerns.

## Project Structure

The application follows a modular structure with clear separation of concerns:

```
app/
├── api/                  # API routes and resources
├── auth/                 # Authentication-related routes and forms
├── errors/               # Error handling and custom exceptions
├── main/                 # Main application routes and forms
├── models/               # Database models (see models/README.md)
├── repositories/         # Data access layer (repository pattern)
├── schemas/              # Serialization schemas (see schemas/README.md)
├── services/             # Business logic layer
├── templates/            # Jinja2 templates for rendering HTML
├── utils/                # Utility functions and classes (see utils/README.md)
├── __init__.py           # Application factory
├── extensions.py         # Flask extensions initialization
├── logging.py            # Logging configuration
└── README.md             # This file
```

## Architecture

The application follows a layered architecture:

1. **Presentation Layer** (api/, auth/, main/, templates/): Handles HTTP requests and responses, renders templates
2. **Service Layer** (services/): Contains business logic and orchestrates operations
3. **Data Access Layer** (repositories/): Abstracts database operations using the repository pattern
4. **Domain Layer** (models/): Defines the core domain entities and their relationships

## Design Patterns

- **Application Factory**: The app is created using a factory function in `__init__.py`
- **Repository Pattern**: Data access is abstracted through repositories
- **Service Layer**: Business logic is encapsulated in service classes
- **Blueprint Pattern**: The application is divided into modular blueprints

## Adding New Features

When adding new features:

1. Define models in the models/ package
2. Create schemas in the schemas/ package
3. Implement data access in the repositories/ package
4. Implement business logic in the services/ package
5. Expose functionality through routes in the appropriate blueprint