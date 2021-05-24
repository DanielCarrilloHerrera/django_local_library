import datetime

from django.shortcuts import render
from django.views import generic
from catalog.models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

#from catalog.forms import RenewBookForm
from catalog.forms import RenewBookModelForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.models import Author
from django.http import HttpResponseForbidden
# Create your views here.

def index(request):
    """View function for home page of site."""

    #Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    #The 'all()' is implied by default.
    num_authors = Author.objects.count()

    #Genres that contain a particular word
    num_genres_particular_word = Genre.objects.filter(name__icontains='p').count()

    #Books that contain a particular word
    num_books_particular_word = Book.objects.filter(title__icontains='o').count()

    #Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres_particular_word': num_genres_particular_word,
        'num_books_particular_word': num_books_particular_word,
        'num_visits': num_visits        
    }

    # Render the HTML template index.html with the data in the context variables
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 5
    #context_object_name = 'my_book_list' # your own name for the list as a template variable
    #queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the titlw war
    #template_name = 'books/my_arbitrary_template_name_list.html'# Specify your own template name/location

    def get_queryset(self):
        #return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
        return Book.objects.all()
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context["some_data"] = 'This is just some data'
        return context

class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan."""
    model = BookInstance
    permission_required = 'catalog.can_see_borrowed'
    context_object_name = 'bookinstance_list_borrowed'
    template_name = 'catalog/book_instance_list_all_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.all().filter(status__exact='o').order_by('due_back')
    

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/book_instance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AuthorListView(generic.ListView):
    model = Book
    paginate_by = 5
    #context_object_name = 'my_author_list' # your own name for the list as a template variable
    #queryset = Author.objects.filter(title__icontains='war')[:5] # Get 5 books containing the titlw war
    #template_name = 'authors/my_arbitrary_template_name_list.html'# Specify your own template name/location

    def get_queryset(self):
        #return Author.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
        return Author.objects.all()
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(AuthorListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context["some_data"] = 'This is just some data'
        return context

class BookDetailView(generic.DetailView):
    model = Book

class AuthorDetailView(generic.DetailView):
    model = Author


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (bindind):
        #form = RenewBookForm(request.POST)
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            #book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    #If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        #form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = 'catalog.can_manage_authors'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = 'catalog.can_manage_authors'
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = 'catalog.can_manage_authors'
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = 'catalog.can_manage_books'
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = 'catalog.can_manage_books'
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = 'catalog.can_manage_books'
    success_url = reverse_lazy('books')

    def delete(self, request, *args, **kwargs):
        
        self.object = self.get_object()

        # check if book has instances on loan
        if self.object.bookinstance_set.filter(status__exact='o').exists():
            return HttpResponseForbidden('This book has instances on loan. Cannot be deleted.')

        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)