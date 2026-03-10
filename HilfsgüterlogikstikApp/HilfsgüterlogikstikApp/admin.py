from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


class CustomAdminSite(admin.AdminSite):
	site_header = 'Relief Supplies Logistics Management'
	site_title = 'Relief Supplies Logistics Admin'
	index_title = 'Operations Control & Resource Overview'

	def index(self, request, extra_context=None):
		extra_context = extra_context or {}
		extra_context['register_url'] = reverse('register')
		return super().index(request, extra_context)

	def get_app_list(self, request, app_label=None):
		app_list = super().get_app_list(request, app_label)
		
		# Define app order
		app_order = {
			'auftraege': 1,
			'pruefung': 2,
			'auth': 3,
		}
		
		# Sort apps by defined order
		app_list.sort(key=lambda app: app_order.get(app.get('app_label'), 999))
		
		for app in app_list:
			if app.get('app_label') == 'auftraege':
				order = {
					'Auftrag': 1,
					'Container': 2,
					'Box': 3,
					'Item': 4,
				}
				app['models'].sort(
					key=lambda model: order.get(model.get('object_name'), 999)
				)
			elif app.get('app_label') == 'pruefung':
				order = {
					'Auftragspruefung': 1,
					'Einzelpruefung': 2,
					'PruefErgebnis': 3,
					'Schwund': 4,
				}
				app['models'].sort(
					key=lambda model: order.get(model.get('object_name'), 999)
				)
		return app_list


admin.site.__class__ = CustomAdminSite

