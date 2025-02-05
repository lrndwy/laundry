from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate, TruncMonth
from apps.laundryApp.models import *
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.db.models import Q

def is_owner(user):
    return user.role == 'owner'

@login_required
@user_passes_test(is_owner)
def owner_dashboard(request):
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
    
    return render(request, 'page/owner/dashboard.html', context)

@login_required
def cetak_laporan(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    # Jika tanggal tidak ada, gunakan rentang 30 hari terakhir
    if not start or not end:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        start = start_date.strftime('%Y-%m-%d')
        end = end_date.strftime('%Y-%m-%d')
    else:
        # Konversi string tanggal ke objek date
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()

    # Query transaksi yang sudah dibayar dalam rentang waktu
    transaksi_qs = Transaksi.objects.filter(
        dibayar='dibayar',
        created_at__date__range=[start_date, end_date]
    )

    # Hitung data untuk grafik
    transaksi_per_hari = transaksi_qs.annotate(
        tgl=TruncDate('created_at')
    ).values('tgl').annotate(
        total=Count('id'),
        pendapatan=Sum('total_harga')
    ).order_by('tgl')

    # Buat list tanggal untuk grafik
    date_list = []
    current = start_date
    while current <= end_date:
        date_list.append(current)
        current += timedelta(days=1)

    # Format data grafik
    chart_data = {
        'labels': [d.strftime('%d %b %Y') for d in date_list],
        'pendapatan': [],
        'transaksi': []
    }

    # Dictionary untuk lookup data transaksi
    transaksi_dict = {t['tgl']: t for t in transaksi_per_hari}

    # Isi data grafik
    for date in date_list:
        if date in transaksi_dict:
            chart_data['pendapatan'].append(float(transaksi_dict[date]['pendapatan']))
            chart_data['transaksi'].append(transaksi_dict[date]['total'])
        else:
            chart_data['pendapatan'].append(0)
            chart_data['transaksi'].append(0)

    # Statistik umum
    stats = {
        'total_transaksi': transaksi_qs.count(),
        'total_pendapatan': transaksi_qs.aggregate(Sum('total_harga'))['total_harga__sum'] or 0,
    }

    # Statistik per outlet
    outlet_stats = Outlet.objects.annotate(
        jumlah_transaksi=Count('transaksi', 
            filter=Q(transaksi__dibayar='dibayar', 
                    transaksi__created_at__date__range=[start_date, end_date])),
        pendapatan=Sum('transaksi__total_harga',
            filter=Q(transaksi__dibayar='dibayar', 
                    transaksi__created_at__date__range=[start_date, end_date])),
        rata_rata_transaksi=Avg('transaksi__total_harga',
            filter=Q(transaksi__dibayar='dibayar', 
                    transaksi__created_at__date__range=[start_date, end_date]))
    )

    context = {
        'stats': stats,
        'outlet_stats': outlet_stats,
        'start_date': start,
        'end_date': end,
        'chart_data': json.dumps(chart_data)
    }
    
    return render(request, 'page/owner/cetak_laporan.html', context)
