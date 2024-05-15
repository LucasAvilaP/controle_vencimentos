
      document.addEventListener('DOMContentLoaded', function () {
          const categoriaData = JSON.parse(document.getElementById('categoriaData').textContent);
          const rawData = JSON.parse(document.getElementById('statusData').textContent);
          console.log("Status Data:", statusData);
      
          const ctx1 = document.getElementById('categoriaChart').getContext('2d');
          const categoriaChart = new Chart(ctx1, {
              type: 'pie',
              data: {
                  labels: categoriaData.map(data => data[0]),
                  datasets: [{
                      label: 'Quantidade por Categoria',
                      data: categoriaData.map(data => data[1]),
                      backgroundColor: [
                          'rgba(255, 99, 132, 0.2)',
                          'rgba(54, 162, 235, 0.2)',
                          'rgba(255, 206, 86, 0.2)',
                          'rgba(75, 192, 192, 0.2)',
                          'rgba(153, 102, 255, 0.2)',
                          'rgba(255, 159, 64, 0.2)'
                      ],
                      borderColor: [
                          'rgba(255, 99, 132, 1)',
                          'rgba(54, 162, 235, 1)',
                          'rgba(255, 206, 86, 1)',
                          'rgba(75, 192, 192, 1)',
                          'rgba(153, 102, 255, 1)',
                          'rgba(255, 159, 64, 1)'
                      ],
                      borderWidth: 1
                  }]
              },
              options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                      legend: {
                          position: 'top',
                      },
                      title: {
                          display: true,
                          text: 'Distribuição de Lotes por Categoria'
                      }
                  }
              }
          });
      
         function prepareChartData(data) {
            return {
                labels: data.map(item => item[0]),
                datasets: [{
                    label: 'Quantidade por Status',
                    data: data.map(item => item[1]),
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.2)',   // Válido
                        'rgba(255, 99, 132, 0.2)',   // Vencido
                        'rgba(50, 206, 86, 0.2)',   // Próximo do Vencimento
                        'rgba(54, 162, 235, 0.2)'    // Urgente
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(54, 162, 235, 1)'
                    ],
                    borderWidth: 1
                }]
            };
        }
    
        const chartData = prepareChartData(rawData);
    
        const ctx = document.getElementById('statusChart').getContext('2d');
        const statusChart = new Chart(ctx, {
            type: 'pie',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Distribuição de Lotes por Status'
                    }
                }
            }
        });
    });
      

      
  