import random

from django.db import models
from django.utils.text import slugify


class CommomM(models.Model):
    
    slug = models.SlugField(max_length=225, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    
    def generate_unique_slug(self):
        slug = slugify(self.name)
        
        if (self.__class__.objects.filter(slug = slug).exists()):
            number = random.randint(10000,99999)
            slug = slug + str(number)

        return slug

    

class Category(CommomM):
    name = models.CharField(max_length=20, blank=True, null=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE, related_name='children',blank=True,null=True)
    description = models.TextField()
    level = models.PositiveIntegerField(null=True, blank=True, default=0)

    def save(self, *args, **kwargs):
        
        if self.parent:
            parent_level = Category.objects.get(name = self.parent).level
            self.level = parent_level + 1
        else:
            self.level = 1
        super().save(*args,**kwargs)


    # def get_level(self):
    #     level = 0
    #     if ca



class BasicProuctDetails(CommomM):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name= "product")
    name = models.CharField(max_length=20, blank=True, null=True)
    total_stock = models.PositiveIntegerField()
    

    def __str__(self):
        return str(self.name)
    

class ImagesM(CommomM):
    product = models.ForeignKey(BasicProuctDetails, on_delete=models.CASCADE, related_name="images")
    images = models.ImageField()

    def __str__(self):
        return self.product
    

class productSpecification(CommomM):
    product = models.ForeignKey(BasicProuctDetails, on_delete=models.CASCADE, related_name="spec")
    specification_heading = models.CharField(max_length=40, null=True, blank=True)
    key = models.CharField(max_length=250, null = True, blank =True)
    related_texts = models.TextField()

    def __str__(self):
        return str(self.product)


class Description(CommomM):
    product = models.ForeignKey(BasicProuctDetails, on_delete=models.CASCADE, related_name="desc")
    image = models.ImageField()
    related_text = models.TextField()

    def __str__(self):
        return self.product


class Reviews(CommomM):
    product = models.ForeignKey(BasicProuctDetails, on_delete=models.CASCADE, related_name="review")
    rating_choices = {
        1 : "One Star",
        2 : "Two Star",
        3 : "Three Star",
        4 : "Four Star",
        5 : "Five Star",
    }
    rating = models.IntegerField(choices=rating_choices, default= None)
    reviews = models.CharField(max_length=50, blank=True,null=True)

    def __str__(self):
        return self.product


    