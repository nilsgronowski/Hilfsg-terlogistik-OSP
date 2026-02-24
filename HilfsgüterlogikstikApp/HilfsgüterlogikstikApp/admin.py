from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
	site_header = 'Hilfsgüter-Logistik Verwaltung'
	site_title = 'Hilfsgüter-Logistik Admin'
	index_title = 'Einsatzsteuerung & Ressourcenübersicht'

	def get_app_list(self, request, app_label=None):
		app_list = super().get_app_list(request, app_label)
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

