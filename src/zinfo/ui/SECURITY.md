# Security Documentation for FastHTML UI

## Overview

The zInfo FastHTML UI provides a web-based interface for browsing, searching, and scanning project metadata. This document outlines the authentication, access control, and security measures implemented to protect the system and its data.

## Authentication

Authentication for the zInfo web UI is **not handled by the application itself**. Instead, authentication is managed by an external service within the local area network (LAN). The zInfo service assumes that:

- Users are authenticated at the network level before accessing the web interface
- The service runs behind a reverse proxy or authentication gateway that handles user authentication
- The zInfo application trusts the upstream authentication service to provide authenticated user context

### Recommended Authentication Setup

For production deployments, implement authentication using:

- **Reverse Proxy with Authentication**: Nginx, Apache, or Traefik with authentication modules
- **LDAP/Active Directory Integration**: For enterprise environments
- **OAuth/OIDC Providers**: For modern authentication flows
- **VPN Requirements**: Restrict access to authenticated VPN users only

## Access Control

The zInfo service user (the account running the web application) has **restricted access** to specific directories and server paths:

### File System Access Restrictions

- **Scan Root Limitation**: The scanner can only operate within the current working directory (`Path.cwd()`)
- **Path Traversal Prevention**: Explicit validation prevents access to parent directories using `..` in paths
- **Absolute Path Resolution**: All paths are resolved to absolute paths and validated against allowed boundaries

### Server Path Restrictions

- **Static Files**: Only serves files from the configured `static/` directory
- **Database Access**: SQLite database access is limited to the configured database path (default: `zinfo.db`)
- **No Arbitrary File Access**: The web interface does not provide endpoints for arbitrary file system access

## Implemented Security Measures

### Input Validation

The application implements comprehensive input validation to prevent injection attacks and abuse:

#### Scan Parameters Validation (`validate_scan_params`)
- **Root Path**: Must resolve to a valid path within the current working directory
- **Path Traversal**: Blocks any path containing `..` components
- **Profile Validation**: Restricts scan profiles to predefined set: `{'quick', 'standard', 'deep', 'custom'}`
- **Custom Depth**: Must be a positive integer when using custom profile

#### Search Parameters Validation (`validate_search_params`)
- **Length Limits**: All search parameters limited to 100 characters maximum
- **Character Restrictions**: Only allows alphanumeric characters, spaces, hyphens, underscores, and dots
- **Regex Pattern**: Uses `^[a-zA-Z0-9\s\-_.]*$` to prevent special characters that could enable injection

#### Resource ID Validation (`validate_detail_id`)
- **Required Field**: ID parameter must be provided and non-empty
- **Whitespace Handling**: Strips whitespace and validates content

#### Pagination Validation (`validate_pagination_params`)
- **Page Numbers**: Must be >= 1
- **Limit Bounds**: Must be between 1 and 1000 (configurable `MAX_LIMIT`)

### Path Traversal Prevention

- **Directory Restriction**: Scan operations are confined to the current working directory
- **Path Resolution**: Uses `Path.resolve()` to canonicalize paths and prevent symbolic link bypasses
- **Boundary Checks**: Validates that resolved paths start with the current working directory

### Error Handling

- **Generic Error Messages**: Server errors return user-friendly messages without exposing internal details
- **Logging**: Full exception information is logged server-side for debugging while hiding from users
- **HTTP Status Codes**: Appropriate status codes (400 for client errors, 500 for server errors)
- **Exception Handlers**: Dedicated handlers for 404 and 500 errors

### Resource Limits

- **Pagination Limits**: Maximum 1000 items per page to prevent memory exhaustion
- **Scan Depth Limits**: Maximum scan depth of 10 levels to prevent runaway operations
- **Parameter Length Limits**: Search parameters capped at 100 characters

## Deployment Considerations

### Network Security

- **Bind Address**: Default binding to `0.0.0.0` - restrict to `127.0.0.1` for local-only access
- **Port Selection**: Default port 5001 - use firewall rules to restrict access
- **HTTPS Enforcement**: Deploy behind SSL/TLS termination proxy
- **Network Segmentation**: Run on isolated network segment with authentication gateway

### Application Security

- **Process Isolation**: Run the zInfo service under a dedicated, restricted user account
- **File Permissions**: Database and log files should have restrictive permissions (600)
- **Log Security**: Ensure log files don't contain sensitive information
- **Backup Security**: Database backups should be encrypted and access-controlled

### Monitoring and Auditing

- **Access Logging**: Enable comprehensive access logging for security auditing
- **Error Monitoring**: Monitor application logs for security-related events
- **Rate Limiting**: Consider implementing rate limiting at the reverse proxy level
- **Health Checks**: Implement health check endpoints for monitoring service availability

## Security Best Practices

### Development Phase

- **Code Review**: All security-related code changes require review
- **Dependency Updates**: Regularly update FastHTML, Starlette, and other dependencies
- **Security Testing**: Include security testing in the development workflow

### Production Deployment

- **Principle of Least Privilege**: Service user should have minimal required permissions
- **Regular Updates**: Keep the system and dependencies updated with security patches
- **Configuration Management**: Use environment variables for sensitive configuration
- **Backup Strategy**: Regular, encrypted backups of the SQLite database

### Operational Security

- **Incident Response**: Have procedures for security incidents
- **Log Retention**: Implement log rotation and retention policies
- **Access Reviews**: Regularly review who has access to the system
- **Security Training**: Ensure administrators understand security implications

## Known Limitations

- **No Built-in Authentication**: Authentication must be provided by external systems
- **Single-User Design**: The application is designed for single-user or small team use
- **No Rate Limiting**: Application-level rate limiting is not implemented
- **No CSRF Protection**: CSRF protection is not implemented (HTMX handles some aspects)
- **No HTTPS**: The application itself does not handle SSL/TLS

## Security Testing

To validate security measures:

1. **Input Validation Testing**: Attempt injection attacks with special characters
2. **Path Traversal Testing**: Try accessing files outside allowed directories
3. **Resource Exhaustion Testing**: Test with large pagination limits and deep scans
4. **Error Handling Testing**: Verify error messages don't leak information

## Contact and Reporting

For security concerns or vulnerabilities, contact the development team through the project's issue tracking system.
