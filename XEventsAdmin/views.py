from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm, UserForm, InventoryForm, CategoryForm, PlacesForm
import requests
import concurrent.futures
import httpx
import asyncio
from django.urls import reverse
from asgiref.sync import async_to_sync
from concurrent.futures import ThreadPoolExecutor
import os
import urllib.parse

API_BASE_URL = 'http://127.0.0.1:8080/api'
API_BASE_URL_AUTH = 'http://127.0.0.1:8080/auth' 

def api_call(method, endpoint, use_auth=False, **kwargs):
    base_url = API_BASE_URL_AUTH if use_auth else API_BASE_URL
    url = f'{base_url}{endpoint}'
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    if response.content and 'application/json' in response.headers.get('Content-Type', ''):
        return response.json()
    else:
        return None



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                data = {'username': username, 'password': password}
                user = api_call('POST', '/login', json=data, use_auth=True)
                request.session['user'] = user
                return redirect('dashboard')
            except requests.exceptions.RequestException as e:
                messages.error(request, 'Credenciales incorrectas o error de conexión.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def dashboard(request):
    if 'user' not in request.session:
        return redirect('login')
    user = user = request.session['user']
    return render(request, 'dashboard.html', {"user": user})

def user_list(request):
    if 'user' not in request.session:
        return redirect('login')
    try:
        users = api_call('GET', '/users')
    except httpx.HTTPError as e:
        messages.error(request, f'Error al obtener usuarios: {e}')
        users = []
    return render(request, 'users_list.html', {'users': users})

def user_create(request):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                data = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'firstName': form.cleaned_data['firstName'],
                'lastName': form.cleaned_data['lastName'],
                'roleId': form.cleaned_data['roleId'],
                }
                api_call('POST', '/users', json=data)
                messages.success(request, 'Usuario creado exitosamente.')
                return redirect('user_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error al crear usuario: {e}')
    else:
        form = UserForm()
    return render(request, 'user_form.html', {'form': form})


def user_edit(request, user_id):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            data = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'firstName': form.cleaned_data['firstName'],
                'lastName': form.cleaned_data['lastName'],
                'roleId': form.cleaned_data['roleId'],
            }
            try:
                api_call('PUT', f'/users/{user_id}', json=data)
                messages.success(request, 'Usuario actualizado exitosamente.')
                return redirect('user_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error al actualizar usuario: {e}')
    else:
        try:
            user_data = api_call('GET', f'/users/{user_id}')
            form = UserForm(initial=user_data)
        except httpx.HTTPError as e:
            messages.error(request, f'Error al obtener datos del usuario: {e}')
            return redirect('user_list')
    return render(request, 'user_form.html', {'form': form})

def user_delete(request, user_id):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        if 'confirm' in request.POST:
            try:
                api_call('DELETE', f'/users/{user_id}')
                messages.success(request, 'Usuario eliminado exitosamente.')
                return redirect('user_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error al eliminar usuario: {e}')
        else:
            return redirect('user_list')
    else:
        try:
            user_data = api_call('GET', f'/users/{user_id}')
        except httpx.HTTPError as e:
            messages.error(request, f'Error al obtener datos del usuario: {e}')
            return redirect('user_list')
    return render(request, 'user_confirm_delete.html', {'user': user_data})


def fetch_data_from_api(endpoints):
    results = {}
    with ThreadPoolExecutor() as executor:
        future_to_endpoint = {executor.submit(requests.get, f'{API_BASE_URL}{ep}'): ep for ep in endpoints}
        for future in concurrent.futures.as_completed(future_to_endpoint):
            endpoint = future_to_endpoint[future]
            try:
                response = future.result()
                results[endpoint] = response.json() if response.status_code == 200 else None
            except Exception as e:
                results[endpoint] = None
    return results

def inventory_list(request):
    if 'user' not in request.session:
        return redirect('login')
    endpoints = ['/inventories', '/inventories/categories']
    data = fetch_data_from_api(endpoints)
    inventory = data.get('/inventories', [])
    category = data.get('/inventories/categories', [])
    return render(request, 'inventory_list.html',{'inventories': inventory, "categories": category})

def inventory_create(request):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                api_call('POST', '/inventories', json=data)
                messages.success(request, 'Created Inventory successfully.')
                return redirect('inventory_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error creating inventory: {e}')
    else:
        form = InventoryForm()
    return render(request, 'inventory_form.html', {'form': form})


def inventory_edit(request, inventory_id):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            try:
                api_call('PUT', f'/inventories/{inventory_id}', json=data)
                messages.success(request, 'Updated Inventory Successfully.')
                return redirect('inventory_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error Update inventory: {e}')
    else:
        try:
            inventory_data = api_call('GET', f'/inventories/{inventory_id}')
            form = InventoryForm(initial=inventory_data)
        except httpx.HTTPError as e:
            messages.error(request, f'Error atemping obtein inventory data: {e}')
            return redirect('inventory_list')
    return render(request, 'inventory_form.html', {'form': form})

def inventory_delete(request, inventory_id):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        if 'confirm' in request.POST:
            try:
                api_call('DELETE', f'/inventories/{inventory_id}')
                messages.success(request, 'Deleted Inventory Successfully')
                return redirect('inventory_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error delete inventory: {e}')
        else:
            return redirect('inventory_list')
    else:
        try:
            inventory_data = api_call('GET', f'/inventories/{inventory_id}')
        except httpx.HTTPError as e:
            messages.error(request, f'Error atemping obtein inventory data: {e}')
            return redirect('inventory_list')
    return render(request, 'inventory_confirm_delete.html', {'inventory': inventory_data})


