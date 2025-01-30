from django.shortcuts import render, redirect
from django.http import JsonResponse
from apps.laundryApp.models import Paket, Outlet
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib import messages

def landing_page(request):
    data_laundry = [
      {
        'id': 1,
        'nama': 'hafiz',
        'alamat': 'jalan raya',
        'no_hp': '081234567890',
        'email': 'hafiz@gmail.com', 
        'password': '1234567890',
        'jenis_laundry': 'cuci kering',
        'harga': '10000',
        'status': 'pending',
        'tanggal': '2025-01-01',
        'jam': '10:00',
      },
      {
        'id': 2, 
        'nama': 'budi',
        'alamat': 'jalan sudirman',
        'no_hp': '081234567891',
        'email': 'budi@gmail.com',
        'password': '1234567891', 
        'jenis_laundry': 'cuci basah',
        'harga': '15000',
        'status': 'selesai',
        'tanggal': '2025-01-02',
        'jam': '11:00',
      },
      {
        'id': 3,
        'nama': 'ani',
        'alamat': 'jalan thamrin',
        'no_hp': '081234567892',
        'email': 'ani@gmail.com',
        'password': '1234567892',
        'jenis_laundry': 'setrika',
        'harga': '8000',
        'status': 'proses',
        'tanggal': '2025-01-03', 
        'jam': '12:00',
      }
    ]
    
    kolom_table = ['id', 'nama', 'alamat', 'no_hp']
    
    data_paket = [
      {
        'id': 1,
        'nama_paket': 'cuci kering',
        'harga': '10000',
      },
      {
        'id': 2,
        'nama_paket': 'cuci basah',
        'harga': '15000',
      },
      {
        'id': 3,
        'nama_paket': 'setrika',
        'harga': '8000',
      },
      {
        'id': 4,
        'nama_paket': 'lainnya',
        'harga': '10000',
      }
    ]
    
    kolom_table_paket = ['id', 'nama_paket', 'harga']
    
    detail_config_laundry = {
        'fields': ['id', 'nama', 'alamat', 'no_hp', 'email', 'jenis_laundry', 'harga', 'status', 'tanggal', 'jam'],
        'labels': {
            'id': 'ID:',
            'nama': 'Nama Lengkap:',
            'alamat': 'Alamat Lengkap:',
            'no_hp': 'Nomor Handphone:',
            'email': 'Alamat Email:',
            'jenis_laundry': 'Jenis Layanan:',
            'harga': 'Harga Layanan:',
            'status': 'Status Pesanan:',
            'tanggal': 'Tanggal Pesanan:',
            'jam': 'Waktu Pesanan:'
        },
        'groups': {
            'Informasi Pelanggan:': ['nama', 'alamat', 'no_hp', 'email'],
            'Detail Pesanan:': ['jenis_laundry', 'harga', 'status'],
            'Waktu:': ['tanggal', 'jam']
        }
    }
    
    detail_config_paket = {
        'fields': ['id', 'nama_paket', 'harga'],
        'labels': {
            'id': 'ID Paket:',
            'nama_paket': 'Nama Paket Layanan:',
            'harga': 'Harga Paket:'
        },
        'groups': {
            'Informasi Paket:': ['nama_paket', 'harga']
        }
    }
    
    context = {
        'table_column_laundry': kolom_table,
        'table_data_laundry': data_laundry,
        'table_column_paket': kolom_table_paket,
        'table_data_paket': data_paket,
        'detail_config_laundry': detail_config_laundry,
        'detail_config_paket': detail_config_paket
    }
    
    return render(request, 'landing_page.html', context)
  
  
@require_http_methods(['GET'])
def get_paket(request):
    # Ambil paket beserta data outlet yang berelasi
    paket_list = []
    pakets = Paket.objects.exclude(detailtransaksi__isnull=False).select_related('outlet')
    
    for paket in pakets:
        paket_data = {
            'id': paket.id,
            'nama_paket': paket.nama_paket,
            'jenis': paket.jenis,
            'harga': paket.harga,
            'created_at': paket.created_at,
            'updated_at': paket.updated_at,
            'outlet': {
                'id': paket.outlet.id,
                'nama': paket.outlet.nama
            }
        }
        paket_list.append(paket_data)
    
    return JsonResponse({'paket': paket_list})
  
@require_http_methods(['GET'])
def get_outlet(request):
    outlet = Outlet.objects.all()
    return JsonResponse({'outlet': list(outlet.values())})

def login_view(request):
    # Redirect jika user sudah login
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'kasir':
            return redirect('kasir_dashboard')
        elif request.user.role == 'owner':
            return redirect('owner_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        if not username or not password:
            messages.error(request, 'Username dan password harus diisi!')
            return render(request, 'page/login.html')
            
        try:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Set session expiry berdasarkan remember me
                    if not remember_me:
                        request.session.set_expiry(0)
                    
                    messages.success(request, f'Selamat datang kembali, {user.username}!')
                    
                    # Redirect berdasarkan role
                    if user.role == 'admin':
                        return redirect('admin_dashboard')
                    elif user.role == 'kasir':
                        return redirect('kasir_dashboard')
                    elif user.role == 'owner':
                        return redirect('owner_dashboard')
                else:
                    messages.error(request, 'Akun Anda telah dinonaktifkan!')
            else:
                messages.error(request, 'Username atau password salah!')
                
        except Exception as e:
            messages.error(request, 'Terjadi kesalahan saat login. Silakan coba lagi!')
            
    return render(request, 'page/login.html')
  
def logout_view(request):
    # Hapus sesi user
    request.session.flush()
    
    # Logout user
    from django.contrib.auth import logout
    logout(request)
    
    # Tampilkan pesan sukses
    messages.success(request, 'Anda berhasil logout!')
    
    # Redirect ke halaman login
    return redirect('login')
