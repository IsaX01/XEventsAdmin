from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=25, required=True, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Password')

ROLE_CHOICES = [
    (2, 'User')
]

class UserForm(forms.Form):
    username = forms.CharField(max_length=25, required=True, label='Username')
    email = forms.EmailField(required=True, label='Email')
    firstName = forms.CharField(max_length=25, required=True, label='First Name')
    lastName = forms.CharField(max_length=25, required=True, label='Last Name')
    categoryId = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label='Category'
    )  

CATEGORY_CHOICES = [
    (1, 'Utilities')
]

IS_AVAILABLE = [
    (True, 'Yes'),
    (False, 'No')
]

MAINTENANCE = [
    ('good_condition', 'Good Condition'),
    ('out_of_stock', 'Out Of Stock')
]

class InventoryForm(forms.Form):
    name = forms.CharField(max_length=25, required=True, label='Name')
    description = forms.CharField(max_length=100, widget=forms.Textarea)
    stockQuantity = forms.IntegerField(required=True, label='Stock Quantity')
    maintenanceStatus = forms.ChoiceField(choices=MAINTENANCE ,required=True, label='Maintenance Status')
    isAvailable = forms.ChoiceField(choices=IS_AVAILABLE, required=True, label='Is Available?')
    categoryId = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=True,
        label='Category'
    )   

class CategoryForm(forms.Form):
    category = forms.CharField(max_length=25, required=True, label='Category Name')

class PlacesForm(forms.Form):
    placeName = forms.CharField(max_length=50, required=True, label='Name')
    description = forms.CharField(max_length=100, widget=forms.Textarea)
    about = forms.CharField(max_length=100, widget=forms.Textarea)
    location = forms.CharField(max_length=50, required=True, label='Location')
    image = forms.ImageField(required=False)
     
    def __str__(self):
        return self.placeName