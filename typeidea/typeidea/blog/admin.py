from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Post, Category,Tag
# Register your models here.

class PostInline(admin.TabularInline):
	fields = ('title','desc')
	extra = 1
	model = Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	inlines = [PostInline,]
	lsit_display = ('name','status','is_nav','creat_time','post_count')
	fields = ('name','status','is_nav')

	def save_model(self,request,obj,form,change):
		obj.owner = request.user
		return super(CategoryAdmin,self).save_model(request,obj,form,change)

	def __str__(self):
		return self.name
	
	def post_count(self,obj):
		return obj.post_set.count()
	post_count.short_description='文章数量'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	lsit_display =('name','status','creat_time')
	fields = ('name','status')

	def save_model(self,request,obj,form,change):
		obj.owner=request.user
		return super(TagAdmin,self).save_model(request,obj,form,change)

	def __str__(self):
		return self.name

class CategoryOwnerFilter(admin.SimpleListFilter):
	title = '分类过滤器'
	parameter_name = 'owner_category'

	def lookups(self,request,models_admin):
		return Category.objects.filter(owner=request.user).values_list('id','name')

	def queryset(self,request,queryset):
		category_id =self.value()
		if category_id:
			return queryset.filter(category_id=self.value())
		return queryset

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	lsit_display = ['title','category','status','creat_time','operator']
	lsit_display_links = []
	list_filter = [CategoryOwnerFilter]
	search_fields = ['title','category__name']
	exclude = ('owner',)

	action_on_top = True
	action_on_bottom = True

	save_on_top = True

	fieldsets = (
		('基础配置',{
			'description':'基础配置描述',
			'fields':(
				('title','category'),
				'status',
			),
		}),
		('内容',{
			'fields':(
				'desc',
				'content',
				),
			}),
		('额外信息',{
			'classes':('collapse',),
			'fields':('tag',),
			}),
		)

	def operator(self,obj):
		return format_html(
			'<a href="{}">编辑</a>',
			reverse('admin:blog_post_change',args=(obj.id,))
			)
	operator.short_description = '操作'

	def save_model(self,request,obj,form,change):
		obj.owner =request.user
		return super(PostAdmin,self).save_model(request,obj,form,change)

	def get_queryset(self,request):
		qs = super(PostAdmin,self).get_queryset(request)
		return qs.filter(owner=request.user)

	def __str__(self):
		return self.title

	class PostAdmin(admin.ModelAdmin):
		class Media:
			css = {
			'all':("http://cdn.bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css",),
			}
			js = ('http://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js',)