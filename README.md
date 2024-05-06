# GoogleAPILogin

This Commit Contains integration for Google API authentication with fastapi-sso library with correct requirements dependencies.
Tasks Done:

1-Check how to resolve JWT to get into the client side without passing jwt, instead use a reference id that points to the server allocated JWT containing the user session data. Consider Redis option or DB.

2-Star implementing generic auth handling for multiple API sso methods (Google/Facebook)

3-Implement different Session token delivery to cross-platform users ((Android/iOS - React Native)/PC - ReactJS)

Project URL https://gossportsco.atlassian.net/browse/GD-2


# Project Next Steps
This README outlines the next steps to be taken in the project. Each step is described briefly for clarity.

1. Define Logging Logic with Trigger Action in Database
Implement a logging logic using trigger action in the database to store session logs for user session tracking. This is the recommended approach for efficient session management.

2. Encrypt JWT for Enhanced Security
Enhance security measures by encrypting JWT (JSON Web Tokens) to prevent easy JWT reading from the client or server side. This step will ensure that sensitive information remains protected.

3. Implement Status Handling for New Registered Users
Develop logic to handle the status of new registered users through the platform using SMTP email service. This will involve sending email notifications to users to confirm their registration status.

4. Create Login Logic and User Interface/Experience
Build login logic and design the corresponding user interface and experience (UI/UX). A seamless and intuitive login process is essential for user engagement and satisfaction.

5. Refactor Code Structure and Improve Documentation
Delve deeper into the code structure to achieve a cleaner interface. Additionally, add documentation to facilitate future development and maintenance.
