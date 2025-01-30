# Table Component

## Usage
### HTML Usage
```html
<html>
    <body>
        {% include 'components/table.html' with 
            table_id="laundryTable"
            table_data=table_data_laundry 
            table_column=table_column_laundry 
            show_export=True
            show_print=True
        %}
        <script>
          // Inisialisasi tabel Laundry
          const tableLaundry = new Table({
              tableId: 'laundryTable',
              data: {{ table_data_laundry|safe }},
              columns: {{ table_column_laundry|safe }},
              filters: [
                  {
                      field: 'status',
                      label: 'Status'
                  },
                  {
                      field: 'jenis_laundry',
                      label: 'Jenis Laundry'
                  }
              ],
              detailConfig: {{ detail_config_laundry|safe }}
          });
        </script>
    </body>   
</html>
```

### in views
```python
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

```


# Dashboard Layouts

## Usage with django-cotton

```html
<div class="flex flex-col h-screen bg-gray-50">
  <c-dashboard-layouts></c-dashboard-layouts>
  <!-- Main Content -->
  <main class="p-4 sm:ml-64">
      <div class="p-4 border-2 border-gray-200 rounded-lg">
          <div class="grid grid-cols-1 gap-4 mb-4">
              <div class="text-2xl font-bold">
                  Dashboard Content
              </div>
          </div>
      </div>
  </main>
</div>

<script src="{% static 'js/flyonui.js' %}"></script>
```
