from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.unregister(Group)
admin.site.register(User)
admin.site.register(Member)
admin.site.register(Outlet)
admin.site.register(Paket)
admin.site.register(Transaksi)
admin.site.register(DetailTransaksi)
admin.site.register(Pelanggan)
