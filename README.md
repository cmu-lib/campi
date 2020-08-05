# CAMPI

*Computer-Aided Metadata for Photoarchives Initiative*

Prototype application for document similarity browsing with photoarchive collections written Summer 2020 by Matthew Lincoln (@mdlincoln) in conjunction with a pilot project with CMU Archives' General Photograph Collection (GPC) with Julia Corrin and Emily Davis, and project management by Scott Weingart.

**PROJECT WHITEPAPER LINK**

This is a prototype implementation of a few computer-vision-aided metadata generation workflows for this specific collection. **_It is not yet meant to be a general-purpose piece of reusable software to be deployed in other contexts._** While the general concepts and workflows could be adaptable to other digital photo collections, the specific data models for photographs and hierarchical organization are tailored specifically to the GPC. Our goal in this short development cycle was to prototype, test, and report out on these workflows, with recommendations for later system work that could integrate concepts from this application with in-production collection management services. We are publishing the code of this prototype system only to illustrate how we went about implementing these workflows and technologies. As we discuss in the project whitepaper, we would need to do significant changes and re-implementations to create a system that would 1) work at scale and 2) interact with production systems such as ArchivesSpace or Islandora.

## Overview

### Docker Compose Services

1. [Django](https://www.djangoproject.com/) [REST Framework](https://www.django-rest-framework.org/) site
2. [PostgreSQL](https://www.postgresql.org/) Database (The Django application utilizes the PGSQL-specific `ArrayField` for efficiently storing image embeddings)
3. A [Vue](https://vuejs.org/)-based SPA frontend that makes calls to the API provided by Django
4. [Nginx](https://nginx.org/) reverse proxy over everything

During the duration of this project, the images themselves were served from a temporary IIIF server outside this stack, running [IIPImage](https://iipimage.sourceforge.io/). Image data in the `test.json` file shows a sample of the paths used, however the URLs are no longer live.

### Django Modules

As this is the most alpha of alpha software, some of these modules could well be refactored into more logically-separate components.

1. `photograph` - Models describing individual photographs as well as annotations on those photographs.
2. `collection` - Models describing different organizational hierarchies for photographs, such as "jobs" defined in the GPC's original organization, and directories in which original TIFFs were stored during digitization.
3. `cv` - Models describing computer vision models and methods for calculating image features, approximate-nearest-neighbor search indices and methods for retrieving nearest neighbors, and close match detection algorithms and the match sets of photographs that they create.
4. `tagging` - Models for a domain-specific-vocabulary and a tagging decision workflow
5. `gcv` - Models and management commands for making image annotation requests to Google Cloud Vision API, storing the raw responses, and parsing raw responses into structured annotations on photographs.
6. `campi` - Helpful abstract models and DRF ViewSet mixin classes used by all the other modules

### Configuration

The docker-compose file expects a .env file specifying certain paths and credentials. .env-template describes these.

---
Code written by Matthew Lincoln
Copyright 2020 Carnegie Mellon University Libraries
