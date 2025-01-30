from django.urls import path
from apps.laundryApp.views import *

urlpatterns = [
	path("admin/", admin_dashboard, name="admin_dashboard"),
	path("admin/member", admin_member, name="admin_member"),
	path("admin/outlet", admin_outlet, name="admin_outlet"),
	path("admin/paket-cucian", admin_paket_cucian, name="admin_paket_cucian"),
	path("admin/regis-pelanggan", admin_regis_pelanggan, name="admin_regis_pelanggan"),
	path("admin/transaksi", admin_transaksi, name="admin_transaksi"),
	path("admin/pengguna", admin_pengguna, name="admin_pengguna"),
 
 path('kasir/dashboard', kasir_dashboard, name='kasir_dashboard'),
 path('kasir/member', kasir_member, name='kasir_member'),
 path('kasir/transaksi', kasir_transaksi, name='kasir_transaksi'),
 path('kasir/paket-cucian', kasir_paket_cucian, name='kasir_paket_cucian'),
 path('kasir/transaksi', kasir_transaksi, name='kasir_transaksi_detail'),
 path('kasir/regis-pelanggan', kasir_regis_pelanggan, name='kasir_regis_pelanggan'),
 
 
 path('owner/dashboard/', owner_dashboard, name='owner_dashboard'),
 path('owner/cetak-laporan/', cetak_laporan, name='cetak_laporan'),
 
 
 
 
 
 path('get_paket/', get_paket, name='get_paket'),
 path('get_outlet/', get_outlet, name='get_outlet'),
 
 
 path('', login_view, name='login'),
 path('logout/', logout_view, name='logout'),
]
