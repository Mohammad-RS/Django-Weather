from django import forms

class AddCityForm(forms.Form):
    city = forms.CharField(max_length=100, required=True, label="Enter A Valid City Name")
    
    

    