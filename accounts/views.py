from django.contrib.auth import login as auth_login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.http import HttpResponseRedirect
from .forms import SignUpForm, CustomAuthenticationForm, UserForm
from .models import User

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def my_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    #Cuando se comete un error en el login se repinta con un login mas grande
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})
   
@login_required
def UserPreferences(request):
    form = "hola mundo"
    return render(request, 'accounts/preferences.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    template_name = 'accounts/my_account.html'
    context_object_name = 'user'
    form_class = UserForm
    success_url = reverse_lazy('my_account')
    """
    ----------------------------------------------------------
        funciones de la clase
    ----------------------------------------------------------
    """
    def get_object(self, queryset=None):
        #funcion calve para identificar al usuario
        return self.request.user

    def get_context_data(self, **kwargs):
        #recuperamos argumentos ya inicializados
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        print (context)
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        return self.render_to_response(context=context)

    def post(self, request, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST)
        if all([form.is_valid()]):
            """
                               Tratamiento del Usuario
            .........................................................
            
            """
            self.object.first_name = form.cleaned_data['first_name']
            self.object.last_name = form.cleaned_data['last_name']
            self.object.email = form.cleaned_data['email']
            self.object.birth_date = form.cleaned_data['birth_date']
            self.object.bio = form.cleaned_data['bio']
            self.object.location = form.cleaned_data['location']

            self.object.save()
            return redirect('my_account')
        else:
            return self.render_to_response(
              self.get_context_data(form=form))
  
