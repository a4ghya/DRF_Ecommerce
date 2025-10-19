from rest_framework import serializers
from home.models import CommomM, productSpecification,BasicProuctDetails,Category, Description,ImagesM, Reviews

class CommonS(serializers.Serializer):
    slug = serializers.slugField(max_length=225, allow_blank = True)
    created_at = serializers.DateTimeField(auto_now_add =True)
    updated_at = serializers.DateTimeField(auto_now =True)

    class Meta:
        read_only_fields = ['slug','created_at','updated_at' ]


class CategoryS(CommonS, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'parent','description','level','slug','created_at','updated_at']
        read_only_fields = ['slug','created_at','updated_at' ]

class BasicProuctDetailsS(CommonS, serializers.ModelSerializer):
    class Meta:
        model = BasicProuctDetails
        fields = ['category','name','total_stock','slug','created_at','updated_at']
        read_only_fields = ['slug','created_at','updated_at' ]

class ImageS(CommonS, serializers.ModelSerializer):
    class Meta:
        model = ImagesM
        fields = ['product','image','slug','created_at','updated_at']
        read_only_fields = ['slug','created_at','updated_at' ]

class productSpecificationS(CommonS, serializers.ModelSerializer):
    class Meta:
        model = productSpecification
        fields = ['product','specification_heading','key','related_texts','slug','created_at','updated_at']
        read_only_fields = ['slug','created_at','updated_at' ]

class DescriptionS(CommonS, serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = ['product','image','realted_text','slug','created_at','updated_at' ]
        read_only_fields = ['slug','created_at','updated_at' ]

class ReviewsS(CommonS, serializers.ModelSerializer):
    class Meta:
        model =Reviews
        fields = ['product', 'rating','reviews','slug','created_at','updated_at']
        read_only_fields = ['slug','created_at','updated_at' ]
    