import decimal
from gettext import ngettext
from pyexpat.errors import messages

from django.contrib import admin
from .models import Topic, Course, Student, Order, Review


# Register your models here.
def make_disc(modeladmin, request, queryset):
    for obj in queryset:
        obj.price = obj.price - decimal.Decimal(obj.price) * decimal.Decimal('0.1')
        obj.save()


class CourseAdmin(admin.ModelAdmin):
    fields = [('title', 'topic'), ('price', 'num_reviews', 'for_everyone')]
    list_display = ('title', 'topic', 'price')
    actions = [make_disc]
    make_disc.short_description = "Update selected Courses with 10%% discount"

    class Meta:
        model = Course


class OrderAdmin(admin.ModelAdmin):
    fields = ['courses', ('student', 'order_status', 'order_date')]
    list_display = ('id', 'student', 'order_status', 'order_date', 'total_items', 'total_cost')


class CourseInline(admin.TabularInline):
    model = Course


class TopicAdmin(admin.ModelAdmin):
    inlines = [CourseInline]
    fields = [('name', 'length')]
    list_display = ('name', 'length')


class StudentAdmin(admin.ModelAdmin):
    fields = [('first_name', 'last_name', 'level', 'registered_courses', 'student_Img')]
    list_display = ('first_name', 'last_name', 'level', 'get_courses')

    def get_courses(self, obj):
        return ", ".join([p.title for p in obj.registered_courses.all()])

    get_courses.short_description = "Registered Courses"


# admin.site.register(Topic)
# admin.site.register(Course)
# admin.site.register(Student)
# admin.site.register(Order)
admin.site.register(Course, CourseAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Review)
