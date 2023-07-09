#!/usr/bin/bash

# Scan models
python3 ../manage.py graph_models -X TimedModel -I Snippet,FindingTemplate,Finding,Vulnerability -g -o source/ref/models/images/finding_models.png

# Generate finding-related models
python3 ../manage.py graph_models -X TimedModel -I AbstractBaseFinding,Snippet,FindingTemplate,Finding,Vulnerability -g -o source/ref/models/images/finding_models.png

# app-permission models
python3 ../manage.py graph_models -X TimedModel -I AppPermission,PermissionFinding -g -o source/ref/models/images/app_permission_models.png

# dependency models
python3 ../manage.py graph_models -X TimedModel -I Package,PackageVulnerability,Dependency -g -o source/ref/models/images/dependency_models.png

# code models
python3 ../manage.py graph_models -I Environment,Team,Project,File,Account,Bundle,User -g -o source/ref/models/images/base_models.png