class TimeChart {
    constructor(elementId) {
        this.elementId = elementId;
        this.normalTime = 100;
        this.abnormalTime = 0;
        this.ctx = document.getElementById(this.elementId).getContext("2d");
//        this.createChart();
    }

    createChart() {
        this.chart = new Chart(this.ctx, {
            type: 'doughnut',   // 圆环图
            data: {             // 图标数据
                labels: ['正常时间', '异常时间'],
                datasets: [{
                    label: '时间占比',
                    data: [this.normalTime, this.abnormalTime],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(255, 99, 132, 0.2)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1   // 边框宽度
                }]
            },
            options: {
                responsive: true,            // 图表会根据容器大小进行响应式调整
                maintainAspectRatio: false,  // 不保持纵横比
                cutoutPercentage: 70,        // 圆环内部空白的百分比
                animation: {                 // 控制动画效果
                    animateScale: true,
                    animateRotate: true      // 放大和旋转的动画效果为开启状态
                }
            }
        });
    }

    updateChartData(newNormalTime, newAbnormalTime) {
        if (newNormalTime <= 0 && newAbnormalTime <= 0) {
            this.chart.data.datasets[0].data = [100, 0]
        } else {
            let normalizedNormalTime = (newNormalTime * 100 / (newNormalTime + newAbnormalTime)).toFixed(1)
            this.chart.data.datasets[0].data = [normalizedNormalTime, 100 - normalizedNormalTime];
        }
        this.chart.update();
    }

}
