from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from .models import LikeCount,LikeRecord


def ErrorResponse(code,message):
    data = {}
    data['code'] = code
    data['status'] = 'ERROR'
    data['message'] = message
    return JsonResponse(data)

def SuccessResponse(like_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = like_num
    return JsonResponse(data)

def like_change(request):
    #获取数据
    user = request.user
    if not user.is_authenticated:
        return ErrorResponse(400,'You have not logined')

    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401,'objext does not exist')

    #判断是否点赞
    if request.GET.get('is_like') == 'true':
        # 要点赞
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type,object_id=object_id,user=user)
        if created:
        #未点赞过，进行点赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type,object_id=object_id)
            like_count.like_num += 1
            like_count.save()
            return SuccessResponse(like_count.like_num)
        else:
        #已点赞过，不能重复点赞
           return ErrorResponse(402,'You have liked this object')
            
        
    else:
    #取消点赞
        if LikeRecord.objects.filter(content_type=content_type,object_id=object_id,user=user).exists():
            like_record = LikeRecord.objects.get(content_type=content_type,object_id=object_id,user=user)
            like_record.delete()
        #删除点赞记录
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type,object_id=object_id)
            if not created:
        #点赞计数已存在
                like_count.like_num -= 1
                like_count.save()
                return SuccessResponse(like_count.like_num)
            else:
                return ErrorResponse(404,'Data error')
        else:
        #还没有点过赞
            return ErrorResponse(403,'You have not liked this object')


