import datetime
from django.shortcuts import render
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Count, Q
from django.core.cache import cache
from django.core.paginator import Paginator

from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data
from blog.models import Blog,BlogType



def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = timezone.now().date() - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today,read_details__date__gte=date)\
              .values('id','title')\
              .annotate(read_num_sum=Sum('read_details__read_num'))\
              .order_by('-read_num_sum')
    return blogs[:7]

def home(request):
    countent_type = ContentType.objects.get_for_model(Blog)
    dates,readnums = get_seven_days_read_data(countent_type)

    #获取7天热门博客缓存数据
    hot_blogs_for_7_days = cache.get('hot_blogs_for_7_days')
    if hot_blogs_for_7_days == None:
        hot_blogs_for_7_days = get_7_days_hot_blogs()
        cache.set('hot_blogs_for_7_days', hot_blogs_for_7_days, 3600)

    context = {}
    context['blogs_count'] = Blog.objects.count()
    context['categories_count'] = BlogType.objects.count()
    context['blog_types'] = BlogType.objects.annotate(blogs_count=Count('blog')).order_by('-blogs_count')
    context['read_nums'] = readnums
    context['dates'] = dates
    context['today_hot_data'] = get_today_hot_data(countent_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(countent_type)
    context['hot_blogs_for_7_days'] = hot_blogs_for_7_days

    return render(request,'home.html',context)

def search(request):
    search_words = request.GET.get('wd', '').strip()
    condition = None
    for word in search_words.split(' '):
        if condition is None:
            condition = Q(title__icontains=word)
        else:
            condition = condition | Q(title__icontains=word)

    search_blogs = []
    if condition != None:
        search_blogs = Blog.objects.filter(condition)

    page_num = request.GET.get('page',1) #获取页码参数
    paginator = Paginator(search_blogs, 10) #每20页进行分页
    page_of_blogs = paginator.get_page(page_num) #获得页码对应的页
    
    context = {}
    context['search_words'] = search_words
    context['page_of_blogs'] = page_of_blogs
    context['search_blogs_count'] = search_blogs.count()
    return render(request, 'search.html', context)