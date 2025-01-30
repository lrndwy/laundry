from django.db import models
from django.contrib.auth.models import AbstractUser

class Pelanggan(models.Model):
    nama = models.CharField(max_length=100)
    alamat = models.TextField(blank=True, null=True)
    no_hp = models.CharField(max_length=25, blank=True, null=True)
    tanggal_waktu = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama
    
    class Meta:
        verbose_name_plural = 'Pelanggan'

class Outlet(models.Model):
    nama = models.CharField(max_length=100)
    alamat = models.TextField()
    telp = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama
      
    class Meta:
        verbose_name_plural = 'Outlet'
        
    

class Paket(models.Model):
    JENIS_PAKET = (
        ('kiloan', 'Kiloan'),
        ('selimut', 'Selimut'),
        ('bed_cover', 'Bed Cover'),
        ('kaos', 'Kaos'),
        ('lainnya', 'Lainnya'),
    )      
    
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    jenis = models.CharField(max_length=100, choices=JENIS_PAKET)
    nama_paket = models.CharField(max_length=100)
    harga = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_paket
      
    class Meta:
        verbose_name_plural = 'Paket'

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('kasir', 'Kasir'),
        ('owner', 'Owner'),
    )
    
    outlet = models.ForeignKey(Outlet, null=True, blank=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')

    def save(self, *args, **kwargs):
        if self.role == 'admin':
            self.is_superuser = True
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
      
      
class Member(models.Model):
    nama_member = models.CharField(max_length=100)
    alamat = models.TextField(blank=True, null=True)
    telp = models.CharField(max_length=25, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_member
      
    class Meta:
        verbose_name_plural = 'Member'


class Transaksi(models.Model):
    STATUS_TRANSAKSI = (
        ('baru', 'Baru'),
        ('proses', 'Proses'),
        ('selesai', 'Selesai'),
        ('diambil', 'Diambil'),
    )
    DIBAYAR_CHOICES = (
        ('dibayar', 'Dibayar'),
        ('belum_dibayar', 'Belum Dibayar'),
    )
    
    pelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, blank=True, null=True)
    total_harga = models.IntegerField(blank=True, null=True)
    kode_invoice = models.CharField(max_length=100, blank=True, null=True)
    tanggal = models.DateTimeField(auto_now_add=True)
    batas_waktu = models.DateTimeField(blank=True, null=True)
    tgl_bayar = models.DateTimeField(auto_now_add=True)
    biaya_tambahan = models.IntegerField(blank=True, null=True)
    diskon = models.IntegerField(blank=True, null=True)
    pajak = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_TRANSAKSI, default='baru')
    dibayar = models.CharField(max_length=20, choices=DIBAYAR_CHOICES, default='belum_dibayar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.kode_invoice
      
    def save(self, *args, **kwargs):
        if not self.user_id and hasattr(self, '_current_user'):
            self.user = self._current_user
        super().save(*args, **kwargs)
        
    @property
    def user_role(self):
        return self.user.role
      
    class Meta:
        verbose_name_plural = 'Transaksi'


class DetailTransaksi(models.Model):
    transaksi = models.ManyToManyField(Transaksi)
    paket = models.ForeignKey(Paket, on_delete=models.CASCADE)
    keterangan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaksi.kode_invoice
      
    class Meta:
        verbose_name_plural = 'Detail Transaksi'
        



