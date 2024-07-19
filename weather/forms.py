from django import forms

"""
for path in settings.STATICFILES_DIRS:
    try: file_path = os.path.join(path, 'weather/worldcities.csv') # STATIC_URL after collection
    except: pass
columns_to_read = ['city']
world_cities = pandas.read_csv(file_path, usecols=columns_to_read).to_dict()
"""

class AddCityForm(forms.Form):
    city = forms.CharField(max_length=100, required=True, label="Enter A Valid City Name")
