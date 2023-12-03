# Losuj To App - User Management ADR

## 1. Custom User Profile with Email Address as Username

## Context

[Provide a brief overview of the need for user management in the "Losuj To" app.]

### Decision
We will implement a custom user profile for the "Losuj To" app, where the email address will serve as the username. This decision aligns with the desire for a custom user profile and simplifies user identification.

### Implementation Steps
- Create a custom user model in Django, extending the AbstractBaseUser and PermissionsMixin.
- Include the necessary fields such as email, first name, last name, etc., in the custom user model.
- Set the custom user model in the Django settings.
- Update user registration and authentication views to use the custom user model.

### Considerations
- Implement proper validation for email addresses.
- Update the admin interface to display and manage the custom user model.

## 2. Google Authentication

### Decision
Users in the "Losuj To" app should have the option to log in using their Google accounts. We will integrate Google authentication for a seamless and secure login experience.

### Implementation Steps
- Utilize a Django package `django-allauth` for social authentication.
- Set up a Google Developer Console project and configure OAuth 2.0 credentials.
- Implement the necessary views and templates for Google login.
- Handle user registration and profile creation upon successful Google authentication.

### Considerations
- Store necessary user information retrieved from Google, such as name and email.
- Implement proper error handling for failed authentication attempts.
- Provide an option for users to link/unlink their Google accounts from their profiles.

## 3. Profile Management

### Decision
Users should be able to manage their profiles within the "Losuj To" app, including updating personal information and changing passwords.

### Implementation Steps
- Create views and templates for user profile management, allowing users to view and update their information.
- Implement password change functionality, adhering to secure practices.
- Ensure proper validation and error handling for profile updates.

### Considerations
- Balance the level of information users can modify with security and privacy concerns.
- Implement email verification for certain profile changes, such as email address updates.

## 4. Invitation System for Participants

### Decision
When a user creates a new event in the "Losuj To" app and provides emails of other participants, an invitation system will be implemented. If the provided emails do not have associated accounts, the application will create temporary accounts for those users specifically tied to the event.

### Implementation Steps
- Extend the event model to include a field for storing invited participants.
- When the event is created, check the provided emails against existing user accounts. For unregistered emails, create temporary accounts associated with the event.
- Generate unique links for each participant in the invitation email to allow access to the event.
- Include information in the email explaining that a temporary account has been created for the event.
- Temporary accounts should have a field in the user model indicating their account type or status (e.g., "temporary").
- Implement a mechanism to expire or remove temporary accounts if the user does not fully register within a specified timeframe.
- Implement a mechanism which allow to store event data associated with the removed account for future use, e.g. to repeat drawing for the next re-occurring event.

### Considerations
- Ensure that the link in the invitation email is secure and time-limited to prevent abuse.
- Provide clear instructions in the email on how to access the event and complete the registration process.
- Implement a user-friendly registration flow for participants who choose to fully register.

## 5. Participant Registration Process

### Decision
Participants with temporary accounts will have the option to fully register in the "Losuj To" app, providing additional information and setting up a password.

### Implementation Steps
- Implement a registration flow that allows participants to click on the unique link provided in the invitation email.
- Upon clicking the link, users are directed to a registration page with pre-filled information based on the temporary account.
- Users provide additional information required for full registration, such as name, password, and any other necessary details.
- After successful registration, update the user account status from "temporary" to "registered."

### Considerations
- Ensure a seamless transition from the temporary account to the fully registered account.
- Communicate the benefits of full registration to encourage participants to complete the process. Only registered user will be able to see the historical drawings. Only the registered users will be able to create events.

## 6. Handling Incomplete Registrations

### Decision
If a participant with a temporary account does not complete the full registration within a specified timeframe, the temporary account will be removed from the users' database.

### Implementation Steps
- Implement a mechanism to track the registration status and timestamp of each temporary account.
- Regularly check for temporary accounts that have not been fully registered within the designated timeframe.
- Remove or expire the temporary accounts that remain incomplete.

### Considerations
- Determine a reasonable timeframe for completing registration based on the event's schedule, e.g. +2 weeks since the event date.
- Communicate clearly to participants the timeframe for completing the registration process.


## Status
Proposed

## Date
2021-12-02

