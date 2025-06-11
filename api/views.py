from rest_framework import generics, mixins, viewsets, permissions, status
from django.shortcuts import render, get_object_or_404
from rest_framework import serializers
from .models import Guide, News, Event, Comment, Favorite, UserProfile, User
from .serializers import GuideSerializer, NewsSerializer, EventSerializer, CommentSerializer, FavoriteSerializer, UserSerializer, RegisterSerializer, PasswordChangeSerializer, LoginSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.decorators import method_decorator
#from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, LoginForm, GuideForm, NewsForm, EventForm
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from rest_framework.parsers import JSONParser
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.contrib import messages
from rest_framework.views import APIView




class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'  # по умолчанию, можно оставить так или изменить

    def get(self, request, *args, **kwargs):
        # Получаем объект пользователя по pk
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        # Можно вернуть HTML-форму для регистрации
        form = RegisterForm()
        return render(request, 'log_reg/register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        if 'text/html' in accept:
            # Обработка формы для HTML
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                # Можно выполнить логин или перенаправление
                return redirect('some-view-name')
            else:
                print(form.errors)
                return render(request, 'log_reg/register.html', {'form': form})
        else:
            # Обработка JSON-запроса
            data = JSONParser().parse(request)
            serializer = RegisterSerializer(data=data)
            if serializer.is_valid():
                User.objects.create_user(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password']
                )
                return JsonResponse({'status': 'success'}, status=201)
            else:
                return JsonResponse(serializer.errors, status=400)


def register_view(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'log_reg/register.html', {'form': form})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('news-list')
        else:
            print(form.errors)
        return render(request, 'log_reg/register.html', {'form': form})

def login_view(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'log_reg/login.html', {'form': form})
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('news-list')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
        # Если форма не валидна или аутентификация не прошла
        return render(request, 'log_reg/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('news-list')


class PasswordChangeAPIView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Возвращаем текущего пользователя
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()

        # Проверяем правильность старого пароля
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Неверный пароль.'}, status=status.HTTP_400_BAD_REQUEST)

        # Устанавливаем новый пароль
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'detail': 'Пароль успешно изменён.'}, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return render(request, 'log_reg/login.html')

    def post(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        if 'text/html' in accept:
            username = request.POST.get('username')
            password = request.POST.get('password')
        else:
            data = JSONParser().parse(request)
            serializer = LoginSerializer(data=data)
            if not serializer.is_valid():
                return JsonResponse(serializer.errors, status=400)
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if 'text/html' in accept:
                return redirect('some-view-name')  # замените на нужное имя маршрута
            else:
                return JsonResponse({'status': 'success'}, status=200)
        else:
            if 'text/html' in accept:
                form = {'username': username, 'password': password, 'error': 'Неверные данные'}
                return render(request, 'log_reg/login.html', {'form': form})
            else:
                return JsonResponse({'error': 'Неверные данные'}, status=400)

class CommentAPIView(APIView):
    def get(self, request, pk=None):
        if request.accepts('application/json'):
            if pk:
                comment = get_object_or_404(Comment, pk=pk)
                serializer = CommentSerializer(comment)
                return Response(serializer.data)
            else:
                comments = Comment.objects.all()
                serializer = CommentSerializer(comments, many=True)
                return Response(serializer.data)
        else:
            # Для обычных запросов — рендерим HTML
            if pk:
                comment = get_object_or_404(Comment, pk=pk)
                return render(request, 'comments/comment_detail.html', {'comment': comment})
            else:
                comments = Comment.objects.all()
                return render(request, 'comments/comment_list.html', {'comments': comments})
            

class NewsListCreateAPIView(generics.ListCreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        if 'text/html' in accept:
            # Для HTML — отдаем шаблон
            news_items = self.get_queryset()
            return render(request, 'news/news_list.html', {'news_items': news_items})
        else:
            # Для JSON — стандартный ответ DRF
            return super().get(request, *args, **kwargs)


class NewsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        news_item = get_object_or_404(News, pk=kwargs['pk'])
        accept = request.headers.get('Accept', '')
        if 'text/html' in accept:
            form = NewsForm(instance=news_item)
            return render(request, 'news/news_edit.html', {'form': form, 'news_item': news_item})
        else:
            # Для JSON
            data = {
                #'id': news_item.id,
                'title': news_item.title,
                'content': news_item.content,
            }
            return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        # Обработка _method из формы
        method = request.POST.get('_method', '').upper()
        if method == 'PUT':
            return self.put(request, *args, **kwargs)
        elif method == 'DELETE':
            return self.delete(request, *args, **kwargs)
        else:
            # Обработка обычных POST-запросов, например создание новости или ошибка
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest("Unknown method")

    def put(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        news_item = get_object_or_404(News, pk=kwargs['pk'])
        if 'text/html' in accept:
            # Обработка формы для редактирования новости
            form = NewsForm(request.POST, instance=news_item)
            if form.is_valid():
                form.save()
                # После сохранения перенаправим на страницу новости
                return redirect('news-detail', pk=news_item.pk)
            else:
                # Если форма невалидна, возвращаем страницу с ошибками
                return render(request, 'news/news_edit.html', {'form': form, 'news_item': news_item})
        else:
            # Для JSON — можно реализовать API-обновление
            from django.http import JsonResponse
            import json
            data = json.loads(request.body)
            form = NewsForm(data, instance=news_item)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    def delete(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        news_item = get_object_or_404(News, pk=kwargs['pk'])
        if 'text/html' in accept:
            # Для HTML — подтверждение удаления (обычно делается через отдельную страницу)
            news_item.delete()
            return redirect('news-list')  # перенаправление на список новостей
        else:
            # Для JSON
            from django.http import JsonResponse
            news_item.delete()
            return JsonResponse({'status': 'deleted'})
        
# Веб-страница: список новостей
def news_list_view(request):
    news_items = News.objects.all()
    return render(request, 'news/news_list.html', {'news_items': news_items})

# Веб-страница: детальная новость
def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    return render(request, 'news/news_detail.html', {'news_item': news_item})

def edit_news(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news_item)
        if form.is_valid():
            print("Form is valid")
        else:
            print("Form errors:", form.errors)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('news-detail', pk=pk)
    else:
        form = NewsForm(instance=news_item)
    return render(request, 'news/news_edit.html', {'form': form, 'news_item': news_item})

class EventListCreateAPIView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        if 'text/html' in accept:
            # возвращаем HTML-страницу
            events = self.get_queryset()
            return render(request, 'events/event_list.html', {'events': events})
        else:
            # возвращаем JSON
            return super().get(request, *args, **kwargs)

class EventDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        event = get_object_or_404(Event, pk=kwargs['pk'])
        if 'text/html' in accept:
            return render(request, 'events/event_detail.html', {'event': event})
        else:
            # JSON ответ
            data = {
                'id': event.id,
                'title': event.title,
                'date': event.date,
                'description': event.description,
                # добавьте поля по необходимости
            }
            return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        # Обработка _method из формы
        method = request.POST.get('_method', '').upper()
        if method == 'PUT':
            return self.put(request, *args, **kwargs)
        elif method == 'DELETE':
            return self.delete(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest("Unknown method")

    def put(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        event = get_object_or_404(Event, pk=kwargs['pk'])
        if 'text/html' in accept:
            form = EventForm(request.POST, instance=event)
            if form.is_valid():
                form.save()
                return redirect('event-detail', pk=event.pk)
            else:
                return render(request, 'events/event_edit.html', {'form': form, 'event': event})
        else:
            # JSON API
            data = json.loads(request.body)
            form = EventForm(data, instance=event)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    def delete(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        event = get_object_or_404(Event, pk=kwargs['pk'])
        event.delete()
        if 'text/html' in accept:
            return redirect('event-list')  # или нужный вам URL
        else:
            return JsonResponse({'status': 'deleted'})
        
def event_list_view(request):
    events = Event.objects.all().prefetch_related('comments')
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})

def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event-detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_edit.html', {'form': form, 'event': event})

class GuideListCreateAPIView(generics.ListCreateAPIView):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer
    
    permission_classes = [permissions.AllowAny]
    #permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        if 'text/html' in accept:
            # Для HTML — рендерим шаблон
            guides = self.get_queryset()
            return render(request, 'guides/guide_list.html', {'guides': guides})
        else:
            # Для JSON — стандартный ответ DRF
            return super().get(request, *args, **kwargs)

class GuideDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        guide = get_object_or_404(Guide, pk=kwargs['pk'])
        if 'text/html' in accept:
            return render(request, 'guides/guide_detail.html', {'guide': guide})
        else:
            data = {
                'id': guide.id,
                'title': guide.title,
                'content': guide.content,
                # добавьте другие поля
            }
            return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        method = request.POST.get('_method', '').upper()
        if method == 'PUT':
            return self.put(request, *args, **kwargs)
        elif method == 'DELETE':
            return self.delete(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest("Unknown method")

    def put(self, request, *args, **kwargs):
        accept = request.headers.get('Accept', '')
        guide = get_object_or_404(Guide, pk=kwargs['pk'])
        if 'text/html' in accept:
            form = GuideForm(request.POST, instance=guide)
            if form.is_valid():
                form.save()
                return redirect('guide-detail', pk=guide.pk)
            else:
                return render(request, 'guides/guide_edit.html', {'form': form, 'guide': guide})
        else:
            data = json.loads(request.body)
            form = GuideForm(data, instance=guide)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    def delete(self, request, *args, **kwargs):
        guide = get_object_or_404(Guide, pk=kwargs['pk'])
        guide.delete()
        if 'text/html' in request.headers.get('Accept', ''):
            return redirect('guide-list')  # или другой URL
        else:
            return JsonResponse({'status': 'deleted'})

# Веб-страница для отображения всех гайдов
def guide_list_view(request):
    guides = Guide.objects.all()

    # Создаем список кортежей: (guide, first_comment)
    guides_with_comments = []
    for guide in guides:
        comments = guide.comments.all()  # все комментарии
        guides_with_comments.append((guide, comments))
    
    return render(request, 'guides/guide_list.html', {'guides_with_comments': guides_with_comments})

# Веб-страница для отображения конкретного гайда
def guide_detail(request, pk):
    guide = get_object_or_404(Guide, pk=pk)
    return render(request, 'guides/guide_detail.html', {'guide': guide})

def create_guide(request):
    if request.method == 'POST':
        form = GuideForm(request.POST, request.FILES)
        if form.is_valid():
            guide = form.save(commit=False)
            # Можно оставить author пустым или установить вручную
            guide.author = None  # или оставить так
            guide.save()
            return redirect(guide.get_absolute_url())
        else:
            print(form.errors)
    else:
        form = GuideForm()
    return render(request, 'guides/guide_form.html', {'form': form})



class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.AllowAny]  # Разрешить неавторизованным

    def get_queryset(self):
        # Можно ограничить выборку или оставить так
        return Favorite.objects.all()

    def perform_create(self, serializer):
        data = self.request.data

        # Получаем user_id из данных
        user_id = data.get('user_id')
        if user_id:
            user = get_object_or_404(User, pk=user_id)
        else:
            # Если не передан user_id, можно установить пользователя по умолчанию или ошибку
            # Например, создаем Favorite без пользователя (если модель позволяет)
            user = None

        content_type_name = data.get('content_type')  # например, 'guide', 'news', 'event'
        object_name = data.get('object_name')        # название объекта

        if not content_type_name or not object_name:
            raise serializers.ValidationError('content_type и object_name обязательны.')

        try:
            content_type = ContentType.objects.get(model=content_type_name.lower())
        except ContentType.DoesNotExist:
            raise serializers.ValidationError('Неверный тип контента.')

        model_class = content_type.model_class()

        # Ищем объект по названию
        obj = model_class.objects.filter(name=object_name).first()
        if not obj:
            raise serializers.ValidationError('Объект с таким названием не найден.')
        
        # Передаем в сериализатор
        serializer.save(
            user=user,
            content_type=content_type,
            object_id=obj.pk
        )

def user_favorites(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # Получение закладок пользователя
    favorites = Favorite.objects.filter(user=user).select_related('content_type')
    
    categorized_favorites = {
        'Guides': [],
        'News': [],
        'Events': [],
    }

    for fav in favorites:
        obj = fav.content_object
        if isinstance(obj, Guide):
            categorized_favorites['Guides'].append(obj)
        elif isinstance(obj, News):
            categorized_favorites['News'].append(obj)
        elif isinstance(obj, Event):
            categorized_favorites['Events'].append(obj)

    context = {
        'categorized_favorites': categorized_favorites,
        'viewed_user': user,
    }
    return render(request, 'favorites/user_favorites.html', context)


def remove_favorite(request, pk):
    favorite = get_object_or_404(Favorite, pk=pk, user=request.user)
    if request.method == 'POST':
        favorite.delete()
    return redirect('user_favorites')  


def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            # Crucial: Get the author from the form data
            author_id = form.cleaned_data['author_id']
            try:
                author = User.objects.get(pk=author_id)
            except User.DoesNotExist:
                return render(request, 'news/news_form.html', {'form': form, 'error_message': 'Пользователь не найден'})
            news = form.save(commit=False)
            news.author = author  # Set the author
            news.save()
            return redirect(news.get_absolute_url())
    else:
        form = NewsForm()
    return render(request, 'news/news_form.html', {'form': form})


def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)  # No FILES for events
        if form.is_valid():
            event = form.save()
            return redirect(event.get_absolute_url())  # Assuming you have get_absolute_url
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})


def profile_detail(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    return render(request, 'log_reg/profile_detail.html', {'profile': profile})







from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TestModel
from .serializers import TestModelSerializer



class TestModelListCreateAPIView(APIView):
    def get(self, request):
        # Получение списка всех объектов
        tests = TestModel.objects.all()
        serializer = TestModelSerializer(tests, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Создание нового объекта
        serializer = TestModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)