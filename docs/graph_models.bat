@echo off

@REM Scan models
py ..\manage.py graph_models -X TimedModel -I Snippet,FindingTemplate,Finding,Vulnerability -g -o source\ref\models\images\finding_models.png

@REM Generate finding-related models
py ..\manage.py graph_models -X TimedModel -I AbstractBaseFinding,Snippet,FindingTemplate,Finding,Vulnerability -g -o source\ref\models\images\finding_models.png

@REM app-permission models
py ..\manage.py graph_models -X TimedModel -I AppPermission,PermissionFinding -g -o source\ref\models\images\app_permission_models.png

@REM dependency models
py ..\manage.py graph_models -X TimedModel -I Package,PackageVulnerability,Dependency -g -o source\ref\models\images\dependency_models.png

@REM code models
py ..\manage.py graph_models -I Environment,Team,Project,File,Account,Bundle,User -g -o source\ref\models\images\base_models.png