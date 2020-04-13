Prototype application for document similarity browsing with photoarchive collections.

Services:

1. django application using Django REST Framework
3. Postgres Database
   1. The Django application utilizes the PGSQL-specific `ArrayField` for efficiently storing image embeddings
4. nginx reverse proxy over everything

---
Matthew Lincoln
