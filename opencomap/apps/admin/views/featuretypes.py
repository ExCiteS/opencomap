from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.template import RequestContext

from opencomap.apps.backend import authorization
import opencomap.apps.backend.models.factory as Factory
from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.featuretype import FeatureType, Field
from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend.models.FeatureType import FIELD_TYPES

@login_required
@require_http_methods(["GET", "POST"])
def createFeaturetype(request, project_id):
	project = authorization.projects.project(request.user, project_id)

	if request.method == "GET":
		return render(request, 'featuretype.new.html', RequestContext(request, {"project": project}))

	if request.method == "POST":
		featuretype = Factory.createFeaturetype(request.POST.get('name'), request.POST.get('description'), request.user, project)
		return redirect('featuretype_view', project.id, featuretype.id)

@login_required
@require_http_methods(["GET"])
def viewFeaturetype(request, project_id, featuretype_id):
	try:
		project = authorization.projects.project(request.user, project_id)
		admin = project.admins.isMember(request.user)
		featuretype = project.featuretype_set.get(pk=featuretype_id)

		return render(request, 'featuretype.html', RequestContext(request, {"project": project, "featuretype": featuretype, "status_types": STATUS_TYPES}))
	except (Project.DoesNotExist, FeatureType.DoesNotExist) as err:
		return render(request, 'featuretype.html', RequestContext(request, {"error": err}))
	
@login_required
@require_http_methods(["GET", "POST"])
def createField(request, project_id, featuretype_id):
	try:
		project = authorization.projects.project(request.user, project_id)
		featuretype = project.featuretype_set.get(pk=featuretype_id)
		admin = project.admins.isMember(request.user)

		if request.method == "GET":
			return render(request, 'field.new.html', RequestContext(request, {"project": project, "featuretype": featuretype, "fieldtypes": FIELD_TYPES}))

		if request.method == "POST":
			field_model = FIELD_TYPES.get(request.POST.get('type')).get('model')
			required = request.POST.get('required') != None
			field = field_model(name=request.POST.get('name'), description=request.POST.get('description'), required=required, featuretype=featuretype)
			field.save()
			return redirect('field_view', project.id, featuretype.id, field.id)

	except (Project.DoesNotExist, FeatureType.DoesNotExist) as err:
		return render(request, 'field.new.html', RequestContext(request, {"error": err}))

def viewField(request, project_id, featuretype_id, field_id):
	try:
		project = authorization.projects.project(request.user, project_id)
		featuretype = project.featuretype_set.get(pk=featuretype_id)
		field = featuretype.field_set.get(pk=field_id)
		return render(request, 'field.html', RequestContext(request, {"project": project, "featuretype": featuretype, "field": field, "status_types": STATUS_TYPES}))
	except (Project.DoesNotExist, FeatureType.DoesNotExist, Field.DoesNotExist) as err:
		return render(request, 'field.html', RequestContext(request, {"error": err}))

