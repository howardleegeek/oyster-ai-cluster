# HOW Report: clawphones

## Architecture

For the "clawphones" project, we can break down the architecture into the following core modules/services:

1. **User Interface (UI) Module**: This module will handle all the user interactions and display components. It will be built using Kotlin for Android, ensuring a native and smooth user experience.
2. **Backend Service**: This will manage the core functionalities such as user authentication, data processing, and communication with external APIs. It will be a RESTful API built using a framework like Ktor or Spring Boot.
3. **Database Service**: This module will handle data storage and retrieval. We can use a lightweight database like SQLite for local storage and potentially integrate with a cloud database for scalability.
4. **Notification Service**: This module will handle push notifications and real-time updates to the user. It will integrate with Firebase Cloud Messaging (FCM) or similar services.
5. **Analytics Module**: This will track user interactions and app performance. It will integrate with analytics tools like Firebase Analytics or Amplitude.

## Existing Code Reusability

From the existing codebase, the following modules can be reused or adapted for the "clawphones" project:

- **clawphones-landing/**: The scripts for rendering and fixing assets can be reused to manage the app's UI components and assets.
- **clawmarketing/**: The `auth.py`, `metrics.py`, and `database.py` files can be adapted for user authentication, tracking, and database management.
- **oyster-agent-components/**: The `index.ts` and `core_types.ts` files can be used as a reference for building the core types and interfaces in Kotlin.
- **bluesky-poster/**: The `queue.py` and `test_rate_limiter.py` files can be adapted for implementing rate limiting and queue management in the backend.
- **nft-mgmt-api/**: The `config.py` and `utils.py` files can be reused for configuration management and utility functions.

## Open-Source Libraries/Frameworks

To accelerate development and ensure reliability, we should leverage the following open-source libraries and frameworks:

- **Retrofit**: For making network requests and handling API interactions.
- **Room**: For local database management.
- **Firebase**: For push notifications, analytics, and cloud functions.
- **Kotlin Coroutines**: For handling asynchronous tasks.
- **Jetpack Compose**: For building the UI components if we decide to use a modern declarative approach.

## MVP Scope

The MVP for "clawphones" should include the following must-have features:

1. **User Authentication**: Allow users to sign up, log in, and manage their profiles.
2. **Core Functionality**: Implement the primary feature of the app, which is the ability to make voice calls or send messages.
3. **Push Notifications**: Enable real-time notifications for incoming calls and messages.
4. **Contact Management**: Allow users to manage their contacts and sync with their device's address book.
5. **Basic Settings**: Provide users with options to manage app settings such as notification preferences and privacy settings.

## What Should NOT Be Built

To avoid reinventing the wheel, we should use existing open-source solutions for the following:

- **Authentication**: Use Firebase Authentication or Auth0 instead of building a custom authentication system.
- **Analytics**: Integrate with Firebase Analytics or Amplitude instead of building a custom analytics solution.
- **Push Notifications**: Use Firebase Cloud Messaging (FCM) instead of building a custom notification service.
- **UI Components**: Utilize Jetpack Compose or other UI libraries instead of building custom components from scratch.

By leveraging these existing solutions, we can focus on the core features and ensure a more robust and reliable application.