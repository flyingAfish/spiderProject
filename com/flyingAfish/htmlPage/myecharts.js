// 基于准备好的dom，初始化echarts实例
var myChart = echarts.init(document.getElementById('echarts_id'));

// 显示标题，图例和空的坐标轴
option = {
    title: {
        text: '异步数据加载示例'
    },
    tooltip: {},
    legend: {
        data:['销量']
    },
    xAxis: {
        data: []
    },
    yAxis: {},
    series: [{
        name: '销量',
        type: 'bar',
        data: []
    }]
};

// 使用刚指定的配置项和数据显示图表。
myChart.setOption(option);

myChart.showLoading();
// 异步加载数据
$.get('data.json').done(function (data) {
    myChart.hideLoading();
    // 填入数据
    myChart.setOption({
        xAxis: {
            data: data.categories
        },
        series: [{
            // 根据名字对应到相应的系列
            name: '销量',
            data: data.data
        }]
    });
});

//        setInterval(function () {
//
//            for (var i = 0; i < 5; i++) {
//                data.shift();
//                data.push(randomData());
//            }
//
//            myChart.setOption({
//                series: [{
//                    data: data
//                }]
//            });
//        }, 1000);

