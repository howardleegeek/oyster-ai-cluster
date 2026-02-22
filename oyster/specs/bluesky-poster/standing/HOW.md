# HOW Report: bluesky-poster

## HOW Report for "bluesky-poster" Project

### 1. Architecture: Core Modules/Services

The "bluesky-poster" project can be structured around the following core modules/services:

1. **Authentication Module**: Handles user authentication and authorization using the AT Protocol. This module will manage user sessions, tokens, and permissions.
2. **Posting Service**: Responsible for creating and publishing posts to Bluesky. It will interface with the AT Protocol to format and send posts.
3. **Media Handling Service**: Manages the upload and attachment of media (images, videos) to posts. This service will handle media processing and storage.
4. **Scheduling Service**: Allows users to schedule posts for future publishing. This service will interact with the Posting Service to publish posts at the designated time.
5. **Analytics Module**: Provides insights into post performance, engagement metrics, and user interactions. This module will collect and analyze data from Bluesky.

### 2. Existing Code Reusability

Several components from our existing codebase can be reused or adapted for the "bluesky-poster" project:

- **clawmarketing/auth.py**: This authentication module can be adapted to handle Bluesky-specific authentication using the AT Protocol.
- **clawmarketing/metrics.py**: The metrics collection and analysis code can be repurposed for the Analytics Module.
- **clawmarketing/config.py**: Configuration management can be reused to handle project settings and environment variables.
- **twitter-poster/playwright_demo.py**: This script, which likely handles automated posting, can be adapted to work with Bluesky's API.
- **bluesky-automation/**: The existing automation tests can be expanded to cover the new posting functionalities.

### 3. Recommended Open-Source Libraries/Frameworks

To accelerate development and ensure reliability, the following open-source libraries and frameworks should be considered:

- **FastAPI**: For building the API endpoints of the Posting and Authentication Services. FastAPI offers high performance and easy integration with Python.
- **Celery**: To handle background tasks such as media processing and post scheduling.
- **Pydantic**: For data validation and settings management, ensuring that the data passed between services is correct.
- **React/Vue.js**: For building any frontend components, if needed. However, for a command-line tool or a simple web interface, this might not be necessary.
- **Poetry**: For dependency management and packaging, ensuring that the project dependencies are well-managed and reproducible.

### 4. MVP Scope

The Minimum Viable Product (MVP) for "bluesky-poster" should include the following must-have features:

1. **User Authentication**: Secure login and token management using the AT Protocol.
2. **Post Creation**: Ability to create and publish text and media posts to Bluesky.
3. **Media Attachment**: Support for attaching images and videos to posts.
4. **Post Scheduling**: Option to schedule posts for future publishing.
5. **Basic Analytics**: Simple metrics on post performance, such as views and engagement.

### 5. What Should NOT Be Built

To avoid reinventing the wheel, the following functionalities should leverage existing open-source solutions:

- **Media Processing**: Use libraries like Pillow for image processing and FFmpeg for video handling instead of building custom solutions.
- **Database Management**: Utilize existing ORM libraries like SQLAlchemy for database interactions instead of writing raw SQL queries.
- **API Testing**: Use frameworks like pytest and requests-mock for API testing instead of building custom testing scripts.
- **Scheduling**: Leverage existing scheduling libraries like APScheduler instead of implementing a custom scheduler.

By focusing on reusing existing code and leveraging open-source libraries, the "bluesky-poster" project can be developed more efficiently and with higher reliability.