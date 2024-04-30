# Auth Module

## Dependencies

### Overview

The dependencies revolve around user authentication.

### Authentication Workflow

* The token is extracted from the header using get_authorization.
* The token is decoded to get its payload.
* The authenticate function:
  * Decodes the token.
  * Retrieves the user and session.
  * Throws appropriate exceptions if the user or session is invalid, or if the user is inactive.
  * Updates the session's last active timestamp.
  * Returns the user and session.

### Summary

* UserAuthorization: Authenticates the user and returns a User In DB instance.
* UserAuthorizationOptional: Authenticates the user, returning UserInDB or None.
* UserAuthorizationWithSession: Authenticates the user and returns a tuple of UserInDB and UserSessionsInDB.
