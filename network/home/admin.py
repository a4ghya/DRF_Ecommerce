from django.contrib import admin
from home.models import CommomM, productSpecification,BasicProuctDetails,Category, Description,ImagesM, Reviews
#from users.models import EndUsers_LogInfo

# Register your models here.
#admin.site.register(CommomM)

class AdminSite(admin.AdminSite):
    site_header = "Admin Adminstration"
    
admin.site.register(productSpecification)
admin.site.register(BasicProuctDetails)
admin.site.register(Category)
admin.site.register(Description)
admin.site.register(ImagesM)
admin.site.register(Reviews)
#admin.site.register(EndUsers_LogInfo)


  # I. making a custom site
class CustomSellerSite(admin.AdminSite):
    site_header = "Seller Site"

seller_site = CustomSellerSite(name = "seller") # II. instance of the site class , with url as name

# seller_site.register(BasicProuctDetails,productSpecification,Category,Description,ImagesM,Reviews)

@admin.register(BasicProuctDetails,productSpecification,Category,Description,ImagesM,Reviews, site =seller_site )  # IV. registering the models and specifying for which site.
class SellerAdmin(admin.ModelAdmin):  # III. making a modeladmin class
    pass