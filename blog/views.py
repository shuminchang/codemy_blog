from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Category, Comment
from .forms import PostForm, EditForm, CommentForm
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Q

# def home(request):
#     return render(request, 'home.html', {})

def LikeView(request, slug):
    post = get_object_or_404(Post, slug=request.POST.get('post_slug'))
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('article-detail', args=[slug]))

class HomeView(ListView):
    model = Post
    template_name = 'home.html'
    # ordering = ['-id']   order by id in descending order
    ordering = ['-post_date']
    paginate_by = 5

    def get_context_data(self, *args, **kwargs):
        cat_menu = Category.objects.all()
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context["cat_menu"] = cat_menu
        return context

## Unsuccess to paginate function-based CategoryView, so switch to class-based
# def CategoryView(request, cats):
#     category_posts = Post.objects.filter(category=cats.replace('-', ' '))
#     paginator = Paginator(category_posts, 2)  # Show 2 posts per page.

#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     context = {
#         'cats': cats.title().replace('-', ' '), 
#         'category_posts': category_posts, 
#         "page_obj": page_obj
#     }

#     return render(request, 'categories.html', context)

class CategoryView(ListView):
    template_name = 'categories.html'
    context_object_name = 'category_posts'
    paginate_by = 5

    def get_queryset(self):
        cats = self.kwargs['cats'].replace('-', ' ')
        return Post.objects.filter(category=cats)

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        cats = self.kwargs['cats'].title().replace('-', ' ')
        context['cats'] = cats
        return context

def CategoryListView(request):
    cat_menu_list = Category.objects.all()
    return render(request, 'category_list.html', {'cat_menu_list': cat_menu_list})

class ArticleDetailView(DetailView):
    model = Post
    template_name = 'article_details.html'

    def get_object(self):
        return get_object_or_404(Post, slug=self.kwargs['slug'])

    def get_context_data(self, *args, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(*args, **kwargs)
        cat_menu = Category.objects.all()

        # Use the object provided by "get_object"
        stuff = self.get_object()
        total_likes = stuff.total_like()

        liked = False
        if stuff.likes.filter(id=self.request.user.id).exists():
            liked = True

        context["cat_menu"] = cat_menu
        context["total_likes"] = total_likes
        context["liked"] = liked
        # https://stackoverflow.com/questions/60497516/django-add-comment-section-on-posts-feed
        # ask chatgpt: modify the function-based view to class-based view
        # context['comments'] = self.object.comments.filter(active=True)  # will get error about don't have "active" argument
        context["comment_form"] = CommentForm()
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()                     # retrieves the current object (a Post object) based on the URL parameters.
        comment_form = CommentForm(request.POST)            # creates an instance of the CommentForm form, populating it with the data submitted in the POST request.
        if comment_form.is_valid():                         # checks if the submitted form data is valid.
            new_comment = comment_form.save(commit=False)   # a new comment object is created but not saved to the database yet
            new_comment.post = self.object                  # The current post object is assigned to the comment's post field.
            new_comment.save()                              # The comment is then saved to the database.
        return self.get(self, request, *args, **kwargs)     #  the view is refreshed using the get method, ensuring that the updated context data is retrieved and the page is rendered with the new comment.
        """
        - return self.get(self, request, *args, **kwargs)) is not the recommended way to handle form submissions in class-based views. 
        - Instead, you might want to consider using Django's built-in FormMixin and ProcessFormView 
        - for handling form submissions in a cleaner and more structured way.
        """

class AddPostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'add_post.html'
    # fields = '__all__'
    # fields = ('title', 'body')

class AddCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'add_comment.html'
    # fields = '__all__'
    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)
    
    success_url = reverse_lazy('home')

class AddCategoryView(CreateView):
    model = Category
    # form_class = PostForm
    template_name = 'add_category.html'
    fields = '__all__'

class UpdatePostView(UpdateView):
    model = Post
    form_class = EditForm
    template_name = 'update_post.html'
    # fields = ['title', 'title_tag', 'body']

class DeletePostView(DeleteView):
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('home')

def SearchArticles(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        if not searched:
            posts = Post.objects.none()
            message = 'You Forgot To Search For a Venue'
        else:
            posts = Post.objects.filter(
                Q(title__icontains=searched) | Q(body__icontains=searched)
            )
            message = ''
        return render(request, 'search_articles.html', {'searched': searched, 'posts': posts, 'message': message})
    else:
        return render(request, 'search_articles.html', {})
