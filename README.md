Prototype application for document similarity browsing with text-heavy archival collections.

Services:

1. django application using Django REST Framework
2. IIIF server powered by IIPImage server
3. Postgres Database
   1. The Djanog application utilizes the PGSQL-specific `ArrayField` for efficiently storing topic terms
4. nginx reverse proxy over everything

---
Matthew Lincoln
