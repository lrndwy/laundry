from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from apps.laundryApp.models import Outlet, Transaksi, DetailTransaksi, Paket, Member, Pelanggan
import json
from django.db.models import Q
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.db.models import Sum, Count, Avg


User = get_user_model()

def is_admin(user):
    return user.role == 'admin'

def get_user_data(user=None):
    """Fungsi helper untuk mendapatkan data user untuk form"""
    if user:
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'outlet': user.outlet.id if user.outlet else None,
            'is_active': user.is_active
        }
    return None

# Admin Views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Filter tanggal
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    # Default 7 hari terakhir jika tidak ada filter tanggal
    if not start and not end:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)  # 6 hari sebelumnya untuk total 7 hari
        start = start_date.strftime('%Y-%m-%d')
        end = end_date.strftime('%Y-%m-%d')
    
    # Base queryset
    transaksi_qs = Transaksi.objects.filter(dibayar='dibayar')
    
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        transaksi_qs = transaksi_qs.filter(created_at__date__range=[start_date, end_date])
    except (ValueError, TypeError):
        # Jika format tanggal tidak valid, gunakan 7 hari terakhir
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        transaksi_qs = transaksi_qs.filter(created_at__date__range=[start_date, end_date])
        start = start_date.strftime('%Y-%m-%d')
        end = end_date.strftime('%Y-%m-%d')

    # Statistik Umum
    stats = {
        'total_pendapatan': transaksi_qs.aggregate(Sum('total_harga'))['total_harga__sum'] or 0,
        'total_transaksi': transaksi_qs.count(),
        'total_outlet': Outlet.objects.count(),
        'total_member': Member.objects.count(),
        'total_pelanggan': Pelanggan.objects.count(),
        'total_paket': Paket.objects.count(),
        'total_user': User.objects.count(),
    }
    
    # Statistik per Outlet
    outlet_stats = Outlet.objects.annotate(
        pendapatan=Sum('transaksi__total_harga', 
                      filter=models.Q(transaksi__dibayar='dibayar', 
                                    transaksi__created_at__date__range=[start_date, end_date])),
        jumlah_transaksi=Count('transaksi', 
                              filter=models.Q(transaksi__dibayar='dibayar',
                                            transaksi__created_at__date__range=[start_date, end_date])),
        rata_rata_transaksi=Avg('transaksi__total_harga', 
                               filter=models.Q(transaksi__dibayar='dibayar',
                                             transaksi__created_at__date__range=[start_date, end_date]))
    )

    # Buat list tanggal lengkap untuk rentang waktu yang dipilih
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    # Data untuk grafik dengan data harian
    daily_data = transaksi_qs.annotate(
        tgl=TruncDate('created_at')
    ).values('tgl').annotate(
        total=Count('id'),
        pendapatan=Sum('total_harga')
    ).order_by('tgl')

    # Convert queryset ke dictionary untuk akses lebih mudah
    transaksi_dict = {d['tgl']: {'total': d['total'], 'pendapatan': d['pendapatan']} for d in daily_data}

    # Format data untuk grafik dengan semua tanggal
    chart_data = {
        'labels': [],
        'pendapatan': [],
        'transaksi': []
    }

    for date in date_list:
        chart_data['labels'].append(date.strftime('%d %B %Y'))
        if date in transaksi_dict:
            chart_data['transaksi'].append(transaksi_dict[date]['total'])
            chart_data['pendapatan'].append(float(transaksi_dict[date]['pendapatan']))
        else:
            chart_data['transaksi'].append(0)
            chart_data['pendapatan'].append(0)

    context = {
        'stats': stats,
        'outlet_stats': outlet_stats,
        'chart_data': json.dumps(chart_data),
        'start_date': start,
        'end_date': end
    }
    
    return render(request, 'page/admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_member(request):
    member_id = None
    
    if request.method == 'POST':
      member_id = request.POST.get('member_id')
      
      member_data = {
        'nama_member': request.POST.get('nama_member'),
        'alamat': request.POST.get('alamat'),
        'telp': request.POST.get('telp')
      }
    
      if member_id:
        member = get_object_or_404(Member, id=member_id)
        for key, value in member_data.items():
          setattr(member, key, value)
        member.save()
        messages.success(request, 'Member berhasil diperbarui')
      else:
        Member.objects.create(**member_data)
        messages.success(request, 'Member berhasil ditambahkan')
        
      return redirect('admin_member')
    
    tambah = request.GET.get('tambah')
    if tambah:
      member_tambah = True
    else:
      member_tambah = False
      
    edit_id = request.GET.get('editId')
    member_edit = None
    if edit_id:
      member_edit = get_object_or_404(Member, id=edit_id)
      
    delete_id = request.GET.get('deleteId')
    if delete_id:
      member = get_object_or_404(Member, id=delete_id)
      member.delete()
      messages.success(request, 'Member berhasil dihapus')
      return redirect('admin_member')
    
    member_list = Member.objects.all()
    data_member = []
    for member in member_list:
      data_member.append({
        'id': member.id,
        'nama_member': member.nama_member,
        'alamat': member.alamat,
        'telp': member.telp
      })
      
    kolom_table_member = ['id', 'nama_member', 'alamat', 'telp']
    
    detail_config_member = {
      'fields': ['id', 'nama_member', 'alamat', 'telp'],
      'labels': {
        'id': 'ID:',
        'nama_member': 'Nama:',
        'alamat': 'Alamat:',
        'telp': 'No. HP:'
      }
    }
    
    context = {
      'table_data_member': data_member,
      'table_column_member': kolom_table_member,
      'detail_config_member': detail_config_member,
      'member_edit': member_edit,
      'member_tambah': member_tambah
    }
    return render(request, 'page/admin/member.html', context)

@login_required 
@user_passes_test(is_admin)
def admin_outlet(request):
    outlet_edit = None
    
    
    if request.method == 'POST':
        outlet_id = request.POST.get('outlet_id')
        
        outlet_data = {
          'nama': request.POST.get('nama'),
          'alamat': request.POST.get('alamat'),
          'telp': request.POST.get('telp')
        }
        
        if outlet_id:
          outlet = get_object_or_404(Outlet, id=outlet_id)
          for key, value in outlet_data.items():
            setattr(outlet, key, value)
          outlet.save()
          messages.success(request, 'Outlet berhasil diperbarui')
        else:
          Outlet.objects.create(**outlet_data)
          messages.success(request, 'Outlet berhasil ditambahkan')
          
        return redirect('admin_outlet')
    
    tambah = request.GET.get('tambah')
    if tambah:
      outlet_tambah = True
    else:
      outlet_tambah = False
      
    edit_id = request.GET.get('editId')
    if edit_id:
      outlet_edit = get_object_or_404(Outlet, id=edit_id)
      
    delete_id = request.GET.get('deleteId')
    if delete_id:
      outlet = get_object_or_404(Outlet, id=delete_id)
      outlet.delete()
      messages.success(request, 'Outlet berhasil dihapus')
      return redirect('admin_outlet')
    
    outlet_list = Outlet.objects.all()
    data_outlet = []
    for outlet in outlet_list:
      data_outlet.append({
        'id': outlet.id,
        'nama': outlet.nama,
        'alamat': outlet.alamat,
        'telp': outlet.telp
      })
      
    kolom_table_outlet = ['id', 'nama', 'alamat', 'telp']
    
    detail_config_outlet = {
      'fields': ['id', 'nama', 'alamat', 'telp'],
      'labels': {
        'id': 'ID:',
        'nama': 'Nama:',
        'alamat': 'Alamat:',
        'telp': 'No. HP:'
      }
    }
    
    context = {
      'table_data_outlet': data_outlet,
      'table_column_outlet': kolom_table_outlet,
      'detail_config_outlet': detail_config_outlet,
      'outlet_edit': outlet_edit,
      'outlet_tambah': outlet_tambah
    }
    return render(request, 'page/admin/outlet.html', context)

@login_required
@user_passes_test(is_admin) 
def admin_paket_cucian(request):
  paket_edit = None
  
  # Handle POST request untuk create/update
  if request.method == 'POST':
        paket_id = request.POST.get('paket_id')
        
        paket_data = {
          'nama_paket': request.POST.get('nama_paket'),
          'jenis': request.POST.get('jenis'),
          'harga': request.POST.get('harga'),
          'outlet_id': request.POST.get('outlet_id')
        }
        
        if paket_id:
          paket = get_object_or_404(Paket, id=paket_id)
          for key, value in paket_data.items():
            setattr(paket, key, value)
          paket.save()
          messages.success(request, 'Paket berhasil diperbarui')
        else:
          Paket.objects.create(**paket_data)
          messages.success(request, 'Paket berhasil ditambahkan')
          
        return redirect('admin_paket_cucian')


  # Handle GET request dengan parameter tambah
  tambah = request.GET.get('tambah')
  if tambah:
    paket_tambah = True
  else:
    paket_tambah = False
    
  # Handle GET request dengan parameter edit_id
  edit_id = request.GET.get('editId')
  if edit_id:
    paket_edit = get_object_or_404(Paket, id=edit_id)
    
  delete_id = request.GET.get('deleteId')
  if delete_id:
    paket = get_object_or_404(Paket, id=delete_id)
    paket.delete()
    messages.success(request, 'Paket berhasil dihapus')
    return redirect('admin_paket_cucian')

  paket_list = Paket.objects.all()
  data_paket = []
  for paket in paket_list:
    data_paket.append({
      'id': paket.id,
      'nama_paket': paket.nama_paket,
      'jenis': paket.jenis,
      'harga': paket.harga,
      'outlet': paket.outlet.nama
    })
    
  kolom_table_paket = ['id', 'nama_paket', 'jenis', 'harga', 'outlet']
  
  detail_config_paket = {
    'fields': ['id', 'nama_paket', 'jenis', 'harga', 'outlet'],
    'labels': {
      'id': 'ID:',
      'nama_paket': 'Nama Paket:',
      'jenis': 'Jenis:',
      'harga': 'Harga:',
      'outlet': 'Outlet:'
    }
  }
    
  context = {
    'table_data_paket': data_paket,
    'table_column_paket': kolom_table_paket,
    'detail_config_paket': detail_config_paket,
    'paket_edit': paket_edit,
    'paket_tambah': paket_tambah,
    'outlets': Outlet.objects.all()
  }
  
  return render(request, 'page/admin/paket_cucian.html', context)

@login_required
@user_passes_test(is_admin)
def admin_regis_pelanggan(request):
    pelanggan_edit = None
    
    #  Handle POST request untuk create/update
    if request.method == 'POST':
        pelanggan_id = request.POST.get('pelanggan_id')
        
        pelanggan_data = {
          'nama': request.POST.get('nama'),
          'alamat': request.POST.get('alamat'),
          'no_hp': request.POST.get('no_hp'),
        }
        
        if pelanggan_id:
          pelanggan = get_object_or_404(Pelanggan, id=pelanggan_id)
          for key, value in pelanggan_data.items():
            setattr(pelanggan, key, value)
          pelanggan.save()
          messages.success(request, 'Pelanggan berhasil diperbarui')
        else:
          Pelanggan.objects.create(**pelanggan_data)
          messages.success(request, 'Pelanggan berhasil ditambahkan')
          
        return redirect('admin_regis_pelanggan')
      
    # Handle GET request dengan parameter tambah
    tambah = request.GET.get('tambah')
    if tambah:
      pelanggan_tambah = True
    else:
      pelanggan_tambah = False
      
    edit_id = request.GET.get('editId')
    if edit_id:
      pelanggan_edit = get_object_or_404(Pelanggan, id=edit_id)

      
    delete_id = request.GET.get('deleteId')
    if delete_id:
      pelanggan = get_object_or_404(Pelanggan, id=delete_id)
      pelanggan.delete()
      messages.success(request, 'Pelanggan berhasil dihapus')
      return redirect('admin_regis_pelanggan')
    
    pelanggan_list = Pelanggan.objects.all()
    data_pelanggan = []
    for pelanggan in pelanggan_list:
      data_pelanggan.append({
        'id': pelanggan.id,
        'nama': pelanggan.nama,
        'alamat': pelanggan.alamat,
        'no_hp': pelanggan.no_hp
      })
      
    kolom_table_pelanggan = ['id', 'nama', 'alamat', 'no_hp']
    
    detail_config_pelanggan = {
      'fields': ['id', 'nama', 'alamat', 'no_hp'],
      'labels': {
        'id': 'ID:',
        'nama': 'Nama:',
        'alamat': 'Alamat:',
        'no_hp': 'No. HP:'
      }
    }
    
    context = {
      'table_data_pelanggan': data_pelanggan,
      'table_column_pelanggan': kolom_table_pelanggan,
      'detail_config_pelanggan': detail_config_pelanggan,
      'pelanggan_edit': pelanggan_edit,
      'pelanggan_tambah': pelanggan_tambah
    }
        
    return render(request, 'page/admin/regis_pelanggan.html', context)

@login_required
@user_passes_test(is_admin)
def admin_transaksi(request, transaksi_id=None):
    if transaksi_id:
        transaksi = get_object_or_404(Transaksi, id=transaksi_id)
        # Ambil ID paket yang terpilih
        selected_paket_ids = [dt.paket.id for dt in transaksi.detailtransaksi_set.all()]
        transaksi.selected_pakets_json = json.dumps(selected_paket_ids)
    else:
        transaksi = None
    
    transaksi_edit = None
    
    if request.method == 'POST':
        transaksi_id = request.POST.get('transaksi_id')
        
        # Convert total_harga ke integer
        try:
            total_harga = int(float(request.POST.get('total_harga', 0)))
        except (ValueError, TypeError):
            total_harga = 0
            
        transaksi_data = {
            'pelanggan': get_object_or_404(Pelanggan, id=request.POST.get('pelanggan')),
            'user': request.user,
            'outlet': get_object_or_404(Outlet, id=request.POST.get('outlet')),
            'total_harga': total_harga,
            'kode_invoice': request.POST.get('kode_invoice'),
            'tanggal': request.POST.get('tanggal'),
            'batas_waktu': request.POST.get('batas_waktu'),
            'tgl_bayar': request.POST.get('tgl_bayar'),
            'biaya_tambahan': request.POST.get('biaya_tambahan') if request.POST.get('biaya_tambahan') else 0,
            'diskon': request.POST.get('diskon') if request.POST.get('diskon') else 0,
            'pajak': request.POST.get('pajak') if request.POST.get('pajak') else 0,
            'status': request.POST.get('status'),
            'dibayar': request.POST.get('dibayar'),
        }

        # Handle member jika ada
        member_id = request.POST.get('member')
        if member_id:
            transaksi_data['member'] = get_object_or_404(Member, id=member_id)
        
        # Ambil ID paket dari form
        paket_ids = request.POST.get('paket').split(',') if request.POST.get('paket') else []
        
        if transaksi_id:
            # Ambil instance transaksi yang akan diupdate
            transaksi = get_object_or_404(Transaksi, id=transaksi_id)
            
            # Update transaksi
            for key, value in transaksi_data.items():
                setattr(transaksi, key, value)
            transaksi.save()
            
            # Hapus detail transaksi lama
            DetailTransaksi.objects.filter(transaksi=transaksi).delete()
            
            # Buat detail transaksi baru
            for paket_id in paket_ids:
                if paket_id:  # Pastikan paket_id tidak kosong
                    detail = DetailTransaksi.objects.create(
                        paket=get_object_or_404(Paket, id=paket_id),
                        keterangan=request.POST.get('keterangan', '')
                    )
                    detail.transaksi.add(transaksi)
            
            messages.success(request, 'Transaksi berhasil diperbarui')
        else:
            # Create new transaksi
            transaksi = Transaksi.objects.create(**transaksi_data)
            
            # Buat detail transaksi
            for paket_id in paket_ids:
                if paket_id:  # Pastikan paket_id tidak kosong
                    detail = DetailTransaksi.objects.create(
                        paket=get_object_or_404(Paket, id=paket_id),
                        keterangan=request.POST.get('keterangan', '')
                    )
                    detail.transaksi.add(transaksi)
            
            messages.success(request, 'Transaksi berhasil ditambahkan')
            
        return redirect('admin_transaksi')
      
    # Handle GET request dengan parameter tambah
    tambah = request.GET.get('tambah')
    if tambah:
      transaksi_tambah = True
    else:
      transaksi_tambah = False
      
    # Handle GET request dengan parameter edit_id
    edit_id = request.GET.get('editId')
    if edit_id:
        transaksi_edit = get_object_or_404(Transaksi, id=edit_id)
        transaksi_detail = DetailTransaksi.objects.filter(transaksi=transaksi_edit)
        
        # Dapatkan semua paket yang sudah digunakan di transaksi lain
        used_pakets = DetailTransaksi.objects.exclude(transaksi=transaksi_edit).values_list('paket_id', flat=True)
        
        # Filter paket yang belum digunakan + paket yang terpilih di transaksi ini
        available_pakets = Paket.objects.filter(
            Q(id__in=[dt.paket.id for dt in transaksi_detail]) |  # paket yang terpilih di transaksi ini
            ~Q(id__in=used_pakets)  # paket yang belum digunakan di transaksi lain
        )
        
        # Format data paket yang tersedia
        paket_data = [{
            'id': paket.id,
            'nama_paket': paket.nama_paket,
            'harga': float(paket.harga),
            'jenis': paket.jenis,
            'outlet': {
                'id': paket.outlet.id,
                'nama': paket.outlet.nama
            } if paket.outlet else None
        } for paket in available_pakets]
        
        # Ubah format data paket terpilih
        selected_pakets = []
        for detail in transaksi_detail:
            selected_pakets.append({
                'id': detail.paket.id,
                'nama_paket': detail.paket.nama_paket,
                'harga': float(detail.paket.harga),
                'jenis': detail.paket.jenis,
                'outlet': {
                    'id': detail.paket.outlet.id,
                    'nama': detail.paket.outlet.nama
                } if detail.paket.outlet else None
            })
        
        # Set selected_pakets_json untuk JavaScript
        transaksi_edit.selected_pakets_json = json.dumps(selected_pakets)
        
        # Format data transaksi untuk template
        transaksi_edit = {
            'id': transaksi_edit.id,
            'pelanggan': transaksi_edit.pelanggan,
            'user': transaksi_edit.user,
            'member': transaksi_edit.member,
            'outlet': transaksi_edit.outlet,
            'total_harga': transaksi_edit.total_harga,
            'kode_invoice': transaksi_edit.kode_invoice,
            'tanggal': transaksi_edit.tanggal.strftime('%Y-%m-%d') if transaksi_edit.tanggal else '',
            'batas_waktu': transaksi_edit.batas_waktu.strftime('%Y-%m-%d') if transaksi_edit.batas_waktu else '',
            'tgl_bayar': transaksi_edit.tgl_bayar.strftime('%Y-%m-%d') if transaksi_edit.tgl_bayar else '',
            'biaya_tambahan': transaksi_edit.biaya_tambahan,
            'diskon': transaksi_edit.diskon,
            'pajak': transaksi_edit.pajak,
            'status': transaksi_edit.status,
            'dibayar': transaksi_edit.dibayar,
            'selected_pakets_json': json.dumps(selected_pakets),
            'detail_transaksi_data': [{
                'paket': {
                    'id': detail.paket.id,
                    'nama_paket': detail.paket.nama_paket,
                    'harga': float(detail.paket.harga),
                    'jenis': detail.paket.jenis,
                    'outlet': {
                        'id': detail.paket.outlet.id,
                        'nama': detail.paket.outlet.nama
                    } if detail.paket.outlet else None
                },
                'keterangan': detail.keterangan,
            } for detail in transaksi_detail]
        }
    else:
        # Untuk kasus tambah transaksi baru
        # Ambil hanya paket yang belum digunakan di transaksi manapun
        used_pakets = DetailTransaksi.objects.values_list('paket_id', flat=True)
        available_pakets = Paket.objects.exclude(id__in=used_pakets)
        
        paket_data = [{
            'id': paket.id,
            'nama_paket': paket.nama_paket,
            'harga': float(paket.harga),
            'jenis': paket.jenis,
            'outlet': {
                'id': paket.outlet.id,
                'nama': paket.outlet.nama
            } if paket.outlet else None
        } for paket in available_pakets]
        
        transaksi_edit = None

    # Handle GET request dengan parameter delete_id
    delete_id = request.GET.get('deleteId')
    if delete_id:
      transaksi = get_object_or_404(Transaksi, id=delete_id)
      transaksi_detail = DetailTransaksi.objects.filter(transaksi=transaksi)
      transaksi_detail.delete()
      transaksi.delete()
      messages.success(request, 'Transaksi berhasil dihapus')
      return redirect('admin_transaksi')
    
    # Ambil semua data transaksi untuk tabel
    transaksi_list = Transaksi.objects.all()
    formatted_data = [format_transaksi_data(transaksi) for transaksi in transaksi_list]
    
    # Definisikan kolom tabel
    kolom_table_transaksi = [
      'id',
      'pelanggan',
      'member',
      'outlet',
      'total_harga',
      'kode_invoice',
      'tanggal',
      'batas_waktu',
      'tgl_bayar',
      'biaya_tambahan',
      'diskon',
      'pajak',
      'status',
      'dibayar'
    ]
    
    # Konfigurasi detail untuk modal
    detail_config_transaksi = {
      'fields': ['id', 'pelanggan', 'user', 'keterangan', 'member', 'outlet', 'total_harga', 'kode_invoice', 'tanggal', 'batas_waktu', 'tgl_bayar', 'biaya_tambahan', 'diskon', 'pajak', 'status', 'dibayar', 'detail_transaksi'],
      'labels': {
        'id': 'ID:',
        'pelanggan': 'Pelanggan:',
        'user': 'User:',
        'keterangan': 'Keterangan:',
        'member': 'Member:',
        'outlet': 'Outlet:',
        'total_harga': 'Total Harga:',
        'kode_invoice': 'Kode Invoice:',
        'tanggal': 'Tanggal:',
        'batas_waktu': 'Batas Waktu:',
        'tgl_bayar': 'Tanggal Bayar:',
        'biaya_tambahan': 'Biaya Tambahan:',
        'diskon': 'Diskon:',
        'pajak': 'Pajak:',
        'status': 'Status:',
        'dibayar': 'Dibayar:',
        'detail_transaksi': 'Detail Transaksi:',
      },
      'groups': {
        'Informasi Transaksi:': ['pelanggan', 'user', 'member', 'outlet', 'total_harga', 'kode_invoice', 'tanggal', 'batas_waktu', 'tgl_bayar', 'biaya_tambahan', 'diskon', 'pajak', 'status', 'dibayar'],
        'Detail Transaksi:': ['detail_transaksi'],
      }
    }
    
    context = {
        'table_data_transaksi': formatted_data,
        'table_data_transaksi_js': json.dumps(formatted_data),
        'table_column_transaksi': kolom_table_transaksi,
        'detail_config_transaksi': detail_config_transaksi,
        'transaksi_edit': transaksi_edit,
        'transaksi_tambah': transaksi_tambah,
        'outlets': Outlet.objects.all(),
        'members': Member.objects.all(),
        'pelanggan': Pelanggan.objects.all(),
        'paket_list_json': json.dumps(paket_data),
    }
      
    return render(request, 'page/admin/transaksi.html', context)

def format_transaksi_data(transaksi):
    return {
        'id': transaksi.id,
        'pelanggan': transaksi.pelanggan.nama,  # mengambil nama pelanggan
        'user': transaksi.user.username,  # mengambil username
        'member': transaksi.member.nama if transaksi.member else None,
        'outlet': transaksi.outlet.nama,  # mengambil nama outlet
        'total_harga': transaksi.total_harga,
        'kode_invoice': transaksi.kode_invoice,
        'tanggal': transaksi.tanggal.strftime('%Y-%m-%d'),
        'batas_waktu': transaksi.batas_waktu.strftime('%Y-%m-%d'),
        'tgl_bayar': transaksi.tgl_bayar.strftime('%Y-%m-%d'),
        'biaya_tambahan': transaksi.biaya_tambahan,
        'diskon': transaksi.diskon,
        'pajak': transaksi.pajak,
        'status': transaksi.status,
        'dibayar': transaksi.dibayar,
        'detail_transaksi': [
            {
                'paket': detail.paket.nama_paket,  # mengambil nama paket
                'harga': detail.paket.harga,
                'jenis': detail.paket.jenis,
                'outlet': detail.paket.outlet.nama
            }
            for detail in transaksi.detailtransaksi_set.all()
        ]
    }

@login_required
@user_passes_test(is_admin)
def admin_pengguna(request):
    user_edit = None
    
    # Handle POST request untuk create/update
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        
        # Data yang akan disimpan
        user_data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'role': request.POST.get('role'),
            'outlet_id': request.POST.get('outlet'),
            'is_active': request.POST.get('is_active') == 'on'
        }
        
        # Jika password diisi
        if request.POST.get('password'):
            user_data['password'] = request.POST.get('password')
            
        if user_id:  # Update existing user
            user = get_object_or_404(User, id=user_id)
            for key, value in user_data.items():
                if key == 'password':
                    user.set_password(value)
                else:
                    setattr(user, key, value)
            user.save()
            messages.success(request, 'Pengguna berhasil diperbarui')
        else:  # Create new user
            User.objects.create_user(**user_data)
            messages.success(request, 'Pengguna berhasil ditambahkan')
            
        return redirect('admin_pengguna')
      
    tambah = request.GET.get('tambah')
    if tambah:
        user_tambah = True
    else:
        user_tambah = False
        
    # Handle GET request dengan parameter edit_id
    edit_id = request.GET.get('editId')
    if edit_id:
        user_edit = get_object_or_404(User, id=edit_id)
        user_edit = get_user_data(user_edit)
    
    # Handle GET request dengan parameter delete_id
    delete_id = request.GET.get('deleteId')
    if delete_id:
        user = get_object_or_404(User, id=delete_id)
        user.delete()
        messages.success(request, 'Pengguna berhasil dihapus')
        return redirect('admin_pengguna')
    
    # Ambil semua data user untuk tabel
    users = User.objects.all()
    data_user = []
    for user in users:
        data_user.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'outlet': user.outlet.nama if user.outlet else '-',
            'is_active': 'Aktif' if user.is_active else 'Tidak Aktif',
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '-'
        })
    
    # Definisikan kolom tabel
    kolom_table_user = ['id', 'username', 'email', 'role', 'outlet', 'is_active', 'last_login']
    
    # Konfigurasi detail untuk modal
    detail_config_user = {
        'fields': ['id', 'username', 'email', 'role', 'outlet', 'is_active', 'last_login'],
        'labels': {
            'id': 'ID:',
            'username': 'Username:',
            'email': 'Email:',
            'role': 'Role:',
            'outlet': 'Outlet:',
            'is_active': 'Status:',
            'last_login': 'Login Terakhir:'
        },
        'groups': {
            'Informasi Akun:': ['username', 'email', 'role'],
            'Status & Outlet:': ['is_active', 'outlet'],
            'Info Login:': ['last_login']
        }
    }

    context = {
        'table_data_user': data_user,
        'table_column_user': kolom_table_user,
        'detail_config_user': detail_config_user,
        'user_edit': user_edit,
        'user_tambah': user_tambah,
        'outlets': Outlet.objects.all()
    }
    
    return render(request, 'page/admin/pengguna.html', context)
