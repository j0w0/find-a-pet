from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.conf import settings
import urllib.parse
from .api import *
from .models import Pet


def sort_pets_by_pic(pets):
    # sort pets by photo availability
    pets_with_pics = []
    pets_no_pics = []
    for pet in pets['animals']:
        if pet['photos']:
            pets_with_pics.append(pet)
        else:
            pets_no_pics.append(pet)
    return pets_with_pics + pets_no_pics


def index(request):
    # get initial page data from petfinder api
    animal_types = get_animal_types()
    featured_pets = get_animals()

    # sort pets by photo availability
    sorted_pets = sort_pets_by_pic(featured_pets)

    return render(request, 'index.html', {
        'animal_types': animal_types,
        'featured_pets': sorted_pets,
        'default_img': settings.STATIC_URL + 'images/dog-icon.png'
    })


def search(request):
    if request.method == "POST":
        # declare/init form values
        zip_code = request.POST.get('zip_code', '')
        animal_type = request.POST.get('pet_type', '')
        size = request.POST.get('size', '')
        gender = request.POST.get('gender', '')
        age = request.POST.get('age', '')

        # conditionally add search params to dictionary
        search = {}

        if animal_type:
            search['type'] = animal_type
        if zip_code:
            search['location'] = zip_code
        if size:
            search['size'] = size
        if gender:
            search['gender'] = gender
        if age:
            search['age'] = age

        search['limit'] = 20

        # use urllib to create urlencoded query to append to redirect url
        search_string = f'?{urllib.parse.urlencode(search)}'
        return redirect(f'/search/{search_string}')

    else:
        # get initial data for page from petfinder api
        animal_types = get_animal_types()
        featured_pets = get_animals()

        # show pets with pics available first on the page
        sorted_pets = sort_pets_by_pic(featured_pets)

        # start params dictionary to send to template via render
        parameters = {
            "animal_types": animal_types,
            "featured_pets": sorted_pets,
            'default_img': settings.STATIC_URL + 'images/dog-icon.png'
        }

        if request.META['QUERY_STRING'] != '':
            # get query string
            query_str = request.META['QUERY_STRING']
            search_results = filter_animals(f'?{query_str}')

            # sort search results by pet photo availability
            sorted_results = sort_pets_by_pic(search_results)

            # add sorted pet list to parameters dict for template rendering
            parameters['search_results'] = sorted_results

            # check to see if pagination links are part of search results
            if '_links' in search_results['pagination']:

                # append to parameters dict if available
                if 'previous' in search_results['pagination']['_links']:
                    parameters['prev_page'] = search_results['pagination']['_links']['previous']['href'][len(
                        '/v2/animals'):]

                if 'next' in search_results['pagination']['_links']:
                    parameters['next_page'] = search_results['pagination']['_links']['next']['href'][len(
                        '/v2/animals'):]

        # g'wan ahead and render the damn thing
        return render(request, 'search.html', parameters)


@login_required
def favorites(request):
    # get this user's favorited pets
    users_pets = request.user.pet_set.all()

    # loop through favs and get pet data from api
    api_pets = []
    for pet in users_pets:
        pet_data = get_animal(pet.api_pet_id)

        # make sure pet is still adoptable
        if pet_data['animal']['status'] == 'adoptable':
            # append to pet list
            api_pets.append(pet_data)
        else:
            # happy for the pet, sad for us the pet is no longer available
            # delete all instances of this favorited pet
            Pet.objects.filter(api_pet_id=pet.api_pet_id).delete()

    return render(request, 'favorites.html', {'users_pets': api_pets})


def pets_show(request, api_pet_id):
    # get this specific pet's data from api
    animal = get_animal(api_pet_id)

    # redirect to favorites if pet id not found
    if 'status' in animal and animal['status'] != 200:
        return redirect('favorites')

    # create initial params to send to template
    params = {
        'animal': animal,
        'default_img': settings.STATIC_URL + 'images/dog-icon.png'
    }

    if request.user.is_authenticated:
        try:
            # see if this pet is a fav of this user
            db_pet = Pet.objects.get(api_pet_id=api_pet_id, user=request.user)
            # add favorite/comment notes from our db to params
            params['pet'] = db_pet
        except Pet.DoesNotExist:
            # don't need to do anything if not found
            pass

    return render(request, 'details.html', params)


@login_required
def pets_update(request):
    # redirect to index if no pet id is in http request
    api_pet_id = request.POST.get('api_pet_id', '')
    if not api_pet_id:
        return redirect('index')

    current_user = request.user
    comment = request.POST.get('comment', '')

    # get pet from our database, add comment, and save/update
    pet = Pet.objects.get(api_pet_id=api_pet_id, user=current_user)
    pet.comments = comment
    pet.save()

    return redirect('pets_show', api_pet_id)


@login_required
def pets_create(request):
    # pet id from request
    api_pet_id = request.POST.get('api_pet_id', '')

    # redirect to index if there's no pet id
    if not api_pet_id:
        return redirect('index')

    # save pet as a user's favorite
    current_user = request.user
    pet = Pet.objects.create(api_pet_id=api_pet_id, user=current_user)

    return redirect('pets_show', api_pet_id)


@login_required
def pets_delete(request):
    # redirect to index if no pet id in request
    api_pet_id = request.POST.get('api_pet_id', '')
    if not api_pet_id:
        return redirect('index')

    # delete user's favorited pet
    current_user = request.user
    Pet.objects.filter(api_pet_id=api_pet_id, user=current_user).delete()

    return redirect('pets_show', api_pet_id)


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)
