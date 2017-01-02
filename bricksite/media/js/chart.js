function showLineChartC3(bindto, columns, width) {
    c3.generate({
        bindto: bindto,
        data: {
            x: 'date',
            columns: columns
        },
        size: {
            width: width
        },
        padding: {
            right: 20
        },
        axis: {
            y: {
                tick: {
                    format: function (d) {
                        var df = Number( d3.format('.3f')(d) );
                        return df;
                    }
                }
            },
            x: {
                type : 'timeseries',
                tick: {
                    format: '%Y-%m-%d'
                }
            }
        }
    });
}