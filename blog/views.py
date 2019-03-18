from django.shortcuts import get_object_or_404,render
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType

from .models import Blog,BlogType
from read_statistics.utils import read_statistics_once


def get_blog_list_common_data(request, blogs_all_list):
    page_num = request.GET.get('page',1) #获取页码参数
    paginator = Paginator(blogs_all_list, settings.NUM_OF_BLOGS_EACH_PAGE) #每2页进行分页
    page_of_blogs = paginator.get_page(page_num) #获得页码对应的页
    current_page = page_of_blogs.number 
    page_range = list(range(max(current_page-2,1),min(paginator.num_pages+1,current_page+3))) #获取页码范围
    # 添加省略号
    if page_range[0] - 1 > 1:
        page_range.insert(0,'...')
    if page_range[-1] + 1 < paginator.num_pages:
        page_range.append('...')   
    # 添加省略页码
    if page_range[0] != 1:
        page_range.insert(0,1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    # 添加日期归档数目
    blog_dates = Blog.objects.dates('created_time','month','DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count
    
    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = BlogType.objects.annotate(blogs_count=Count('blog'))
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)   
    return render(request,'blog/blog_list.html',context)

def blog_detail(request,blog_pk):   
    blog = get_object_or_404(Blog,id=blog_pk)
    read_cookie_key = read_statistics_once(request,blog)

    context = {}
    context['previous_blog'] = Blog.objects.filter(created_time__gt = blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt = blog.created_time).first()
    context['blog'] = blog   
    response = render(request,'blog/blog_detail.html',context)
    response.set_cookie(read_cookie_key,'true',max_age = 60)
    return response

def blogs_with_type(request, blogs_type_pk):
    blog_type = get_object_or_404(BlogType, pk = blogs_type_pk)  
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render(request,'blog/blogs_with_type.html',context)

def blogs_with_date(request, year, month):  
    blogs_all_list = Blog.objects.filter(created_time__year = year, created_time__month = month)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year, month)
    return render(request,'blog/blogs_with_date.html',context)




