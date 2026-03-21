# Secure MFA Healthcare Access Portal

## Overview
The Secure MFA Healthcare Access Portal is a Python web application designed to protect sensitive healthcare-style data through layered security controls.

## Features
- Username and password authentication
- Multi-factor authentication
- Role-based access control
- Audit logging
- Sensitive data masking or tokenization
- Web-based interface
- Unit and property-based testing
- Dockerized setup

## Project Structure
- `app/routes/` handles URL endpoints
- `app/controllers/` coordinates request flow
- `app/models/` defines the core domain objects
- `app/services/` contains business logic
- `app/security/` contains lower-level security helpers and patterns
- `app/repositories/` handles data access
- `tests/` contains automated tests
- `docs/uml/` stores UML diagrams and architecture documentation

## UML Diagrams

<!--![Context / Use Case View](./Docs/Uml/01_context_use_case.puml)-->

<!--![Logical / Class View](./Docs/Uml/02_logical_class_view.puml)-->

<!--![Process / Sequence View](./Docs/Uml/03_process_sequence_view.puml)-->

<!--![Development / Package View](./Docs/Uml/04_development_package_view.puml)-->

<!--![Physical / Deployment View](./Docs/Uml/05_physical_deployment_view.puml)-->