def category_create(request):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                api_call('POST', '/inventories/categories', json=data)
                messages.success(request, 'Created Inventory Category successfully.')
                return redirect('inventory_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error creating inventory category: {e}')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

def category_edit(request, category_id):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            try:
                api_call('PUT', f'/inventories/categories/{category_id}', json=data)
                messages.success(request, 'Updated Inventory Category Successfully.')
                return redirect('inventory_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error Update inventory: {e}')
    else:
        try:
            category_data = api_call('GET', f'/inventories/categories/{category_id}')
            form = CategoryForm(initial=category_data)
        except httpx.HTTPError as e:
            messages.error(request, f'Error atemping obtein inventory category data: {e}')
            return redirect('inventory_list')
    return render(request, 'category_form.html', {'form': form})

def category_delete(request, category_id):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        if 'confirm' in request.POST:
            try:
                api_call('DELETE', f'/inventories/categories/{category_id}')
                messages.success(request, 'Deleted Inventory Category Successfully')
                return redirect('inventory_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error delete inventory: {e}')
        else:
            return redirect('inventory_list')
    else:
        try:
            category_data = api_call('GET', f'/inventories/categories/{category_id}')
        except httpx.HTTPError as e:
            messages.error(request, f'Error atemping obtein inventory data: {e}')
            return redirect('inventory_list')
    return render(request, 'category_confirm_delete.html', {'category': category_data})


def places_list(request):
    if 'user' not in request.session:
        return redirect('login')
    try:
        places = api_call('GET', '/places')
        for place in places:
            image_path = place.get('image')
            if image_path:
                image_path = image_path.replace('\\', '/')
                image_filename = os.path.basename(image_path)
                image_filename_encoded = urllib.parse.quote(image_filename)
                image_url = f"http://localhost:8080git/images/{image_filename_encoded}"
            else:
                image_url = '/static/images/default-placeholder.png'

            place['image_url'] = image_url
    except httpx.HTTPError as e:
        messages.error(request, f'Error atemping obtein places: {e}')
        places = []
    return render(request, 'places_list.html', {'places': places})

def places_create(request):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = PlacesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                data = {
                'placeName': form.cleaned_data['placeName'],
                'description': form.cleaned_data['description'],
                'about': form.cleaned_data['about'],
                'location': form.cleaned_data['location'],
                }
                files = {
                    'image': request.FILES['image'] if 'image' in request.FILES else None,
                    'imageFileName': (request.FILES['image'].name if 'image' in request.FILES else None),
                }

                multipart_data = {
                    'placeName': (None, data['placeName']),
                    'description': (None, data['description']),
                    'about': (None, data['about']),
                    'location': (None, data['location']),
                }

                if files['image']:
                    multipart_data['image'] = (files['imageFileName'], files['image'].read())
                    multipart_data['imageFileName'] = (None, files['imageFileName'])
                else:
                    pass

                api_call('POST', '/places', files=multipart_data)
                print(request)
                messages.success(request, 'Created Place successfully.')
                return redirect('places_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error place category: {e}')
    else:
        form = PlacesForm()
    return render(request, 'category_form.html', {'form': form})

def places_edit(request, place_id):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = PlacesForm(request.POST, request.FILES)
        if form.is_valid():
            data=form.cleaned_data
            try:
                data = {
                'placeName': form.cleaned_data['placeName'],
                'description': form.cleaned_data['description'],
                'about': form.cleaned_data['about'],
                'location': form.cleaned_data['location'],
                }
                files = {
                    'image': request.FILES['image'] if 'image' in request.FILES else None,
                    'imageFileName': (request.FILES['image'].name if 'image' in request.FILES else None),
                }

                multipart_data = {
                    'placeName': (None, data['placeName']),
                    'description': (None, data['description']),
                    'about': (None, data['about']),
                    'location': (None, data['location']),
                }

                if files['image']:
                    multipart_data['image'] = (files['imageFileName'], files['image'].read())
                    multipart_data['imageFileName'] = (None, files['imageFileName'])
                else:
                    pass
                api_call('PUT', f'/places/{place_id}', files=multipart_data)
                messages.success(request, 'Updated place Successfully.')
                return redirect('places_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error Update place: {e}')
    else:
        try:
            places_data = api_call('GET', f'/places/{place_id}')
            form = PlacesForm(initial=places_data)
        except httpx.HTTPError as e:
            messages.error(request, f'Error atemping obtein place data: {e}')
            return redirect('places_list')
    return render(request, 'places_form.html', {'form': form})

def places_delete(request, place_id):
    if 'user' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        if 'confirm' in request.POST:
            try:
                api_call('DELETE', f'/places/{place_id}')
                messages.success(request, 'Deleted Place Successfully')
                return redirect('places_list')
            except httpx.HTTPError as e:
                messages.error(request, f'Error delete place: {e}')
        else:
            return redirect('places_list')
    else:
        try:
            places_data = api_call('GET', f'/places/{place_id}')
        except httpx.HTTPError as e:
            messages.error(request, f'Error atemping obtein place data: {e}')
            return redirect('places_list')
    return render(request, 'places_confirm_delete.html', {'places': places_data})
