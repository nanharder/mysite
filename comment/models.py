import threading
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

class SendEmail(threading.Thread):
    def __init__(self,subject,text,email):
        self.subject = subject
        self.text = text
        self.email = email 
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject,self.text,settings.EMAIL_HOST_USER,[self.email])
        msg.content_subtype = "html"
        msg.send()
        
        
class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="comments",on_delete=models.CASCADE)
    
    root = models.ForeignKey('self',related_name="root_comment",null =True,on_delete =models.CASCADE)
    parent = models.ForeignKey('self',related_name="parent_comment",null =True,on_delete =models.CASCADE)
    reply_to = models.ForeignKey(User,null=True,related_name="replies", on_delete=models.CASCADE)
    
    def __str__(self):
        return self.text

    def send_mail(self):
        #发送邮件通知
        if self.parent is None:
            #评论博客
            subject = '有人评论你的博客'
            email = self.content_object.get_email()

        else:
            #回复评论
            subject = '有人回复你的评论'            
            email = self.reply_to.email

        if email != '':
            context = {}
            context['text'] = self.text
            context['url'] =  self.content_object.get_url() 
            text = render_to_string('comment/send_email.html', context)                        
            send_mail = SendEmail(subject,text,email)
            send_mail.start()

    class Meta:
        ordering = ['comment_time']

