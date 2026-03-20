# Secure MFA Healthcare Access Portal

## Overview
The Secure MFA Healthcare Access Portal is a Python web application designed to improve the security of systems that store sensitive healthcare-style information. The application addresses common weaknesses in password-only authentication by implementing multi-factor authentication, role-based access control, audit logging, and masking or tokenization of sensitive identifiers.

## Features
- Username and password authentication
- Multi-factor authentication
- Role-based access control
- Audit logging of security-related events
- Masking or tokenization of sensitive fields
- Web-based interface
- Unit and property-based testing
- Dockerized setup

## Tech Stack
- Python
- Flask
- pytest
- hypothesis
- Docker

## How to run 
make install
make test
make run